from examiner import app, db
from examiner.exam_data import all_exams
from examiner.db_models import Student


def get_now_in_seconds() -> int:
    import time
    return round(time.time())


def add_time(student_id, added_seconds):
    """this function adds time to a students exam time. if the student's exam is not found or the 
    [added_seconds] is greater than the duration of the exam, the function returns a string response"""

    response = 'nothing happened'
    with app.app_context():
        student = Student.query.get(student_id)
        if student.exam_start_time:
            exam = next((e for e in all_exams if e.id == student.id_exam_logged_in), None)
            if exam is None:
                response = f"exam was not found for {student.full_name} "
                return response

            if student.exam_ongoing:
                student.exam_start_time += added_seconds
            else:
                exam_duration_seconds = exam.duration * 60
                if added_seconds > exam_duration_seconds:
                    response = f'added seconds{added_seconds} greater than exam duration in seconds{exam_duration_seconds}'
                    return response

                # the timer is based on the start time of the exam
                # to add 10s to a 60s seconds exam, you set the [start_time] to 50seconds (60-10)
                # before now. so the timer starts counting down from 10
                elapsed_time = exam_duration_seconds - added_seconds
                student.exam_start_time = get_now_in_seconds() - elapsed_time
                student.exam_ongoing = True
            db.session.commit()
            response = f'added seconds{added_seconds} greater than exam duration in seconds{exam_duration_seconds}'
    return response
