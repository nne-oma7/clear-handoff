
const complaintForm = document.getElementById("complaint-form");
const messageInput = document.getElementById("complaint-message");
const characterCount = document.getElementById("character-count");

const questionArea = document.getElementById("question-area");
const questionTitle = document.getElementById("question-title");
const questionIntro = document.getElementById("question-intro");
const dynamicQuestions = document.getElementById("dynamic-questions");

const errorMessage = document.getElementById("error-message");
const successMessage = document.getElementById("success-message");
const formActions = document.getElementById("form-actions");
const formBottomNote = document.getElementById("form-bottom-note");

const continueButton = document.getElementById("continue-button");
const buttonLabel = document.getElementById("button-label");
const stepCounter = document.getElementById("step-counter");

const stepOne = document.getElementById("step-one");
const stepTwo = document.getElementById("step-two");
const stepThree = document.getElementById("step-three");

let currentStep = 1;
let detectedCategory = null;
let detectedQuestions = [];
let isSubmitting = false;


messageInput.addEventListener("input", () => {
    characterCount.textContent =
        `${messageInput.value.length.toLocaleString()} / 20,000`;
});


function showError(message) {
    errorMessage.textContent = message;
    errorMessage.hidden = false;
}


function clearError() {
    errorMessage.textContent = "";
    errorMessage.hidden = true;
}


function setStep(step) {
    currentStep = step;

    stepOne.classList.toggle("active", step === 1);
    stepTwo.classList.toggle("active", step === 2);
    stepThree.classList.toggle("active", step === 3);

    stepOne.classList.toggle("completed", step > 1);
    stepTwo.classList.toggle("completed", step > 2);

    stepCounter.textContent = `${step} of 3`;

    const kicker = document.getElementById("form-kicker");
    const title = document.getElementById("form-title");
    const intro = document.getElementById("form-intro");

    if (step === 1) {
        kicker.textContent = "STEP 01 / YOUR STORY";
        title.textContent = "What happened?";
        intro.textContent =
            "Explain the issue as you experienced it. Include anything you think might help, even if you're not sure what's important.";

        buttonLabel.textContent = "Continue";
    } else if (step === 2) {
        kicker.textContent = "STEP 02 / THE DETAILS";
        title.textContent = "Help us understand";
        intro.textContent =
            "We've identified the likely issue type. Answer what you can so the support team has useful details to investigate.";

        buttonLabel.textContent = "Submit complaint";
    }
}


function renderQuestions(questions) {
    dynamicQuestions.replaceChildren();

    for (const question of questions) {
        const field = document.createElement("div");
        field.className = "question-field";

        const label = document.createElement("label");
        label.htmlFor = `answer-${question.key}`;
        label.textContent = question.question;

        const input = document.createElement("input");
        input.className = "question-input";
        input.id = `answer-${question.key}`;
        input.name = question.key;
        input.type = "text";
        input.autocomplete = "off";
        input.maxLength = 2000;
        input.placeholder = "Your answer (optional)";

        const reason = document.createElement("p");
        reason.className = "question-reason";
        reason.textContent = question.reason;

        field.append(label, input, reason);
        dynamicQuestions.appendChild(field);
    }
}


async function analyzeComplaint() {
    clearError();

    const message = messageInput.value.trim();

    if (!message) {
        showError("Please describe what happened before continuing.");
        messageInput.focus();
        return;
    }

    continueButton.disabled = true;
    buttonLabel.textContent = "Analysing...";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        if (!response.ok) {
            throw new Error("We couldn't analyse your complaint. Please try again.");
        }

        const result = await response.json();

        detectedCategory = result.category;
        detectedQuestions = result.follow_up_questions;

        renderQuestions(detectedQuestions);

        questionTitle.textContent =
            `Details for your ${detectedCategory.replaceAll("_", " ")}`;

        questionIntro.textContent =
            "These questions help us prepare your complaint for investigation. You can leave unknown details blank.";

        questionArea.hidden = false;
        messageInput.readOnly = true;

        setStep(2);
        window.scrollTo({ top: 0, behavior: "smooth" });

    } catch (error) {
        showError(
            error.message ||
            "Something went wrong. Please check your connection and try again."
        );
    } finally {
        continueButton.disabled = false;
        buttonLabel.textContent = currentStep === 1
            ? "Continue"
            : "Submit complaint";
    }
}


function readErrorMessage(result) {
    // FastAPI sends validation errors as a list of {msg: ...} objects.
    if (Array.isArray(result.detail)) {
        return result.detail
            .map(item => String(item.msg).replace("Value error, ", ""))
            .join(" ");
    }

    return result.detail?.message || result.detail || null;
}


async function submitComplaint() {
    clearError();

    if (isSubmitting) {
        return;
    }
    

        const contactName = document.getElementById("contact-name").value.trim();
    const contactEmail = document.getElementById("contact-email").value.trim();
    const contactPhone = document.getElementById("contact-phone").value.trim();

    if (!contactEmail && !contactPhone) {
        showError("Please give us an email address or a phone number so we can update you.");
        document.getElementById("contact-email").focus();
        return;
    }


    const message = messageInput.value.trim();
    const answers = {};

    for (const question of detectedQuestions) {
        const input = document.getElementById(
            `answer-${question.key}`
        );

        if (input && input.value.trim()) {
            answers[question.key] = input.value.trim();
        }
    }

    isSubmitting = true;
    continueButton.disabled = true;
    buttonLabel.textContent = "Submitting...";

    try {
        const response = await fetch("/complaints", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
             body: JSON.stringify({
                message: message,
                answers: answers,
                contact_name: contactName,
                contact_email: contactEmail,
                contact_phone: contactPhone
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                readErrorMessage(result) ||
                "We couldn't submit your complaint. Please try again."
            );
        }

        document.getElementById("reference-number").textContent =
            `CH-${String(result.id).padStart(6, "0")}`;

        const statusText = {
            awaiting_information:
                "Your complaint is saved. Some details are still missing, but you can submit without them.",
            ready_for_review:
                "Your complaint is saved and ready for support review."
        };

        document.getElementById("submission-status").textContent =
            statusText[result.status] ||
            "Your complaint has been saved.";

        complaintForm.reset();
        characterCount.textContent = "0 / 20,000";

        document.getElementById("form-view").querySelector(".form-heading").hidden = true;
        document.getElementById("form-intro").hidden = true;
        document.getElementById("message-section").hidden = true;
        formActions.hidden = true;
        formBottomNote.hidden = true;
        successMessage.hidden = false;

        setStep(3);
        window.scrollTo({ top: 0, behavior: "smooth" });

    } catch (error) {
        showError(
            error.message ||
            "Something went wrong while submitting. Please try again."
        );
    } finally {
        isSubmitting = false;
        continueButton.disabled = false;

        if (currentStep === 1) {
            buttonLabel.textContent = "Continue";
        } else if (currentStep === 2) {
            buttonLabel.textContent = "Submit complaint";
        }
    }
}


complaintForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (currentStep === 1) {
        await analyzeComplaint();
    } else if (currentStep === 2) {
        await submitComplaint();
    }
});


document.getElementById("new-complaint").addEventListener("click", () => {
    currentStep = 1;
    detectedCategory = null;
    detectedQuestions = [];

    complaintForm.reset();
    dynamicQuestions.replaceChildren();

    messageInput.readOnly = false;
    questionArea.hidden = true;
    successMessage.hidden = true;

    document.getElementById("form-view").querySelector(".form-heading").hidden = false;
    document.getElementById("form-intro").hidden = false;
    document.getElementById("message-section").hidden = false;
    formActions.hidden = false;
    formBottomNote.hidden = false;

    clearError();
    setStep(1);

    characterCount.textContent = "0 / 20,000";
    messageInput.focus();
});