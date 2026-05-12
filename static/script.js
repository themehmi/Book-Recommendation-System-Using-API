document.addEventListener('DOMContentLoaded', () => {
    // --- State ---
    const MAX_QUESTIONS = 10;
    let history = [];
    let currentQuestion = "";

    // --- DOM Elements ---
    const elements = {
        startSection: document.getElementById('start-section'),
        quizSection: document.getElementById('quiz-section'),
        loadingSection: document.getElementById('loading-section'),
        resultsSection: document.getElementById('results-section'),
        errorSection: document.getElementById('error-section'),
        startBtn: document.getElementById('start-btn'),
        quizForm: document.getElementById('quiz-form'),
        answerInput: document.getElementById('answer-input'),
        questionText: document.getElementById('question-text'),
        loadingTextDisplay: document.getElementById('loading-text-display'),
        booksGrid: document.getElementById('books-grid'),
        errorText: document.getElementById('error-text'),
        retryBtn: document.getElementById('retry-btn'),
        restartBtn: document.getElementById('restart-btn'),
        progressContainer: document.getElementById('progress-container'),
        progressBar: document.getElementById('progress-bar'),
        progressText: document.getElementById('progress-text')
    };

    // --- Initialization ---
    elements.startBtn.addEventListener('click', startQuiz);
    elements.quizForm.addEventListener('submit', handleAnswer);
    
    elements.retryBtn.addEventListener('click', () => {
        elements.errorSection.classList.add('hidden');
        if (history.length >= MAX_QUESTIONS) {
            fetchRecommendations();
        } else {
            fetchNextQuestion();
        }
    });

    elements.restartBtn.addEventListener('click', () => {
        history = [];
        elements.resultsSection.classList.add('hidden');
        elements.startSection.classList.remove('hidden');
        elements.progressContainer.classList.add('hidden');
        // Reset progress bar
        updateProgress();
    });

    // --- Core Logic ---

    async function startQuiz() {
        elements.startSection.classList.add('hidden');
        elements.progressContainer.classList.remove('hidden');
        history = [];
        updateProgress();
        await fetchNextQuestion();
    }

    async function fetchNextQuestion() {
        // Show loading state if we are transitioning between questions
        if (history.length > 0) {
            showLoading("Refining the search...");
            elements.quizSection.classList.add('hidden');
        }

        try {
            const response = await fetch('/api/next_question', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ history })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Unable to connect to the archive.');

            // Check if backend signaled completion early
            if (data.done || history.length >= MAX_QUESTIONS) {
                await fetchRecommendations();
                return;
            }

            currentQuestion = data.question;
            elements.questionText.textContent = currentQuestion;
            elements.answerInput.value = '';
            
            hideLoading();
            elements.quizSection.classList.remove('hidden');
            elements.answerInput.focus();

        } catch (error) {
            console.error(error);
            showError(error.message);
        }
    }

    async function handleAnswer(e) {
        e.preventDefault();
        const answer = elements.answerInput.value.trim();
        if (!answer) return;

        history.push({ question: currentQuestion, answer });
        updateProgress();

        if (history.length >= MAX_QUESTIONS) {
            await fetchRecommendations();
        } else {
            elements.quizSection.classList.add('hidden');
            showLoading("Considering your thoughts...");
            await fetchNextQuestion();
        }
    }

    async function fetchRecommendations() {
        showLoading("Curating your final selections...");
        elements.quizSection.classList.add('hidden');
        elements.progressContainer.classList.add('hidden');

        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ history })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Curation failed.');

            renderBooks(data.recommendations);
            hideLoading();
            elements.resultsSection.classList.remove('hidden');

        } catch (error) {
            console.error(error);
            showError(error.message);
        }
    }

    // --- UI Helpers ---

    function updateProgress() {
        const count = history.length;
        const currentNum = Math.min(count + 1, MAX_QUESTIONS);
        const percentage = (count / MAX_QUESTIONS) * 100;
        
        if (elements.progressBar) {
            elements.progressBar.style.width = `${percentage}%`;
        }
        if (elements.progressText) {
            elements.progressText.textContent = `Inquiry ${currentNum} of ${MAX_QUESTIONS}`;
        }
    }

    function showLoading(msg) {
        elements.loadingTextDisplay.textContent = msg;
        elements.loadingSection.classList.remove('hidden');
        elements.errorSection.classList.add('hidden');
        elements.quizSection.classList.add('hidden');
        elements.startSection.classList.add('hidden');
    }

    function hideLoading() {
        elements.loadingSection.classList.add('hidden');
    }

    function showError(msg) {
        hideLoading();
        elements.errorText.textContent = msg;
        elements.errorSection.classList.remove('hidden');
        elements.quizSection.classList.add('hidden');
        elements.progressContainer.classList.add('hidden');
    }

    function renderBooks(books) {
        elements.booksGrid.innerHTML = '';
        if (!books || books.length === 0) {
            elements.booksGrid.innerHTML = '<p class="body-text">No recommendations found in the current selection.</p>';
            return;
        }

        books.forEach((book, index) => {
            const card = document.createElement('div');
            card.className = 'book-card';
            
            // Staggered animation effect
            card.style.animation = `fadeUp 0.6s ease forwards`;
            card.style.animationDelay = `${index * 0.15}s`;
            card.style.opacity = '0';

            card.innerHTML = `
                <div class="book-meta">${escapeHtml(book.genre || 'Literature')}</div>
                <h3 class="book-title">${escapeHtml(book.title || 'Untitled Work')}</h3>
                <div class="book-author">By ${escapeHtml(book.author || 'Unknown Author')}</div>
                <div class="book-summary">${escapeHtml(book.summary || '')}</div>
                <div class="book-reason">${escapeHtml(book.reason || 'Selected based on your reading profile.')}</div>
            `;
            
            elements.booksGrid.appendChild(card);
        });
    }

    function escapeHtml(unsafe) {
        return (unsafe || '').toString()
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
});
