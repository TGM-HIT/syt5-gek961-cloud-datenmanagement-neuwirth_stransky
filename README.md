# Cloud-Datenmanagement

## Einführung
Diese Übung zeigt die Anwendung von verteilten Webservices an einer simplen Anforderung.

## Ziele
Das Ziel dieser Übung ist eine Webanbindung zur Benutzeranmeldung umzusetzen. Dabei soll sich ein Benutzer registrieren und am System anmelden können.
Die Kommunikation zwischen Client und Service soll mit Hilfe einer REST Schnittstelle umgesetzt werden.

## Voraussetzungen
 Grundlagen einer höheren Programmiersprache; Verständnis über relationale Datenbanken und dessen Anbindung mittels ODBC oder ORM-Frameworks; Verständnis von Restful Webservices

## Aufgabenstellung
Es ist ein Webservice zu implementieren, welches eine einfache Benutzerverwaltung implementiert. Dabei soll die Webapplikation mit den Endpunkten /auth/admin/register, /auth/signin und /auth/verify erreichbar sein.

## Grundanforderungen
### Registrierung
Diese soll mit einem Namen, einer eMail-Adresse als BenutzerID, einer Liste an Rollen (ADMIN, READER, MODERATOR) und einem Passwort erfolgen. Dabei soll noch auf keine besonderen Sicherheitsmerkmale Wert gelegt werden, jedoch ist das Passwort nicht unverschlüsselt abzulegen. Die Registrierung der Benutzer kann nur durch Administratoren erfolgen. Die Daten sollen in einem geeigneten Datastore (z.B. relationale Datenbank) abgelegt werden.
Beim initialen Start sollen Benutzer aus einem JSON-File geladen werden können. Dabei dürfen die Passwörter auf keinen Fall unverschlüsselt gespeichert sein.

### Login
Der Benutzer soll sich mit seiner ID und seinem Passwort entsprechend einloggen können. Bei einem erfolgreichen Login soll eine entsprechende HTTP-Response zurück geben und ein signiertes JWT mitgeliefert werden, die auch die genehmigten Rollen enthält.

/auth/verify gibt ein 403 UNAUTHORIZEDzurück, wenn das mitgelieferte JWT nicht der Signatur entspricht. Ansonsten wird eine positive Rückmeldung generiert und die Rolle bestätigt.
Verwenden Sie auf jeden Fall ein gängiges Build-Management-Tool (z.B. Gradle). Dabei ist zu beachten, dass ein einfaches Deployment möglich ist (auch Datenbank mit z.B. file-based DBMS). Überprüfen Sie die Funktionalität mit einfachen Methoden, die einfach nachvollziehbar sind und dokumentieren Sie diese (z.B. mit curl Befehlen).

## Umsetzung:
Wir haben einen Docker-Container mit folgender Datenbank erstellt:

![img.png](img.png)

## Fragestellungen


#### Welche grundlegenden Elemente müssen bei einer REST Schnittstelle zur Verfügung gestellt werden?

client-server-Trennung: klare Rollentrennung zwischen Datenanfrage und Datenauslieferung

Zustandslosigkeit: Jede Anfrage enthält nur die Daten die zu dem Verständnis und damit auch der Ausfürhung nötig sind

Caching: Ein weiteres Kennzeichen von REST ist die Möglichkeit der Zwischenspeicherung (Caching) von Daten. Diese werden explizit als „cacheable“ oder „non-cacheable“ gekennzeichnet, je nach erfolgter Auswahl zwischengespeichert und bei identischer Anfrage erneut verwendet.

Einheitliche Schnittstelle:  Alle Anfragen müssen ein einheitliches Format aufweisen 

#### Wie stehen diese mit den HTTP-Befehlen in Verbindung?
Die Informationen werden als Hypertext Transfer Protocol (HTTP) bereitgestellt. Dabei gibt es folgende HTTP-Befehle um HTTP-Anfragen mit einer RESTful-API durchzuführen:

GET: Abrufen von Ressourcen, z. B. durch den Browser beim Laden einer Webseite.

POST: Übermitteln von Daten an den Server, z. B. über ein Formular wie ein Kontaktformular.

PUT: Erstellen oder Aktualisieren von bereits vorhandenen Ressourcen auf dem Server.

DELETE: Entfernen von Ressourcen vom Server.

#### Welche Datenbasis bietet sich für einen solchen Use-Case an?

Für das Umsetzten dieser Aufgabe würde ich eine rationale Datenbank empfehlen. Wir haben in dem Fall MySQL verwendet.

#### Welche Erfordernisse bezüglich der Datenbasis sollten hier bedacht werden?

Dabei sollte folgendes beachtet werden:
Die Daten müssen Konsitent sein
Die Sicherheit der Daten muss gewähleistet werden

#### Verschiedene Frameworks bieten schnelle Umsetzungsmöglichkeiten, welche Eckpunkte müssen jedoch bei einer öffentlichen Bereitstellung (Production) von solchen Services beachtet werden?

Ein der öffentlichen Bereitstellung von Services auf verschiedenen Frameworks sollten folgende Punkte beachtet werden: 
Erstens ist die Sicherheit entscheidend, einschließlich Authentifizierung, Autorisierung und Datenverschlüsselung. Zweitens muss die Leistung durch Caching und Skalierbarkeit optimiert werden. Drittens ist die Verfügbarkeit wichtig, was regelmäßige Backups und Monitoring umfasst. Die Einhaltung von Datenschutzbestimmungen wie der DSGVO ist unerlässlich. Zudem sollte eine klare Dokumentation bereitgestellt werden, und ein Plan für Wartung und Support ist notwendig, um die Stabilität der Services zu gewährleisten.

## Quellen:

+ "REST-API verständlich erklärt für Nicht-Entwickler" https://www.lobster-world.com/de/wiki/rest-api/ 
+ "Flask Doku" https://flask-session.readthedocs.io/en/latest
+ "Hashlib" https://docs.python.org/3/library/hashlib.html
+ "Docker" https://www.datacamp.com/tutorial/set-up-and-configure-mysql-in-docker

