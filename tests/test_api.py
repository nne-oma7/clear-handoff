import pytest

from issue_classifier import identify_issue, get_questions

CONTACT = {"contact_email": "ada@example.com"}


def submit(client, message="My withdrawal failed", **extra):
    """Submit a complaint with valid contact details unless overridden."""
    body = {"message": message, **CONTACT, **extra}
    return client.post("/complaints", json=body)


# ---------- classifier ----------

@pytest.mark.parametrize("message,expected", [
    ("My withdrawal keeps failing", "withdrawal_issue"),
    ("I sent money but the recipient has not got it", "transfer_issue"),
    ("I tried to top up my wallet", "deposit_issue"),
    ("I can't log in to my account", "account_access_issue"),
    ("There is an unauthorized transaction on my account", "security_issue"),
    ("Something strange happened", "other"),
])
def test_identify_issue(message, expected):
    assert identify_issue(message) == expected


def test_security_wins_over_other_keywords():
    assert identify_issue("fraud on my withdrawal") == "security_issue"


def test_unknown_category_falls_back_to_other_questions():
    assert get_questions("nonsense") == get_questions("other")


# ---------- /analyze ----------

def test_analyze_returns_category_and_questions(client):
    r = client.post("/analyze", json={"message": "My withdrawal failed"})
    assert r.status_code == 200
    body = r.json()
    assert body["category"] == "withdrawal_issue"
    assert len(body["follow_up_questions"]) > 0


def test_analyze_rejects_empty_message(client):
    assert client.post("/analyze", json={"message": ""}).status_code == 422


# ---------- submitting complaints ----------

def test_submit_with_no_answers_is_awaiting_information(client):
    r = submit(client)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "awaiting_information"
    assert len(body["missing_information"]) == len(get_questions("withdrawal_issue"))


def test_submit_with_all_answers_is_ready_for_review(client):
    answers = {q["key"]: "x" for q in get_questions("withdrawal_issue")}
    r = submit(client, answers=answers)
    assert r.status_code == 201
    assert r.json()["status"] == "ready_for_review"
    assert r.json()["missing_information"] == []


def test_unknown_answer_keys_and_blank_answers_are_dropped(client):
    r = submit(client, answers={"amount": "  5000  ", "bogus": "x", "time": "   "})
    assert r.json()["customer_provided_details"] == {"amount": "5000"}


def test_missing_information_includes_reason(client):
    r = submit(client)
    for item in r.json()["missing_information"]:
        assert item["question"]
        assert item["reason"]
        assert item["reason"] != "This information was not provided."


def test_submit_rejects_empty_message(client):
    assert submit(client, message="").status_code == 422


def test_original_message_is_preserved_exactly(client):
    text = "i made a transaction but i dnt know whether the money is in"
    r = submit(client, message=text)
    assert r.json()["original_complaint"] == text


# ---------- contact details ----------

def test_submit_requires_email_or_phone(client):
    r = client.post("/complaints", json={"message": "My withdrawal failed"})
    assert r.status_code == 422


def test_submit_rejects_invalid_email(client):
    r = client.post("/complaints", json={
        "message": "hello", "contact_email": "not-an-email"
    })
    assert r.status_code == 422


def test_submit_rejects_invalid_phone(client):
    r = client.post("/complaints", json={
        "message": "hello", "contact_phone": "123"
    })
    assert r.status_code == 422


def test_phone_only_is_accepted(client):
    r = client.post("/complaints", json={
        "message": "hello", "contact_phone": "0801 234 5678"
    })
    assert r.status_code == 201


def test_contact_details_are_saved_and_cleaned(client):
    r = client.post("/complaints", json={
        "message": "hello",
        "contact_name": "  Ada Okafor  ",
        "contact_email": "  ADA@Example.COM ",
    })
    contact = r.json()["customer_contact"]
    assert contact["name"] == "Ada Okafor"
    assert contact["email"] == "ada@example.com"


# ---------- staff: list, view, status ----------

def test_list_is_newest_first(client):
    a = submit(client, message="first").json()["id"]
    b = submit(client, message="second").json()["id"]
    ids = [c["id"] for c in client.get("/complaints").json()]
    assert ids == [b, a]


def test_get_single_complaint_and_404(client):
    cid = submit(client, message="hello").json()["id"]
    assert client.get(f"/complaints/{cid}").status_code == 200
    assert client.get("/complaints/99999").status_code == 404


def test_update_status(client):
    cid = submit(client, message="hello").json()["id"]
    r = client.patch(f"/complaints/{cid}/status", json={"status": "under_investigation"})
    assert r.status_code == 200
    assert client.get(f"/complaints/{cid}").json()["status"] == "under_investigation"


def test_invalid_status_rejected(client):
    cid = submit(client, message="hello").json()["id"]
    r = client.patch(f"/complaints/{cid}/status", json={"status": "nope"})
    assert r.status_code == 400


def test_status_update_on_missing_ticket_404(client):
    r = client.patch("/complaints/99999/status", json={"status": "resolved"})
    assert r.status_code == 404


# ---------- customer tracking ----------

def test_track_with_matching_email(anonymous_client):
    cid = submit(anonymous_client).json()["id"]
    r = anonymous_client.post("/track/lookup", json={
        "reference": f"CH-{cid:06d}", "contact": "ADA@example.com"
    })
    assert r.status_code == 200
    body = r.json()
    assert body["reference"] == f"CH-{cid:06d}"
    assert body["status_label"]


def test_track_accepts_reference_without_prefix(anonymous_client):
    cid = submit(anonymous_client).json()["id"]
    r = anonymous_client.post("/track/lookup", json={
        "reference": str(cid), "contact": "ada@example.com"
    })
    assert r.status_code == 200


def test_track_matches_phone_in_different_formats(anonymous_client):
    r = anonymous_client.post("/complaints", json={
        "message": "hello", "contact_phone": "08012345678"
    })
    cid = r.json()["id"]
    r = anonymous_client.post("/track/lookup", json={
        "reference": f"CH-{cid:06d}", "contact": "+234 801 234 5678"
    })
    assert r.status_code == 200


def test_track_wrong_contact_and_unknown_reference_look_identical(anonymous_client):
    cid = submit(anonymous_client).json()["id"]
    wrong_contact = anonymous_client.post("/track/lookup", json={
        "reference": f"CH-{cid:06d}", "contact": "someone@else.com"
    })
    unknown_ref = anonymous_client.post("/track/lookup", json={
        "reference": "CH-999999", "contact": "ada@example.com"
    })
    assert wrong_contact.status_code == 404
    assert unknown_ref.status_code == 404
    assert wrong_contact.json() == unknown_ref.json()


def test_track_does_not_reveal_internal_details(anonymous_client):
    cid = submit(anonymous_client, message="secret complaint text").json()["id"]
    r = anonymous_client.post("/track/lookup", json={
        "reference": f"CH-{cid:06d}", "contact": "ada@example.com"
    })
    text = r.text
    assert "secret complaint text" not in text
    assert "ada@example.com" not in text
    assert "missing_information" not in text


# ---------- pages ----------

def test_pages_load(client):
    assert client.get("/").status_code == 200
    assert client.get("/track").status_code == 200
    assert client.get("/dashboard").status_code == 200


# ---------- staff login ----------

def test_dashboard_requires_login(anonymous_client):
    r = anonymous_client.get("/dashboard")
    assert r.status_code == 401
    assert "Basic" in r.headers["www-authenticate"]


def test_staff_endpoints_require_login(anonymous_client):
    assert anonymous_client.get("/complaints").status_code == 401
    assert anonymous_client.get("/complaints/1").status_code == 401
    r = anonymous_client.patch("/complaints/1/status", json={"status": "resolved"})
    assert r.status_code == 401


def test_wrong_password_is_rejected(anonymous_client):
    r = anonymous_client.get("/complaints", auth=("staff", "wrong"))
    assert r.status_code == 401


def test_correct_login_is_accepted(anonymous_client):
    r = anonymous_client.get("/complaints", auth=("staff", "test-password"))
    assert r.status_code == 200


def test_customers_can_use_public_pages_without_login(anonymous_client):
    assert anonymous_client.get("/").status_code == 200
    assert anonymous_client.get("/track").status_code == 200
    assert anonymous_client.post("/analyze", json={"message": "withdrawal"}).status_code == 200
    assert submit(anonymous_client, message="withdrawal").status_code == 201


def test_unconfigured_login_blocks_everyone(anonymous_client, monkeypatch):
    monkeypatch.delenv("STAFF_PASSWORD")
    r = anonymous_client.get("/complaints", auth=("staff", "test-password"))
    assert r.status_code == 503

def test_demo_switch_opens_dashboard_without_login(anonymous_client, monkeypatch):
    monkeypatch.setenv("DEMO_OPEN_DASHBOARD", "1")
    assert anonymous_client.get("/dashboard").status_code == 200
    assert anonymous_client.get("/complaints").status_code == 200