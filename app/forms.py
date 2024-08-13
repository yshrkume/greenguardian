from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    DateField,
    SelectField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo


class SignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class PlantForm(FlaskForm):
    name = StringField("Plant Name", validators=[DataRequired()])
    purchase_date = DateField("Purchase Date", format="%Y-%m-%d")
    light_conditions = SelectField(
        "Light Conditions",
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        validators=[DataRequired()],
    )
    watering_frequency = SelectField(
        "Watering Frequency",
        choices=[
            ("daily", "Daily"),
            ("every 3 days", "Every 3 Days"),
            ("weekly", "Weekly"),
            ("bi-weekly", "Bi-weekly"),
            ("monthly", "Monthly"),
        ],
        validators=[DataRequired()],
    )
    fertilizing_frequency = SelectField(
        "Fertilizing Frequency",
        choices=[
            ("never", "Never"),
            ("monthly", "Monthly"),
            ("bi-monthly", "Bi-monthly"),
            ("seasonally", "Seasonally"),
        ],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Notes")
    submit = SubmitField("Save")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password")
    confirm_password = PasswordField(
        "Confirm Password", validators=[EqualTo("password")]
    )
    submit = SubmitField("Update")
