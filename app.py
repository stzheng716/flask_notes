"""Flask app for notes app."""

import os

from flask import Flask, render_template, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User

from forms import RegisterForm

app = Flask(__name__)


app.config["SECRET_KEY"] = "secret"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///notes"
)

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.get("/")
def get_homepage():
    """redirect to register"""
    
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def get_homepage():
    """render the register form"""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username=username, password=password, email=email, 
                   first_name=first_name, last_name=last_name)
        
        db.session.add(new_user)
        db.session.commit()

        return redirect(f"/users/{username}")
    
    return render_template("register.html", form=form)