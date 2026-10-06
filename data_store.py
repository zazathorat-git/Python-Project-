"""
data_store.py
=============
Handles all data persistence using plain JSON files.
No external libraries needed — just Python's built-in `json` and `os` modules.

Data is saved in the `data/` folder as JSON files:
  - users.json      → stores user accounts
  - documents.json  → stores uploaded documents
  - requests.json   → stores document requests
"""

import json   # for reading/writing JSON files
import os     # for file path operations


# ── Folder and file paths ──────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")   # ./data/
USERS_FILE     = os.path.join(DATA_DIR, "users.json")
DOCUMENTS_FILE = os.path.join(DATA_DIR, "documents.json")
REQUESTS_FILE  = os.path.join(DATA_DIR, "requests.json")


def _ensure_data_dir():
    """Create the data/ directory if it doesn't already exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _read_json(filepath):
    """
    Read a JSON file and return its contents as a Python dict/list.
    If the file doesn't exist yet, return an empty list [].
    """
    if not os.path.exists(filepath):
        return []                         # fresh start
    with open(filepath, "r") as f:
        return json.load(f)               # parse JSON → Python object


def _write_json(filepath, data):
    """
    Write a Python object (dict or list) to a JSON file.
    `indent=2` makes the file human-readable.
    """
    _ensure_data_dir()
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)     # Python object → JSON text


# ── User helpers ───────────────────────────────────────────────────────────
def load_users():
    return _read_json(USERS_FILE)

def save_users(users):
    _write_json(USERS_FILE, users)


# ── Document helpers ───────────────────────────────────────────────────────
def load_documents():
    return _read_json(DOCUMENTS_FILE)

def save_documents(documents):
    _write_json(DOCUMENTS_FILE, documents)


# ── Request helpers ────────────────────────────────────────────────────────
def load_requests():
    return _read_json(REQUESTS_FILE)

def save_requests(requests):
    _write_json(REQUESTS_FILE, requests)
