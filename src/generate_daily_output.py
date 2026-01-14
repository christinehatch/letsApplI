"""
v1.1: Generate a daily, prioritized job feed from multiple source adapters.
This script is intentionally read-only and rule-based.
"""


from datetime import datetime
from sources.example_company import fetch_jobs as fetch_company_jobs
from sources.example_board import fetch_jobs as fetch_board_jobs

def hours_since(first_seen_at, now):
    delta = now - first_seen_at
    return int(delta.total_seconds() // 3600)

jobs = fetch_company_jobs() + fetch_board_jobs()
# Input data composed from source adapters
def is_high_priority(job, now):
    return hours_since(job["first_seen_at"], now) <= 24 and "Engineer" in job["title"]
def is_medium_priority(job, now):
    return hours_since(job["first_seen_at"], now) <= 24

def is_low_priority(job, now):
    return hours_since(job["first_seen_at"], now) > 24
def build_reasons(job, now):
    reasons = []

    if job["first_seen_at"].date() == now.date():
        reasons.append("First seen today")

    if "Engineer" in job["title"]:
        reasons.append("Matches core role keyword")

    if job.get("referral"):
        reasons.append("Referral connection exists")

    return reasons

def format_job(job, now):
    first_seen_at = job["first_seen_at"]
    hours_ago = hours_since(first_seen_at, now)

    lines = [
        f"**{job['title']}**",
        f"- Company: {job['company']}",
        f"- Location: {job['location']}",
        f"- Source: {job['source']}",
        f"- First seen: {hours_ago} hours ago (first seen at {first_seen_at.strftime('%I:%M %p')})",
    ]

    reasons = build_reasons(job, now)
    if reasons:
        lines.append("- Why this is here:")
        for r in reasons:
            lines.append(f"  - {r}")

    if job.get("referral"):
        lines.append(f"- Referral signal: {job['referral']}")

    lines.append("")
    return lines

def generate_markdown(jobs):
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now()

    high = [j for j in jobs if is_high_priority(j, now)]
    medium = [j for j in jobs if is_medium_priority(j, now) and j not in high]
    low = [j for j in jobs if is_low_priority(j, now)]

    lines = [
        f"Date: {today}",
        "",
        "## 🔥 New Today (High Priority)",
        "_First seen today and matches core role signals._",
        "",
    ]

    if not high:
        lines.append("_No high-priority jobs today._\n")

    for job in high:
        lines.extend(format_job(job, now))

    lines.extend([
        "",
        "## 🟡 New but Lower Priority",
        "",
        "",
        "_First seen today but with weaker signals._",
        "",
    ])

    if not medium:
        lines.append("_No medium-priority jobs today._\n")

    for job in medium:
        lines.extend(format_job(job, now))

    lines.extend([
        "",
        "## 🧊 Skipped / Deprioritized",
        "",
        "",
        "_Older postings or out-of-scope roles._",
        "",

    ])

    if not low:
        lines.append("_No deprioritized jobs today._\n")


    for job in low:
        lines.extend(format_job(job, now))


    return "\n".join(lines)
if __name__ == "__main__":
    output = generate_markdown(jobs)
    with open("DAILY_OUTPUT.md", "w") as f:
        f.write(output)

    print("Generated DAILY_OUTPUT.md")

