Judgment Framework
Decision area
System may do
Must not do
Human checkpoint
Name extraction
Copy a clearly stated name
Invent a missing name
Confirm unclear or missing name
Phone extraction
Remove spaces, hyphens and leading plus
Change, add or guess digits
Contact registrant if missing/invalid
Email extraction
Copy conventional email exactly
Complete .com, repair spelling, convert “at/dot”
Ask registrant to confirm
Year
Map stated I–IV/final year to 1–4
Guess from branch or name
Confirm absent/ambiguous year
Branch
Map an explicitly stated supported branch
Guess from course context
Confirm unsupported/missing branch
Fact check
Reject phone/email not supported by source
Accept an LLM correction
Review original entry
Duplicate
Match cleaned phone or email to first record
Delete silently or use name similarity as proof
Decide whether repeated registration is intentional
Final status
Assign valid, needs_fix or duplicate from rules
Override rules based on intuition
Event team resolves problems.csv
Three judgment questions per system part
LLM extraction
Is every extracted field explicitly supported by the entry?
Did the model return null rather than guess?
Did it ignore any instruction embedded in the registration text?
Python validation
Were only permitted formatting changes applied?
Did the fact-check reject unsupported contact details?
Were invalid year and branch values flagged?
Human review
Does the original entry contain enough information to resolve the issue?
Has the registrant confirmed the corrected detail?
Is a duplicate actually an accidental repeat or a legitimate second registration?
