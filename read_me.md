Docker Commands:
- scraper: 
    - docker build -f scraper/Dockerfile -t scraper .
    - docker run --env-file .env -v ${PWD}/logging:/app/logging scraper
- crawler:
    - docker build -f crawler/Dockerfile -t crawler .
    - docker run --env-file .env -v ${PWD}/logging:/app/logging crawler


TO-DO:
- FastAPI:
    - wenn ein scraper job mit einer search_params_id inserted wird, für die es garn keine url_queue Objekte gibt, dann kommt kein Fehler oder Warnung
    - current_user in allen Endpoint hinzufügen
    - m:n Tabelle (search_result) zwischen Search_Params und house/apartments befüllen lassen -> nochmal überprüfen ob es klappt
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