from examiner.models import Exam, ClassType, Cohort
from pathlib import Path


exam_questions_root = Path(r'examiner\src_files\exam_questions\exams')
dummy_password = 'password'


all_exams = [
    Exam(
        exam_id='1',
        title='Python basics',
        participant_class=[ClassType.AIML, ClassType.RDA],
        participant_cohort=Cohort.C9,
        duration=10,
        questions_src_file=exam_questions_root/'Python basics.xlsx',
        password=dummy_password
    ),
    Exam(
        exam_id='2',
        title='Deep learning basics',
        participant_class=ClassType.AIML,
        participant_cohort=Cohort.C8,
        duration=45,
        questions_src_file=exam_questions_root/'Deep learning basics.xlsx',
        password=dummy_password
    ),
    Exam(
        exam_id='3',
        title='IoT basics',
        participant_class=ClassType.RDA,
        participant_cohort=[Cohort.C8, Cohort.C9],
        duration=120,
        questions_src_file=exam_questions_root/'IoT basics.xlsx',
        password=dummy_password
    )
]
