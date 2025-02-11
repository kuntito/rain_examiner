from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField ,SubmitField
from wtforms.validators import DataRequired, Length
from abc import ABC, abstractmethod


class ExamLoginForm(FlaskForm):
    student_id = StringField(
        validators=[
            DataRequired(),
            Length(min=3)
        ], 
        render_kw={"placeholder": "Student id"}
    )

    password = PasswordField(
        validators=[
            DataRequired(),
            Length(min=5)
        ], 
        render_kw={"placeholder": "Exam password"}
    )

    submit = SubmitField('Login')

    @property
    def fields(self):
        return [self.student_id, self.password]
