from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db
from .sentiment import analyze_sentiment, load_sentiment_model
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Run setup code when FastAPI starts.
    """

    # Create database tables if they do not already exist.
    Base.metadata.create_all(bind=engine)

    # Load the AI sentiment model once during startup.
    load_sentiment_model()

    yield


app = FastAPI(
    title="Ticket Analyzer API",
    description="Backend API for the Ticket Analyzer project.",
    version="0.4.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    """
    Confirm that the Ticket Analyzer API is running.
    """

    return {
        "message": "Ticket Analyzer API is running"
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """
    Confirm that FastAPI and PostgreSQL are available.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable",
        ) from error

    return {
        "status": "ok"
    }


@app.post(
    "/tickets",
    response_model=schemas.TicketResponse,
    status_code=201,
)
def create_ticket(
    ticket_data: schemas.TicketCreate,
    db: Session = Depends(get_db),
):
    """
    Analyze the ticket message and save the result in PostgreSQL.
    """

    # Send the ticket message to the AI model.
    try:
        sentiment_result = analyze_sentiment(
            ticket_data.message
        )

    except (RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail="Could not analyze ticket sentiment",
        ) from error

    # Create a database object using the real AI result.
    new_ticket = models.Ticket(
        title=ticket_data.title,
        message=ticket_data.message,
        category=ticket_data.category,
        sentiment=sentiment_result["label"],
        confidence=sentiment_result["confidence"],
    )

    # Save the ticket in PostgreSQL.
    try:
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Could not save the ticket",
        ) from error

    return new_ticket


@app.get(
    "/tickets",
    response_model=list[schemas.TicketResponse],
)
def get_tickets(
    db: Session = Depends(get_db),
):
    """
    Return all saved tickets, with the newest ticket first.
    """

    try:
        statement = select(models.Ticket).order_by(
            models.Ticket.created_at.desc()
        )

        tickets = db.scalars(statement).all()

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve tickets",
        ) from error

    return tickets