Docker Commands:
- scraper: 
    - docker build -f scraper/Dockerfile -t scraper .
    - docker run --env-file .env -v ${PWD}\logging:/app/logging scraper
- crawler:
    - docker build -f crawler/Dockerfile -t crawler .
    - docker run --env-file .env -v ${PWD}\logging:/app/logging crawler


TO-DO:
- Factory-Pattern vereinfachen
- nicht jedes mal neue Agency generieren, wenn Estate inserted wird
- Logging-Dashboard mit Prometheus and Grafana
- Train various Machine Learning Models (e.g. Classification models, recommender systems, regression für preis vorhersage)
    - good deal detector
- Web-App
- andere Immo-Seiten anschließen
- generelle Datenanalyse