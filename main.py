from datetime import datetime
import random
import string
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, relationship

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
    logged_in = db.Column(db.Boolean, default=False)

class Shortener(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_link = db.Column(db.String(255))
    short_link = db.Column(db.String(30), unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', backref='links')

with app.app_context():
        db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        long_link = request.form.get("url")
        user = session.get('user_id')
        if Users.logged_in == True:
            existing_link = Shortener.query.filter_by(long_link=long_link).first()
            if existing_link:
            # Link already exists, return the existing short link
                short_link = existing_link.short_link
                success_message = f"Long link already shortened! Your short link is: http://localhost:80/{short_link}"
            else:
                short_link = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

                new_link = Shortener(long_link=long_link, short_link=short_link)
                db.session.add(new_link)
                db.session.commit()

                generated_short_link = new_link.short_link
                success_message = f"Long link successfully shortened! Your short link is: http://localhost:80/{generated_short_link}"
            context = {
                "success_message": success_message,
            }
            links = Shortener.query.all()
            return render_template("index.html", **context, links=links)
        
        else:
            user_links = Shortener.query.count()
            if user_links >= 5:
                links = Shortener.query.all()
                success_message = "Limit reached. Pls login to continue creating"
            else:
                existing_link = Shortener.query.filter_by(long_link=long_link).first()
                if existing_link:
                 # Link already exists, return the existing short link
                    short_link = existing_link.short_link
                    success_message = f"Long link already shortened! Your short link is: http://localhost:80/{short_link}"
                else:
                    short_link = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

                    new_link = Shortener(long_link=long_link, short_link=short_link)
                    db.session.add(new_link)
                    db.session.commit()

                    generated_short_link = new_link.short_link
                    success_message = f"Long link successfully shortened! Your short link is: http://localhost:80/{generated_short_link}"
            context = {
                "success_message": success_message,
                "user_links": user_links
            }
            links = Shortener.query.all()
            print(user_links)
            return render_template("index.html", **context, links=links)
    return render_template("index.html")
    

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
        new_user.logged_in = True  # Set logged_in to True after successful signup
        print("Logged in")
        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash("Username is already in use.")
    return render_template('login.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()
        Users.logged_in = True
        print("Im in")

        if username == username:
            return redirect(url_for("index"))
            
        else:
            flash("Invalid credentials")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")

    return render_template('login.html')


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
            return jsonify({'message': 'Link deleted successfully!'})
        else:
            return jsonify({'message': 'Link not found'})
        

@app.route('/<short_code>')
def redirect_to_long_link(short_code):
    link = Shortener.query.filter_by(short_link=short_code).first()
    if link:
        return redirect(link.long_link)
    else:
        return "Link not found."

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80, debug=True)
