TO-DO:
- FastAPI:
    - Endpoint for ML-Predciciton
    - User Berechtigungssystem bauen
    - DELETE Endpoints für user
    - Überprüfen, ob das mit den check_online_availability klappt -> warten bis haus auf offline gesetzt ist

- Web-App
    - genaueres Fehler Logging im Frontend
    - Admin Seite

- Database:

- Machine Learning:
    - alle ml modelle sollten auf dem gleichen test_datensatz trainiert werden -> test datensatz in db laden und daraus ziehen
    - bei mlflow alle modelle nacheinander trainieren lassen und dann gucken welches den besten score hat und dann das beste als champion deklarieren
    - Train various Machine Learning Models (e.g. Classification models, recommender systems, regression für preis vorhersage)
    - good deal detector
    - generelle Datenanalyse

- Sonstiges:
    - Test schreiben, die automatisch beim Deployment ausgeführt werden
    - Fehler bei Bathrooms mit String "1.5" 
    - ImmoWelt hinzufügen
        - crawl() in base crawler aufnehmen
    - Factory-Pattern vereinfachen