# AufgabeA2



## Vorraussetzung zum Ausführen
    -Docker mit Docker-Compose installiert
## Build
    - docker compose build oder docker-compose build abhängig vom betriebssystem und der Docker version
## Ausführung
    - docker compose up -d oder docker-compose up -d
## Fehler Quellen
Wenn die python application schneller bereit ist, als die db startet der web container neu
## Wie viele Anfragen an die API sind erforderlich, um sämtliche in den Wireframes dargestellten Informationen aus der Datenbank zu lesen?
3 
GET http://127.0.0.1:8080/clients/{c_id}
GET http://127.0.0.1:8080/drivers/{d_id}
GET http://127.0.0.1:8080/rides/{r_id}
die Waypoints werden als liste im JSON des GET rides mitgeliefert
