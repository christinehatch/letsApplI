from datetime import datetime, timedelta

def fetch_jobs():
    now = datetime.now()
    return [
        {
            "source": "ExampleBoard",
            "source_job_id": "backend-001",  # ← REQUIRED (explicit, stable)
            "title": "Backend Engineer",
            "company": "BoardCo",
            "location": "Hybrid",
            "first_seen_at": now - timedelta(hours=10),
            "referral": None,
        }
    ]
