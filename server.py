from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Setup (SQLite)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Predefined chatbot responses
responses = {
    "hi": "How can I assist you? What disease are you suffering from?",
    "fever": "A simple remedy for fever is ginger and honey tea...",
    "cough": "A simple remedy for cough is to drink warm honey and ginger tea...",
    "headache": "Drink plenty of water, apply a cold compress...",  
    "cold": "Inhale steam with eucalyptus oil, drink warm fluids...",
    "throat infection": "Gargle with warm salt water...",
    "indigestion": "Drink warm water with a pinch of baking soda..."
}

@app.route("/")
def home():
    if "user" in session:
        return render_template("index.html", username=session["user"])
    return redirect(url_for("login"))

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower()
    bot_response = responses.get(user_message, "Sorry, I don't understand. Please try again.")  
    return jsonify({"response": bot_response})

# User Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return "Username already exists!", 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")

# User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = username
            return redirect(url_for("home"))
        return "Invalid credentials!", 400

    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

