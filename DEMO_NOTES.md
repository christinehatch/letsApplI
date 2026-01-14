# letsA(ppl)I — Demo Notes

This project demonstrates a human-in-the-loop approach to application support.

The demo focuses on:
- Explicit prioritization rules
- Transparency of reasoning
- Reduction of cognitive load without automation

This demo does not show:
- Live scraping
- AI-generated advice
- Automated submissions

Those are intentional omissions.

## How to Demo letsA(ppl)I (v0)

This is a **v0 decision-support prototype**, not a finished product.

**What it demonstrates:**
- How job listings can be prioritized using explicit, inspectable rules
- How same-day postings are surfaced without black-box AI
- How outputs are designed for *human review*, not auto-application

**How to run the demo:**
1. Open `src/job_data.py` to see sample job inputs
2. Run `python src/generate_daily_output.py`
3. Review the generated `DAILY_OUTPUT.md`
4. Walk through *why* each job appears where it does

**What this demo intentionally does NOT show:**
- No scraping
- No auto-apply
- No personalization claims
- No AI agents acting on the user’s behalf

This demo exists to prove **scope discipline and human-in-the-loop design**, not automation.

