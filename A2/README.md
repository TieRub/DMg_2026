# Aufgabe A2

## Vorraussetzung zum Ausführen
    -Docker mit Docker-Compose installiert
## Build
    - docker compose build oder docker-compose build abhängig vom Betriebssystem und der Docker Version
## Ausführung
    - docker compose up -d oder docker-compose up -d
## Fehler Quellen
Wenn die Python Application schneller bereit ist, als die DB, startet der Web Container neu
## Wie viele Anfragen an die API sind erforderlich, um sämtliche in den Wireframes dargestellten Informationen aus der Datenbank zu lesen?
3 
GET http://127.0.0.1:8080/customers/{c_id}
GET http://127.0.0.1:8080/products/{p_id}
GET http://127.0.0.1:8080/orders/{o_id}
Die OrderPositions werden als Liste im JSON des GET orders mitgeliefert.
