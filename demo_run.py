# -*- coding: utf-8 -*-
"""
demo_run.py
===========
Automated demo of the DigiLocker Tracker.
Runs without any user input — shows all features back-to-back.
"""

import sys
import os

# Fix Windows terminal encoding so emojis/Unicode print correctly
sys.stdout.reconfigure(encoding="utf-8")

# Add project folder to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

# ── Clean slate: remove old data files so demo is reproducible ─────────────
import shutil
data_path = os.path.join(os.path.dirname(__file__), "data")
if os.path.exists(data_path):
    shutil.rmtree(data_path)

import auth
import documents
import requests as req_module
import display

SEP = "\n" + "=" * 65 + "\n"


# ══════════════════════════════════════════════════════════════════════════
print(SEP)
print("  🇮🇳  DigiLocker Document Request & Verification Tracker")
print("       AUTOMATED DEMO RUN")
print(SEP)


# ══════════════════════════════════════════════════════════════════════════
# STEP 1 — Register users
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 1 — Registering Users")

users_to_create = [
    ("Riya Sharma",    "riya",    "pass123",   "citizen"),
    ("Arjun Mehta",    "arjun",   "pass456",   "citizen"),
    ("Officer Priya",  "priya_o", "officer@1", "officer"),
]

for name, uname, pwd, role in users_to_create:
    ok, msg = auth.register_user(name, uname, pwd, role)
    display.success(msg) if ok else display.error(msg)


# ══════════════════════════════════════════════════════════════════════════
# STEP 2 — Login citizens
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 2 — Logging In")

ok, riya   = auth.login_user("riya",    "pass123")
ok2, arjun = auth.login_user("arjun",   "pass456")
ok3, priya = auth.login_user("priya_o", "officer@1")

display.success(f"Logged in: {riya['name']} ({riya['role']})")
display.success(f"Logged in: {arjun['name']} ({arjun['role']})")
display.success(f"Logged in: {priya['name']} ({priya['role']})")


# ══════════════════════════════════════════════════════════════════════════
# STEP 3 — Citizens upload documents
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 3 — Citizens Upload Documents to Locker")

uploads = [
    # (username, doc_type, doc_number, authority)
    ("riya",  "Aadhaar Card",       "1234-5678-9012", "UIDAI"),
    ("riya",  "PAN Card",           "ABCDE1234F",     "Income Tax Dept"),
    ("riya",  "Driving Licence",    "DL-2023-56789",  "RTO Delhi"),
    ("arjun", "Passport",           "P1234567",       "Passport Seva"),
    ("arjun", "Voter ID",           "ABC1234567",     "Election Commission"),
    ("arjun", "Marksheet",          "CBSE-2022-88",   "CBSE Board"),
]

for uname, dtype, dnum, auth_name in uploads:
    ok, msg = documents.add_document(uname, dtype, dnum, auth_name)
    display.success(msg) if ok else display.error(msg)


# ══════════════════════════════════════════════════════════════════════════
# STEP 4 — Citizens create document requests
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 4 — Citizens Submit Document Requests")

req_list = [
    ("riya",  "Income Certificate",  "Bank loan application",   "Tehsildar Office"),
    ("riya",  "Caste Certificate",   "College admission form",  "District Collector"),
    ("arjun", "Birth Certificate",   "Passport renewal",        "Municipal Corp"),
    ("arjun", "Income Certificate",  "Scholarship form",        "Tehsildar Office"),
]

req_ids = []
for uname, dtype, purpose, auth_name in req_list:
    ok, msg = req_module.create_request(uname, dtype, purpose, auth_name)
    display.success(msg) if ok else display.error(msg)
    if ok:
        req_ids.append(msg.split("ID: ")[-1])   # extract the req ID from message


# ══════════════════════════════════════════════════════════════════════════
# STEP 5 — Officer views all documents
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 5 — Officer Views All Documents")
all_docs = documents.get_all_documents()
display.print_documents(all_docs)


# ══════════════════════════════════════════════════════════════════════════
# STEP 6 — Officer verifies some documents
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 6 — Officer Verifies / Rejects Documents")

# Get doc IDs from the loaded list
doc_ids = [d["doc_id"] for d in all_docs]

# Verify first 4, reject last 2
for i, doc_id in enumerate(doc_ids):
    if i < 4:
        ok, msg = documents.verify_document(doc_id, "priya_o", "Verified",
                                            "Documents match original records.")
    else:
        ok, msg = documents.verify_document(doc_id, "priya_o", "Rejected",
                                            "Blurry image / mismatch detected.")
    display.success(msg) if ok else display.error(msg)


# ══════════════════════════════════════════════════════════════════════════
# STEP 7 — Citizen checks their updated document status
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 7 — Riya Checks Her Document Locker (Updated Status)")
riya_docs = documents.get_my_documents("riya")
display.print_documents(riya_docs)

display.header("STEP 7b — Arjun Checks His Document Locker (Updated Status)")
arjun_docs = documents.get_my_documents("arjun")
display.print_documents(arjun_docs)


# ══════════════════════════════════════════════════════════════════════════
# STEP 8 — Officer views all pending requests
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 8 — Officer Views Pending Requests")
pending = req_module.get_pending_requests()
display.print_requests(pending)


# ══════════════════════════════════════════════════════════════════════════
# STEP 9 — Officer approves/rejects requests
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 9 — Officer Resolves Document Requests")

for i, req in enumerate(pending):
    if i % 2 == 0:
        ok, msg = req_module.resolve_request(
            req["req_id"], "priya_o", "Approved",
            "Request verified and approved. Collect from office.")
    else:
        ok, msg = req_module.resolve_request(
            req["req_id"], "priya_o", "Rejected",
            "Incomplete application form. Please reapply.")
    display.success(msg) if ok else display.error(msg)


# ══════════════════════════════════════════════════════════════════════════
# STEP 10 — Citizens check their request status
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 10 — Riya Checks Her Request Status")
display.print_requests(req_module.get_my_requests("riya"))

display.header("STEP 10b — Arjun Checks His Request Status")
display.print_requests(req_module.get_my_requests("arjun"))


# ══════════════════════════════════════════════════════════════════════════
# STEP 11 — Citizen cancels a pending request (create a new one first)
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 11 — Riya Creates & Then Cancels a Request")
ok, msg = req_module.create_request("riya", "Other", "Testing cancellation", "Any Office")
display.success(msg) if ok else display.error(msg)

# Get the new request ID (it'll be the last one)
riya_reqs = req_module.get_my_requests("riya")
last_req_id = riya_reqs[-1]["req_id"]
ok, msg = req_module.cancel_request(last_req_id, "riya")
display.success(msg) if ok else display.error(msg)


# ══════════════════════════════════════════════════════════════════════════
# STEP 12 — Riya deletes a document
# ══════════════════════════════════════════════════════════════════════════
display.header("STEP 12 — Riya Deletes Her Driving Licence")
riya_docs_fresh = documents.get_my_documents("riya")
dl_doc = next((d for d in riya_docs_fresh if d["doc_type"] == "Driving Licence"), None)
if dl_doc:
    ok, msg = documents.delete_document(dl_doc["doc_id"], "riya")
    display.success(msg) if ok else display.error(msg)

display.header("Riya's Locker After Deletion")
display.print_documents(documents.get_my_documents("riya"))


# ══════════════════════════════════════════════════════════════════════════
print(SEP)
print("  ✅  DEMO COMPLETE — All features demonstrated!")
print("  To run the interactive app: python main.py")
print(SEP)
