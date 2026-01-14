def fetch_jobs():
    """
    V1.1 source adapter.
    Mimics a job board feed.
    """
    return [
        {
            "title": "Backend Engineer",
            "company": "BoardCo",
            "location": "Hybrid",
            "source": "ExampleBoard",
            "first_seen_hours_ago": 10,
            "referral": None,
        }
    ]

