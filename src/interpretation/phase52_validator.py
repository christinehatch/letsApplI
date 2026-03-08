class Phase52Validator:

    REQUIRED_KEYS = [
        "role_summary",
        "capability_domains",
        "requirement_analysis",
        "project_signals",
    ]

    def validate(self, interpretation: dict) -> dict:

        if not isinstance(interpretation, dict):
            raise ValueError("Interpretation must be a dictionary")

        for key in self.REQUIRED_KEYS:
            if key not in interpretation:
                raise ValueError(f"Missing required field: {key}")

        role_summary = interpretation["role_summary"]

        if not isinstance(role_summary, dict):
            raise ValueError("role_summary must be an object")

        if "title" not in role_summary or "summary" not in role_summary:
            raise ValueError("role_summary must contain title and summary")

        if not isinstance(role_summary["title"], str):
            raise ValueError("role_summary.title must be a string")

        if not isinstance(role_summary["summary"], str):
            raise ValueError("role_summary.summary must be a string")

        for field in [
            "capability_domains",
            "requirement_analysis",
            "project_signals",
        ]:

            if not isinstance(interpretation[field], list):
                raise ValueError(f"{field} must be a list")

        return interpretation
