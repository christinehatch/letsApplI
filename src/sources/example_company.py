def fetch_jobs():
    """
    V1 source adapter.
    Returns jobs in the standard internal format.
    """
    return [
        {
            "title": "Example Product Engineer",
            "company": "ExampleCo",
            "location": "Remote",
            "source": "ExampleCo Careers",
            "first_seen_hours_ago": 4,
            "referral": None,
        }
    ]
