# -*- coding: utf-8 -*-
import json, unicodedata, re
import countries
from botocore.vendored import requests
from bs4 import BeautifulSoup

DEBUG = False
STATUS_URL = "https://voyage.gc.ca/destinations/"
SPECIAL_COUNTRIES_OUTPUT = {
    'belgique': {'key': 'prudence Belgique', 'val': ' prudence en Belgique'},
    'canada': {'key': 'aux États-Unis', 'val': ' au Canada'},
    'coree-du-nord': {'key': 'Le gouvernement canadien n’a pas de bureau en Corée du Nord. ', 'val': 'Peu de bureaux consulaires sont présents dans le pays. '},
    'ile-maurice': {'key': ' de Maurice', 'val': " à l'île Maurice"}
}

# --------------- Helpers that build all of the responses ----------------------

def ssml_to_text(ssml):
    """ Remove all ssml tags
    """
    return re.sub(r"<[^>]+>", "", ssml)

def build_response(session_attributes, title, output, reprompt_text, should_end_session):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes, 'response': {
            'outputSpeech': {'type': 'SSML', 'ssml': "<speak>{}</speak>".format(output)},
            'card': {'type': 'Simple', 'title': title, 'content': ssml_to_text(output)},
            'reprompt': {'outputSpeech': {'type': 'SSML', 'ssml': "<speak>{}</speak>".format(reprompt_text)}},
            'shouldEndSession': should_end_session
        }
    }

# --------------- Functions that control the skill's behavior ------------------

def get_start_end_response(should_end_session):
    session_attributes = {}
    if should_end_session:
        card_title = "Bon voyage!"
        speech_output = ""
        reprompt_text = "Bon voyage!"
    else:
        card_title = "Conseils aux voyageurs"
        speech_output = "Bienvenue a conseils aux voyageurs. "
        reprompt_text = "Demandez le status d'un pays en disant: " \
        "Alexa, demande à Conseils Aux Voyageurs le status de la France."

    return build_response(session_attributes, 
        card_title, speech_output + reprompt_text, reprompt_text, should_end_session)


def clean_country(raw_country):
    """
        Remove leading "l'", all accents, spaces and quotes.
    """
    #
    if raw_country[0:2]=="l'":
        raw_country = raw_country[2:]
    country = ''.join((c for c in unicodedata.normalize('NFD', raw_country) if unicodedata.category(c) != 'Mn'))
    country = re.sub(r"(\s|')", "-", country) # replace space and quotes with dash
    return country
  

def clean_output(text):
  res = text.replace(u'(voir ci-dessous)', u'')
  res = text.replace(u'ci-dessous', u'suivant')
  res = res.replace(u' du Canada ', u' ')
  res = res.replace(u' aux Canadiens ', u' aux voyageurs ')
  res = res.replace(u"du service d’Inscription des Canadiens à l’étranger", u'de votre représentant consulaire')
  res = res.replace(u';', ',')
  res.replace(u"Situation en matière de sécurité Inscription des Canadiens à l’étranger", u'')
  return re.sub(r"(\s\s+|\s$)", "", res) # remove extra whitespaces


def fetch_info_for(raw_country):
    country = clean_country(raw_country)
    if country in countries.SPECIAL_COUNTRIES_INPUT:
        page = requests.get(STATUS_URL + countries.SPECIAL_COUNTRIES_INPUT[country]["c"])
        if page.status_code == 200:
            advisories = BeautifulSoup(page.content, 'html.parser').find(id='advisories')
            if advisories:
                empty_tags = advisories.find_all(href="#securite")
                if empty_tags:
                    for empty_tag in empty_tags:
                        empty_tag.clear()
                advices = advisories('p')
                if advices:
                    advice_array = []
                    for advice in advices:
                        advice_array.append("{}".format(advice))
                    res = BeautifulSoup("".join(advice_array)).get_text(' ', strip=True)
                    if country in SPECIAL_COUNTRIES_OUTPUT:
                        res = res.replace(SPECIAL_COUNTRIES_OUTPUT[country]['key'], SPECIAL_COUNTRIES_OUTPUT[country]['val'])
                    return clean_output(res)
    return ''


def clean_country_info_intent(speech):
    # https://regex101.com/r/uzNDps/1/
    res = re.sub(r"(aller|situation|statut|statue|status)\s(a|à|a|a|du|de)(u|x|s| la)*\s", '', speech)
    return res

def get_country_info(intent, session):
    """ Fetch country status from voyage.gc.ca
    """
    # "intent": { "name": "CountryStatusIntent", "confirmationStatus": "NONE", "slots": {
    # "paysFR": { "name": "paysFR", "value": "france", "confirmationStatus": "NONE", "source": "USER" } } }
    if DEBUG:
        print("intent CountryStatusIntent slotes : {}".format(json.dumps(intent['slots'])))

    card_title = "Status du pays"
    session_attributes = {}
    should_end_session = True
    speech_output = "Je n'ai pas d'information pour le pays demandé. "
    reprompt_text = "Rendez-vous sur diplomatie.gouv.fr, " \
    "ou voyage<say-as interpret-as='spell-out'>.gc.ca</say-as>, " \
    "section conseils aux voyageurs pour plus d'informations."

    if 'paysFR' in intent['slots']:
        print("COUNTRY {}".format(intent['slots']['paysFR']))
        country = clean_country_info_intent(intent['slots']['paysFR']['value'])
        session_attributes = {"country": country}
        res = fetch_info_for(country)
        if len(res)>5:
            speech_output = "{} ".format(res)
        else:
            speech_output = "Je n'ai pas d'information pour le pays {}. ".format(country)
            print("UNKNOWN intent CountryStatusIntent slotes : {}".format(json.dumps(intent['slots'])))
        
    return build_response(session_attributes, card_title, 
        speech_output + reprompt_text, speech_output, should_end_session)


# --------------- Events ------------------

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "CountryStatusIntent":
        return get_country_info(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_start_end_response(False)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return get_start_end_response(True)
    else:
        return get_start_end_response(False)


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    if DEBUG:
        print("event : {}".format(json.dumps(event)))

    if event['session']['new']:
        if DEBUG:
            print("on_session_started requestId=" + event['request']['requestId'] + ", sessionId=" + event['session']['sessionId'])
    if event['request']['type'] == "LaunchRequest":
        if DEBUG:
            print("on_launch requestId=" + event['request']['requestId'] + ", sessionId=" + event['session']['sessionId'])
        return get_start_end_response(False)
    elif event['request']['type'] == "IntentRequest":
        if DEBUG:
            print("on_intent requestId=" + event['request']['requestId'] + ", sessionId=" + event['session']['sessionId'])
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        if DEBUG:
            print("on_session_ended requestId=" + event['request']['requestId'] + ", sessionId=" + event['session']['sessionId'])
