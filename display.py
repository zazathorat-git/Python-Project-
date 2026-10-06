"""
display.py
==========
Pretty-print helpers for the terminal UI.

Concepts used:
  - String formatting with f-strings
  - Loops over lists
  - ANSI colour codes for coloured output (works on most terminals)
"""

# ── ANSI colour codes ──────────────────────────────────────────────────────
# These are special escape sequences that terminals interpret as colours.
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
MAGENTA= "\033[95m"


def header(text):
    """Print a big section header."""
    width = 60
    print()
    print(CYAN + "═" * width + RESET)
    print(CYAN + BOLD + f"  {text}".center(width) + RESET)
    print(CYAN + "═" * width + RESET)


def success(msg):
    print(GREEN + "✔  " + msg + RESET)

def error(msg):
    print(RED + "✘  " + msg + RESET)

def info(msg):
    print(YELLOW + "ℹ  " + msg + RESET)

def prompt(msg):
    """Show a prompt and return stripped user input."""
    return input(BLUE + "▶  " + msg + RESET).strip()


# ── Status badge colours ───────────────────────────────────────────────────
STATUS_COLORS = {
    "Pending Verification": YELLOW,
    "Verified":             GREEN,
    "Rejected":             RED,
    "Pending":              YELLOW,
    "Approved":             GREEN,
    "Cancelled":            MAGENTA,
}

def _colored_status(status):
    color = STATUS_COLORS.get(status, RESET)
    return color + status + RESET


def print_documents(docs):
    """Print a formatted table of documents."""
    if not docs:
        info("No documents found.")
        return

    header_row = f"{'ID':<10} {'Type':<22} {'Doc Number':<18} {'Issuing Auth':<20} {'Status':<25} {'Uploaded'}"
    print(BOLD + header_row + RESET)
    print("─" * 110)
    for doc in docs:
        status_str = _colored_status(doc['status'])
        print(
            f"{doc['doc_id']:<10} "
            f"{doc['doc_type']:<22} "
            f"{doc['doc_number']:<18} "
            f"{doc['issuing_authority']:<20} "
            f"{status_str:<35} "           # extra width for colour codes
            f"{doc['uploaded_at']}"
        )
        if doc.get("remarks"):
            print(f"  {'':>8}  Remarks: {doc['remarks']}")
    print()


def print_requests(reqs):
    """Print a formatted table of requests."""
    if not reqs:
        info("No requests found.")
        return

    header_row = f"{'Req ID':<10} {'Citizen':<15} {'Doc Type':<22} {'Purpose':<25} {'Authority':<20} {'Status'}"
    print(BOLD + header_row + RESET)
    print("─" * 120)
    for req in reqs:
        status_str = _colored_status(req['status'])
        print(
            f"{req['req_id']:<10} "
            f"{req['citizen']:<15} "
            f"{req['doc_type']:<22} "
            f"{req['purpose']:<25} "
            f"{req['authority']:<20} "
            f"{status_str}"
        )
        if req.get("officer_note"):
            print(f"  {'':>8}  Note: {req['officer_note']}")
    print()


def print_menu(options):
    """
    Print a numbered menu.
    `options` is a list of strings.
    """
    print()
    for i, opt in enumerate(options, start=1):
        print(f"  {CYAN}{i}{RESET}. {opt}")
    print()


def divider():
    print(CYAN + "─" * 60 + RESET)
