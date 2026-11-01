One-Page Specification — Event Registration Cleaner
Domain: Events | Application: Individual, console-based Python tool
Problem
Event teams receive registrations through forms and informal messages. Entries may contain inconsistent separators, missing fields, invalid contact details, and repeated submissions. Manually consolidating them is slow and can introduce dangerous contact-detail errors.
Input
One UTF-8 CSV file named registrations.csv, with columns id,entry and at least 20 registration entries. Each entry is original text; quoted CSV fields may contain commas.
Extraction contract
An LLM extracts name, phone, email, year, and branch into one JSON object. Missing or uncertain values are null. Phone formatting may remove spaces, hyphens and a leading plus only; no digit may be added, removed or changed. Email is copied as written; email written in words such as “at” or “dot” becomes null. Year is 1–4; “final year” means 4 and I–IV map to 1–4. Branch is CSE, IT, AIDS, ECE, EEE, MECH, CIVIL, other, or null.
Python verification and cleaning
Python checks that returned phone digits and email text are supported by the original entry. It title-cases names and collapses repeated spaces; removes permitted phone separators and optional leading 91 or 0 before validating a 10-digit number starting 6/7/8/9; lowercases and validates email; validates year 1–4 and branch. Unsupported branch becomes other.
Duplicate and status rules
After cleaning, a record is a duplicate if its cleaned phone OR cleaned email has appeared earlier. It is linked to the first matching registration. Status is duplicate, needs_fix, or valid. A record with missing/invalid fields or a failed fact check needs human review. Duplicates are reported, not silently deleted.
Outputs
clean_list.csv: valid records only.
problems.csv: every needs_fix or duplicate record, with reasons and original entry.
summary.txt: status counts and valid registrations grouped by branch and year.
Human checkpoint
The event team reviews problems.csv and contacts registrants to confirm or correct details. The program never guesses or contacts people automatically.
Required functions
read_entry(), is_valid(), check_facts(), clean_phone(), clean_email(), clean(), process(), write_reports().
Approval gate: Faculty must approve this specification and the input dataset before implementation is treated as final.
