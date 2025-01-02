document.addEventListener('DOMContentLoaded', () => {
    const questionsContainer = document.getElementById('id_questions');
    const button = document.getElementById('id_button');
    const results = document.getElementById('id_results');

    fetch('questions.json')
        .then(response => response.json())
        .then(data => {
            renderQuestions(data.questions);
        })
        .catch(() => {
            questionsContainer.innerHTML = '<p class="text-danger">question error</p>';
        });

    function renderQuestions(questions) {
        let content = "";
        for (let i = 0; i < questions.length; i++) {
            content += `
                <div class="mb-3">
                    <p><strong>${i + 1}. ${questions[i].question}</strong></p>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="question${i}" id="q${i}a1" value="${questions[i].a1}">
                        <label class="form-check-label" for="q${i}a1">${questions[i].a1}</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="question${i}" id="q${i}a2" value="${questions[i].a2}">
                        <label class="form-check-label" for="q${i}a2">${questions[i].a2}</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="question${i}" id="q${i}a3" value="${questions[i].a3}">
                        <label class="form-check-label" for="q${i}a3">${questions[i].a3}</label>
                    </div>
                </div>
            `;
        }
        questionsContainer.innerHTML = content;
    }

    button.addEventListener('click', () => {
        let allAnswered = true;
        let checkedAnswers = {};

        const questionElements = document.querySelectorAll('[name^="question"]');
        const uniqueQuestions = [...new Set(Array.from(questionElements).map(el => el.name))];

        for (let question of uniqueQuestions) {
            const selectedOption = document.querySelector(`input[name="${question}"]:checked`);
            if (!selectedOption) {
                allAnswered = false;
                break;
            }
            checkedAnswers[question] = selectedOption.value;
        }

        if (!allAnswered) {
            results.innerHTML = '<p class="text-danger">Vastaa kaikkiin kysymyksiin ennen tarkistusta!</p>';
            return;
        }

        fetch('questions.json')
            .then(response => response.json())
            .then(data => {
                let correct = 0;
                let quizQuestions = data.questions;

                for (let i = 0; i < quizQuestions.length; i++) {
                    let correctAnswer = quizQuestions[i].answer;
                    let userAnswer = checkedAnswers[`question${i}`];
                    if (userAnswer === correctAnswer) correct++;
                }

                let wrong = quizQuestions.length - correct;
                let output = `
                    <p class="text-success">Oikeita vastauksia: ${correct}</p>
                    <p class="text-danger">Vääriä vastauksia: ${wrong}</p>
                `;
                results.innerHTML = output;
            })
            .catch(() => {
                results.innerHTML = '<p class="text-danger">check error</p>';
            });
    });
});
