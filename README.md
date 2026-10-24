# 🤝 ClearHandoff

### Complaints that don't get dropped.

Picture this. A customer sends a message to a company's support team:

> *"i tried to withdraw my money yesterday and it failed and they still debited me please help"*

A support agent reads it and has to ask: *How much? Which account? What time? Do you have a transaction reference?*

The customer replies a few hours later with half the answers. The agent asks again. Eventually the ticket reaches an engineer with a vague summary, and the engineer asks the same questions all over again. 😩

Nobody in that chain did anything wrong. **The information was just collected in the wrong order, by the wrong person.** ClearHandoff is my attempt at fixing that. 💚

---

## 🚀 Try it live

| What | Link |
|---|---|
| 📝 Customer complaint form | http://142.93.58.215:8001/ |
| 🔎 Track a complaint | http://142.93.58.215:8001/track |
| 🧑‍💼 Staff dashboard | http://142.93.58.215:8001/dashboard |

**See the whole story in about 3 minutes:**
1. Open the complaint form and describe a problem in your own words. Answer what you can and skip what you don't know. Note the reference number you get (it looks like `CH-000001`).
2. Open the staff dashboard. Your ticket is there, with the contact details, the original words and a list of what's still missing.
3. Change the ticket's status, for example to "under investigation".
4. Go to the tracking page and enter your reference number and the email or phone you used. You'll see the new status. 🎉

**Please use fake details.** This is a demo. The dashboard is deliberately left open so you can look around without a password, which means anyone with the link can see submitted tickets. The demo also runs over plain `http://`, so don't type anything real.

---

## 🧭 What actually happens to a complaint? (no engineering degree needed)

Think of ClearHandoff as a very organised front desk.

1. **The customer tells their story**, in their own words. No scary forms.
2. **ClearHandoff listens and works out the type of problem** (a failed withdrawal, a missing deposit, a login problem, something suspicious...). Then it asks only the follow-up questions that matter for *that* problem. Anything the customer doesn't know can be skipped.
3. **The customer leaves a way to be reached**, an email or a phone number, and gets a **reference number**.
4. **The complaint is saved**, with the customer's original words kept *exactly* as written.
5. **A support agent opens the dashboard** and finds a clean, organised brief instead of a messy message: what the customer said, what they provided, and what is still missing and *why that matters*.
6. **The agent updates the status** as work moves along. When it's time to involve engineering, one click copies the whole handoff report.
7. **The customer can check progress any time** with their reference number and contact details, and sees a friendly status, never anything private.

The result: fewer "can you send me that again?" messages, faster investigations and customers who feel heard. 💚

---

## 💡 What it does

**For the customer, it feels like being listened to:**
- Describe the problem in your own words
- Get smart follow-up questions, skip what you don't know
- Receive a reference number and check your status later

**For the support and engineering team, it feels like being handed a clean brief instead of a mystery:**
- The customer's original words, **stored exactly as written** and never rewritten
- The details they provided, organised
- A clear list of **what's still missing, and why it matters** (like "helps support locate the transaction")
- A one-click copy of the full engineering handoff report
- A status workflow, from received to resolved
- Search by reference, name, email, phone or complaint text

---

## 🛡️ Design decisions I care about

- **It never invents facts.** The report separates what the customer *said* from what has been *verified*. Guesswork dressed up as certainty is how investigations go wrong.
- **Tracking leaks nothing.** A wrong reference number and a wrong contact detail get the exact same reply, so nobody can use the tracking page to discover which tickets exist. It shows a friendly status and never the complaint itself.
- **The server is the boss of the rules.** Contact details, statuses and answers are all checked on the backend, so skipping the website and talking to the API directly doesn't get around them.
- **Staff data can be locked.** The dashboard and every ticket endpoint can require a staff login, and passwords are compared in a way that doesn't leak information through timing. For the live demo only, there's a switch that opens the dashboard so reviewers can look around.
- **39 automated tests** check classification, validation, tracking privacy, status updates and access control, so I can change things without quietly breaking them.

---

## 🧰 Built with
Python · FastAPI · SQLAlchemy · SQLite · vanilla JavaScript · pytest

---

## 💻 Run it on your computer

```
pip install -r requirements.txt
```

Set the staff login (PowerShell):
```
$env:STAFF_USERNAME="your-username"
$env:STAFF_PASSWORD="your-strong-password"
```

Or skip the login while you're just exploring:
```
$env:DEMO_OPEN_DASHBOARD="1"
```

Start it:
```
uvicorn main:app --reload
```

- Customers: http://127.0.0.1:8000/
- Tracking: http://127.0.0.1:8000/track
- Staff: http://127.0.0.1:8000/dashboard

Run the tests with `pytest`.

---

## ☁️ How the live demo is hosted

The demo runs on a small Ubuntu server as a background service (gunicorn with a uvicorn worker, managed by `systemd`). That means it keeps running when my laptop is closed and starts again by itself after a reboot. The staff login and the demo switch are read from environment variables, so no secrets live in this repository.

---

## 🚧 Honest limitations (and what I'd build next)

I'm still learning, and I'd rather be upfront about where this prototype ends:

- **Issue detection is keyword-based.** It handles common cases but not typos or unusual wording. A smarter, model-assisted classifier is the obvious next step.
- **Staff access is basic.** There's one shared login, plus the demo switch that opens the dashboard for reviewers. Production would use individual staff accounts with hashed passwords, roles and a record of who changed what.
- **No notifications yet.** Customers have to check the tracking page. Email or SMS updates would close that gap.
- **SQLite is a prototype choice.** A real deployment would use Postgres.
- **The demo runs over plain HTTP.** A real deployment needs HTTPS and a proper domain.

---

## 📖 Tech words, translated

- **Backend:** the part of the app that works behind the scenes: the rules, the saving, the thinking.
- **API:** a set of doors other software can knock on to ask the backend for things.
- **Database:** where the complaints are stored, like a very tidy filing cabinet.
- **Dashboard:** the screen the support team uses to see and manage tickets.
- **Server:** a computer that stays switched on so everyone can reach the app.
- **Automated tests:** little checks that run by themselves to make sure nothing broke.

---

## 💚 Why I built this

I'm an economics graduate teaching myself backend engineering. I wanted to build something that mirrors a real operational problem instead of another to-do app. ClearHandoff has taught me API design, validation, authentication, privacy-aware design, testing and putting an app on a real server, and I'm still improving it.

**Built by Nneoma**, learning software engineering one step at a time. 💚