# Importieren von Flask, mysql.connector und hashlib
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import mysql.connector
import hashlib
from flask_cors import CORS, cross_origin
import json
import os

# Flask-App initialisieren
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
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

# Verbindung zur Datenbank herstellen
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()


# Benutzer aus JSON-Datei laden und initial in Datenbank einfügen
def load_users_from_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            users = json.load(file)

            # Check if the JSON is a dictionary with 'users' key or a list
            if isinstance(users, dict):
                user_list = users.get('users', [])
            elif isinstance(users, list):
                user_list = users
            else:
                print("Invalid JSON format.")
                return

            for user in user_list:
                email = user.get('email')
                password = user.get('password')

                # Ensure the password exists
                if password is None:
                    print(f"Skipping user {email} due to missing password.")
                    continue  # Skip this user if the password is missing

                raw_password = password + "1KASmdfsjeWiud/§"
                hashed_password = hash_password(raw_password)
                role = user.get('role', 'READER')
                cursor.execute("INSERT IGNORE INTO users (email, password, role) VALUES (%s, %s, %s)",
                               (email, hashed_password, role))
            conn.commit()


# Passwort hash-Funktion
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Passwort-Prüfung
def check_password(stored_hash, password_to_check):
    return stored_hash == hash_password(password_to_check)


# Registrierung (nur Administratoren können Benutzer registrieren)
@app.route('/auth/admin/register', methods=['POST'])
@cross_origin()
@jwt_required()
def register():
    current_user = get_jwt_identity()
    if current_user['role'] != 'ADMIN':
        return jsonify({'msg': 'Nur Administratoren koennen Benutzer registrieren!'}), 403

    email = request.json.get('email')
    password = request.json.get('password')
    role = request.json.get('role', 'READER')

    if role not in ["ADMIN", "READER", "MODERATOR"]:
        role = "READER"

    raw_password = password + "1KASmdfsjeWiud/§"
    hashed_password = hash_password(raw_password)

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({'msg': 'E-Mail existiert bereits!'}), 400
    else:
        cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
                       (email, hashed_password, role))
        conn.commit()
        return jsonify({'msg': 'Benutzer erfolgreich registriert!'}), 201


# Login und JWT-Erstellung
@app.route('/auth/signin', methods=['POST'])
@cross_origin()
def signin():
    email = request.json.get('email')
    password = request.json.get('password') + "1KASmdfsjeWiud/§"

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and check_password(user[2], password):
        access_token = create_access_token(identity={'username': user[1], 'role': user[3]})

        # Save the token to users.json
        save_token_to_json(email, access_token)

        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'msg': 'Falsche Anmeldeinformationen!'}), 401


# Funktion zum Speichern des Tokens in users.json
def save_token_to_json(email, token, file_path='users.json'):
    # Check if the file exists and load data
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                # Ensure data is a dictionary
                if isinstance(data, list):
                    data = {'users': data}
            except json.JSONDecodeError:
                data = {'users': []}  # Initialize if file is not properly formatted JSON
    else:
        data = {'users': []}

    # Update or add user token
    for user in data['users']:
        if user['email'] == email:
            user['token'] = token
            break
    else:
        data['users'].append({'email': email, 'token': token})

    # Write updated data back to users.json
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


# JWT-Verifizierung
@app.route('/auth/verify', methods=['GET'])
@cross_origin()
@jwt_required()
def verify():
    current_user = get_jwt_identity()
    return jsonify({'msg': 'Token gueltig!', 'user': current_user}), 200


# Default-Admin erstellen
def create_default_admin():
    cursor.execute("SELECT * FROM users WHERE role = 'ADMIN'")
    existingadmin = cursor.fetchone()

    # Erstelle nur einen Admin, wenn keiner existiert
    if not existingadmin:
        email = "admin@example.com"
        raw_password = "adminpass" + "1KASmdfsjeWiud/§"  # Salt hinzufügen
        hashed_password = hash_password(raw_password)
        role = "ADMIN"

        cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
                       (email, hashed_password, role))
        conn.commit()
        print(f"Default admin user created with email '{email}' and password 'adminpass'.")


if __name__ == '__main__':
    create_default_admin()  # Erstelle Standard-Admin beim Start
    # Benutzer aus einer JSON-Datei beim Start laden
    load_users_from_json('users.json')
    app.run(debug=True)
