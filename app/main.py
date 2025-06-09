from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes

# Create FastAPI instance
app = FastAPI(
    title="Wasserstoff AI Internship Backend",
    description="Document Question Answering + Theme Detection System",
    version="1.0.0"
)

# Allow requests from frontend (Streamlit or others)
origins = [
    "http://localhost",
    "http://localhost:8501",  # Streamlit default
    "http://127.0.0.1:8501",
    "*"  # Optional: allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use ["*"] only in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(routes.router)

# Optional: Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Wasserstoff AI Backend API"}

