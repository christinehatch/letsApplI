from phase5.proposal import Proposal

def get_mock_proposals():
    return [
        Proposal.create(
            text="This is an example AI-generated phrasing suggestion.",
            context="phrasing_suggestion"
        )
    ]

