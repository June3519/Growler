from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class forgotpasswordForm(FlaskForm):
    email = EmailField('E-Mail', validators=[DataRequired(), Email()])
    submit = SubmitField("ResetPassword")