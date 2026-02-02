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
