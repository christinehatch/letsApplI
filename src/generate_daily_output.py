"""
v0: Generate a daily, prioritized job feed from predefined inputs.
This script is intentionally read-only and rule-based.
"""

from datetime import datetime
from job_data import jobs
# Fake job data (this will later be replaced by real sources)
def is_high_priority(job):
    return (
        job["first_seen_hours_ago"] <= 24
        and "Engineer" in job["title"]
    )
def is_medium_priority(job):
    return job["first_seen_hours_ago"] <= 24

def is_low_priority(job):
    return job["first_seen_hours_ago"] > 24

def build_reasons(job):
    reasons = []

    if job["first_seen_hours_ago"] <= 24:
        reasons.append("Posted today")

    if "Engineer" in job["title"]:
        reasons.append("Matches core role keyword")

    if job.get("referral"):
        reasons.append("Referral connection exists")

    return reasons
def format_job(job):
    lines = [
        f"**{job['title']}**",
        f"- Company: {job['company']}",
        f"- Location: {job['location']}",
        f"- Source: {job['source']}",
        f"- First seen: {job['first_seen_hours_ago']} hours ago",
    ]

    reasons = build_reasons(job)
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

    high = [j for j in jobs if is_high_priority(j)]
    medium = [j for j in jobs if is_medium_priority(j) and j not in high]
    low = [j for j in jobs if is_low_priority(j)]

    lines = [
        "# letsA(ppl)I — Daily Job Feed",
        f"Date: {today}",
        "",
        "## 🔥 New Today (High Priority)",
        "_Posted today and matches core role signals._",
        "",
    ]

    if not high:
        lines.append("_No high-priority jobs today._\n")

    for job in high:
        lines.extend(format_job(job))

    lines.extend([
        "",
        "## 🟡 New but Lower Priority",
        "",
        "",
        "_Posted today but with weaker signals._",
        "",
    ])

    if not medium:
        lines.append("_No medium-priority jobs today._\n")

    for job in medium:
        lines.extend(format_job(job))

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
        lines.extend(format_job(job))

    return "\n".join(lines)
if __name__ == "__main__":
    output = generate_markdown(jobs)
    with open("DAILY_OUTPUT.md", "w") as f:
        f.write(output)

    print("Generated DAILY_OUTPUT.md")

