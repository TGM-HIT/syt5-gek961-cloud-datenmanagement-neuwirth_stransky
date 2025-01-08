# EK9.6 Middleware Engineering "Cloud-Datenmanagement" - Taskdescription

## Einführung
Diese Übung zeigt die Anwendung von verteilten Webservices an einer simplen Anforderung.

## Ziele
Das Ziel dieser Übung ist eine Webanbindung zur Benutzeranmeldung umzusetzen. Dabei soll sich ein Benutzer registrieren und am System anmelden können.
Die Kommunikation zwischen Client und Service soll mit Hilfe einer REST Schnittstelle umgesetzt werden.

## Kompetenzzuordnung
EK SYT9 Dezentrale Systeme | Middleware Engineering | Serviceorientiert
"Sicherheitskonzepte für serviceorientierte Architekturen konzipieren"
"Konzepte anhand eines Webservices umsetzen"
EK SYT9 Dezentrale Systeme | Datenmanagement | Speicherkonzepte
"Skalierbares und verteiltes Datenmanagement zur Generierung von dynamischen Inhalten einsetzen"
Voraussetzungen
Grundlagen einer höheren Programmiersprache
Verständnis über relationale Datenbanken und dessen Anbindung mittels ODBC oder ORM-Frameworks
Verständnis von Restful Webservices
Grundlagenübung Middleware Engineering "Cloud-Datenmanagement"
Aufgabenstellung
Es ist ein Webservice zu implementieren, welches eine einfache Benutzerverwaltung implementiert. Dabei soll die Webapplikation mit den Endpunkten /auth/admin/register, /auth/signin und /auth/verify erreichbar sein.

## Erweiterungen

### Sicherheitsüberlegungen
Die REST-Schnittstelle ist schnell und einfach aufgesetzt und ist meist durch Frameworks auch leicht zu erweitern. Bei der Implementierung von neuen Funktionalitäten vergisst man aber schnell auf die notwendige Absicherung von verbreiteten Angriffsvektoren. Welche sind diese? Wie kann zum Beispiel die funktionale Anforderung der Registrierung und des Logins von der Datenhaltung getrennt und abgesichert werden? Ist dies sinnvoll?

Wie können die Eingabe und Übermittlung einfach und schnell sicherer gestaltet werden? Welche Services kommen hierzu verbreitet zum Einsatz?

### Regressions-Tests
Die erfolgreiche Implementierung soll mit entsprechenden Testfällen (Acceptance-Tests bez. aller funktionaler Anforderungen mittels Unit-Tests) dokumentiert werden. Testberichte sind auch dazu da, eine fortgehende Implementierung bzw. eine fehlerhafte Implementierung aufzuzeigen. Nutzen Sie diese!

## Abgabe
Die entsprechenden Konfigurationsdateien und Deployment-Anweisungen sind im README.md festzuhalten. Etwaiger Programmcode ist ebenfalls zu dokumentieren. Implementierungen müssen entsprechend beschrieben und leicht deployable sein!

## Umsetzung

### Angriffsvektoren
#### SQL-Injection
#### Unsichere Speicherung von User Credentials
#### Brute-Force-Attacken

### Gegenmaßnahmen
#### Input Validation (z.B. regex)

```python
# Email-Prüfung
def is_valid_email(email):
    email_regex = r'/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$/'
    return re.match(email_regex, email) is not None

# In der Methode register
if not is_valid_email(email):
    return jsonify({'msg': 'Invalid email format!'}), 400
```

#### Debugging ausschalten

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
```

#### Rate-Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Flask-Limiter initialisieren
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]
)

@app.route('/auth/signin', methods=['POST'])
@limiter.limit("10 per minute")
def signin():

# Weiteres Rate-Limiting für Endpunkte hinzufügen
```

## Bewertung
Gruppengrösse: 1-2 Person(en)

###  Erweiterte Anforderungen überwiegend erfüllt
Umsetzung von erweiterten Sicherheitsrichtlinien
### Erweiterte Anforderungen zur Gänze erfüllt
Überprüfung der funktionalen Anforderungen mittels Regressionstests
Classroom Repository
Hier finden Sie das Abgabe-Repository zum Entwickeln und Commiten Ihrer Lösung.

## Quellen
- [Android Restful Webservice Tutorial – Introduction to RESTful webservice – Part 1](https://www.androidhive.info/2014/05/android-working-with-volley-library-1/)
- [Registration and Login Example with Spring Boot, Spring Security, Spring Data JPA, and HSQL](https://www.codejava.net/frameworks/spring-boot/user-registration-and-login-tutorial)
- [Getting Started with Couchbase and Spring Data Couchbase](https://spring.io/blog/2015/03/16/getting-started-with-couchbase-and-spring-data-couchbase)
- [REST with Java (JAX-RS) using Jersey - Tutorial](https://www.vogella.com/tutorials/REST/article.html)
- [Creating a 'hello world' RESTful web service with Spring](https://spring.io/guides/gs/rest-service/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [Eve. The Simple Way to REST](https://docs.python-eve.org/en/stable/)
- [Heroku makes it easy to deploy and scale Java apps in the cloud](https://devcenter.heroku.com/articles/deploying-spring-boot-apps-to-heroku)

https://flask-limiter.readthedocs.io/en/stable/
https://martin-grellmann.de/regulaere-ausdruecke-regex-in-sql
