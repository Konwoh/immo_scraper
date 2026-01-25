import requests
import json
from parser import EstateParserCreator

cookies = {
    'IS24VisitId': 'vid217f62bd-6a5b-4ca6-8a1b-bd4bf93c9251',
}

headers = {
    'accept': 'application/json',
    'x-is24-feature': 'adKeysAndStringValues,virtualTour,referencePriceV3,verificationArray,unpublished,listFirstListing,xxlListingType,immersiveSearch,modernizationCalculator,presale',
    'x-is24-device': 'iphone',
    'priority': 'u=3',
    'x-emb-st': '1769259013083',
    'accept-language': 'de-de',
    'user-agent': 'ImmoScout_27.11_26.2_._',
    'x-emb-id': '0526B033-7C95-4CB9-B788-94E898CFEDF1',
    # 'cookie': 'IS24VisitId=vid217f62bd-6a5b-4ca6-8a1b-bd4bf93c9251',
}

params = {
    'searchId': '7a29154a-9d4b-4719-8fa4-4e649eff4947',
    'referrer': 'resultlist',
}

response = requests.get(
    'https://api.mobile.immobilienscout24.de/expose/164932300',
    params=params,
    cookies=cookies,
    headers=headers,
)

parser = EstateParserCreator().create_parser()
estate = parser.parse(response)

print(estate)


#TODO:
# - besseres Error Handling und Log von Fehlern
# - Check, ob alle properties überhaupt existieren, wenn nicht -> Log schreiben
# - Instanziierung der gesammelten Werte in RealEstate Class eventuell mit Dependency Injection
