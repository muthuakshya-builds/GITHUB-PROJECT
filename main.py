"""Event Registration Cleaner - LLM extraction + deterministic Python validation.

Run:
  python main.py --demo
  python main.py --input registrations.csv

For live extraction, set GEMINI_API_KEY in your environment and install requirements.
The Gemini adapter is isolated in extract_with_llm(); replace it if your Week 12
course API uses a different provider. Never put an API key in this file.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ALLOWED_BRANCHES = {"CSE", "IT", "AIDS", "ECE", "EEE", "MECH", "CIVIL"}
FIELDS = ("name", "phone", "email", "year", "branch")


def read_entry(row: dict[str, str]) -> tuple[str, str]:
    """Return registration ID and original unmodified entry text."""
    return (str(row.get("id", "")).strip(), str(row.get("entry", "")).strip())


def extraction_prompt(entry: str) -> str:
    """Build the five-role structured extraction instruction."""
    return f"""
AUTHORITY: You extract registration facts. Never invent, infer, repair, or improve contact details.
EXEMPLAR: Return exactly this JSON shape:
{{"name":"Priya K","phone":"9840012345","email":"PRIYA.K@gmail.com","year":2,"branch":"CSE"}}
CONSTRAINT: phone must contain only digits copied from the entry, with spaces, hyphens and a leading + removed.
Do not add/remove/change digits. Email must be copied exactly as written. If an email is written in words
such as 'at' or 'dot', return null. Use null for missing values. Year must be integer 1-4 or null.
Branch must be one of CSE, IT, AIDS, ECE, EEE, MECH, CIVIL, other, or null.
RUBRIC: Every non-null value must be directly supported by the entry. Do not guess.
METADATA: Output one JSON object only, with keys name, phone, email, year, branch. No markdown.
ENTRY: {entry}
""".strip()


def extract_with_llm(entry: str) -> dict[str, Any]:
    """Extract fields with Gemini. Raises a clear error if API setup is missing."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Use --demo for local testing, or configure "
            "the Week 12 API adapter and environment variable."
        )
    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError("Install dependencies with: pip install -r requirements.txt") from exc

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=extraction_prompt(entry),
        config={"response_mime_type": "application/json"},
    )
    data = json.loads(response.text)
    if not isinstance(data, dict):
        raise ValueError("LLM response was not a JSON object.")
    return {field: data.get(field) for field in FIELDS}


def extract_demo(entry: str) -> dict[str, Any]:
    """Small deterministic extractor for offline demonstration and test runs."""
    result = {field: None for field in FIELDS}
    # Name: look for explicit Name: label or first segment before common separators.
    m = re.search(r"\bname\s*:\s*([^,|;]+)", entry, re.I)
    if m:
        result["name"] = m.group(1).strip()
    else:
        first = re.split(r"\s*[|;]\s*|\s+-\s+|,\s*(?:ph|phone|mobile|email)\b", entry, maxsplit=1, flags=re.I)[0]
        first = re.sub(r"^(?:registration|name)\s*:\s*", "", first, flags=re.I)
        if not re.search(r"\d", first) and len(first.split()) <= 5:
            result["name"] = first.strip(" ,:-")

    # Phone: take a digit run/sequence with separators, but don't fabricate digits.
    m = re.search(r"(?:ph(?:one)?|mobile|mob|contact)\s*[:=]?\s*(\+?[\d][\d\s-]{7,}\d)", entry, re.I)
    if not m:
        m = re.search(r"(\+91[\s-]?)?\d{5}[\s-]?\d{5}", entry)
    if m:
        result["phone"] = re.sub(r"\D", "", m.group(0))

    # Email only if written in conventional email form.
    m = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", entry, re.I)
    if m:
        result["email"] = m.group(0)

    year_patterns = [
        (r"\b(?:1st|first|I)\s*year\b", 1),
        (r"\b(?:2nd|second|II)\s*year\b", 2),
        (r"\b(?:3rd|third|III)\s*year\b", 3),
        (r"\b(?:4th|fourth|IV|final)\s*year\b", 4),
    ]
    for pattern, year in year_patterns:
        if re.search(pattern, entry, re.I):
            result["year"] = year
            break

    for branch in sorted(ALLOWED_BRANCHES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(branch)}\b", entry, re.I):
            result["branch"] = branch
            break
    if result["branch"] is None and re.search(r"\b(?:MECH|CIVIL|AIDS)\b", entry, re.I):
        result["branch"] = "other"
    return result


def check_facts(entry: str, extracted: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Reject extracted phone/email values not supported by the original entry."""
    checked = dict(extracted)
    problems = []
    raw_digits = re.sub(r"\D", "", entry)
    phone = checked.get("phone")
    if phone is not None:
        phone_digits = re.sub(r"\D", "", str(phone))
        if not phone_digits or phone_digits not in raw_digits:
            checked["phone"] = None
            problems.append("phone failed source fact-check")
    email = checked.get("email")
    if email is not None:
        email_text = str(email).strip()
        if email_text.lower() not in entry.lower():
            checked["email"] = None
            problems.append("email failed source fact-check")
    return checked, problems


def clean_phone(value: Any) -> str | None:
    if value is None:
        return None
    digits = re.sub(r"\D", "", str(value))
    if digits.startswith("91") and len(digits) > 10:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) > 10:
        digits = digits[1:]
    if len(digits) == 10 and digits[0] in "6789":
        return digits
    return None


def clean_email(value: Any) -> str | None:
    if value is None:
        return None
    email = str(value).strip().lower()
    if " " in email or email.count("@") != 1:
        return None
    local, domain = email.split("@")
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        return None
    if not re.fullmatch(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", email):
        return None
    return email


def clean(extracted: dict[str, Any]) -> dict[str, Any]:
    """Apply deterministic formatting and validation transformations."""
    name = extracted.get("name")
    if name is not None:
        name = " ".join(str(name).split()).title()
    year = extracted.get("year")
    try:
        year = int(year) if year is not None else None
    except (TypeError, ValueError):
        year = None
    branch = extracted.get("branch")
    if branch is not None:
        branch = str(branch).strip().upper()
        if branch not in ALLOWED_BRANCHES:
            branch = "other"
    return {
        "name": name,
        "phone": clean_phone(extracted.get("phone")),
        "email": clean_email(extracted.get("email")),
        "year": year if year in {1, 2, 3, 4} else None,
        "branch": branch,
    }


def is_valid(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return validity and field-level reasons."""
    reasons = []
    if not record.get("name"):
        reasons.append("missing name")
    if not record.get("phone"):
        reasons.append("missing or invalid phone")
    if not record.get("email"):
        reasons.append("missing or invalid email")
    if record.get("year") not in {1, 2, 3, 4}:
        reasons.append("missing or invalid year")
    if record.get("branch") in (None, "other"):
        reasons.append("missing or unsupported branch")
    return not reasons, reasons


def process(rows: list[dict[str, str]], demo: bool = False) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract, fact-check, clean, validate and deduplicate every registration."""
    seen_phone: dict[str, str] = {}
    seen_email: dict[str, str] = {}
    all_results = []
    problem_results = []

    for row in rows:
        reg_id, original = read_entry(row)
        try:
            extracted = extract_demo(original) if demo else extract_with_llm(original)
            extracted, fact_issues = check_facts(original, extracted)
            cleaned = clean(extracted)
            valid, reasons = is_valid(cleaned)
            reasons = fact_issues + reasons

            duplicate_of = None
            phone = cleaned.get("phone")
            email = cleaned.get("email")
            if phone and phone in seen_phone:
                duplicate_of = seen_phone[phone]
            elif email and email in seen_email:
                duplicate_of = seen_email[email]

            if duplicate_of:
                status = "duplicate"
                reasons.append(f"duplicate of {duplicate_of}")
            elif valid and not fact_issues:
                status = "valid"
            else:
                status = "needs_fix"

            # First occurrence owns each usable identifier, even if another field needs review.
            if phone and phone not in seen_phone:
                seen_phone[phone] = reg_id
            if email and email not in seen_email:
                seen_email[email] = reg_id

            result = {"id": reg_id, **cleaned, "status": status, "reasons": "; ".join(reasons),
                      "duplicate_of": duplicate_of, "original_entry": original}
        except Exception as exc:
            result = {"id": reg_id, **{f: None for f in FIELDS}, "status": "needs_fix",
                      "reasons": f"extraction/processing error: {exc}", "duplicate_of": None,
                      "original_entry": original}
        all_results.append(result)
        if result["status"] != "valid":
            problem_results.append(result)
    return all_results, problem_results


def write_reports(results: list[dict[str, Any]], problems: list[dict[str, Any]], output_dir: str = ".") -> None:
    """Write the three required reports."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    valid_fields = ["id", "name", "phone", "email", "year", "branch"]
    with (out / "clean_list.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=valid_fields)
        writer.writeheader()
        for row in results:
            if row["status"] == "valid":
                writer.writerow({k: row.get(k) for k in valid_fields})

    problem_fields = ["id", "status", "reasons", "duplicate_of", "original_entry",
                      "name", "phone", "email", "year", "branch"]
    with (out / "problems.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=problem_fields)
        writer.writeheader()
        for row in problems:
            writer.writerow({k: row.get(k) for k in problem_fields})

    counts = Counter(row["status"] for row in results)
    branch_counts = Counter(row["branch"] for row in results if row["status"] == "valid")
    year_counts = Counter(row["year"] for row in results if row["status"] == "valid")
    lines = [
        "EVENT REGISTRATION CLEANING SUMMARY",
        f"Total entries: {len(results)}",
        f"Valid: {counts.get('valid', 0)}",
        f"Needs fix: {counts.get('needs_fix', 0)}",
        f"Duplicates: {counts.get('duplicate', 0)}",
        "",
        "Valid registrations by branch:",
    ]
    lines.extend(f"  {key}: {value}" for key, value in sorted(branch_counts.items()))
    lines += ["", "Valid registrations by year:"]
    lines.extend(f"  Year {key}: {value}" for key, value in sorted(year_counts.items()))
    (out / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_csv(path: str) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not {"id", "entry"}.issubset(reader.fieldnames or []):
            raise ValueError("Input CSV must contain columns: id,entry")
        return list(reader)


def main() -> None:
    parser = argparse.ArgumentParser(description="Event Registration Cleaner")
    parser.add_argument("--input", default="registrations.csv")
    parser.add_argument("--output", default="output")
    parser.add_argument("--demo", action="store_true", help="Use local demo extractor, no API call")
    args = parser.parse_args()
    rows = load_csv(args.input)
    results, problems = process(rows, demo=args.demo)
    write_reports(results, problems, args.output)
    print(f"Processed {len(results)} entries.")
    print(f"Valid: {sum(r['status']=='valid' for r in results)}")
    print(f"Needs fix: {sum(r['status']=='needs_fix' for r in results)}")
    print(f"Duplicates: {sum(r['status']=='duplicate' for r in results)}")
    print(f"Reports saved in: {args.output}/")


if __name__ == "__main__":
    main()
