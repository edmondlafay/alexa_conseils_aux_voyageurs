# -*- coding: utf-8 -*-
import json, unicodedata, re
from botocore.vendored import requests
from bs4 import BeautifulSoup

DEBUG = False
STATUS_URL = "https://voyage.gc.ca/destinations/"
SPECIAL_COUNTRIES_INPUT = {
  "acores":{"c":"acores","f":""},
  "afghanistan":{"c":"afghanistan","f":"afghanistan"},
  "afrique-du-sud":{"c":"afrique-du-sud","f":"afrique-du-sud"},
  "albanie":{"c":"albanie","f":"albanie"},
  "algerie":{"c":"algerie","f":"algerie"},
  "allemagne":{"c":"allemagne","f":"allemagne"},
  "andorre":{"c":"andorre","f":"andorre"},
  "angleterre":{"c":"royaume-uni","f":"royaume-uni"},
  "angola":{"c":"angola","f":"angola"},
  "anguilla":{"c":"anguilla","f":""},
  "antarctique":{"c":"antarctique","f":"antarctique"},
  "antigua":{"c":"antigua-et-barbuda","f":"antigua-et-barbuda"},
  "antigua-et-barbuda":{"c":"antigua-et-barbuda","f":"antigua-et-barbuda"},
  "arabie-saoudite":{"c":"arabie-saoudite","f":"arabie-saoudite"},
  "argentine":{"c":"argentine","f":"argentine"},
  "armenie":{"c":"armenie","f":"armenie"},
  "aruba":{"c":"aruba","f":""},
  "assores":{"c":"acores","f":""},
  "australie":{"c":"australie","f":"australie"},
  "autriche":{"c":"autriche","f":"autriche"},
  "azerbaidjan":{"c":"azerbaidjan","f":"azerbaidjan"},
  "bahamas":{"c":"bahamas","f":"bahamas"},
  "bahrein":{"c":"bahrein","f":"bahrein"},
  "bangladesh":{"c":"bangladesh","f":"bangladesh"},
  "barbade":{"c":"barbade","f":"barbade"},
  "barbuda":{"c":"antigua-et-barbuda","f":"antigua-et-barbuda"},
  "belarus":{"c":"belarus","f":""},
  "belgique":{"c":"belgique","f":"belgique"},
  "belize":{"c":"belize","f":"belize"},
  "benin":{"c":"benin","f":"benin"},
  "bermudes":{"c":"bermudes","f":""},
  "bhoutan":{"c":"bhoutan","f":"bhoutan"},
  "bielorussie":{"c":"belarus","f":"bielorussie"},
  "birmanie":{"c":"myanmar","f":"birmanie"},
  "bolivie":{"c":"bolivie","f":"bolivie"},
  "bonaire":{"c":"bonaire","f":""},
  "bosnie":{"c":"bosnie-herzegovine","f":"bosnie-herzegovine"},
  "bosnie-herzegovine":{"c":"bosnie-herzegovine","f":"bosnie-herzegovine"},
  "botswana":{"c":"botswana","f":"botswana"},
  "bresil":{"c":"bresil","f":"bresil"},
  "brezil":{"c":"bresil","f":"bresil"},
  "brunei":{"c":"brunei-darussalam","f":"brunei"},
  "bulgarie":{"c":"bulgarie","f":"bulgarie"},
  "burkina-faso":{"c":"burkina-faso","f":"burkina-faso"},
  "burundi":{"c":"burundi","f":"burundi"},
  "cabo-verde":{"c":"cabo-verde","f":""},
  "cambodge":{"c":"cambodge","f":"cambodge"},
  "cameroun":{"c":"cameroun","f":"cameroun"},
  "canada":{"c":"canada","f":"canada-quebec-compris"},
  "canaries":{"c":"iles-canaries","f":""},
  "centrafrique":{"c":"republique-centrafricaine","f":"republique-centrafricaine"},
  "chili":{"c":"chili","f":"chili"},
  "chine":{"c":"chine","f":"chine"},
  "chypre":{"c":"chypre","f":"chypre"},
  "colombie":{"c":"colombie","f":"colombie"},
  "comores":{"c":"comores","f":"comores"},
  "congo":{"c":"congo-brazzaville","f":"congo"},
  "coree":{"c":"coree-sud","f":"coree-du-sud"},
  "coree-du-nord":{"c":"coree-nord-rpdc","f":"coree-du-nord"},
  "coree-du-sud":{"c":"coree-sud","f":"coree-du-sud"},
  "costa-rica":{"c":"costa-rica","f":"costa-rica"},
  "costarica":{"c":"costa-rica","f":"costa-rica"},
  "cote-d-ivoire":{"c":"cote-d-ivoire","f":"cote-d-ivoire"},
  "cote-divoire":{"c":"cote-d-ivoire","f":"cote-d-ivoire"},
  "croatie":{"c":"croatie","f":"croatie"},
  "cuba":{"c":"cuba","f":"cuba"},
  "curacao":{"c":"curacao","f":""},
  "curassoa":{"c":"curacao","f":""},
  "danemark":{"c":"danemark","f":"danemark"},
  "djibouti":{"c":"djibouti","f":"djibouti"},
  "dominique":{"c":"dominique","f":"dominique"},
  "ecosse":{"c":"royaume-uni","f":"royaume-uni"},
  "egypte":{"c":"egypte","f":"egypte"},
  "emirats":{"c":"emirats-arabes-unis","f":"emirats-arabes-unis"},
  "emirats-arabes":{"c":"emirats-arabes-unis","f":"emirats-arabes-unis"},
  "emirats-arabes-unis":{"c":"emirats-arabes-unis","f":"emirats-arabes-unis"},
  "equateur":{"c":"equateur","f":"equateur"},
  "erythree":{"c":"erythree","f":"erythree"},
  "espagne":{"c":"espagne","f":"espagne"},
  "estonie":{"c":"estonie","f":"estonie"},
  "eswatini":{"c":"eswatini","f":"swaziland"},
  "etats-federes-de-micronesie":{"c":"micronesie-efm","f":""},
  "etats-unis":{"c":"etats-unis","f":"etats-unis"},
  "ethiopie":{"c":"ethiopie","f":"ethiopie"},
  "falkland":{"c":"iles-falkland","f":""},
  "fidji":{"c":"fidji","f":"iles-fidji"},
  "finlande":{"c":"finlande","f":"finlande"},
  "france":{"c":"france","f":"france"},
  "gabon":{"c":"gabon","f":"gabon"},
  "gambie":{"c":"gambie","f":"gambie"},
  "gaza":{"c":"israel-la-cisjordanie-et-la-bande-de-gaza","f":"israel-territoires-palestiniens"},
  "georgie":{"c":"georgie","f":"georgie"},
  "ghana":{"c":"ghana","f":"ghana"},
  "gibraltar":{"c":"gibraltar","f":""},
  "grece":{"c":"grece","f":"grece"},
  "grenade":{"c":"grenade","f":"grenade"},
  "groenland":{"c":"groenland","f":""},
  "guadeloupe":{"c":"guadeloupe","f":""},
  "guam":{"c":"guam","f":""},
  "guatemala":{"c":"guatemala","f":"guatemala"},
  "guinee":{"c":"guinee","f":"guinee"},
  "guinee-bissao":{"c":"guinee-bissau","f":"guinee-bissao"},
  "guinee-bissau":{"c":"guinee-bissau","f":"guinee-bissao"},
  "guinee-equatoriale":{"c":"guinee-equatoriale","f":"guinee-equatoriale"},
  "guyana":{"c":"guyana","f":"guyana"},
  "guyane":{"c":"guyane-francaise","f":""},
  "haiti":{"c":"haiti","f":"haiti"},
  "herzegovine":{"c":"bosnie-herzegovine","f":"bosnie-herzegovine"},
  "holland":{"c":"pays-bas","f":"pays-bas"},
  "hollande":{"c":"pays-bas","f":"pays-bas"},
  "honduras":{"c":"honduras","f":"honduras"},
  "hong-kong":{"c":"hong-kong","f":"hong-kong"},
  "hongkong":{"c":"hong-kong","f":"hong-kong"},
  "hongrie":{"c":"hongrie","f":"hongrie"},
  "ile-maurice":{"c":"maurice-ile","f":"maurice"},
  "iles-caimans":{"c":"caimans-iles","f":""},
  "iles-canaries":{"c":"iles-canaries","f":""},
  "iles-cook":{"c":"iles-cook","f":"iles-cook"},
  "iles-fidji":{"c":"fidji","f":"iles-fidji"},
  "iles-mariannes-du-nord":{"c":"mariannes-du-nord-iles","f":""},
  "iles-marshall":{"c":"marshall-iles","f":""},
  "iles-turques-et-caiques":{"c":"iles-turks-et-caicos","f":""},
  "iles-vierges-britanniques":{"c":"iles-vierges-britanniques","f":""},
  "iles-vierges-des-etats-unis":{"c":"iles-vierges-americaines","f":""},
  "inde":{"c":"inde","f":"inde"},
  "indonesie":{"c":"indonesie","f":"indonesie"},
  "irak":{"c":"iraq","f":"irak"},
  "iran":{"c":"iran","f":"iran"},
  "irlande":{"c":"irlande","f":"irlande"},
  "islande":{"c":"islande","f":"islande"},
  "israel":{"c":"israel-la-cisjordanie-et-la-bande-de-gaza","f":"israel-territoires-palestiniens"},
  "italie":{"c":"italie","f":"italie"},
  "jamaique":{"c":"jamaique","f":"jamaique"},
  "japon":{"c":"japon","f":"japon"},
  "jordanie":{"c":"jordanie","f":"jordanie"},
  "kazakhstan":{"c":"kazakhstan","f":"kazakhstan"},
  "kenya":{"c":"kenya","f":"kenya"},
  "kirghizistan":{"c":"kirghizistan","f":"kirghizistan"},
  "kiribati":{"c":"kiribati","f":""},
  "kosovo":{"c":"kosovo","f":"kosovo"},
  "koweit":{"c":"koweit","f":"koweit"},
  "la-reunion":{"c":"la-reunion","f":""},
  "laos":{"c":"laos","f":"laos"},
  "lesotho":{"c":"lesotho","f":"lesotho"},
  "lettonie":{"c":"lettonie","f":"lettonie"},
  "liban":{"c":"liban","f":"liban"},
  "liberia":{"c":"liberia","f":"liberia"},
  "libye":{"c":"libye","f":"libye"},
  "liechtenstein":{"c":"liechtenstein","f":""},
  "lituanie":{"c":"lituanie","f":"lituanie"},
  "luxembourg":{"c":"luxembourg","f":"luxembourg"},
  "macao":{"c":"macao","f":"macao"},
  "madagascar":{"c":"madagascar","f":"madagascar"},
  "malaisie":{"c":"malaisie","f":"malaisie"},
  "malawi":{"c":"malawi","f":"malawi"},
  "maldives":{"c":"maldives","f":"maldives"},
  "mali":{"c":"mali","f":"mali"},
  "malouines":{"c":"myanmar","f":""},
  "malte":{"c":"malte","f":"malte"},
  "maroc":{"c":"maroc","f":"maroc"},
  "martinique":{"c":"martinique","f":""},
  "maurice":{"c":"maurice-ile","f":"maurice"},
  "mauritanie":{"c":"mauritanie","f":"mauritanie"},
  "mayotte":{"c":"mayotte","f":""},
  "mexique":{"c":"mexique","f":"mexique"},
  "micronesie":{"c":"micronesie-efm","f":""},
  "moldavie":{"c":"moldova","f":"moldavie"},
  "moldova":{"c":"moldova","f":"moldavie"},
  "monaco":{"c":"monaco","f":"monaco"},
  "mongolie":{"c":"mongolie","f":"mongolie"},
  "montenegro":{"c":"montenegro","f":"montenegro"},
  "montserrat":{"c":"montserrat","f":""},
  "mozambique":{"c":"mozambique","f":"mozambique"},
  "myanmar":{"c":"myanmar","f":"birmanie"},
  "namibie":{"c":"namibie","f":"namibie"},
  "nauru":{"c":"nauru","f":""},
  "nepal":{"c":"nepal","f":"nepal"},
  "nicaragua":{"c":"nicaragua","f":"nicaragua"},
  "niger":{"c":"niger","f":"niger"},
  "nigeria":{"c":"nigeria","f":"nigeria"},
  "niue":{"c":"niue","f":""},
  "norvege":{"c":"norvege","f":"norvege"},
  "nouvelle-caledonie":{"c":"nouvelle-caledonie","f":""},
  "nouvelle-guinee":{"c":"papouasie-nouvelle-guinee","f":"papouasie-nouvelle-guinee"},
  "nouvelle-zelande":{"c":"nouvelle-zelande","f":"nouvelle-zelande"},
  "oman":{"c":"oman","f":"oman"},
  "ouganda":{"c":"ouganda","f":"ouganda"},
  "ouzbekistan":{"c":"ouzbekistan","f":"ouzbekistan"},
  "pakistan":{"c":"pakistan","f":"pakistan"},
  "palaos":{"c":"palaos","f":"republique-des-palaos"},
  "palestine":{"c":"israel-la-cisjordanie-et-la-bande-de-gaza","f":"israel-territoires-palestiniens"},
  "panama":{"c":"panama","f":"panama"},
  "papouasie":{"c":"papouasie-nouvelle-guinee","f":"papouasie-nouvelle-guinee"},
  "papouasie-nouvelle-guinee":{"c":"papouasie-nouvelle-guinee","f":"papouasie-nouvelle-guinee"},
  "paraguay":{"c":"paraguay","f":"paraguay"},
  "pays-bas":{"c":"pays-bas","f":"pays-bas"},
  "pays-bas-caribeens":{"c":"bonaire","f":""},
  "pays-de-galles":{"c":"royaume-uni","f":"royaume-uni"},
  "perou":{"c":"perou","f":"perou"},
  "philippines":{"c":"philippines","f":"philippines"},
  "pologne":{"c":"pologne","f":"pologne"},
  "polynesie-francaise":{"c":"polynesie-francaise","f":""},
  "porto-rico":{"c":"puerto-rico","f":""},
  "portorico":{"c":"puerto-rico","f":""},
  "portugal":{"c":"portugal","f":"portugal"},
  "qatar":{"c":"qatar","f":"qatar"},
  "republique-centrafricaine":{"c":"republique-centrafricaine","f":"republique-centrafricaine"},
  "republique-de-macedoine":{"c":"macedoine","f":"ancienne-republique-yougoslave-de-macedoine-arym"},
  "republique-democratique-du-congo":{"c":"congo-kinshasa","f":"republique-democratique-du-congo"},
  "republique-dominicaine":{"c":"republique-dominicaine","f":"republique-dominicaine"},
  "republique-du-congo":{"c":"congo-brazzaville","f":"congo"},
  "republique-tcheque":{"c":"republique-tcheque","f":"republique-tcheque"},
  "reunion":{"c":"la-reunion","f":""},
  "roumanie":{"c":"roumanie","f":"roumanie"},
  "royaume-uni":{"c":"royaume-uni","f":"royaume-uni"},
  "russie":{"c":"russie","f":"russie"},
  "rwanda":{"c":"rwanda","f":"rwanda"},
  "saint-barthelemy":{"c":"saint-barthelemy","f":""},
  "saint-kitts-et-nevis":{"c":"saint-kitts-et-nevis","f":""},
  "saint-marin":{"c":"saint-marin","f":""},
  "saint-martin":{"c":"saint-martin","f":""},
  "saint-pierre-et-miquelon":{"c":"saint-pierre-et-miquelon","f":""},
  "saint-vincent-et-grenadines":{"c":"saint-vincent-et-grenadines","f":"saint-vincent-et-les-grenadines"},
  "saint-vincent-et-les-grenadines":{"c":"saint-vincent-et-grenadines","f":"saint-vincent-et-les-grenadines"},
  "sainte-lucie":{"c":"sainte-lucie","f":"sainte-lucie"},
  "salomon":{"c":"salomon-iles","f":"iles-salomon"},
  "salvador":{"c":"salvador","f":"salvador"},
  "samoa":{"c":"samoa","f":"samoa"},
  "samoa-americaines":{"c":"samoa-americaines","f":""},
  "sao-tome-et-principe":{"c":"sao-tome-et-principe","f":"sao-tome-et-principe"},
  "saotome-et-principe":{"c":"sao-tome-et-principe","f":"sao-tome-et-principe"},
  "senegal":{"c":"senegal","f":"senegal"},
  "serbie":{"c":"serbie","f":"serbie"},
  "seychelles":{"c":"seychelles","f":"seychelles"},
  "sierra-leone":{"c":"sierra-leone","f":"sierra-leone"},
  "sierraleone":{"c":"sierra-leone","f":"sierra-leone"},
  "singapour":{"c":"singapour","f":"singapour"},
  "sint-maarten":{"c":"sint-maarten","f":""},
  "sintmaarten":{"c":"sint-maarten","f":""},
  "slovaquie":{"c":"slovaquie","f":"slovaquie"},
  "slovenie":{"c":"slovenie","f":"slovenie"},
  "somalie":{"c":"somalie","f":"somalie"},
  "soudan":{"c":"soudan","f":"soudan"},
  "soudan-du-sud":{"c":"sudan-du-sud","f":"sudan-du-sud"},
  "sri-lanka":{"c":"sri-lanka","f":"sri-lanka"},
  "srilanka":{"c":"sri-lanka","f":"sri-lanka"},
  "suede":{"c":"suede","f":"suede"},
  "suisse":{"c":"suisse","f":"suisse"},
  "suriname":{"c":"suriname","f":"suriname"},
  "swaziland":{"c":"eswatini","f":"swaziland"},
  "syrie":{"c":"syrie","f":"syrie"},
  "tadjikistan":{"c":"tadjikistan","f":"tadjikistan"},
  "taiwan":{"c":"taiwan","f":"taiwan"},
  "tanzanie":{"c":"tanzanie","f":"tanzanie"},
  "tchad":{"c":"tchad","f":"tchad"},
  "tchequie":{"c":"republique-tcheque","f":"republique-tcheque"},
  "thailande":{"c":"thailande","f":"thailande"},
  "timor-est":{"c":"timor-leste-timor-oriental","f":"timor-est"},
  "timor-leste":{"c":"timor-leste-timor-oriental","f":"timor-est"},
  "timor-oriental":{"c":"timor-leste-timor-oriental","f":"timor-est"},
  "togo":{"c":"togo","f":"togo"},
  "tokelau":{"c":"tokelau","f":""},
  "tonga":{"c":"tonga","f":"tonga"},
  "trinite":{"c":"trinite-et-tobago","f":"trinite-et-tobago"},
  "trinite-et-tobago":{"c":"trinite-et-tobago","f":"trinite-et-tobago"},
  "tunisie":{"c":"tunisie","f":"tunisie"},
  "turkmenistan":{"c":"turkmenistan","f":"turkmenistan"},
  "turquie":{"c":"turquie","f":"turquie"},
  "tuvalu":{"c":"tuvalu","f":""},
  "ukraine":{"c":"ukraine","f":"ukraine"},
  "uruguay":{"c":"uruguay","f":"uruguay"},
  "vanuatu":{"c":"vanuatu","f":"vanuatu"},
  "vatican":{"c":"italie","f":"italie"},
  "venezuela":{"c":"venezuela","f":"venezuela"},
  "viet-nam":{"c":"vietnam","f":"vietnam"},
  "vietnam":{"c":"vietnam","f":"vietnam"},
  "yemen":{"c":"yemen","f":"yemen"},
  "zambie":{"c":"zambie","f":"zambie"},
  "zimbabwe":{"c":"zimbabwe","f":"zimbabwe"}
}
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
    if country in SPECIAL_COUNTRIES_INPUT:
        page = requests.get(STATUS_URL + SPECIAL_COUNTRIES_INPUT[country]["c"])
        if page.status_code == 200:
            advisories = BeautifulSoup(page.content, 'html.parser').find(id='advisories')
            if advisories:
                empty_tags = advisories.find_all(href="#securite")
                if empty_tags:
                    for empty_tag in empty_tags:
                        empty_tag.clear()
                advice_array = []
                for advice in advisories:
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
        country = clean_country_info_intent(intent['slots']['paysFR']['value'])
        print("COUNTRY {}".format(country))
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
