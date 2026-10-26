from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from config import SECRET_KEY, DATABASE_URL

app = Flask(__name__)

app.secret_key = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.String, nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

def get_current_user():
    if "email" in session:
        email = session.get("email")
        return User.query.filter_by(email=email).first()
    return None

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session:
        flash("You must be logged in to access dashboard.")
        return redirect(url_for("login"))

    if request.method == "POST":
        current_user = get_current_user()
        content = request.form.get("content")
        user_id = current_user.id

        new_post = Post(
            user_id=user_id,
            content=content,
        )

        db.session.add(new_post)
        db.session.commit()
        flash("New post created successfully!")
        return redirect(url_for("dashboard"))

    posts = Post.query.all()
    return render_template("dashboard.html", user=get_current_user(), all_posts=posts)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("pass")

        if User.query.filter_by(email=email).first() is not None:
            flash("User already exists with this email! Login.")
            return redirect(url_for("signup"))

        password_hash = generate_password_hash(password)

        new_user = User(
            name=fullname,
            email=email,
            password_hash=password_hash,
        )

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        flash("You are already logged in!")
        return redirect("dashboard")
    
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("pass")

        current_user = User.query.filter_by(email=user_email).first()

        if current_user is None:
            flash("User does not exist. Please sign up.", category="red")
            return redirect(url_for("login"))

        password_hash = current_user.password_hash

        if not check_password_hash(password_hash, user_password):
            flash("Incorrect password entered! Try again.")
            return redirect(url_for("login"))

        session["username"] = current_user.name
        session["email"] = current_user.email

        flash("Login successful!", category="green")

        return redirect(url_for("dashboard"))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)

