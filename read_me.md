Docker Commands:
- scraper: docker run --env-file .env -v ${PWD}\logging:/app/logging scraper
- crawler: docker run --env-file .env -v ${PWD}\logging:/app/logging crawler

TO-DO:
- Variierung der Suchparameter (Stand jetzt: Wohnungen in Leipzig)
- Logging-Dashboard mit Prometheus and Grafana
- Train various Machine Learning Models (e.g. Classification models, recommender systems, regression für preis vorhersage)
    - good deal detector
- Web-App
- andere Immo-Seiten anschließen
- generelle Datenanalyse