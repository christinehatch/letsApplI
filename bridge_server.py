import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

# Adds the project root to the Python path so 'src' is discoverable
sys.path.append(os.path.join(os.getcwd(), "src"))

from ui.read_job import read_job_for_ui, get_fetcher
from phase5.phase5_1.types import ConsentPayload
from phase5.phase5_2.interpreter import Phase52Interpreter
from phase5.phase5_2.types import InterpretationInput

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class HandoffPayload(BaseModel):
    job_id: str
    consent: dict
    request_to_fetch: bool = False # NEW: Accept the fetch flag

@app.post("/api/read-job")
async def handle_read_job(payload: HandoffPayload):
    try:
        # 1. Phase 5.1: Process Authority
        # We pass the scope "hydrate" directly to the ConsentPayload
        consent = ConsentPayload(
            job_id=payload.job_id,
            scope=payload.consent["scope"],  # This will be "hydrate"
            granted_at=datetime.fromisoformat(payload.consent["granted_at"].replace("Z", "+00:00")),
            revocable=payload.consent["revocable"]
        )

        fetcher = get_fetcher(consent.job_id)
        read_result = read_job_for_ui(consent, fetcher)

        # 2. Principled Routing
        # If the scope is "hydrate", we MUST return early.
        # The interpreter is physically prevented from running.
        if consent.scope == "hydrate" or payload.request_to_fetch:
            print(f">>> Phase 5.1 HYDRATE Authority for {payload.job_id}")
            return {
                "job_id": read_result.job_id,
                "content": read_result.content,
                "requirements": [],
                "availability": read_result.source.availability
            }

        # 3. Phase 5.2: Invoke Interpreter (Intelligence)
        # This only runs if request_to_fetch is False
        interpreter = Phase52Interpreter()
        interpretation_input = InterpretationInput(
            job_id=read_result.job_id,
            raw_content=read_result.content,
            read_at=read_result.read_at
        )

        interpreter.set_input(interpretation_input)
        interpretation_result = interpreter.interpret()

        return {
            "job_id": read_result.job_id,
            "content": read_result.content,
            "requirements": interpretation_result.artifacts.get("requirements", []),
            "availability": read_result.source.availability
        }
    except Exception as e:
        print(f"Bridge Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)