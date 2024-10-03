# Importieren von Flask, mysql.connector und hashlib
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import mysql.connector
import hashlib

#Stellt sicher, dass der templates folder wirklich gefunden wurde
app = Flask(__name__, template_folder='../templates')
app.secret_key = 'geheimnisvollesgeheimnis'

# JWT secret key for JWT management
app.config['JWT_SECRET_KEY'] = 'jwt_geheimnisvoll'
jwt = JWTManager(app)

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

# Erstelle einen Hash des Passworts mit SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Hash das zu überprüfende Passwort
def check_password(stored_hash, password_to_check):
    return stored_hash == hash_password(password_to_check)

#Folgender Rest-Befehl und die dazugehörige Methode sollen 
#den User standartmäßig auf /login führen
@app.route('/')
def index():
    if 'username' in session:     
        return render_template('index.html', username=session['username'])
    return redirect(url_for('signin'))

#die Methode wir bei /register aufgerufen
# Registrierung nur durch Administratoren
@app.route('/auth/admin/register', methods=['POST'])
@jwt_required()  # Nur angemeldete Benutzer können Benutzer registrieren
def register():
    # Hole den angemeldeten Benutzer
    current_user = get_jwt_identity()
    if current_user['role'] != 'ADMIN':
        return jsonify({'msg': 'Nur Administratoren können Benutzer registrieren!'}), 403

    email = request.json.get('email')
    password = request.json.get('password')
    role = request.json.get('role', 'READER')

    # Überprüfen ob Role gültig ist
    if role not in ["ADMIN", "READER", "MODERATOR"]:
        role = "READER"

    # Hash and salt the password
    raw_password = request.form['password'] + "1KASmdfsjeWiud/§"
    hashed_password = hash_password(raw_password)

    # Überprüfen, ob der Benutzer bereits existiert
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({'msg': 'E-Mail existiert bereits!'}), 400
    else:
        # Benutzer registrieren
        cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
                       (email, hashed_password, role))
        conn.commit()
        return jsonify({'msg': 'Benutzer erfolgreich registriert!'}), 201

# Login und JWT-Erstellung
@app.route('/auth/signin', methods=['POST'])
def signin():
    email = request.json.get('email')
    password = request.json.get('password') + "1KASmdfsjeWiud/§"

    # Benutzer anhand der E-Mail abrufen
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and check_password(user[3], password):  # Passwort überprüfen (user[3] ist das Passwort)
        # JWT erstellen
        access_token = create_access_token(identity={'username': user[1], 'role': user[4]})
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'msg': 'Falsche Anmeldeinformationen!'}), 401

# JWT-Verifizierung
@app.route('/auth/verify', methods=['GET'])
@jwt_required()  # JWT wird benötigt
def verify():
    current_user = get_jwt_identity()  # Hole die Identität aus dem JWT
    return jsonify({'msg': 'Token gültig!', 'user': current_user}), 200

if __name__ == '__main__':
    app.run(debug=True)