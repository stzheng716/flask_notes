from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField

from wtforms.validators import InputRequired, Email, Length


class RegisterForm(FlaskForm):
    """Form for adding a user."""

    username = StringField("Username", validators=[
                           InputRequired(), Length(max=20)])

    password = PasswordField("Password", validators=[
                             InputRequired(), Length(max=100)])

    email = StringField("Email", validators=[
                        InputRequired(), Email(), Length(max=50)])

    first_name = StringField("First name", validators=[
                             InputRequired(), Length(max=30)])

    last_name = StringField("Last name", validators=[
                            InputRequired(), Length(max=50)])


class LoginForm(FlaskForm):
    """Form for authenticating a user."""

    username = StringField("Username", validators=[
                           InputRequired(), Length(max=20)])

    password = PasswordField("Password", validators=[
                             InputRequired(), Length(max=100)])

class AddNoteForm(FlaskForm):
    """Form for adding a new note."""

    title = StringField("Title", validators=[InputRequired(), Length(max=100)])

    content = TextAreaField("Content", validators=[InputRequired()])

class EditNoteForm(FlaskForm):
    """Form for adding a new note."""

    title = StringField("Title", validators=[InputRequired(), Length(max=100)])

    content = TextAreaField("Content", validators=[InputRequired()])


class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""