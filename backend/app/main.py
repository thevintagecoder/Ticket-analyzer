from fastapi import FastAPI

app = FastAPI(
    title="Ticket analyzer API",
    description="Backend API for the ticket analyzer project",
    version= "0.1.0",
)

@app.get("/")
def read_root()-> dict[str, str]:
    return {"message": "Ticket Analyser API is running"}


@app.get("/health")
def health_check()-> dict[str, str]:
    return {"status:ok"}
