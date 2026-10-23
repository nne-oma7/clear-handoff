
ISSUE_QUESTIONS = {
    "withdrawal_issue": [
        {
            "key": "transaction_reference",
            "question": "What is the withdrawal transaction reference, if available?",
            "reason": "Helps support locate the transaction."
        },
        {
            "key": "amount",
            "question": "How much were you trying to withdraw?",
            "reason": "Identifies the amount involved."
        },
        {
            "key": "time",
            "question": "When did you attempt the withdrawal?",
            "reason": "Helps narrow down the transaction record."
        },
        {
            "key": "debited",
            "question": "Was your account debited?",
            "reason": "Helps establish whether funds left the account."
        },
        {
            "key": "error_message",
            "question": "What error message or transaction status did you see?",
            "reason": "Helps identify the failure point."
        }
    ],

    "transfer_issue": [
        {
            "key": "transaction_reference",
            "question": "What is the transfer reference, if available?",
            "reason": "Helps locate the transfer."
        },
        {
            "key": "amount",
            "question": "How much were you trying to transfer?",
            "reason": "Identifies the amount involved."
        },
        {
            "key": "time",
            "question": "When did you make the transfer?",
            "reason": "Helps locate the relevant transaction."
        },
        {
            "key": "transfer_status",
            "question": "What status did the transfer show?",
            "reason": "Helps distinguish pending, failed and successful transfers."
        },
        {
            "key": "recipient_outcome",
            "question": "Did the recipient receive the money?",
            "reason": "Helps establish the reported outcome."
        }
    ],

    "deposit_issue": [
        {
            "key": "amount",
            "question": "How much were you trying to deposit?",
            "reason": "Identifies the amount involved."
        },
        {
            "key": "time",
            "question": "When did you make the deposit?",
            "reason": "Helps locate the payment."
        },
        {
            "key": "payment_method",
            "question": "Which payment method did you use?",
            "reason": "Helps identify the payment route."
        },
        {
            "key": "transaction_reference",
            "question": "Do you have a payment reference or receipt number?",
            "reason": "Helps support trace the payment."
        },
        {
            "key": "payment_debited",
            "question": "Did the money leave your bank account or payment source?",
            "reason": "Helps establish the reported payment outcome."
        }
    ],

    "account_access_issue": [
        {
            "key": "time",
            "question": "When did the access problem begin?",
            "reason": "Helps establish when the problem started."
        },
        {
            "key": "error_message",
            "question": "What error message did you see?",
            "reason": "Helps identify the reported failure."
        },
        {
            "key": "steps_tried",
            "question": "What have you already tried to fix the problem?",
            "reason": "Prevents support from unnecessarily repeating troubleshooting."
        },
        {
            "key": "device",
            "question": "Which device and app or browser were you using?",
            "reason": "Helps investigate possible device-specific issues."
        }
    ],

    "security_issue": [
        {
            "key": "time",
            "question": "When did you notice the suspicious activity?",
            "reason": "Helps establish the reported timeline."
        },
        {
            "key": "activity",
            "question": "What activity did you notice that you do not recognise?",
            "reason": "Helps identify the customer's security concern."
        },
        {
            "key": "transaction_reference",
            "question": "Is there a transaction reference associated with the activity?",
            "reason": "May help support locate the reported activity."
        }
    ],

    "other": [
        {
            "key": "time",
            "question": "When did the problem occur?",
            "reason": "Helps establish the timeline."
        },
        {
            "key": "expected_result",
            "question": "What did you expect to happen?",
            "reason": "Clarifies the expected behaviour."
        },
        {
            "key": "actual_result",
            "question": "What actually happened?",
            "reason": "Clarifies the reported problem."
        },
        {
            "key": "steps_tried",
            "question": "What have you already tried?",
            "reason": "Helps avoid repeated troubleshooting."
        },
        {
            "key": "error_message",
            "question": "Did you see an error message?",
            "reason": "May help identify the cause."
        }
    ]
}


def identify_issue(message: str) -> str:
    text = message.lower()

    security_keywords = [
        "fraud",
        "scam",
        "unauthorised",
        "unauthorized",
        "suspicious activity",
        "hacked",
        "unknown transaction",
        "money stolen"
    ]

    withdrawal_keywords = [
        "withdrawal",
        "withdraw",
        "cash out",
        "cashout"
    ]

    transfer_keywords = [
        "transfer",
        "sent money",
        "recipient",
        "beneficiary"
    ]

    deposit_keywords = [
        "deposit",
        "fund wallet",
        "add money",
        "top up",
        "top-up"
    ]

    access_keywords = [
        "cannot log in",
        "can't log in",
        "cannot login",
        "can't login",
        "login problem",
        "sign in",
        "account locked",
        "forgot password"
    ]

    if any(word in text for word in security_keywords):
        return "security_issue"

    if any(word in text for word in withdrawal_keywords):
        return "withdrawal_issue"

    if any(word in text for word in transfer_keywords):
        return "transfer_issue"

    if any(word in text for word in deposit_keywords):
        return "deposit_issue"

    if any(word in text for word in access_keywords):
        return "account_access_issue"

    return "other"


def get_questions(category: str) -> list[dict]:
    return ISSUE_QUESTIONS.get(
        category,
        ISSUE_QUESTIONS["other"]
    )