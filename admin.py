from examiner import app, db
from examiner.db_models import Student
from examiner.exam_data import all_exams
from examiner.utility import add_time
from pathlib import Path
import os
import pandas as pd


def grab_students():
    '''tito: please ignore the data validation extension warning, 
    it is a safety measure to ensure the right class_type and cohort are entered in workbook
    '''
    students_wb = Path(r'examiner\src_files\students\students.xlsx')

    if students_wb.exists():
        students_df = pd.read_excel(students_wb)

        if students_df['id'].is_unique:
            students = [ 
                Student(
                    id=values['id'],
                    first_name=values['first_name'],
                    last_name=values['last_name'],
                    class_type=values['class_type'],
                    cohort=values['cohort']
                ) for _, values in students_df.iterrows()
            ]
            return students
        else:
            raise Exception('There are students with duplicate ids')
    else:
        raise Exception(f'student workbook file not found, check path {students_wb}')


def add_students_to_db():
    students = grab_students()
    with app.app_context():
        for student in students:
            db.session.add(student)
            db.session.commit()
    print('+++students added to db')


def create_db():
    with app.app_context():
        db.create_all()
    print('+++db created')


def delete_db():
    with app.app_context():
        db.drop_all()
    print('+++db deleted')


def recreate_db():
    user_input = input('recreate db? y/n: ')
    if user_input.lower() == 'y':
        delete_db()
        delete_student_scripts()
        create_db()
        add_students_to_db()
        print('+++db recreated')
    else:
        print('---db not recreated')


def find_exam(exam_id):
    return next((e for e in all_exams if e.id == exam_id), None)


def add_time_mins(minutes, student_id):
    add_time(student_id=student_id, added_seconds=minutes*60)


def delete_student_scripts():
    root = Path(r'examiner\src_files\exam_questions\student_scripts')
    scripts = [x for x in root.rglob('*.xlsx')]
    folders = [f for f in root.rglob('*') if f.is_dir()]
    if scripts:
        try:
            for s in scripts:
                os.remove(str(s))
            print('+++existing student scripts deleted')
        except:
            print('---existing student scripts not deleted, try manual delete')

    if folders:
        try:
            for f in folders:
                os.remove(str(f))
            print('---empty folders removed')
        except:
            print('---empty folders could not be removed, try manual delete')


def reset_student_info(student_id):
    with app.app_context():
        student = Student.query.get(student_id)
        if student:
            student.id_exam_logged_in = None
            student.id_exam_taken = None
            student.exam_start_time = None
            student.exam_ongoing = None

            if student.questions_src_file:
                student_questions_file = Path(student.questions_src_file)
                if student_questions_file.exists():
                    try:
                        os.remove(student_questions_file)
                        print(f'+++question file deleted, student_id={student_id}')
                    except:
                        print(f'---could not delete {student_questions_file} for student with id={student_id}, try manual delete')
            
            # resetting student questions file
            student.questions_src_file = None

            if student.marked_script_src_file:
                exam_script_file = Path(student.marked_script_src_file)
                if exam_script_file.exists():
                    try:
                        os.remove(exam_script_file)
                        print(f'+++marked script file deleted, student_id={student_id}')
                    except:
                        print(f'---could not delete {exam_script_file} for student with id={student_id}, try manual delete')

            # resetting marked script file
            student.marked_script_src_file = None

        else:
            print(f'---student with id={student_id} not in db')
        db.session.commit()


def get_percentage(score, max_score) -> str:
    return f'{((score*100)/max_score):.2f}%'


def collate_results(exam_id):
    with app.app_context():
        students = Student.query.all()
    if students:
        students_for_exam = [s for s in students if s.id_exam_taken == exam_id]
        if students_for_exam:
            columns=[
                'id', 
                'full_name', 
                'class_type', 
                'cohort', 
                'score', 
                'max_score', 
                'percentage'
            ]

            result_collation_df = pd.DataFrame(columns=columns)
            
            for index, s in enumerate(students_for_exam):
                student_script = pd.read_excel(s.marked_script_src_file, keep_default_na=False)
                student_score = student_script['score'].sum()
                test_max_score = student_script['score'].count()
                student_percentage = get_percentage(score=student_score, max_score=test_max_score)

                result_collation_df.loc[index] = [
                    s.id,
                    s.full_name,
                    s.class_type,
                    s.cohort,
                    student_score,
                    test_max_score,
                    student_percentage
                ]
            # the collated results should be stored in the exams folder which is the folder containing
            # the folder containing any student's marked script. Hence the parent.parent
            root = Path(students_for_exam[0].marked_script_src_file).parent.parent
            result_collation_filename = root/f'collated_results_{root.stem}.xlsx'
            result_collation_df.to_excel(str(result_collation_filename), index=False)
            print(f'results collated for exam with id={exam_id}\nfile={result_collation_filename}')
        else:
            print('---There are no students for that exam')
    else:
        print('---There are no students in database')


if __name__ == '__main__':
    user_input = input('perform admin operation? y/n: ')
    if user_input.lower() == 'y':
        recreate_db()
        # reset_student_info(student_id='david.nottidge@rain.com')
        # collate_results(exam_id='3')