TO-DO:
- FastAPI:
    - POST, PUT, DELETE Endpoints zu den fehlenden Sachen noch hinzufügen
    - Überprüfen, ob das mit den check_online_availability klappt -> warten bis haus auf offline gesetzt ist
        -> klappt nicht zu 100%, neues Verfahren implementieren, wo neue URLs normal inserted werden und bei den URLs, die nicht gefunden wurden, wird nochmal ein separater URL fetch gemacht und geguckt

- Web-App
    - genaueres Fehler Logging im Frontend
    - Seitenleiste zur Navigation
    - Seite zum starten der Jobs
    - Admin Seite

- Fehler bei Bathrooms mit String "1.5" 
- URL-QUeue wird in crawler/base.py mit values obj aufgefüllt -> ändern
- Front-End bauen
- Request aus Worker Class rausbekommen und mit in Parser Class aufnehmen
- ImmoWelt hinzufügen
    - crawl() in base crawler aufnehmen
- Hinzufügen von Grundstücken zu immoScout
- Factory-Pattern vereinfachen
- Train various Machine Learning Models (e.g. Classification models, recommender systems, regression für preis vorhersage)
    - good deal detector

- generelle Datenanalyse