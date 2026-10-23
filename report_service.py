import json

from issue_classifier import get_questions


def calculate_missing(category: str, answers: dict) -> list[str]:
    questions = get_questions(category)
    missing = []

    for question in questions:
        key = question["key"]
        answer = answers.get(key, "")

        if not str(answer).strip():
            missing.append(key)

    return missing


def build_engineering_report(record) -> dict:
    answers = json.loads(record.answers or "{}")
    missing_keys = json.loads(
        record.missing_information or "[]"
    )

    questions = get_questions(record.category)

    question_lookup = {
        question["key"]: question
        for question in questions
    }

    missing_details = []

    for key in missing_keys:
        question = question_lookup.get(key, {})

        missing_details.append({
            "key": key,
            "question": question.get(
                "question",
                "Additional information required."
            ),
            "reason": question.get(
                "reason",
                "This information was not provided."
            )
        })

    return {
        "id": record.id,
        "original_complaint": record.original_message,
        "category": record.category,
        "customer_provided_details": answers,
        "missing_information": missing_details,
        "questions_for_this_issue": questions,
        "investigation_note": (
            "Customer-reported information has not been "
            "independently verified. Review available records "
            "before drawing conclusions."
        ),
        "customer_contact": {
            "name": record.contact_name,
            "email": record.contact_email,
            "phone": record.contact_phone
        },
        "status": record.status,
        "created_at": record.created_at
    }


CUSTOMER_STATUS_TEXT = {
    "received": (
        "Received",
        "We have received your complaint and it is in our queue."
    ),
    "awaiting_information": (
        "Awaiting information",
        "Your complaint is saved. Some details are still missing, "
        "so our team may contact you."
    ),
    "under_investigation": (
        "Under investigation",
        "Our team is looking into your complaint now."
    ),
    "ready_for_review": (
        "Ready for review",
        "Your complaint has the details we need and is waiting "
        "for our team to review it."
    ),
    "escalated_to_engineering": (
        "Passed to our technical team",
        "Your complaint has been passed to our technical team."
    ),
    "resolved": (
        "Resolved",
        "Your complaint has been marked as resolved."
    )
}


def build_customer_status(record) -> dict:
    label, message = CUSTOMER_STATUS_TEXT.get(
        record.status,
        ("In progress", "Your complaint is being handled.")
    )

    return {
        "reference": f"CH-{record.id:06d}",
        "status": record.status,
        "status_label": label,
        "message": message,
        "submitted_at": record.created_at
    }