class InterpretationNotAuthorizedError(Exception):
    """
    Raised when interpretation is attempted without proper authorization
    or without a valid Phase 5.1-derived input.
    """
    pass


class InvalidInputSourceError(Exception):
    """
    Raised when interpretation input does not originate
    from a valid Phase 5.1 ReadResult.
    """
    pass
class Phase52ValidationError(Exception):
    """
    Raised when Phase 5.2 output violates schema or structural constraints.
    """

    def __init__(self, reason_code: str, violation_detail: str, raw_excerpt: str = ""):
        self.reason_code = reason_code
        self.violation_detail = violation_detail
        self.raw_excerpt = raw_excerpt
        super().__init__(f"{reason_code}: {violation_detail}")