from datetime import datetime
import random
import string
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SESSION_TYPE"] = "filesystem"

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    fullname = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))

class Shortener(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_link = db.Column(db.String(255))
    short_link = db.Column(db.String(30), unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
        db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        long_link = request.form.get("url")
        short_link = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

        new_link = Shortener(long_link=long_link, short_link=short_link)
        db.session.add(new_link)
        db.session.commit()

        generated_short_link = new_link.short_link

        success_message = f"Long link successfully shortened! Your short link is: http://localhost:80/{generated_short_link}"

        # Pass shortened link and message to the template
        context = {
            "success_message": success_message,
        }
        links = Shortener.query.all()
        return render_template("index.html", **context, links=links)

    return render_template("index.html")
    

@app.route('/delete_link/<int:link_id>', methods=['POST', 'GET'])
def delete_link(link_id):
    if request.method == 'GET':
        # Confirmation logic can be added here (optional)
        pass
    else:
        link = Shortener.query.get(link_id)
        if link:
            db.session.delete(link)
            db.session.commit()
            #flash("Link deleted successfully!")
            #return redirect(url_for('index'))
            return jsonify({'message': 'Link deleted successfully!'})
        else:
            return jsonify({'message': 'Link not found'})
        
"""
@app.route('/database')
def database():
    links = Shortener.query.all()
    return render_template("database.html", links=links)
"""

@app.route('/<short_code>')
def redirect_to_long_link(short_code):
    link = Shortener.query.filter_by(short_link=short_code).first()
    if link:
        return redirect(link.long_link)
    else:
        return "Link not found."


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            flash("Username is taken")
            return redirect(url_for('signup'))

        new_user = Users(fullname=fullname,
                         username=username,
                         password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            #flash("Welcome")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash("Username is already in use.")
    return render_template('signup.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()

        if username == username:
            return redirect(url_for("index"))
            
        else:
            flash("Invalid credentials")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")

    return render_template('login.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80, debug=True)