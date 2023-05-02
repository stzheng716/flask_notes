"""Flask app for notes app."""

import os

from flask import Flask, render_template, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User

from forms import RegisterForm, LoginForm, CSRFProtectForm

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
def register():
    """render the register form, if registration is successful,
    redirect to their user page"""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        if User.query.get(username):
            form.username.errors = ["Username taken"]
            return render_template("register.html", form=form)

        new_user = User.register(username=username,
                                 password=password,
                                 email=email,
                                 first_name=first_name,
                                 last_name=last_name)

        db.session.add(new_user)
        db.session.commit()

        session["username"] = new_user.username

        return redirect(f"/users/{username}")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """render the login form, if login is successful,
    redirect to their user page"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username=username,
                                 password=password)

        if user:
            session["username"] = user.username
            return redirect(f"/users/{username}")
        else:
            form.username.errors = ["Invalid username or password"]

    return render_template("login.html", form=form)

@app.get("/users/<username>")
def display_user_info(username):
    """Requires authentication. Displays all user info for
    this user (except for the password)"""

    s_user = session.get("username")

    form = CSRFProtectForm()
    # not logged in
    if not s_user:
        flash("You must be logged in to view that page.")
        return redirect("/login")

    # trying to view other user's page
    elif s_user != username:
        flash("You don't have access to that page.")
        return redirect(f"/users/{s_user}")

    user = User.query.get_or_404(username)
    return render_template("user.html", user=user, form=form)

@app.post("/logout")
def logout():
    """log users out and redirects to / """

    form = CSRFProtectForm()

    if form.validate_on_submit():

        flash("Logged out")
        session.pop("username", None)

    return redirect("/")