from datetime import datetime, timedelta

def fetch_jobs():
    now = datetime.now()
    return [
        {
            "title": "Backend Engineer",
            "company": "BoardCo",
            "location": "Hybrid",
            "source": "ExampleBoard",
            "first_seen_at": now - timedelta(hours=10),
            "referral": None,
        }
    ]
