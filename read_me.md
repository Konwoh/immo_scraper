Docker Commands:
- scraper: 
    - docker build -f scraper/Dockerfile -t scraper .
    - docker run --env-file .env -v ${PWD}/logging:/app/logging scraper
- crawler:
    - docker build -f crawler/Dockerfile -t crawler .
    - docker run --env-file .env -v ${PWD}/logging:/app/logging crawler


TO-DO:
- FastAPI:
    - Überprüfen, ob das mit den check_online_availability klappt -> warten bis haus auf offline gesetzt ist
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
- Web-App
    - Crud Fenster zum hinzufügen von search_param Kombinationen
- generelle Datenanalyse