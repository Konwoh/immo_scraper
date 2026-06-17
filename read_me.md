TO-DO:
- FastAPI:
    - User Berechtigungssystem bauen
    - DELETE Endpoints für user
    - Überprüfen, ob das mit den check_online_availability klappt -> warten bis haus auf offline gesetzt ist

- Web-App
    - genaueres Fehler Logging im Frontend
    - Admin Seite

- Database:
    - Inserting in DB failed: (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint \"uq_search_result_apartment\"\
     -> eventuell ein ON CONFLICT DO NOTING bei search_result Tabelle hinzufügen    

- Machine Learning:
    - Pipeline Classe machen und dann alles mit Prefect zusammenführen
    - beim  Outlier Remover sollte eine Art verwendet werden besser an Boxplots Ausreißer mit IQR orientieren
    - Train various Machine Learning Models (e.g. Classification models, recommender systems, regression für preis vorhersage)
    - good deal detector
    - generelle Datenanalyse

- Sonstiges:
    - Test schreiben, die automatisch beim Deployment ausgeführt werden
    - Fehler bei Bathrooms mit String "1.5" 
    - ImmoWelt hinzufügen
        - crawl() in base crawler aufnehmen
    - Factory-Pattern vereinfachen