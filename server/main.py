from celery.result import AsyncResult
from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from server.worker import create_task


app = FastAPI()

@app.post("/execute", status_code=201)
def run_task(payload = Body(...)):
    # task_type = payload["type"]
    task = create_task.delay("experiment")
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)
