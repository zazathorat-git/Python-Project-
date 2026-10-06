"""
requests.py
===========
Document Request System.

A citizen can REQUEST a specific document type from an officer/authority.
The officer sees pending requests and can Approve or Reject them.

Concepts used:
  - uuid, datetime (built-in)
  - List comprehensions
  - Dictionary manipulation
"""

import uuid
import datetime
import data_store


# Request statuses lifecycle:
#   Pending → Approved
#           → Rejected
STATUS_PENDING  = "Pending"
STATUS_APPROVED = "Approved"
STATUS_REJECTED = "Rejected"


def create_request(citizen_username, doc_type, purpose, authority):
    """
    Citizen creates a new document request.

    Parameters:
        citizen_username – who is requesting
        doc_type         – what document they need (e.g. "Income Certificate")
        purpose          – why they need it       (e.g. "Bank loan application")
        authority        – which office to contact (e.g. "Tehsildar Office")
    """
    if not doc_type.strip() or not purpose.strip():
        return False, "Document type and purpose cannot be empty."

    requests = data_store.load_requests()

    # Prevent duplicate pending requests for same doc type
    for req in requests:
        if (req["citizen"] == citizen_username and
                req["doc_type"] == doc_type and
                req["status"] == STATUS_PENDING):
            return False, f"You already have a pending request for '{doc_type}'."

    new_request = {
        "req_id":    str(uuid.uuid4())[:8].upper(),
        "citizen":   citizen_username,
        "doc_type":  doc_type,
        "purpose":   purpose,
        "authority": authority,
        "status":    STATUS_PENDING,
        "created_at": _now(),
        "resolved_at": None,
        "officer_note": ""
    }

    requests.append(new_request)
    data_store.save_requests(requests)
    return True, f"Request submitted! Your Request ID: {new_request['req_id']}"


def get_my_requests(citizen_username):
    """Return all requests made by a specific citizen."""
    requests = data_store.load_requests()
    return [r for r in requests if r["citizen"] == citizen_username]


def get_all_requests():
    """Return all requests (officer view)."""
    return data_store.load_requests()


def get_pending_requests():
    """Return only requests with status 'Pending'."""
    requests = data_store.load_requests()
    return [r for r in requests if r["status"] == STATUS_PENDING]


def resolve_request(req_id, officer_username, new_status, note=""):
    """
    Officer resolves a request: Approve or Reject.

    Parameters:
        req_id          – which request to resolve
        officer_username – who is resolving
        new_status      – "Approved" or "Rejected"
        note            – optional message to citizen
    """
    if new_status not in (STATUS_APPROVED, STATUS_REJECTED):
        return False, "Status must be 'Approved' or 'Rejected'."

    requests = data_store.load_requests()
    for req in requests:
        if req["req_id"] == req_id:
            if req["status"] != STATUS_PENDING:
                return False, f"Request {req_id} is already '{req['status']}'. Cannot change."
            req["status"]       = new_status
            req["resolved_at"]  = _now()
            req["officer_note"] = note
            req["resolved_by"]  = officer_username
            data_store.save_requests(requests)
            return True, f"Request {req_id} has been '{new_status}'."

    return False, f"No request found with ID '{req_id}'."


def cancel_request(req_id, citizen_username):
    """Allow a citizen to cancel their own pending request."""
    requests = data_store.load_requests()
    for req in requests:
        if req["req_id"] == req_id and req["citizen"] == citizen_username:
            if req["status"] != STATUS_PENDING:
                return False, "Only pending requests can be cancelled."
            req["status"]      = "Cancelled"
            req["resolved_at"] = _now()
            data_store.save_requests(requests)
            return True, f"Request {req_id} cancelled."

    return False, "Request not found or you don't own it."


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
