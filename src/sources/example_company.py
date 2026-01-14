from datetime import datetime, timedelta

def fetch_jobs():
    now = datetime.now()
    return [
        {
            "title": "Example Product Engineer",
            "company": "ExampleCo",
            "location": "Remote",
            "source": "ExampleCo Careers",
            "first_seen_at": now - timedelta(hours=4),
            "referral": None,
        }
    ]
