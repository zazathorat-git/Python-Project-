/**
 * demo_run.js
 * ===========
 * DigiLocker Document Request & Verification Tracker
 * Full demo run — no npm packages needed, uses only Node.js built-ins.
 *
 * Run with:  agy-node demo_run.js
 */

const fs   = require("fs");
const path = require("path");
const crypto = require("crypto");

// ── Data directory ─────────────────────────────────────────────────────────
const DATA_DIR  = path.join(__dirname, "data");
const U_FILE    = path.join(DATA_DIR, "users.json");
const D_FILE    = path.join(DATA_DIR, "documents.json");
const R_FILE    = path.join(DATA_DIR, "requests.json");

// Clean slate
if (fs.existsSync(DATA_DIR)) fs.rmSync(DATA_DIR, { recursive: true });
fs.mkdirSync(DATA_DIR, { recursive: true });

// ── Helpers ────────────────────────────────────────────────────────────────
const read  = f => fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : [];
const write = (f, d) => fs.writeFileSync(f, JSON.stringify(d, null, 2));
const now   = () => new Date().toISOString().replace("T", " ").slice(0, 19);
const uid   = () => crypto.randomUUID().split("-")[0].toUpperCase();
const hash  = p => crypto.createHash("sha256").update(p).digest("hex");

// ── ANSI colours ───────────────────────────────────────────────────────────
const C = {
  reset: "\x1b[0m", bold: "\x1b[1m",
  green: "\x1b[92m", red: "\x1b[91m", yellow: "\x1b[93m",
  cyan:  "\x1b[96m", blue: "\x1b[94m", magenta: "\x1b[95m",
};
const ok  = m => console.log(C.green  + "  ✔  " + m + C.reset);
const err = m => console.log(C.red    + "  ✘  " + m + C.reset);
const inf = m => console.log(C.yellow + "  ℹ  " + m + C.reset);
const hdr = t => {
  const w = 65;
  console.log("\n" + C.cyan + "═".repeat(w) + C.reset);
  console.log(C.cyan + C.bold + ("  " + t).padEnd(w) + C.reset);
  console.log(C.cyan + "═".repeat(w) + C.reset);
};

// ── Auth ───────────────────────────────────────────────────────────────────
function registerUser(name, username, password, role) {
  const users = read(U_FILE);
  if (users.find(u => u.username === username))
    return [false, `Username '${username}' already taken.`];
  users.push({ name, username, password: hash(password), role });
  write(U_FILE, users);
  return [true, `Account created for '${username}' as ${role}!`];
}

function loginUser(username, password) {
  const users = read(U_FILE);
  const user  = users.find(u => u.username === username && u.password === hash(password));
  return user ? [true, user] : [false, "Invalid username or password."];
}

// ── Documents ──────────────────────────────────────────────────────────────
function addDocument(owner, docType, docNumber, issuingAuth) {
  const docs = read(D_FILE);
  if (docs.find(d => d.owner === owner && d.doc_type === docType && d.doc_number === docNumber))
    return [false, "Document already in locker."];
  const doc = {
    doc_id: uid(), owner, doc_type: docType, doc_number: docNumber,
    issuing_authority: issuingAuth, status: "Pending Verification",
    uploaded_at: now(), verified_at: null, remarks: ""
  };
  docs.push(doc);
  write(D_FILE, docs);
  return [true, `Document '${docType}' added with ID: ${doc.doc_id}`];
}

function getMyDocuments(owner) { return read(D_FILE).filter(d => d.owner === owner); }
function getAllDocuments()      { return read(D_FILE); }

function verifyDocument(docId, officer, status, remarks = "") {
  const docs = read(D_FILE);
  const doc  = docs.find(d => d.doc_id === docId);
  if (!doc) return [false, `No document found: ${docId}`];
  Object.assign(doc, { status, verified_at: now(), remarks, verified_by: officer });
  write(D_FILE, docs);
  return [true, `Document ${docId} marked as '${status}'.`];
}

function deleteDocument(docId, owner) {
  let docs = read(D_FILE);
  const before = docs.length;
  docs = docs.filter(d => !(d.doc_id === docId && d.owner === owner));
  if (docs.length === before) return [false, "Document not found or not yours."];
  write(D_FILE, docs);
  return [true, `Document ${docId} deleted.`];
}

// ── Requests ───────────────────────────────────────────────────────────────
function createRequest(citizen, docType, purpose, authority) {
  const reqs = read(R_FILE);
  if (reqs.find(r => r.citizen === citizen && r.doc_type === docType && r.status === "Pending"))
    return [false, `Pending request for '${docType}' already exists.`];
  const req = {
    req_id: uid(), citizen, doc_type: docType, purpose, authority,
    status: "Pending", created_at: now(), resolved_at: null, officer_note: ""
  };
  reqs.push(req);
  write(R_FILE, reqs);
  return [true, `Request submitted! ID: ${req.req_id}`];
}

function getMyRequests(citizen) { return read(R_FILE).filter(r => r.citizen === citizen); }
function getPendingRequests()    { return read(R_FILE).filter(r => r.status === "Pending"); }

function resolveRequest(reqId, officer, status, note = "") {
  const reqs = read(R_FILE);
  const req  = reqs.find(r => r.req_id === reqId);
  if (!req) return [false, `Request not found: ${reqId}`];
  if (req.status !== "Pending") return [false, `Already '${req.status}'.`];
  Object.assign(req, { status, resolved_at: now(), officer_note: note, resolved_by: officer });
  write(R_FILE, reqs);
  return [true, `Request ${reqId} → '${status}'.`];
}

function cancelRequest(reqId, citizen) {
  const reqs = read(R_FILE);
  const req  = reqs.find(r => r.req_id === reqId && r.citizen === citizen);
  if (!req) return [false, "Request not found or not yours."];
  if (req.status !== "Pending") return [false, "Only pending requests can be cancelled."];
  req.status = "Cancelled"; req.resolved_at = now();
  write(R_FILE, reqs);
  return [true, `Request ${reqId} cancelled.`];
}

// ── Pretty table printers ──────────────────────────────────────────────────
const STATUS_COLOR = {
  "Pending Verification": C.yellow, "Verified": C.green,   "Rejected": C.red,
  "Pending": C.yellow,              "Approved": C.green,   "Cancelled": C.magenta,
};
const cs = s => (STATUS_COLOR[s] || C.reset) + s + C.reset;

function printDocuments(docs) {
  if (!docs.length) { inf("No documents found."); return; }
  console.log(C.bold + `${"ID".padEnd(10)} ${"Type".padEnd(22)} ${"Doc Number".padEnd(18)} ${"Authority".padEnd(20)} ${"Status".padEnd(26)} Uploaded` + C.reset);
  console.log("─".repeat(115));
  for (const d of docs) {
    console.log(
      `${d.doc_id.padEnd(10)} ${d.doc_type.padEnd(22)} ${d.doc_number.padEnd(18)} ${d.issuing_authority.padEnd(20)} ${cs(d.status).padEnd(38)} ${d.uploaded_at}`
    );
    if (d.remarks) console.log(`${"".padEnd(10)} Remarks: ${d.remarks}`);
  }
  console.log();
}

function printRequests(reqs) {
  if (!reqs.length) { inf("No requests found."); return; }
  console.log(C.bold + `${"Req ID".padEnd(10)} ${"Citizen".padEnd(15)} ${"Doc Type".padEnd(22)} ${"Purpose".padEnd(28)} ${"Authority".padEnd(20)} Status` + C.reset);
  console.log("─".repeat(120));
  for (const r of reqs) {
    console.log(
      `${r.req_id.padEnd(10)} ${r.citizen.padEnd(15)} ${r.doc_type.padEnd(22)} ${r.purpose.padEnd(28)} ${r.authority.padEnd(20)} ${cs(r.status)}`
    );
    if (r.officer_note) console.log(`${"".padEnd(10)} Note: ${r.officer_note}`);
  }
  console.log();
}

// ══════════════════════════════════════════════════════════════════════════
// DEMO STARTS HERE
// ══════════════════════════════════════════════════════════════════════════

const SEP = "\n" + "=".repeat(65) + "\n";
console.log(SEP);
console.log("  🇮🇳  DigiLocker Document Request & Verification Tracker");
console.log("       AUTOMATED DEMO RUN");
console.log(SEP);

// ── STEP 1: Register users ─────────────────────────────────────────────────
hdr("STEP 1 — Registering Users");
[
  ["Riya Sharma",   "riya",    "pass123",   "citizen"],
  ["Arjun Mehta",   "arjun",   "pass456",   "citizen"],
  ["Officer Priya", "priya_o", "officer@1", "officer"],
].forEach(([n, u, p, r]) => { const [s, m] = registerUser(n, u, p, r); s ? ok(m) : err(m); });

// ── STEP 2: Login ──────────────────────────────────────────────────────────
hdr("STEP 2 — Logging In");
const [, riya]  = loginUser("riya",    "pass123");
const [, arjun] = loginUser("arjun",   "pass456");
const [, priya] = loginUser("priya_o", "officer@1");
ok(`Logged in: ${riya.name} (${riya.role})`);
ok(`Logged in: ${arjun.name} (${arjun.role})`);
ok(`Logged in: ${priya.name} (${priya.role})`);

// ── STEP 3: Upload documents ───────────────────────────────────────────────
hdr("STEP 3 — Citizens Upload Documents to Locker");
[
  ["riya",  "Aadhaar Card",    "1234-5678-9012", "UIDAI"],
  ["riya",  "PAN Card",        "ABCDE1234F",     "Income Tax Dept"],
  ["riya",  "Driving Licence", "DL-2023-56789",  "RTO Delhi"],
  ["arjun", "Passport",        "P1234567",       "Passport Seva"],
  ["arjun", "Voter ID",        "ABC1234567",     "Election Commission"],
  ["arjun", "Marksheet",       "CBSE-2022-88",   "CBSE Board"],
].forEach(([u, t, n, a]) => { const [s, m] = addDocument(u, t, n, a); s ? ok(m) : err(m); });

// ── STEP 4: Submit requests ────────────────────────────────────────────────
hdr("STEP 4 — Citizens Submit Document Requests");
[
  ["riya",  "Income Certificate", "Bank loan application",  "Tehsildar Office"],
  ["riya",  "Caste Certificate",  "College admission form", "District Collector"],
  ["arjun", "Birth Certificate",  "Passport renewal",       "Municipal Corp"],
  ["arjun", "Income Certificate", "Scholarship form",       "Tehsildar Office"],
].forEach(([u, t, p, a]) => { const [s, m] = createRequest(u, t, p, a); s ? ok(m) : err(m); });

// ── STEP 5: Officer views all documents ────────────────────────────────────
hdr("STEP 5 — Officer Views All Documents");
printDocuments(getAllDocuments());

// ── STEP 6: Officer verifies documents ────────────────────────────────────
hdr("STEP 6 — Officer Verifies / Rejects Documents");
const allDocs = getAllDocuments();
allDocs.forEach((doc, i) => {
  const [s, m] = i < 4
    ? verifyDocument(doc.doc_id, "priya_o", "Verified",  "Matches original records.")
    : verifyDocument(doc.doc_id, "priya_o", "Rejected",  "Blurry image / mismatch detected.");
  s ? ok(m) : err(m);
});

// ── STEP 7: Citizens check updated locker ─────────────────────────────────
hdr("STEP 7 — Riya's Document Locker (After Verification)");
printDocuments(getMyDocuments("riya"));

hdr("STEP 7b — Arjun's Document Locker (After Verification)");
printDocuments(getMyDocuments("arjun"));

// ── STEP 8: Officer views pending requests ─────────────────────────────────
hdr("STEP 8 — Officer Views Pending Requests");
printRequests(getPendingRequests());

// ── STEP 9: Officer resolves requests ─────────────────────────────────────
hdr("STEP 9 — Officer Resolves Requests");
getPendingRequests().forEach((req, i) => {
  const [s, m] = i % 2 === 0
    ? resolveRequest(req.req_id, "priya_o", "Approved", "Verified. Collect from office.")
    : resolveRequest(req.req_id, "priya_o", "Rejected", "Incomplete form. Please reapply.");
  s ? ok(m) : err(m);
});

// ── STEP 10: Citizens check request status ─────────────────────────────────
hdr("STEP 10 — Riya's Request Status");
printRequests(getMyRequests("riya"));

hdr("STEP 10b — Arjun's Request Status");
printRequests(getMyRequests("arjun"));

// ── STEP 11: Cancel a request ──────────────────────────────────────────────
hdr("STEP 11 — Riya Creates & Cancels a New Request");
const [s11, m11] = createRequest("riya", "Birth Certificate", "Testing cancellation", "Any Office");
s11 ? ok(m11) : err(m11);
const riyaReqs   = getMyRequests("riya");
const lastReqId  = riyaReqs[riyaReqs.length - 1].req_id;
const [s11b, m11b] = cancelRequest(lastReqId, "riya");
s11b ? ok(m11b) : err(m11b);

// ── STEP 12: Delete a document ─────────────────────────────────────────────
hdr("STEP 12 — Riya Deletes Her Driving Licence");
const dlDoc = getMyDocuments("riya").find(d => d.doc_type === "Driving Licence");
if (dlDoc) {
  const [s, m] = deleteDocument(dlDoc.doc_id, "riya");
  s ? ok(m) : err(m);
}

hdr("Riya's Locker After Deletion");
printDocuments(getMyDocuments("riya"));

console.log(SEP);
console.log("  ✅  DEMO COMPLETE — All features demonstrated!");
console.log("  To run the full interactive app: python main.py  (requires Python)");
console.log(SEP);
