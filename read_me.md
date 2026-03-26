Docker Commands:
- scraper: 
    - docker build -f scraper/Dockerfile -t scraper .
    - docker run --env-file .env -v ${PWD}/logging:/app/logging scraper
- crawler:
    - docker build -f crawler/Dockerfile -t crawler .
    - docker run --env-file .env -v ${PWD}/logging:/app/logging crawler


TO-DO:
- ImmoWelt hinzufügen
    - crawl() in base crawler aufnehmen
- Hinzufügen von Grundstücken zu immoScout
- Factory-Pattern vereinfachen
- Train various Machine Learning Models (e.g. Classification models, recommender systems, regression für preis vorhersage)
    - good deal detector
- Web-App
    - Crud Fenster zum hinzufügen von search_param Kombinationen
- generelle Datenanalyse