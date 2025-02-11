from examiner import app, db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        user = Student.query.get(user_id)
    return user


class Student(db.Model, UserMixin):
    id = db.Column(db.String(), primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    class_type = db.Column(db.String(4), nullable=False)
    cohort = db.Column(db.String(2), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    #TODO the data type of this column should match that of the exam_id in the [Exam] model
    id_exam_logged_in = db.Column(db.String(2), nullable=True)
    id_exam_taken = db.Column(db.String(2), nullable=True)
    exam_start_time = db.Column(db.Integer, nullable=True)
    exam_ongoing = db.Column(db.Boolean, nullable=True)
    questions_src_file = db.Column(db.String(), unique=True, nullable=True)
    marked_script_src_file = db.Column(db.String(), unique=True, nullable=True)

    def __repr__(self) -> str:
        return f"Student('{self.full_name}', '{self.class_type})'"

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

        
