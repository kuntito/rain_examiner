from examiner import app, db
from pathlib import Path
from examiner.db_models import Student
from examiner.models import Exam
from examiner.utility import get_now_in_seconds
from flask import render_template, abort, redirect, url_for, flash, request
from examiner.exam_data import all_exams
from examiner.forms import ExamLoginForm
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd



def find_exam(exam_id):
    return next((e for e in all_exams if e.id == exam_id), None)


@app.route('/')
@app.route('/exams')
def exams():
    if current_user.is_authenticated:
        flash(f'log out to access exams page', 'normal')
        return redirect(url_for('exam_details'))

    return render_template(
        'exams.html',
        title='exams',
        exams=all_exams
    )


# TODO place function elsewhere
def is_student_eligible(student, exam) -> bool:
    # [exam.participant_cohort] has it's name stored as C7, C8, C9
    # while [student.cohort] stores its values as 7, 8, 9.
    student_cohort = f'C{student.cohort}'

    # [exam] properties [participant_class] and [participant_cohort] can be a list of strings or a string
    return (student.class_type in exam.participant_class or student.class_type == exam.participant_class) and\
             (student_cohort in exam.participant_cohort or student_cohort == exam.participant_cohort)


# TODO place function elsewhere
def flash_and_refresh(message, url, message_type='normal'):
    flash(message, message_type)
    return redirect(url)



@app.route('/exam-login/<string:exam_id>', methods=['GET', 'POST'])
def exam_login(exam_id):
    exam = find_exam(exam_id)
    if not exam:
        abort(404)

    if current_user.is_authenticated:
        if current_user.id_exam_logged_in != exam.id:
            current_user_exam = find_exam(current_user.id_exam_logged_in)
            # tell the user they have to logout of the current exam before logging into a new one
            return flash_and_refresh(
                message=f'To access {exam.title}, Log out from {current_user_exam.title}',
                message_type='normal',
                url = url_for('exams')
            )
        else:
            return redirect(url_for('exam_details'))

    form = ExamLoginForm()

    if form.validate_on_submit():
        with app.app_context():
            # grabbing the students info based on their id, returns None if student not found
            student = Student.query.get(form.student_id.data.lower())
        password = form.password.data

        if student:
            if not is_student_eligible(student, exam):
                return flash_and_refresh(
                    message=f'{student.full_name} is ineligible to write {exam.title}',
                    message_type='error',
                    url = url_for('exam_login', exam_id=exam_id)
                )


            if password == exam.password:
                with app.app_context():
                    _student = Student.query.get(student.id)

                    if _student.id_exam_logged_in:
                        return flash_and_refresh(
                            message="login failed, you're logged in somewhere else",
                            message_type='error',
                            url = url_for('exam_login', exam_id=exam_id)
                        )
                    
                    _student.id_exam_logged_in = exam.id
                    db.session.commit()

                login_user(student)

                next_page = request.args.get('next')
                return redirect(f'{next_page}/{exam_id}' if next_page else url_for('exam_details'))
            else:
                return flash_and_refresh(
                    message=f'Login failed, check student id or exam password',
                    message_type='error',
                    url = url_for('exam_login', exam_id=exam_id)
                )
        else:
            return flash_and_refresh(
                message=f'user id not in database',
                message_type='error',
                url = url_for('exam_login', exam_id=exam_id)
            )

    return render_template(
        'exam_login.html',
        title='exam login',
        form=form,
        exam=exam
    )


@app.route('/exam-details', methods=['GET', 'POST'])
@login_required
def exam_details():
    if current_user.id_exam_logged_in == None:
        return redirect(url_for('log_out'))

    exam = find_exam(current_user.id_exam_logged_in)

    if not exam:
        abort(404)

    return render_template(
        'exam_details.html',
        title='exam details',
        exam=exam,
        exam_details=exam.details
    )


# TODO move this function elsewhere
def initialize_student_questions(student, exam):
    """when an exam is started, a copy of the students question is made
where the students answers will also be stored. This copy is used to save
the students answers and for subsequent marking
"""
    # student questions and options are shuffled
    student_questions = pd.read_excel(exam.questions_src_file)\
        .drop(['correct_option_text', 'correct_option_id'], axis=1)\
        .drop_duplicates('id')\
        .sample(frac=1)\
        .sample(frac=1, axis=1)
    student_questions['selected_option_id'] = ''
    student_questions['selected_option_text'] = ''

    root = Path(r'examiner\src_files\exam_questions\student_scripts')
    exam_folder = root/f'{exam.id}_{exam.title}'
    exam_folder.mkdir(exist_ok=True)

    # create a folder for the student, the paths used here are pathlib objects
    questions_src_filename = Path(f'{student.id}_{exam.id}_{exam.title}.xlsx')
    student_folder = exam_folder/questions_src_filename.stem
    student_folder.mkdir(exist_ok=True)

    student_questions_file = student_folder/questions_src_filename
    student_questions.to_excel(student_questions_file, index=False)

    with app.app_context():
        Student.query.get(student.id).questions_src_file = str(student_questions_file)
        db.session.commit()



@app.route('/on-exam-start', methods=['POST'])
def on_exam_start():
    response = ''
    exam = find_exam(current_user.id_exam_logged_in)

    with app.app_context():
        # [student] and [current_user] are the same object, but in order to commit a change to the database
        # a query for that object has to be made then changes made to that object which is [student] in this case
        student = Student.query.get(current_user.id)
        start_time = get_now_in_seconds()
        student.exam_ongoing = True
        student.id_exam_taken = exam.id
        student.exam_start_time = start_time
        
        db.session.commit()

    initialize_student_questions(current_user, exam)
    response = f'server has been notified that {current_user.full_name} has started exam, start time {start_time}'

    return response


@app.route('/current-user-exam-start-time', methods=['POST'])
@login_required
def current_user_exam_start_time():
    # with open('foo.txt', 'a+') as f:
    #     f.writelines(f'{current_user.exam_start_time}\ntype={type(current_user.exam_start_time)}')

    if not current_user.exam_ongoing:
      abort(403)

    with app.app_context():
      start_time = Student.query.get(current_user.id).exam_start_time

    # integers are invalid html reponses, hence the conversion to string
    return str(start_time)


# The server's current time in ms
@app.route('/now', methods=['POST'])
def now():
    # with open('foo.txt', 'a+') as f:
    #     f.writelines(f'{str(get_now_in_seconds())}\n')
    # integers are invalid html reponses, hence the conversion to string
    return str(get_now_in_seconds())



@app.route('/questions')
@login_required
def questions():
    if current_user.id_exam_logged_in == None:
        return redirect(url_for('log_out'))

    if not current_user.exam_ongoing:
        return redirect(url_for('exam_details'))
    
    exam = find_exam(current_user.id_exam_logged_in)
    # with open('foo.txt', 'a+') as f:
    #     f.writelines(f'{current_user.questions_src_file}')
    student_questions = Exam.grab_questions(current_user.questions_src_file)

    return render_template(
        'questions.html',
        title='questions',
        exam=exam,
        questions=[q for q in student_questions]
    )


@app.route('/questions-grid')
@login_required
def questions_grid():
    if current_user.id_exam_logged_in == None:
        return redirect(url_for('log_out'))

    if not current_user.exam_ongoing:
        return redirect(url_for('exam_details'))
    
    exam = find_exam(current_user.id_exam_logged_in)
    student_questions = Exam.grab_questions(current_user.questions_src_file)

    return render_template(
        'questions_grid.html',
        title='questions',
        exam=exam,
        questions=[q for q in student_questions]
    )


# TODO place function elsewhere
def update_selected_option(question_id, option_id, option_text, student):
    df = pd.read_excel(student.questions_src_file, keep_default_na=False)
    filter = df['id'] == question_id

    df.loc[filter, 'selected_option_id'] = option_id
    df.loc[filter, 'selected_option_text'] = option_text
    df.to_excel(student.questions_src_file, index=False)


@app.route('/on-option-selected', methods=['POST'])
def on_option_selected():
    value = request.get_json()
    question_id = value["question_id"]
    option_id = value["option_id"]
    option_text = value["option_text"]
    exam_id = value["exam_id"]

    update_selected_option(question_id=question_id, option_id=option_id, option_text=option_text, student=current_user)

    info = f'question {question_id}, option {option_id}, exam_id {exam_id}'

    response = f'Server: {info} received\n'

    return response


# TODO move function elsewhere
def save_marked_script(student, marked_script_df: pd.DataFrame):
    '''saves [script_with_marks] as an excel file and returns it's file path as pathlib.Path object'''
    x = Path(student.questions_src_file)
    
    marked_script_file = x.parent/f'Marked-{x.name}'

    marked_script_df.to_excel(str(marked_script_file), index=False)

    with app.app_context():
        _student = Student.query.get(student.id)
        _student.marked_script_src_file = str(marked_script_file)
        db.session.commit()
    
    return marked_script_file


# TODO move function elsewhere
def mark_script(student, marking_guide_file):
    '''It returns a tuple of the marked script (pandas.Dataframe) and the total_score(int)
The marked script has a column that contains the score for each question'''
    marking_guide = pd.read_excel(marking_guide_file, keep_default_na=False)\
        .drop_duplicates('id')\
        .sort_values('id')
    student_script = pd.read_excel(student.questions_src_file, keep_default_na=False)\
        .sort_values('id')

    script_with_marks = pd.merge(
        marking_guide, 
        student_script[['id', 'selected_option_id', 'selected_option_text']], 
        on='id'
    )
    script_with_marks['score'] = (script_with_marks['correct_option_id'] == script_with_marks['selected_option_id']).astype(int)

    return script_with_marks


def mark_and_save_script(student, marking_guide_file):
    marked_script_df = mark_script(student, marking_guide_file)
    save_marked_script(student=student, marked_script_df=marked_script_df)


@app.route('/on-exam-end', methods=['POST'])
@login_required
def on_exam_end():
    with app.app_context():
        Student.query.get(current_user.id).exam_ongoing = False
        db.session.commit()

    exam = find_exam(current_user.id_exam_logged_in)
    try:
        response = 'exam not marked and not saved'
        mark_and_save_script(student=current_user, marking_guide_file=exam.questions_src_file)
    except Exception as e:
        with open('exam_end_log.txt', 'a+') as f:
            f.writelines(f'''
user_name = {current_user.full_name}
user_id = {current_user.id}
{e}''')
    else:
        response = 'exam marked and saved'

    return response


@app.route('/exam-result')
@login_required
def exam_result():
    if current_user.id_exam_logged_in == None:
        return redirect(url_for('log_out'))

    score = None
    question_review_details = None
    exam = find_exam(current_user.id_exam_logged_in)

    if current_user.questions_src_file and Path(current_user.questions_src_file).exists():
        if not current_user.marked_script_src_file or not Path(current_user.marked_script_src_file).exists():
            mark_and_save_script(student=current_user, marking_guide_file=exam.questions_src_file)
        
        marked_script = pd.read_excel(current_user.marked_script_src_file, keep_default_na=False)
        score = marked_script['score'].sum()

        question_review_details = [{
            'question_text': row['question_text'],
            'correct_answer': str(row['correct_option_text']),
            'your_answer': str(row['selected_option_text']),
            'student_is_correct': row['score']
        } for _, row in marked_script.iterrows()]

        # with open('foo.txt', 'a+') as f:
        #     f.writelines(f'{question_review_details}\n')

    else:
        flash('user has no exam record')
    
    return render_template(
        'exam_result.html',
        title='Exam result',
        score=score,
        exam=exam,
        question_review_details=question_review_details
    )


@app.route('/log-out')
@login_required
def log_out():
    with app.app_context():
        Student.query.get(current_user.id).id_exam_logged_in = None
        db.session.commit()

    logout_user()
    return redirect(url_for('exams'))