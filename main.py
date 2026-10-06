# -*- coding: utf-8 -*-
"""
main.py
=======
DigiLocker Document Request & Verification Tracker
===================================================

Entry point of the application.
Runs a menu-driven terminal UI.

Two roles:
  🟢 Citizen  – register/login, upload docs, make requests, track status
  🔵 Officer  – verify documents, approve/reject requests

HOW TO RUN:
    python main.py

No pip installs needed — only Python built-ins are used:
    json, os, uuid, datetime, hashlib, getpass
"""

import getpass      # built-in: hides password input (no echo in terminal)
import sys          # built-in: for clean exit

# Fix Windows terminal encoding so emojis/Unicode print correctly
sys.stdout.reconfigure(encoding="utf-8")

import auth         # our module: register / login
import documents    # our module: manage documents
import requests     # our module: manage requests
import display      # our module: pretty-print helpers


# ══════════════════════════════════════════════════════════════════════════
#  CITIZEN MENUS
# ══════════════════════════════════════════════════════════════════════════

def citizen_menu(user):
    """Main loop for a logged-in citizen."""
    while True:
        display.header(f"👤 Citizen Dashboard — {user['name']}")
        display.print_menu([
            "📂 My Documents (Locker)",
            "➕ Upload / Add a Document",
            "🗑  Delete a Document",
            "📋 My Document Requests",
            "📨 Create a New Request",
            "❌ Cancel a Request",
            "🚪 Logout"
        ])
        choice = display.prompt("Enter your choice")

        if choice == "1":
            citizen_view_documents(user)
        elif choice == "2":
            citizen_add_document(user)
        elif choice == "3":
            citizen_delete_document(user)
        elif choice == "4":
            citizen_view_requests(user)
        elif choice == "5":
            citizen_create_request(user)
        elif choice == "6":
            citizen_cancel_request(user)
        elif choice == "7":
            display.success("Logged out. Goodbye!")
            break
        else:
            display.error("Invalid choice. Please try again.")


def citizen_view_documents(user):
    display.header("📂 My Document Locker")
    docs = documents.get_my_documents(user["username"])
    display.print_documents(docs)
    input("Press Enter to go back...")


def citizen_add_document(user):
    display.header("➕ Upload a Document")

    # Show allowed document types as a numbered list
    print("  Available document types:")
    for i, dt in enumerate(documents.ALLOWED_TYPES, 1):
        print(f"    {i}. {dt}")
    print()

    doc_type_input = display.prompt("Enter document type (exact name from list)")
    doc_number     = display.prompt("Enter document number")
    issuing_auth   = display.prompt("Enter issuing authority (e.g. UIDAI, Passport Seva)")

    ok, msg = documents.add_document(
        owner_username    = user["username"],
        doc_type          = doc_type_input,
        doc_number        = doc_number,
        issuing_authority = issuing_auth
    )
    if ok:
        display.success(msg)
    else:
        display.error(msg)
    input("Press Enter to continue...")


def citizen_delete_document(user):
    display.header("🗑  Delete a Document")
    docs = documents.get_my_documents(user["username"])
    display.print_documents(docs)

    if not docs:
        input("Press Enter to go back...")
        return

    doc_id = display.prompt("Enter Document ID to delete")
    confirm = display.prompt(f"Are you sure you want to delete {doc_id}? (yes/no)")
    if confirm.lower() == "yes":
        ok, msg = documents.delete_document(doc_id, user["username"])
        display.success(msg) if ok else display.error(msg)
    else:
        display.info("Deletion cancelled.")
    input("Press Enter to continue...")


def citizen_view_requests(user):
    display.header("📋 My Document Requests")
    reqs = requests.get_my_requests(user["username"])
    display.print_requests(reqs)
    input("Press Enter to go back...")


def citizen_create_request(user):
    display.header("📨 Create a Document Request")
    doc_type  = display.prompt("What document do you need? (e.g. Income Certificate)")
    purpose   = display.prompt("Purpose / Reason (e.g. Bank loan)")
    authority = display.prompt("Authority to contact (e.g. Tehsildar Office)")

    ok, msg = requests.create_request(
        citizen_username = user["username"],
        doc_type         = doc_type,
        purpose          = purpose,
        authority        = authority
    )
    display.success(msg) if ok else display.error(msg)
    input("Press Enter to continue...")


def citizen_cancel_request(user):
    display.header("❌ Cancel a Request")
    reqs = requests.get_my_requests(user["username"])
    display.print_requests(reqs)

    if not reqs:
        input("Press Enter to go back...")
        return

    req_id = display.prompt("Enter Request ID to cancel")
    ok, msg = requests.cancel_request(req_id, user["username"])
    display.success(msg) if ok else display.error(msg)
    input("Press Enter to continue...")


# ══════════════════════════════════════════════════════════════════════════
#  OFFICER MENUS
# ══════════════════════════════════════════════════════════════════════════

def officer_menu(user):
    """Main loop for a logged-in officer."""
    while True:
        display.header(f"🔵 Officer Dashboard — {user['name']}")
        display.print_menu([
            "📄 View ALL Documents (all citizens)",
            "✅ Verify / Reject a Document",
            "📋 View ALL Requests",
            "⏳ View PENDING Requests Only",
            "✔  Approve / Reject a Request",
            "🚪 Logout"
        ])
        choice = display.prompt("Enter your choice")

        if choice == "1":
            officer_view_all_docs()
        elif choice == "2":
            officer_verify_doc(user)
        elif choice == "3":
            officer_view_all_requests()
        elif choice == "4":
            officer_view_pending_requests()
        elif choice == "5":
            officer_resolve_request(user)
        elif choice == "6":
            display.success("Logged out. Goodbye!")
            break
        else:
            display.error("Invalid choice. Please try again.")


def officer_view_all_docs():
    display.header("📄 All Documents — All Citizens")
    docs = documents.get_all_documents()
    display.print_documents(docs)
    input("Press Enter to go back...")


def officer_verify_doc(user):
    display.header("✅ Verify or Reject a Document")
    docs = documents.get_all_documents()
    display.print_documents(docs)

    if not docs:
        input("Press Enter to go back...")
        return

    doc_id = display.prompt("Enter Document ID")
    print("  Status options:")
    print("    1. Verified")
    print("    2. Rejected")
    status_choice = display.prompt("Choose status (1 or 2)")

    new_status = "Verified" if status_choice == "1" else "Rejected" if status_choice == "2" else None
    if new_status is None:
        display.error("Invalid choice.")
        input("Press Enter to continue...")
        return

    remarks = display.prompt("Add remarks (optional, press Enter to skip)")

    ok, msg = documents.verify_document(doc_id, user["username"], new_status, remarks)
    display.success(msg) if ok else display.error(msg)
    input("Press Enter to continue...")


def officer_view_all_requests():
    display.header("📋 All Document Requests")
    reqs = requests.get_all_requests()
    display.print_requests(reqs)
    input("Press Enter to go back...")


def officer_view_pending_requests():
    display.header("⏳ Pending Requests")
    reqs = requests.get_pending_requests()
    display.print_requests(reqs)
    input("Press Enter to go back...")


def officer_resolve_request(user):
    display.header("✔  Approve or Reject a Request")
    reqs = requests.get_pending_requests()
    display.print_requests(reqs)

    if not reqs:
        input("Press Enter to go back...")
        return

    req_id = display.prompt("Enter Request ID")
    print("  Action:")
    print("    1. Approve")
    print("    2. Reject")
    action = display.prompt("Choose action (1 or 2)")

    new_status = "Approved" if action == "1" else "Rejected" if action == "2" else None
    if new_status is None:
        display.error("Invalid choice.")
        input("Press Enter to continue...")
        return

    note = display.prompt("Officer note for citizen (optional)")
    ok, msg = requests.resolve_request(req_id, user["username"], new_status, note)
    display.success(msg) if ok else display.error(msg)
    input("Press Enter to continue...")


# ══════════════════════════════════════════════════════════════════════════
#  AUTH SCREENS
# ══════════════════════════════════════════════════════════════════════════

def screen_register():
    display.header("📝 Register New Account")
    name     = display.prompt("Full Name")
    username = display.prompt("Choose a Username")
    password = getpass.getpass("▶  Choose a Password: ")    # hidden input
    print("  Roles:")
    print("    1. Citizen")
    print("    2. Officer")
    role_choice = display.prompt("Choose role (1 or 2)")
    role = "citizen" if role_choice == "1" else "officer" if role_choice == "2" else ""

    ok, msg = auth.register_user(name, username, password, role)
    display.success(msg) if ok else display.error(msg)
    input("Press Enter to continue...")


def screen_login():
    display.header("🔐 Login")
    username = display.prompt("Username")
    password = getpass.getpass("▶  Password: ")     # hidden input

    ok, result = auth.login_user(username, password)
    if ok:
        display.success(f"Welcome back, {result['name']}! Role: {result['role']}")
        input("Press Enter to continue...")
        return result       # return the user dict
    else:
        display.error(result)
        input("Press Enter to continue...")
        return None


# ══════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════

def main():
    """
    Application entry point.
    Shows the welcome screen and lets users register or login.
    """
    while True:
        display.header("🇮🇳  DigiLocker Document Request & Verification Tracker")
        print("""
  Welcome! This app simulates a DigiLocker-style system where:
    🟢 Citizens  can upload documents, track verification status,
                and request documents from authorities.
    🔵 Officers  can verify documents and approve/reject requests.
        """)
        display.print_menu(["Register (New User)", "Login", "Exit"])
        choice = display.prompt("Enter your choice")

        if choice == "1":
            screen_register()
        elif choice == "2":
            user = screen_login()
            if user:
                # Route to the correct dashboard based on role
                if user["role"] == "citizen":
                    citizen_menu(user)
                elif user["role"] == "officer":
                    officer_menu(user)
        elif choice == "3":
            print("\n  Thank you for using DigiLocker Tracker. Bye! 👋\n")
            sys.exit(0)
        else:
            display.error("Invalid choice. Enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
