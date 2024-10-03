# Importieren von Flask, mysql.connector und hashlib
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import hashlib

#Stellt sicher, dass der templates folder wirklich gefunden wurde
app = Flask(__name__, template_folder='../templates')
app.secret_key = 'geheimnisvollesgeheimnis'

# MySQL-Konfiguration
db_config = {
    'host': 'localhost',
    'port': 8080,
    'user': 'root',
    'password': 'Password12345!',
    'database': 'login'
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
    return redirect(url_for('auth/signin'))

#die Methode wir bei /register aufgerufen
@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    #Überprüft ob die POST-Methode requestet ist
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']

        if (role != "ADMIN" and role != "READER" and role != "MODERATOR"):
            role = "READER"

        # Hash and salt the password
        raw_password = request.form['password'] + "1KASmdfsjeWiud/§"
        hashed_password = hash_password(raw_password)

        #Überprüft ob es den user schon gibt
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "Benutzername bereits vorhanden. Bitte wählen Sie einen anderen Benutzernamen."
        else:
            #Wenn es den User noch nicht gibt --> füge ein neues username, password paar hinzu
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",(username, hashed_password, role))
            conn.commit()
            return "Erfolgreich registriert!"
    #So lange nicht POST sondern GET verlangt wird, wird nur die normale webseite angezeigt
    return render_template('register.html')

#Diese methode wird aufgerufen, wenn /login in der URL steht
@app.route('auth/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password'] + "1KASmdfsjeWiud/§"

        #Ich hole mir die Daten zum richtigen Username
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        #Überprüfung ob der user exsitiert und das passwort übereinstimmt
        if user and check_password(user[2], raw_password): 
            #Ich erstelle 2. Sessions damit ich nicht immer den Server nach dem
            #Passwort und Userfragen muss; Damit ist der login_status auf true
            #und den username wurde auch gespeichert
            session['logged_in'] = True
            session['username'] = username
            #es geht auf die index-seite
            return redirect(url_for('index'))
        else:
            return "Falsche Anmeldeinformationen. Bitte versuchen Sie es erneut."
    #So lange nicht POST sondern GET verlangt wird, wird nur die normale webseite angezeigt
    return render_template('signin.html')

#Wenn man auf Logout geht werden die Sessions gelöscht und man ist nicht mehr angemeldet
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)