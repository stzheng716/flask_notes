from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField

from wtforms.validators import InputRequired, Email, Length


class RegisterForm(FlaskForm):
    """Form for adding a user."""

    username = StringField("Username", validators=[
                           InputRequired(), Length(max=20)])
    
    password = PasswordField("password", validators=[
                             InputRequired(), Length(max=100)])
    
    email = StringField("Email", validators=[
                        InputRequired(), Email(), Length(max=50)])
    
    first_name = StringField("First name", validators=[
                             InputRequired(), Length(max=30)])
    
    last_name = StringField("last name", validators=[
                            InputRequired(), Length(max=50)])
