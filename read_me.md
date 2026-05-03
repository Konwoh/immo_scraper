Docker Commands:
- scraper: 
    - docker build -f scraper/Dockerfile -t scraper .
    - docker run --env-file .env -v ${PWD}/logging:/app/logging scraper
- crawler:
    - docker build -f crawler/Dockerfile -t crawler .
    - docker run --env-file .env -v ${PWD}/logging:/app/logging crawler


TO-DO:
- FastAPI:
    - current_user in allen Endpoint hinzufügen
    - m:n Tabelle (search_result) zwischen Search_Params und house/apartments befüllen lassen
- URL-QUeue wird in crawler/base.py mit values obj aufgefüllt -> ändern
- Umstrukturierung der Ordner:
    - database und schema und fast api in ein ordern backend z.B.
- Front-End bauen
- bei start_crawler funktion argumente hinzufügen, so dass search params übergeben werden können und keine aus der datenbank gezogen werden
    -> Alternative Dropdown Menü, wo User eine Zeile aus DB auswählen kann und die wird dann gescraped
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