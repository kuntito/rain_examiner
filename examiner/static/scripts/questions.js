/** @format */

const idNextQuestionButton = "next-question-btn";
const idPreviousQuestionButton = "prev-question-btn";
const idExamSubmitButton = "submit-question-btn";

let currentIndex = localStorage.getItem(_CURRENT_QUESTION_INDEX);
if (currentIndex === null) {
	currentIndex = 0;
} else {
	currentIndex = Number(currentIndex);
}

const questionCount = _questions.length;
if (questionCount) {
	loadQuestion(currentIndex, questionCount);
}


function loadQuestion(index, maxCount) {
	const question = _questions[index];
    console.log(question);
	loadQuestionCountAndText(index, question);
	loadQuestionOptions(question);
	loadQuestionNavButtons(index, maxCount);
}


function loadQuestionCountAndText(question_index, question) {
	document.getElementById(
		"question-header-container"
	).innerHTML = `<h3>Question ${question_index + 1}/${questionCount}</h3>
<h2>${question.question_text}</h2>`;
}


function onOptionSelected(option, question) {
    // when a question option is clicked, it should be sent to the server for storage
    document.getElementById(`${option.id}`).onclick = function() {
        console.log(`Question ${question.id}, Option ${option.id} selected`);
        const xhr = new XMLHttpRequest();
        xhr.open(
            "POST",
            // [onOptionSelectedUrl] is initialized in [questions.html]
            _onOptionSelectedUrl,
            true
        );

        xhr.onload = function () {
            if (this.status === 200) {
                console.log(this.responseText);
            }
        };

        xhr.setRequestHeader(
            'Content-type',
            'application/json; charset=utf-8',
        )

        const data = {
            "question_id": question.id,
            "option_id" : option.id,
            "option_text": option.text,
            // [_examId] is initialized in [questions.html]
            "exam_id": _examId
        };

        console.log(_onOptionSelectedUrl);
        console.log('data to send', data);

        xhr.send(
            JSON.stringify(data)
        );
    }
}


function loadQuestionOptions(question) {
    const radioGroupName = `question-options`
	document.getElementById("question-options-container").innerHTML = question.options
		.map(
			(option) =>
`<div class="h3 mb-5">
    <input type="radio" name="${radioGroupName}" id="${option.id}">
    <label for="${option.id}">${option.text}</label>
</div>
`
		)
		.join("");

    // The server is notified when an option is selected and stores the value in the [selected_option_id] property
    // So the app always shows the users selected option even after navigation from that page
    if (question.selected_option_id) {
        document.getElementById(question.selected_option_id).checked = true;
    }

    question.options.forEach(option => onOptionSelected(option, question));
}



function renderQuestionNavButton(button_id, button_text) {
	return `<button id="${button_id}" class="btn">${button_text}</button>`;
}


function addQuestionNavButtons(index, maxCount) {
	let buttonsToAdd = "";
	if (index > 0) {
		buttonsToAdd += `${renderQuestionNavButton(idPreviousQuestionButton, "Previous")}`;
	}

	if (index === maxCount - 1) {
		// [submitExamUrl] is initialized in [questions.html]
		buttonsToAdd += renderQuestionNavButton(idExamSubmitButton, "Submit");
	} else {
		buttonsToAdd += renderQuestionNavButton(idNextQuestionButton, "Next");
	}

	document.getElementById("question-nav-buttons").innerHTML = buttonsToAdd;
}


function submitExam() {
    if (confirm('Submit exam?')) {
		endExam();
	}
}


function loadNextQuestion() {
	changeCurrentIndex(currentIndex + 1);
}


function loadPrevQuestion() {
	changeCurrentIndex(currentIndex - 1);
}


function changeCurrentIndex(val) {
	currentIndex = (val >= 0 && val <= questionCount - 1)? val : currentIndex;
	console.log(currentIndex);
	localStorage.setItem(_CURRENT_QUESTION_INDEX, currentIndex);
	window.location.reload();
}


function addOnClickListenersQuestionNavButtons() {
    const nextButton = document.getElementById(idNextQuestionButton);
    const previousButton = document.getElementById(idPreviousQuestionButton);
    const submitButton = document.getElementById(idExamSubmitButton);
    if (nextButton) {
        nextButton.addEventListener("click", loadNextQuestion);
    }
    
    if (previousButton) {
        previousButton.addEventListener("click", loadPrevQuestion);
    }

    if (submitButton) {
        submitButton.addEventListener("click", submitExam)
    }
}


function loadQuestionNavButtons(index, maxCount) {
    addQuestionNavButtons(index, maxCount);
    addOnClickListenersQuestionNavButtons();
}
