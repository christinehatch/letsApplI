class Phase51Error(Exception):
    """Base error for all Phase 5.1 failures."""
    pass


class NotAuthorizedError(Phase51Error):
    """Raised when read is attempted without valid consent."""
    pass


class InvalidScopeError(Phase51Error):
    """Raised when consent scope is missing or incorrect."""
    pass


class ConsentRevokedError(Phase51Error):
    """Raised when consent is revoked during execution."""
    pass


class SourceUnavailableError(Phase51Error):
    """Raised when the job source is blocked or unavailable."""
    pass

