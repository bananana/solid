from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import Email, InputRequired


class ContactForm(FlaskForm):
  name = StringField("Name", validators=[InputRequired()])
  email = StringField("Your e-mail address", 
                      validators=[InputRequired(), Email()])
  message = TextAreaField("Message", validators=[InputRequired()])
  send_to_self = BooleanField(label="Send a copy of this message to yourself")
