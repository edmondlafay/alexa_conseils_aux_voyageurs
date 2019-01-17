# -*- coding: utf-8 -*-
"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
import json, unicodedata
from botocore.vendored import requests
from bs4 import BeautifulSoup

DEBUG = False
STATUS_URL = "https://voyage.gc.ca/destinations/"
SPECIAL_COUNTRIES_INPUT = {
    'angleterre': 'royaume-uni',
    'brezil': 'bresil',
    'canada': 'etats-unis',
    'centrafrique': 'republique-centrafricaine',
    'congo': 'congo-kinshasa',
    'coree': 'coree-sud',
    'coree-du-sud': 'coree-sud',
    'coree-du-nord': 'coree-nord-rpdc',
    'emirats': 'emirats-arabes-unis',
    'gaza': 'israel-la-cisjordanie-et-la-bande-de-gaza',
    'hollande':'pays-bas',
    'iles-caimans':'caimans-iles',
    'ile-maurice': 'maurice-ile',
    'israel': 'israel-la-cisjordanie-et-la-bande-de-gaza',
    'soudan-du-sud': 'sudan-du-sud',
    'trinite': 'trinite-et-tobago'
}
SPECIAL_COUNTRIES_OUTPUT = {
    'belgique': {'key': 'prudence Belgique', 'val': ' prudence en Belgique'},
    'canada': {'key': 'aux États-Unis', 'val': ' au Canada'},
    'coree-du-nord': {'key': 'Le gouvernement canadien n’a pas de bureau en Corée du Nord. ', 'val': 'Peu de bureaux consulaires sont présents dans le pays. '},
    'ile-maurice': {'key': ' de Maurice', 'val': " à l'île Maurice"}
}

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {'type': 'PlainText', 'text': output},
        'card': {'type': 'Simple', 'title': title, 'content': output},
        'reprompt': {'outputSpeech': {'type': 'PlainText', 'text': reprompt_text}},
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes, 'response': speechlet_response
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
        reprompt_text = "Demandez le status d'un pays en disant: Alexa, demande à Conseils Aux Voyageurs quel est le status de la France."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output + reprompt_text, reprompt_text, should_end_session))


def fetch_info_for(raw_country):
    country = ''.join((c for c in unicodedata.normalize('NFD', raw_country) if unicodedata.category(c) != 'Mn'))
    country = country.replace(u' ', u'-').replace(u"'", u'-')
    if country in SPECIAL_COUNTRIES_INPUT:
        page = requests.get(STATUS_URL + SPECIAL_COUNTRIES_INPUT[country])
    else:
        page = requests.get(STATUS_URL + country)
    if page.status_code == 200:
        advisories = BeautifulSoup(page.content, 'html.parser').find(id='advisories')
        if advisories:
            advice = advisories.find("p")
            if advice:
                res = ' '.join(advice.stripped_strings).replace(u'\xa0', u' ')
                if country in SPECIAL_COUNTRIES_OUTPUT:
                    res = res.replace(SPECIAL_COUNTRIES_OUTPUT[country]['key'], SPECIAL_COUNTRIES_OUTPUT[country]['val'])
                res = res.replace(u'(voir ci-dessous)', u'')
                res = res.replace(u' du Canada ', u' ')
                res = res.replace(u"Inscrivez-vous auprès du service d’inscription des Canadiens à l’étranger et lisez attentivement les messages diffusés par celui-ci. Situation en matière de sécurité Inscription des Canadiens à l’étranger", u' ')
                return res
    return ''


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
    country_not_found = True
    reprompt_text = "Rendez-vous sur diplomatie.gouv.fr ou voyage.gc.ca section conseils aux voyageurs pour des informations detaillées en français."

    if 'paysFR' in intent['slots']:
        country = intent['slots']['paysFR']['value']
        print("COUNTRY {}".format(country))
        session_attributes = {"country": country}
        res = fetch_info_for(country)
        if len(res)>5:
            country_not_found = False
            speech_output = "{} ".format(res)
    
    if country_not_found:
        print("UNKNOWN intent CountryStatusIntent slotes : {}".format(json.dumps(intent['slots'])))
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output + reprompt_text, reprompt_text, should_end_session))


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
