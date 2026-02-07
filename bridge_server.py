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


@app.post("/api/read-job")
async def handle_read_job(payload: HandoffPayload):
    try:
        # 1. Phase 5.1: Process Consent
        ts_str = payload.consent["granted_at"].replace("Z", "+00:00")
        consent = ConsentPayload(
            job_id=payload.job_id,
            scope=payload.consent["scope"],
            granted_at=datetime.fromisoformat(ts_str),
            revocable=payload.consent["revocable"]
        )

        # Inside bridge_server.py -> handle_read_job
        print(f"\n>>> BRIDGE CALL: Job ID {payload.job_id}")

        fetcher = get_fetcher(consent.job_id)
        read_result = read_job_for_ui(consent, fetcher)

        # ADD THIS LINE:
        print(f">>> HYDRATION RESULT: '{read_result.content[:30]}...' (Length: {len(read_result.content or '')})")
        # REFINEMENT: If content is missing, return early or handle gracefully
        if not read_result.content:
            return {
                "job_id": read_result.job_id,
                "content": "Job content is currently unavailable.",
                "requirements": [],
                "availability": read_result.source.availability
            }
        # 3. Phase 5.2: Invoke Interpreter
        # This takes the output of 5.1 and feeds it into the 5.2 contract
        interpreter = Phase52Interpreter()
        interpretation_input = InterpretationInput(
            job_id=read_result.job_id,
            raw_content=read_result.content,
            read_at=read_result.read_at
        )

        # Inside handle_read_job in bridge_server.py
        interpreter.set_input(interpretation_input)
        interpretation_result = interpreter.interpret()

        return {
            "job_id": read_result.job_id,
            "content": read_result.content,
            # Map the artifact list to the UI's expected key
            "requirements": interpretation_result.artifacts.get("requirements", []),
            "availability": read_result.source.availability
        }
    except Exception as e:
        print(f"Bridge Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)