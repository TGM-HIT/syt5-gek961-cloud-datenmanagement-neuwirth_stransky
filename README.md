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
Konektivität zu unserer Daten bank:
```python
# MySQL-Konfiguration
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Password12345!',
    'database': 'accounts'
}
#Die verbindung zur Datenbank wird hergestellt
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()
```
An dieser Stelle sind wir für eine Zeit stecken geblieben, da wir ben Docker-Container falsch konfiguriert hatten:
Wir haben den falschen Prot expost

Wir haben einen Docker-Container mit folgender Datenbank erstellt:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL
);
```

Um das Passwort nicht einfach plain in unsere Datenbank zu schreiben haben wir es mithilfe von hashlib gehasht:

```python
# Erstelle einen Hash des Passworts mit SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Hash das zu überprüfende Passwort
def check_password(stored_hash, password_to_check):
    return stored_hash == hash_password(password_to_check)

#In der Methode registrate haben wir die methode mit folgedenem Befehl aufgerufen:

raw_password = request.form['password'] + "1KASmdfsjeWiud/§"
hashed_password = hash_password(raw_password)
```

Wir haben probiert die Aufgabe schon eine Woche vorher zu lössen, deswegen haben wir eine session verwendet:

```python
@app.route('/')
def index():
    if 'username' in session:     
        return render_template('index.html', username=session['username'])

#in der Methode login:
session['logged_in'] = True
session['username'] = username

#in der Methode ausloggen:
session.pop('username', None)
session.pop('logged_in', None)
```
Diese Umsetzung hat funktioniert, aber wir konnten sie im labor nicht verwenden.

#### JWT

Für die Umsetzung dieser Aufgabe haben wir den JOSN-Web-Token verwendet. Ein JSON Web Token (JWT) ist ein standardisiertes Access Token nach RFC 7519. 
Es ermöglicht den sicheren Datenaustausch zwischen zwei Parteien, da es alle relevanten Informationen über eine Entität enthält. Daher muss nicht die ganze Zeit die Datenbank abgefragt werden.

```python
# der gehiem JWT schlüssel 
app.config['JWT_SECRET_KEY'] = 'jwt_geheimnisvoll'
jwt = JWTManager(app)

#Beim login wir ein JWT vergeben
if user and check_password(user[3], password):  # Passwort überprüfen (user[3] ist das Passwort)
    # JWT erstellen
    access_token = create_access_token(identity={'username': user[1], 'role': user[4]})
    return jsonify({'access_token': access_token}), 200

#In verfiy wird der gültige jwt abgefragt
def verify():
    current_user = get_jwt_identity()  # Hole die Identität aus dem JWT
    return jsonify({'msg': 'Token gültig!', 'user': current_user}), 200

#In registrate wird auch der JWT abgefragt um die Rolle es angemeldeten Benutzers zu überprüfen:
current_user = get_jwt_identity()
    if current_user['role'] != 'ADMIN':
        return jsonify({'msg': 'Nur Administratoren können Benutzer registrieren!'}), 403

```
#### Fazit
Das Einrichten, wie auch verwenden eines gemeinsamen Git-Repos hat uns aufgehalten.
Außerdem wir mit der Verbindung zum Docker viel Zeit verloren.
Wir haben viel Zeit verloren, da wir die ganze Aufgabe mit einem Web-Interface umsetzen wollte --> siehe templates Ordner.

Wir konnten am Schluss unser Program aufgrund diverser Fehler nicht testen:




## Fragestellungen


#### Welche grundlegenden Elemente müssen bei einer REST Schnittstelle zur Verfügung gestellt werden?

client-server-Trennung: klare Rollentrennung zwischen Datenanfrage und Datenauslieferung

Zustandslosigkeit: Jede Anfrage enthält nur die Daten die zu dem Verständnis und damit auch der Ausfürhung nötig sind

Einheitliche Schnittstelle: Alle Anfragen müssen ein einheitliches Format aufweisen 

Alle Daten müssen in JOSN gespeicher werden

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
Erstens ist die Sicherheit entscheidend, einschließlich Authentifizierung, Autorisierung und Datenverschlüsselung. Außerdem ist die Verfügbarkeit wichtig, was regelmäßige Backups und Monitoring umfasst. 
Da man hier mit User-Daten arbeitet, ist die Einhaltung von Datenschutzbestimmungen wie der DSGVO ist wichtig. 
Zudem sollte eine klare Dokumentation bereitgestellt werden, um eine gut Wartung des System zu gewährleisten.

## Quellen:

+ "REST-API verständlich erklärt für Nicht-Entwickler" https://www.lobster-world.com/de/wiki/rest-api/ 
+ "REST" https://www.talend.com/de/resources/was-ist-rest-api/
+ "Flask Doku" https://flask-session.readthedocs.io/en/latest
+ "Hashlib" https://docs.python.org/3/library/hashlib.html
+ "Docker" https://www.datacamp.com/tutorial/set-up-and-configure-mysql-in-docker

