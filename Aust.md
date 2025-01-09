Email Verification:

Erstellung einer gmail Adresse und erstellung eines App Passwortes unter Google Account > Security > App Password

Erstellung eines Config Files mit mail server, username, password, port, TLS, SSL

flask_mail importieren , um Emails zu schicken
itsdangerous importieren (URLSafeTimedSerializer) um Strings mit einem Secret zu serialisieren

serializer = URLSafeTimedSerializer('secret')

Token erstellen mittels token = serializer.dumps(email, salt='secret')

neue route erstellen, für den confirmation link

```
@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='secret', max_age=60)
    except SignatureExpired:
        return 'The token is expired'
    return 'The token works'
```

Statt token is expired und token works muss man anschließend die Logik zur confirmation einbauen, z.B. in der Datenbank confirm_email auf True setzen

https://www.youtube.com/watch?v=vF9n248M1yk&ab_channel=PrettyPrinted
