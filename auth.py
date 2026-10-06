"""
auth.py
=======
User authentication: registration and login.

Concepts used:
  - Functions
  - Lists and dictionaries
  - Simple string hashing with Python's built-in `hashlib`
  - Loading/saving data through data_store.py
"""

import hashlib          # built-in: used to hash passwords (never store plain text!)
import data_store       # our own module


def _hash_password(password):
    """
    Convert a plain-text password into a SHA-256 hash string.
    This way we never store the real password — only its fingerprint.

    Example:
        "secret123"  →  "9b8769a4a742959a..."
    """
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name, username, password, role):
    """
    Create a new user account.

    Parameters:
        name     – full name   (e.g. "Riya Sharma")
        username – unique ID   (e.g. "riya123")
        password – plain text  (will be hashed before saving)
        role     – "citizen" or "officer"

    Returns:
        (True, success_message)  or  (False, error_message)
    """
    users = data_store.load_users()          # read existing users from JSON

    # ── Validation ─────────────────────────────────────────────────────────
    if not username or not password:
        return False, "Username and password cannot be empty."

    # Check if the username is already taken
    for user in users:
        if user["username"] == username:
            return False, f"Username '{username}' is already taken."

    if role not in ("citizen", "officer"):
        return False, "Role must be 'citizen' or 'officer'."

    # ── Build the user record ───────────────────────────────────────────────
    new_user = {
        "name":     name,
        "username": username,
        "password": _hash_password(password),   # store HASH, not plain text
        "role":     role
    }

    users.append(new_user)          # add to the list
    data_store.save_users(users)    # persist to JSON file
    return True, f"Account created for '{username}' as {role}!"


def login_user(username, password):
    """
    Verify credentials and return the user record if they match.

    Returns:
        (True, user_dict)  if credentials are correct
        (False, error_msg) otherwise
    """
    users = data_store.load_users()
    hashed = _hash_password(password)

    for user in users:
        if user["username"] == username and user["password"] == hashed:
            return True, user      # ✅ match found

    return False, "Invalid username or password."
