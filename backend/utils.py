import random

def select_random_questions(questions, num_questions):
    """Selects a random sample of question IDs from a list of questions."""
    if num_questions > len(questions):
        raise ValueError("Number of questions requested exceeds available questions.")
    selected_questions = random.sample(questions, num_questions)
    return [q.id for q in selected_questions]

def shuffle_questions(exam_questions):
    """Shuffles the order of ExamQuestion objects."""
    random.shuffle(exam_questions)
    return exam_questions
