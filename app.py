"""Flask app for notes app."""

import os

from flask import Flask, render_template, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
# from flask_sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Note

from forms import RegisterForm, LoginForm, CSRFProtectForm, AddEditNoteForm

app = Flask(__name__)

#FIXME: global const for session/username key

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

    s_username = session.get("username")

    # already logged in
    if s_username:
        flash("You are already logged in.")
        return redirect(f"/users/{s_username}")

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
        try:
            db.session.commit()
        except IntegrityError as exc:
            print(exc)
            # breakpoint()
            form.email.errors = ["Email taken"]
            return render_template("register.html", form=form)

        session["username"] = new_user.username

        return redirect(f"/users/{username}")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """render the login form, if login is successful,
    redirect to their user page"""

    s_username = session.get("username")

    # already logged in
    if s_username:
        flash("You are already logged in.")
        return redirect(f"/users/{s_username}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(
            username=username,
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

    s_username = session.get("username")

    # not logged in
    if not s_username:
        flash("You must be logged in to view that page.")
        return redirect("/login")

    # trying to view other user's page
    elif s_username != username:
        flash("You don't have access to that page.")
        return redirect(f"/users/{s_username}")

    form = CSRFProtectForm()
    user = User.query.get_or_404(username)


    return render_template("user.html", user=user, form=form, notes=user.notes)

@app.post("/logout")
def logout():
    """log users out and redirects to / """

    form = CSRFProtectForm()

    if form.validate_on_submit():

        flash("Logged out")
        session.pop("username", None)

    return redirect("/")

@app.post("/users/<username>/delete")
def delete_user(username):
    """delete user """

    s_username = session.get("username")

    if not s_username:
        flash("You must be log in to delete user.")
        return redirect("/login")

    # trying to delete other users
    elif s_username != username:
        flash("You can't delete others.")
        return redirect(f"/users/{s_username}")

    form = CSRFProtectForm()

    if form.validate_on_submit():

        #FIXME: handle notes for this user

        user = User.query.get_or_404(username)

        db.session.delete(user)
        db.session.commit()

        flash("Deleted user")
        session.pop("username", None)

    return redirect("/")


@app.get("/notes/<int:note_id>/")
def display_note(note_id):
    """
    Must be authenticated.
    Displays the note title and content given its id.
    """

    s_username = session.get("username")

    # not logged in
    if not s_username:
        flash("You must log in to view notes.")
        return redirect(f"/login")

    #FIXME: authorization

    note = Note.query.get_or_404(note_id)

    return render_template("note.html", note=note)

@app.route("/users/<username>/notes/add", methods=["GET", "POST"])
def add_note(username):
    """
    Must be authenticated.
    GET: render the add note page for a given user
    POST: add the note and redirect to /users/<username>
    """

    s_username = session.get("username")

    # not logged in
    if not s_username:
        flash("You must log in to add a note.")
        return redirect(f"/login")

    if s_username != username:
        flash("You don't have permission to do that.")
        return redirect(f"/users/{s_username}")

    form = AddEditNoteForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        note = Note(title=title, content=content, owner_username=s_username)

        db.session.add(note)
        db.session.commit()

        return redirect(f"/users/{s_username}")

    return render_template("add_note.html", form=form)


@app.route("/notes/<int:note_id>/update", methods=["GET", "POST"])
def update_note(note_id):
    """
    Must be authenticated.
    GET: render the update note page for a given note id
    POST: update the note and redirect to /users/<username>
    """

    s_username = session.get("username")

    # not logged in
    if not s_username:
        flash("You must log in to update a note.")
        return redirect(f"/login")

    #FIXME: authorization

    note = Note.query.get_or_404(note_id)

    form = AddEditNoteForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{s_username}")

    return render_template("update_note.html", form=form)


@app.post("/notes/<int:note_id>/delete")
def delete_note(note_id):
    """
    Must be authenticated.
    Deletes the note and redirects to /users/<username>
    """

    s_username = session.get("username")

    # not logged in
    if not s_username:
        flash("You must log in to delete a note.")
        return redirect(f"/login")

    #FIXME: authorization

    form = CSRFProtectForm()

    if form.validate_on_submit():
        flash("Note deleted!")

        note = Note.query.get_or_404(note_id)

        db.session.delete(note)
        db.session.commit()

    return redirect(f"/users/{s_username}")