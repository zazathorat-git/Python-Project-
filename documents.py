"""
documents.py
============
Manage the citizen's document locker.

Concepts used:
  - uuid module  → generate unique IDs without collisions
  - datetime     → timestamp every action
  - List iteration and filtering
"""

import uuid           # built-in: generates unique identifiers like "a3f7c..."
import datetime       # built-in: get current date/time
import data_store


# Allowed document types (like DigiLocker categories)
ALLOWED_TYPES = [
    "Aadhaar Card",
    "PAN Card",
    "Passport",
    "Driving Licence",
    "Voter ID",
    "Birth Certificate",
    "Marksheet",
    "Income Certificate",
    "Caste Certificate",
    "Other"
]


def add_document(owner_username, doc_type, doc_number, issuing_authority):
    """
    Add (upload) a document to the citizen's locker.

    Each document gets:
      - a unique `doc_id`   (UUID)
      - a `status`          (starts as "Pending Verification")
      - a `uploaded_at`     timestamp
    """
    if doc_type not in ALLOWED_TYPES:
        return False, f"Invalid document type. Choose from: {ALLOWED_TYPES}"

    if not doc_number.strip():
        return False, "Document number cannot be empty."

    documents = data_store.load_documents()

    # Check for duplicates (same owner + same doc_type + same number)
    for doc in documents:
        if (doc["owner"] == owner_username and
                doc["doc_type"] == doc_type and
                doc["doc_number"] == doc_number):
            return False, "This document already exists in your locker."

    new_doc = {
        "doc_id":            str(uuid.uuid4())[:8].upper(),   # short unique ID
        "owner":             owner_username,
        "doc_type":          doc_type,
        "doc_number":        doc_number,
        "issuing_authority": issuing_authority,
        "status":            "Pending Verification",          # initial status
        "uploaded_at":       _now(),
        "verified_at":       None,                            # set when verified
        "remarks":           ""
    }

    documents.append(new_doc)
    data_store.save_documents(documents)
    return True, f"Document '{doc_type}' added with ID: {new_doc['doc_id']}"


def get_my_documents(owner_username):
    """Return all documents belonging to `owner_username`."""
    documents = data_store.load_documents()
    return [doc for doc in documents if doc["owner"] == owner_username]


def get_all_documents():
    """Return every document (officer view)."""
    return data_store.load_documents()


def verify_document(doc_id, officer_username, new_status, remarks=""):
    """
    Officer action: update verification status of a document.

    Allowed statuses:
      "Verified"  – document is genuine
      "Rejected"  – document failed verification
    """
    allowed_statuses = ("Verified", "Rejected")
    if new_status not in allowed_statuses:
        return False, f"Status must be one of: {allowed_statuses}"

    documents = data_store.load_documents()
    for doc in documents:
        if doc["doc_id"] == doc_id:
            doc["status"]       = new_status
            doc["verified_at"]  = _now()
            doc["remarks"]      = remarks
            doc["verified_by"]  = officer_username
            data_store.save_documents(documents)
            return True, f"Document {doc_id} marked as '{new_status}'."

    return False, f"No document found with ID '{doc_id}'."


def delete_document(doc_id, owner_username):
    """Allow a citizen to remove a document from their locker."""
    documents = data_store.load_documents()
    original_count = len(documents)

    # Keep only documents that do NOT match the deletion criteria
    documents = [
        doc for doc in documents
        if not (doc["doc_id"] == doc_id and doc["owner"] == owner_username)
    ]

    if len(documents) == original_count:
        return False, "Document not found or you don't own it."

    data_store.save_documents(documents)
    return True, f"Document {doc_id} deleted."


def _now():
    """Return current datetime as a formatted string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
