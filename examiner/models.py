import re
import pandas as pd
import json

# TODO mandate parameter data types in all classes
from enum import Enum

 
class ClassType(Enum):
    AIML = 1
    RDA = 2


class Cohort(Enum):
    C7 = 1
    C8 = 2
    C9 = 3


class JsonClass:    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=2)


# class QuestionOption(JsonClass):
#     def __init__(self, option_id, option_text) -> None:
#         super().__init__()
#         self.id = option_id
#         self.text = option_text


# class Question(JsonClass):
#     def __init__(self, question_id, question_text, question_options) -> None:
#         super().__init__()
#         self.id = question_id
#         self.question_text = question_text
#         self.options = question_options
#         self.selected_option_id = None


class Exam(JsonClass):
    def __init__(self, exam_id, title, participant_class, participant_cohort, duration, questions_src_file, password) -> None:
        super().__init__()
        self.id = exam_id
        self.title = title
        self._participant_class = participant_class
        self._participant_cohort = participant_cohort
        self.duration = duration
        self.questions_src_file = questions_src_file
        self.password = password


    @staticmethod
    def grab_questions(wb_path):
        """returns a list of questions from an excel file. It grabs each row and generates a dictionary
with key value pairs {column_name: column_value}
The columns names should be index, question_text, option1, option2, option3, option4.
The options can be more or less than 4. It is imperative that the option columns be in the
regex format 'option\d+' as that is the recognized pattern. The option columns are stored in a list.
Any other column can be added as the need arises"""
        df = pd.read_excel(wb_path, keep_default_na=False).drop_duplicates('id')
        questions = []
        for _ , row in df.iterrows():
            question_dict = {}
            options = []
            for k, v in row.items():

                pattern = r'option\d+'
                if re.fullmatch(pattern, k.lower()):
                    options.append({
                        'id':k,
                        'text':v
                    })
                else:
                    question_dict[k] = v
            else:
                question_dict['options'] = options

            questions.append(question_dict)
        
        return questions


    @property
    def participant_class(self):
        if type(self._participant_class) == list:
            return ' & '.join([c.name for c in self._participant_class])
        else:
            return self._participant_class.name

    @property
    def participant_cohort(self):
        if type(self._participant_cohort) == list:
            return ' & '.join([c.name for c in self._participant_cohort])
        else:
            return self._participant_cohort.name

    @property
    def questions(self):
        return self.grab_questions(self.questions_src_file)

    @property
    def details(self):
        return {
            'exam title': self.title,
            'duration': f'{self.duration} min(s)'
        }
