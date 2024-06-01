from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Définition du modèle de la base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Page d'accueil
@app.route("/")
def home():
    if 'username' in request.cookies:
        return render_template("home.html")
    else:
        return redirect(url_for('login'))

# Page de connexion
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('userId')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return redirect(url_for("home"))
    return render_template("login.html")

# Page d'inscription
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('userId')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        if password == confirm_password:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
