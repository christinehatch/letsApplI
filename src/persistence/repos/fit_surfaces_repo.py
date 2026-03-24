from dataclasses import dataclass
from persistence.errors import InterpretationNotFoundError
from sqlite3 import IntegrityError


@dataclass(frozen=True)
class FitSurfaceRecord:
    id: int
    job_id: int
    interpretation_id: int
    fit_surface_hash: str
    algorithm_version: str
    algorithm_config_hash: str
    surface_json: str
    created_at: str


class FitSurfaceRepo:

    def __init__(self, conn):
        self.conn = conn

    def create_fit_surface(
        self,
        job_id: int,
        interpretation_id: int,
        fit_surface_hash: str,
        algorithm_version: str,
        algorithm_config_hash: str,
        surface_json: str,
        created_at: str,
    ) -> FitSurfaceRecord:

        interp = self.conn.execute(
            "SELECT job_id FROM interpretations WHERE id = ?",
            (interpretation_id,),
        ).fetchone()

        if not interp:
            raise InterpretationNotFoundError()

        if interp["job_id"] != job_id:
            raise IntegrityError("ArtifactMismatchError")

        self.conn.execute(
            """
            INSERT INTO fit_surfaces (
                job_id, interpretation_id,
                fit_surface_hash,
                algorithm_version, algorithm_config_hash,
                surface_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(interpretation_id, fit_surface_hash) DO NOTHING
            """,
            (
                job_id,
                interpretation_id,
                fit_surface_hash,
                algorithm_version,
                algorithm_config_hash,
                surface_json,
                created_at,
            ),
        )

        row = self.conn.execute(
            """
            SELECT * FROM fit_surfaces
            WHERE interpretation_id = ? AND fit_surface_hash = ?
            """,
            (interpretation_id, fit_surface_hash),
        ).fetchone()

        return FitSurfaceRecord(**row)
