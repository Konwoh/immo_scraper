import requests
import json

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

response = json.loads(response.text)

for section in response["sections"]:
    if section["type"] == "TOP_ATTRIBUTES":
        for attribute in section["attributes"]:
            if attribute["label"] == "Zimmer":
                rooms = float(attribute["text"])
            elif attribute["label"] == "Wohnfläche":
                living_space = attribute["text"]
            elif attribute["label"] == "Grundstück":
                property_space = attribute["text"]
    elif section["type"] == "MAP":
        if section["addressLine1"] == "Die vollständige Adresse der Immobilie erhältst du vom Anbieter.":
            plz_city = section["addressLine2"]
    elif section["type"] == "ATTRIBUTE_LIST" and section["title"] == "Hauptkriterien":
        for attribute in section["attributes"]:
            if attribute["label"] == "Haustyp:":
                estate_type = attribute["text"]
            elif attribute["label"] == "Schlafzimmer:":
                sleeping_rooms = int(attribute["text"])
            elif attribute["label"] == "Anzahl Garage/Stellplatz:":
                garage_parking_slots = int(attribute["text"])
    elif (section["type"] == "ATTRIBUTE_LIST") and (section["title"] == "Kosten"):
        for attribute in section["attributes"]:
            if attribute["label"] == "Kaufpreis:":
                price = attribute["text"]
            elif attribute["label"] == "Preis/m²:":
                price_m2 = attribute["text"]
            elif attribute["label"] == "Mieteinnahmen pro Monat:":
                rent_income = attribute["text"]
    elif (section["type"] == "FINANCE_COSTS"):
        incidental_purchase_costs = section["additionalCosts"]["value"]
        total_costs = section["totalCosts"]["value"]
        broker_commision = section["brokerCommission"]["percentage"]
        land_transfer_tax = section["landTransferTax"]["percentage"]
        notary_fees = section["notaryCosts"]["percentage"]
        land_registry_entry = section["landRegistryEntry"]["percentage"]
        
    elif (section["type"] == "ATTRIBUTE_LIST") and (section["title"] == "Bausubstanz & Energieausweis"):
        for attribute in section["attributes"]:
            if attribute["label"] == "Baujahr:":
                building_year = attribute["text"]
            elif attribute["label"] == "Objektzustand:":
                estate_condtion = attribute["text"]
            elif attribute["label"] == "Qualität der Ausstattung:":
                interior_quality = attribute["text"]
            elif attribute["label"] == "Heizungsart:":
                heating_type = attribute["text"]
            elif attribute["label"] == "Energieausweistyp:":
                energy_performance_certificate_type = attribute["text"]
            elif attribute["label"] == "Wesentliche Energieträger:":
                energy_source = attribute["text"]
            elif attribute["label"] == "Endenergiebedarf:":
                energy_demand = attribute["text"]
            elif attribute["label"] == "Energieeffizienzklasse:":
                energy_efficiency_class = attribute["url"]
    elif section["type"] == "TEXT_AREA" and section["title"] == "Ausstattung":
        general_description = section["text"]
    elif section["type"] == "TEXT_AREA" and section["title"] == "Lage":
        place_description = section["text"]
    elif section["type"] == "AGENTS_INFO":
        name = section["name"]
        rating = float(section["rating"]["value"])
        rating_count = int(section["rating"]["numberOfStars"])
        agent_address = section["address"] 
        
print(rooms, property_space, living_space, plz_city, estate_type, sleeping_rooms, garage_parking_slots, price, price_m2, rent_income, energy_demand)


#TODO:
# - Check, ob alle properties überhaupt existieren, wenn nicht -> Log schreiben
# - Instanziierung der gesammelten Werte in RealEstate Class eventuell mit Dependency Injection