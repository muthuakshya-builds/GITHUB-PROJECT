# Event Registration Cleaner

A Python tool that extracts event registration details from messy text entries, checks every extracted fact against the original text, cleans valid formats, detects duplicates, and writes review reports.

## Important design rule

**LLM extracts. Python verifies and decides. Humans resolve uncertain records.**

The program never invents or silently corrects a phone number or email address.

## Project files

- `main.py` — required Python functions, LLM adapter, validation and report generation
- `registrations.csv` — sample input with 20 entries
- `system_prompt.txt` — five-role prompt framework
- `tests/` — evaluation and red-team cases
- `docs/` — specification, judgment framework, cost note, AI journal and reflection template
- `.env.example` — safe environment-variable template
- `.gitignore` — excludes secrets and generated files

## Requirements

- Python 3.10+
- For live LLM extraction: install `requirements.txt` and configure the Week 12 API key.
- This starter adapter uses Google Gemini (`google-genai`). If your Week 12 class API is different, replace only `extract_with_llm()` in `main.py` with the course-approved API call. Keep the JSON contract and Python validation unchanged.

## Run offline

```bash
python main.py --demo
```

This uses a basic local demonstration extractor and does not make an API call. It is for checking the workflow only; final LLM assessment evidence must use the approved Week 12 API.

## Run with the LLM

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set `GEMINI_API_KEY` as an environment variable. Do not paste it into `main.py`, `system_prompt.txt`, GitHub, or screenshots.
3. Run:

```bash
python main.py
```

Optional input/output paths:

```bash
python main.py --input registrations.csv --output output
```

## Generated reports

- `output/clean_list.csv` — valid registrations only
- `output/problems.csv` — records needing human review, with reasons and original entry
- `output/summary.txt` — counts and valid registrations by branch and year

## Safety and limitations

- The local demo extractor is intentionally simple and is not a substitute for the LLM.
- An LLM extraction error is marked `needs_fix`; it is not silently treated as valid.
- The team must contact registrants to resolve missing or invalid details.
- Similar names alone are not confirmed duplicates. The required duplicate rule uses cleaned phone or email.
