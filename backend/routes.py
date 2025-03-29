from flask import Blueprint, jsonify, request, abort
from backend.database import db
from backend.models import Question, Exam, ExamQuestion, Student
from backend.utils import select_random_questions, shuffle_questions
import csv  # Import the csv module

main_bp = Blueprint('main', __name__)

@main_bp.route('/upload_questions', methods=['POST'])
def upload_questions():
    """Handles uploading a CSV file and storing questions in the database."""
    if 'file' not in request.files:
        abort(400, "No file provided", 400)

    file = request.files['file']
    if file.filename == '':
        abort(400, "Empty filename", 400)

    if file:
        try:
            csvfile = csv.reader(file.read().decode('utf-8').splitlines())
            header = next(csvfile)  # Skip header row (if any)
            for row in csvfile:
                # Assuming CSV structure: text, option1, option2, option3, option4, correct_answer, topic, difficulty
                # Adjust the indices below based on your CSV structure
                new_question = Question(
                    text=row[0],
                    option1=row[1],
                    option2=row[2],
                    option3=row[3],
                    option4=row[4],
                    correct_answer=row[5],
                    topic=row[6],
                    difficulty=int(row[7]) if row[7] else None  # Handle empty difficulty
                )
                db.session.add(new_question)
            db.session.commit()
            return jsonify({"message": "Questions uploaded successfully"}), 200
        except Exception as e:
            db.session.rollback()  # Rollback changes in case of error
            abort(500, f"Error uploading CSV: {str(e)}", 500)
    else:
        abort(400, "Invalid file", 400)

@main_bp.route('/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    return jsonify([{"id": q.id, "text": q.text, "option1": q.option1, "option2": q.option2, "option3": q.option3, "option4": q.option4} for q in questions])

@main_bp.route('/questions', methods=['POST'])
def create_question():
    data = request.get_json()
    new_question = Question(text=data['text'], option1=data['option1'], option2=data['option2'], option3=data['option3'], option4=data['option4'], correct_answer=data['correct_answer'], topic=data.get('topic'), difficulty=data.get('difficulty'))
    db.session.add(new_question)
    db.session.commit()
    return jsonify({"message": "Question created"}), 201

@main_bp.route('/exams', methods=['POST'])
def create_exam():
    data = request.get_json()
    num_questions = data['num_questions']
    duration = data['duration']
    questions = Question.query.all()
    selected_question_ids = select_random_questions(questions, num_questions)

    new_exam = Exam(num_questions=num_questions, duration=duration)
    db.session.add(new_exam)
    db.session.commit()

    exam_questions = []
    for i, question_id in enumerate(selected_question_ids):
        exam_question = ExamQuestion(exam_id=new_exam.id, question_id=question_id, question_order=i + 1, question_id=question_id)
        exam_questions.append(exam_question)

    # Shuffle the questions for each candidate
    shuffled_exam_questions = shuffle_questions(exam_questions)

    db.session.add_all(exam_questions)
    db.session.commit()

    return jsonify({"message": "Exam created", "exam_id": new_exam.id}), 201

@main_bp.route('/exams/<int:exam_id>/questions', methods=['GET'])
def get_exam_questions(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    # Fetch the ExamQuestion entries and join with the Question model
    exam_questions = db.session.query(ExamQuestion, Question).join(Question).filter(ExamQuestion.exam_id == exam_id).order_by(ExamQuestion.question_order).all()
    # Ensure questions are shuffled
    questions_list = []
    for eq, q in exam_questions:
        questions_list.append({
            "id": q.id,  # Use question_id from ExamQuestion
            "text": q.text,
            "option1": q.option1,
            "option2": q.option2,
            "option3": q.option3,
            "option4": q.option4,
            "question_order": eq.question_order  # Include question_order
        })
    return jsonify(questions_list)

@main_bp.route('/exams/<int:exam_id>/submit', methods=['POST'])
def submit_exam(exam_id):
    data = request.get_json()
    answers = data['answers']

    exam = Exam.query.get_or_404(exam_id)
    exam_questions = ExamQuestion.query.filter_by(exam_id=exam_id).all()

    if len(answers) != len(exam_questions):
        abort(400, "Number of answers does not match number of questions", 400)

    for eq in exam_questions:
        eq.student_answer = answers.get(str(eq.question_id))  # Use question.id
    db.session.commit()

    return jsonify({"message": "Exam submitted"}), 200

@main_bp.route('/exams/<int:exam_id>/results', methods=['GET'])
def get_exam_results(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    exam_questions = db.session.query(ExamQuestion, Question).join(Question).filter(ExamQuestion.exam_id == exam_id).order_by(ExamQuestion.question_order).all()

    correct_count = 0
    attempted_count = 0
    results = []

    for eq, q in exam_questions:
        correct = (eq.student_answer == q.correct_answer)
        if correct:
            correct_count += 1
        if eq.student_answer is not None:
            attempted_count += 1
        results.append({
            "question_id": q.question_id,  # Use question_id
            "question_text": q.text,
            "correct_answer": q.correct_answer,
            "student_answer": eq.student_answer,
            "correct": correct
        })

    total_questions = len(exam_questions)
    percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    skipped_count = total_questions - attempted_count
    unattempted_count = total_questions - attempted_count

    return jsonify({
        "exam_id": exam_id,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "attempted_count": attempted_count,
        "skipped_count": skipped_count,
        "unattempted_count": unattempted_count,
        "percentage": percentage,
        "results": results
    })
