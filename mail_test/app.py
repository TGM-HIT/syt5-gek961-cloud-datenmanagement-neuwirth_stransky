from flask import Flask, request, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# Create a Flask application instance
app = Flask(__name__)
app.config.from_pyfile('mail.cfg')

serializer = URLSafeTimedSerializer('secret')
mail = Mail(app)

# Define a route and its corresponding request handler
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return '<form action="/" method="POST"><input name="email"><input type="submit"></form>'
    
    email = request.form['email']
    token = serializer.dumps(email, salt='email-confirmation')

    msg = Message(subject='Confirm Your Email', 
                  sender='sytek0901@gmail.com',
                  recipients=[email])

    link = url_for('confirm_email', token=token, external=True)

    msg.body = 'Your link is 127.0.0.1:5000{}'.format(link)

    mail.send(msg)

    # In the actual register form: create the user but set the confirm_email to false
    return 'A confirmation email has been sent to {}.'.format(email)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirmation', max_age=60)
        # Update the confirm_email field in the database to True
        return 'Your email has been confirmed. Welcome {}!'.format(email)
    except SignatureExpired:
        return 'The confirmation link has expired. Please try again.'
    
# Run the application
if __name__ == "__main__":
    app.run(debug=True)
