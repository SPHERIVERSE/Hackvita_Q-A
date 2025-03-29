from backend.database import db

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable-False)
    option3 = db.Column(db.String(200), nullable-False)
    option4 = db.Column(db.String(200), nullable-False)
    correct_answer = db.Column(db.String(1), nullable=False)  # '1', '2', '3', or '4'
    topic = db.Column(db.String(100))
    difficulty = db.Column(db.Integer)  # 1-Easy, 2-Medium, 3-Hard

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_questions = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    start_time = db.Column(db.DateTime)

class ExamQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable-False)
    question_order = db.Column(db.Integer, nullable=False)  # Order of question in exam
    student_answer = db.Column(db.String(1))

class Student(db.Model):  # Basic Student model
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
