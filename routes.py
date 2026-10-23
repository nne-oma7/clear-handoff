import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import require_staff
from database import get_db
from models import ComplaintRecord
from contact import contact_matches, parse_reference
from schemas import (
    ComplaintInput,
    ComplaintSubmission,
    StatusUpdate,
    TrackRequest
)
from issue_classifier import identify_issue, get_questions
from report_service import (
    build_customer_status,
    build_engineering_report,
    calculate_missing
)

router = APIRouter()

ALLOWED_STATUSES = {
    "received",
    "awaiting_information",
    "under_investigation",
    "ready_for_review",
    "escalated_to_engineering",
    "resolved"
}


@router.post("/analyze")
def analyze_complaint(data: ComplaintInput):
    category = identify_issue(data.message)
    questions = get_questions(category)

    return {
        "original_complaint": data.message,
        "category": category,
        "follow_up_questions": questions,
        "submission_note": (
            "You may leave unknown details unanswered. "
            "The complaint can still be submitted, and "
            "missing information will be flagged."
        ),
        "security_note": (
            "Never provide passwords, PINs or OTPs."
        )
    }


@router.post("/complaints", status_code=201)
def submit_complaint(
    data: ComplaintSubmission,
    db: Session = Depends(get_db)
):
    category = identify_issue(data.message)
    questions = get_questions(category)

    allowed_keys = {
        question["key"] for question in questions
    }

    answers = {
        key: str(value).strip()
        for key, value in data.answers.items()
        if key in allowed_keys and str(value).strip()
    }

    missing = calculate_missing(category, answers)

    if missing:
        status = "awaiting_information"
    else:
        status = "ready_for_review"

    record = ComplaintRecord(
        original_message=data.message,
        category=category,
        answers=json.dumps(answers),
        missing_information=json.dumps(missing),
        status=status,
        contact_name=data.contact_name,
        contact_email=data.contact_email,
        contact_phone=data.contact_phone,
        created_at=datetime.now(timezone.utc).isoformat()
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return build_engineering_report(record)


@router.post("/track/lookup")
def track_complaint(
    data: TrackRequest,
    db: Session = Depends(get_db)
):
    record = None
    complaint_id = parse_reference(data.reference)

    if complaint_id is not None:
        record = db.query(ComplaintRecord).filter(
            ComplaintRecord.id == complaint_id
        ).first()

    if record is None or not contact_matches(record, data.contact):
        raise HTTPException(
            status_code=404,
            detail="We couldn't find a complaint matching those details."
        )

    return build_customer_status(record)


@router.get("/complaints", dependencies=[Depends(require_staff)])
def list_complaints(
    db: Session = Depends(get_db)
):
    records = (
        db.query(ComplaintRecord)
        .order_by(ComplaintRecord.id.desc())
        .all()
    )

    return [
        build_engineering_report(record)
        for record in records
    ]


@router.get("/complaints/{complaint_id}", dependencies=[Depends(require_staff)])
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    record = db.query(ComplaintRecord).filter(
        ComplaintRecord.id == complaint_id
    ).first()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found."
        )

    return build_engineering_report(record)


@router.patch("/complaints/{complaint_id}/status", dependencies=[Depends(require_staff)])
def update_complaint_status(
    complaint_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db)
):
    if data.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid complaint status.",
                "allowed_statuses": sorted(ALLOWED_STATUSES)
            }
        )

    record = db.query(ComplaintRecord).filter(
        ComplaintRecord.id == complaint_id
    ).first()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found."
        )

    record.status = data.status

    db.commit()
    db.refresh(record)

    return build_engineering_report(record)