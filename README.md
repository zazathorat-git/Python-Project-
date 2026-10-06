# 🇮🇳 DigiLocker Document Request & Verification Tracker

A terminal-based Python application that simulates India's **DigiLocker** system — allowing citizens to upload documents, request new ones, and track verification status, while officers can verify and approve/reject requests.

> **Built with 100% Python built-ins** — no `pip install` needed!

---

## 📁 Project Structure

```
digilocker_tracker/
├── main.py         → Interactive app entry point (run this!)
├── auth.py         → User registration & login (SHA-256 hashed passwords)
├── data_store.py   → JSON-based data persistence layer
├── documents.py    → Document upload, verification, deletion
├── requests.py     → Document request submit / approve / reject / cancel
├── display.py      → Coloured terminal UI (ANSI colours, menus, tables)
├── demo_run.py     → Automated demo (no user input needed)
└── data/           → Auto-created JSON data files (gitignored)
    ├── users.json
    ├── documents.json
    └── requests.json
```

---

## 🚀 How to Run

### Requirements
- Python 3.x (no external libraries needed)

### Interactive Mode
```bash
python main.py
```

### Automated Demo (see all features at once)
```bash
python demo_run.py
```

---

## 👥 Two Roles

### 🟢 Citizen
- Register & Login
- Upload documents to their locker (Aadhaar, PAN, Passport, etc.)
- Track document **verification status** (Pending / Verified / Rejected)
- Submit document **requests** to authorities
- Cancel pending requests
- Delete documents from locker

### 🔵 Officer
- Login with officer credentials
- View **all** citizens' documents
- **Verify** or **Reject** documents with remarks
- View all pending document requests
- **Approve** or **Reject** requests with notes to citizen

---

## 📋 Supported Document Types

| Document | Issuing Authority |
|----------|-------------------|
| Aadhaar Card | UIDAI |
| PAN Card | Income Tax Dept |
| Passport | Passport Seva |
| Driving Licence | RTO |
| Voter ID | Election Commission |
| Birth Certificate | Municipal Corp |
| Marksheet | CBSE / State Board |
| Income Certificate | Tehsildar Office |
| Caste Certificate | District Collector |
| Other | Any Authority |

---

## 🔑 Python Concepts Used

| Concept | Where Used |
|---------|-----------|
| `json` module | Persistent file storage (`data_store.py`) |
| `hashlib` (SHA-256) | Password hashing (`auth.py`) |
| `uuid` module | Unique document/request IDs |
| `datetime` module | Timestamps on every action |
| `os` module | File path management |
| `getpass` module | Hidden password input |
| Functions & modules | Entire project structure |
| Lists & dictionaries | All data records |
| List comprehensions | Filtering documents/requests |
| f-strings | All display formatting |
| ANSI colour codes | Terminal UI (`display.py`) |

---

## 💾 Data Storage

All data is saved locally as **JSON files** inside the `data/` folder:

```json
// data/users.json
[
  {
    "name": "Riya Sharma",
    "username": "riya",
    "password": "sha256_hash_here",
    "role": "citizen"
  }
]
```

---

## 🛡️ Security Note

Passwords are **never stored in plain text**. They are hashed using SHA-256 via Python's built-in `hashlib` before saving to disk.

---

## 📸 Sample Output

```
════════════════════════════════════════════════════════════
           STEP 7 — Riya's Document Locker
════════════════════════════════════════════════════════════
ID         Type          Doc Number      Authority       Status     Uploaded
───────────────────────────────────────────────────────────────────────────
2289F78A   Aadhaar Card  1234-5678-9012  UIDAI           Verified   2026-10-05
C8915482   PAN Card      ABCDE1234F      Income Tax Dept Verified   2026-10-05
```

---

## 📄 License

MIT License — free to use and modify.
