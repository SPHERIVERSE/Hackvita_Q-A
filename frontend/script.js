const examSetupContainer = document.getElementById('exam-setup-container');
const examIdInput = document.getElementById('exam-id-input');
const startExamBtn = document.getElementById('start-exam-btn');
const quizContainer = document.getElementById('quiz-container');
const quizHeader = document.getElementById('quiz-header');
const questionContainer = document.getElementById('question-container');
const questionText = document.getElementById('question');
const optionsContainer = document.getElementById('options-container');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const questionNumber = document.getElementById('question-number');
const submitBtn = document.getElementById('submit-btn');
const timerDisplay = document.getElementById('time');
const quoteContainer = document.getElementById('quote-container');

let questions = [];
let currentQuestionIndex = 0;
let answers = {};
let timerInterval;
let examId;
let examDuration;
let examEndTime;

// --- Functions ---
async function fetchExamQuestions(examId) {
    try {
        const response = await fetch(`/exams/${examId}/questions`); // Fetch questions from backend
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        questions = await response.json();
        if (!Array.isArray(questions) || questions.length === 0) {
            throw new Error('No questions found for this exam.');
        }
        examDuration = 10 * 60; // 10 minutes in seconds
        examEndTime = new Date(Date.now() + examDuration * 1000);
        displayQuestion();
        startTimer();
        quizContainer.style.display = 'block';
        examSetupContainer.style.display = 'none';
    } catch (error) {
        console.error('Error fetching questions:', error);
        alert('Failed to fetch exam questions. Please check the Exam ID and try again.');
    }
}

function displayQuestion() {
    const currentQuestion = questions[currentQuestionIndex];
    questionText.textContent = currentQuestion.text;
    questionNumber.textContent = `${currentQuestionIndex + 1} / ${questions.length}`;
    optionsContainer.innerHTML = '';
    for (let i = 1; i <= 4; i++) {
        const optionButton = document.createElement('button');
        optionButton.classList.add('option');
        optionButton.dataset.option = i;
        optionButton.textContent = currentQuestion[`option${i}`];
        optionButton.addEventListener('click', () => selectAnswer(i));
        optionsContainer.appendChild(optionButton);
    }
    prevBtn.disabled = currentQuestionIndex === 0;
    nextBtn.disabled = currentQuestionIndex === questions.length - 1;
}
