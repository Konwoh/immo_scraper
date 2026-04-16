Docker Commands:
- scraper: 
    - docker build -f scraper/Dockerfile -t scraper .
    - docker run --env-file .env -v ${PWD}/logging:/app/logging scraper
- crawler:
    - docker build -f crawler/Dockerfile -t crawler .
    - docker run --env-file .env -v ${PWD}/logging:/app/logging crawler


TO-DO:
- DB Polling: Worker der alle paar Sekunden die Job Tabelle abfragt und guckt ob was neues drin ist
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