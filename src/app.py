# Importieren von Flask, mysql.connector und hashlib
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import mysql.connector
from mysql.connector import Error
import hashlib
from flask_cors import CORS, cross_origin
import json
import os
import time
import re
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from bcrypt import hashpw, gensalt, checkpw

# Flask-App initialisieren
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Secret keys
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'geheimnisvollesgeheimnis')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt_geheimnisvoll')

# Flask-Limiter initialisieren
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]
)

# JWT-Manager initialisieren
jwt = JWTManager(app)

# MySQL-Konfiguration mit Umgebungsvariablen
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Password12345!'),
    'database': os.getenv('DB_NAME', 'accounts')
}


# Database connection with retry logic
def connect_to_db_with_retries(retries=5, delay=5):
    for attempt in range(retries):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            print("Database connection successful")
            return conn, cursor
        except Error as e:
            print(f"Attempt {attempt + 1} of {retries} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Unable to connect to the database after multiple attempts.")


# Establish connection with retries
conn, cursor = connect_to_db_with_retries()

# Path to users.json (from environment or default to 'users.json' in the current directory)
USERS_JSON_PATH = os.getenv('USERS_JSON_PATH', 'users.json')

# Ensure the users.json file exists
if not os.path.exists(USERS_JSON_PATH):
    with open(USERS_JSON_PATH, 'w') as file:
        json.dump({'users': []}, file)


# Benutzer aus JSON-Datei laden und initial in Datenbank einfügen
def load_users_from_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            users = json.load(file)

            # Checken ob die JSON-Datei ein Dictionary oder eine Liste ist
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
                try:
                    cursor.execute("INSERT IGNORE INTO users (email, password, role) VALUES (%s, %s, %s)",
                                   (email, hashed_password, role))
                except Error as e:
                    print(f"Error inserting user {email}: {e}")
            conn.commit()


# Passwort hash-Funktion
def hash_password(password):
    return hashpw(password.encode(), gensalt()).decode()


# Passwort-Prüfung
def check_password(stored_hash, password_to_check):
    return checkpw(password_to_check.encode(), stored_hash.encode())

# Email-Prüfung
def is_valid_email(email):
    email_regex = r'/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$/'
    return re.match(email_regex, email) is not None


# Registrierung (nur Administratoren können Benutzer registrieren)
@app.route('/auth/admin/register', methods=['POST'])
@cross_origin()
@jwt_required()
@limiter.limit("10 per minute")
def register():
    current_user = get_jwt_identity()
    if current_user['role'] != 'ADMIN':
        return jsonify({'msg': 'Nur Administratoren koennen Benutzer registrieren!'}), 403

    email = request.json.get('email')
    password = request.json.get('password')
    role = request.json.get('role', 'READER')

    # Validate Input
    if not is_valid_email(email):
        return jsonify({'msg': 'Invalid email format!'}), 400

    if role not in ["ADMIN", "READER", "MODERATOR"]:
        role = "READER"

    raw_password = password + "1KASmdfsjeWiud/§"
    hashed_password = hash_password(raw_password)

    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'msg': 'E-Mail existiert bereits!'}), 400
        else:
            cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
                           (email, hashed_password, role))
            conn.commit()
            return jsonify({'msg': 'Benutzer erfolgreich registriert!'}), 201
    except Error as e:
        print(f"Error during user registration: {e}")
        return jsonify({'msg': 'Fehler beim Registrieren des Benutzers!'}), 500


# Login und JWT-Erstellung
@app.route('/auth/signin', methods=['POST'])
@limiter.limit("10 per minute")
def signin():
    email = request.json.get('email')
    password = request.json.get('password')
    password_salted = password + "1KASmdfsjeWiud/§"

    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password(user[2], password_salted):
            access_token = create_access_token(identity={'username': user[1], 'role': user[3]})
            # Speichern des Benutzers in users.json
            user_data = {
                'email': email,
                'token': access_token,
                'password': password,
                'role': user[3]
            }
            save_user_to_json(user_data)

            return jsonify({'access_token': access_token}), 200

        return jsonify({'msg': 'Falsche Anmeldeinformationen!'}), 401
    except Error as e:
        print(f"Error during sign-in: {e}")
        return jsonify({'msg': 'Fehler beim Anmelden!'}), 500


# Zum Testen
# Funktion zum Speichern des vollständigen Benutzers in users.json
def save_user_to_json(user_data, file_path='users.json'):
    # Checken ob die Datei existiert und laden
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                if isinstance(data, list):
                    data = {'users': data}
            except json.JSONDecodeError:
                data = {'users': []}
    else:
        data = {'users': []}

    # Update oder hinzufügen des Benutzers
    for user in data['users']:
        if user['email'] == user_data['email']:
            user.update(user_data)
            break
    else:
        data['users'].append(user_data)

    # Die Daten in die Datei schreiben
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


# JWT-Verifizierung
@app.route('/auth/verify', methods=['GET'])
@cross_origin()
@jwt_required()
@limiter.limit("10 per minute")
def verify():
    current_user = get_jwt_identity()
    return jsonify({'msg': 'Token gueltig!', 'user': current_user}), 200


# Default-Admin erstellen
def create_default_admin():
    try:
        cursor.execute("SELECT * FROM users WHERE role = 'ADMIN'")
        existingadmin = cursor.fetchone()

        # Erstelle nur einen Admin, wenn keiner existiert
        if not existingadmin:
            email = "admin@example.com"
            raw_password = "adminpass"
            hashed_password = hash_password(raw_password)
            role = "ADMIN"

            cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
                           (email, hashed_password, role))
            conn.commit()
            print(f"Default admin user created with email '{email}' and password 'adminpass'.")
    except Error as e:
        print(f"Error during default admin creation: {e}")


if __name__ == '__main__':
    create_default_admin()  # Erstelle Standard-Admin beim Start
    # Benutzer aus einer JSON-Datei beim Start laden
    load_users_from_json(USERS_JSON_PATH)
    app.run(host='0.0.0.0', debug=False)
