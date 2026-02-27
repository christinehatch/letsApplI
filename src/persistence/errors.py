# src/persistence/errors.py

class PersistenceError(Exception):
    pass


class JobNotFoundError(PersistenceError):
    pass


class HydrationNotFoundError(PersistenceError):
    pass


class InterpretationNotFoundError(PersistenceError):
    pass


class ArtifactMismatchError(PersistenceError):
    pass


class InvalidHashError(PersistenceError):
    pass


class IllegalTransitionError(PersistenceError):
    pass
