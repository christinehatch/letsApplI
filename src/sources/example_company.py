from datetime import datetime, timedelta

def fetch_jobs():
    now = datetime.now()
    return [
        {
            "source": "ExampleCo Careers",
            "source_job_id": "product-eng-001",  # ← REQUIRED
            "title": "Example Product Engineer",
            "company": "ExampleCo",
            "location": "Remote",
            "first_seen_at": now - timedelta(hours=4),
            "referral": None,
        }
    ]
