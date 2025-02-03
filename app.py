from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask import render_template, session, redirect, url_for
from flask import redirect, url_for, session
from flask import Flask, request, jsonify
import json
import os
app = Flask(__name__)
app.secret_key = 'secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pythamoua@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'hjoctejcfgenstmy'     # Replace with your email password

mail = Mail(app)
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Password in plain text
    is_active = db.Column(db.Boolean, default=False)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        raw_password = request.form['password']  # Password in plain text

        new_user = User(first_name=first_name, last_name=last_name, phone=phone, email=email, password=raw_password)

        try:
            db.session.add(new_user)
            db.session.commit()

            # Sending email with plain text password
            msg = Message('Welcome to MRUSSE225', sender='pythamoua@gmail.com', recipients=[email])
            msg.body = (
                f"Welcome {first_name} {last_name}!\n\n"
                f"Your account details:\n"
                f"Name: {first_name} {last_name}\n"
                f"Phone: {phone}\n"
                f"Email: {email}\n"
                f"Password: {raw_password}\n\n"
                f"Thank you for joining us!"
            )
            mail.send(msg)

            flash('Registration successful! Check your email for details.', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash('Error: Email already exists or invalid data.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:  # Direct comparison with plain text password
            if user.is_active:
                session['user_id'] = user.id
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Your account is inactive. Please contact support.', 'warning')
                return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/logout')
def logout():
    # Suppression de la session utilisateur pour déconnecter l'utilisateur
    session.pop('user_id', None)  # Assure-toi d'utiliser le bon nom de variable pour la session
    return redirect(url_for('login'))  # Rediriger vers la page de connexion




@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)






@app.route('/admin', methods=['GET', 'POST'])
def admin():
    users = User.query.all()

    if request.method == 'POST':
        user_id = request.form['user_id']
        action = request.form['action']

        user = User.query.get(user_id)
        if action == 'activate':
            user.is_active = True
        elif action == 'deactivate':
            user.is_active = False
        elif action == 'delete':
            db.session.delete(user)  # Supprimer l'utilisateur
            db.session.commit()
            flash(f'User {user.email} deleted successfully.', 'success')
            return redirect(url_for('admin'))

        db.session.commit()
        flash('User status updated successfully.', 'success')
        return redirect(url_for('admin'))

    return render_template('admin.html', users=users)

@app.route("/NouvelleBourses")
def NouvelleBourses():
    return render_template("NouvelleBourses.html")

@app.route('/parametre')
def parametre():
    user = {"first_name": "Utilisateur"}  # Remplace par les données dynamiques si nécessaire
    return render_template('parametre.html', user=user)


DATA_FILE = "comments.json"

# Vérifier si le fichier existe, sinon le créer
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump([], file)

# Charger les commentaires depuis le fichier
def load_comments():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Sauvegarder les commentaires dans le fichier
def save_comments(comments):
    with open(DATA_FILE, "w") as file:
        json.dump(comments, file, indent=4)


   
@app.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.json
    comments = load_comments()
    print("Requête reçue !")  # Vérifie si la requête arrive
    print(request.json)  # Affiche les données reçues
    new_comment = {
        "id": len(comments) + 1,
        "name": data["name"],
        "message": data["message"],
        "replies": []
    }

    comments.append(new_comment)
    save_comments(comments)
    return jsonify({"status": "success", "message": "Commentaire ajouté"}), 200

@app.route('/get_comments', methods=['GET'])
def get_comments():
    return jsonify(load_comments())

@app.route('/add_reply', methods=['POST'])
def add_reply():
    data = request.json
    comments = load_comments()

    for comment in comments:
        if str(comment["id"]) == data["comment_id"]:
            reply = {
                "name": data["name"],
                "message": data["message"]
            }
            comment["replies"].append(reply)
            save_comments(comments)
            return jsonify({"status": "success", "message": "Réponse ajoutée"}), 200

    return jsonify({"status": "error", "message": "Commentaire non trouvé"}), 400




if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables if they don't exist
    app.run(debug=True)
