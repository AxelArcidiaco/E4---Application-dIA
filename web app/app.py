# Importation des bibliothèques requises
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "42isTheAnswer"  # Nécessaire pour les sessions
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

# Définition du modèle de la base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Création de la base de données si elle n'existe pas
with app.app_context():
    db.create_all()

# Page d'accueil
@app.route("/")
def home():
    if "username" in session:
        return render_template("home.html", image_url=session.get('image_url'))
    else:
        return redirect(url_for("login"))

# Page de connexion
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("userId")
        password = request.form.get("password")
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["username"] = user.username
            return redirect(url_for("home"))
    return render_template("login.html")

# Page d'inscription
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("userId")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")
        if password == confirm_password:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html")

# Déconnexion
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# Upload d'image
@app.route("/upload", methods=["POST"])
def upload():
    if 'image' not in request.files:
        return redirect(url_for("home"))
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for("home"))
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        session['uploaded_image'] = filepath
        session['image_url'] = url_for('uploaded_file', filename=file.filename)
        return redirect(url_for("home"))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/classify', methods=['POST'])
def classify():
    if 'uploaded_image' not in session:
        return jsonify({'result': 'Aucune image chargée'})
    image_path = session['uploaded_image']

    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
        response = requests.post('http://127.0.0.1:8000/classify/', files=files)

    if response.status_code == 200:
        result = response.json().get('result')
    else:
        result = 'Erreur de classification'

    return jsonify({'result': result})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
