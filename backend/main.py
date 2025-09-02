from fastapi import FastAPI
from backend.api import router
from backend.utils.startup_checker import run_backend_startup_checks

# Run backend startup checks
run_backend_startup_checks()

app = FastAPI()

app.include_router(router)
