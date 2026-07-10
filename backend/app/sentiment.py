import os
from typing import Any, TypedDict

# These settings must be applied before importing torch or transformers.
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from dotenv import load_dotenv
from transformers import pipeline


load_dotenv()


MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "distilbert/distilbert-base-uncased-finetuned-sst-2-english",
)


class SentimentResult(TypedDict):
    """
    Describes the result returned by analyze_sentiment().
    """

    label: str
    confidence: float


# At first, no model has been loaded.
_sentiment_pipeline: Any = None


def get_model_device() -> torch.device:
    """
    Choose the best available device.

    On an Apple Silicon Mac, use the MPS GPU.
    On other systems, fall back to the CPU.
    """

    if torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def load_sentiment_model() -> None:
    """
    Load the sentiment model into memory.

    This function should run once when FastAPI starts.
    """

    global _sentiment_pipeline

    # Do not load it again if it is already available.
    if _sentiment_pipeline is not None:
        return

    device = get_model_device()

    print(f"Loading sentiment model: {MODEL_NAME}")
    print(f"Using model device: {device}")

    _sentiment_pipeline = pipeline(
        task="sentiment-analysis",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        device=device,
    )

    print("Sentiment model loaded successfully.")


def analyze_sentiment(text: str) -> SentimentResult:
    """
    Analyze one English message.

    Returns a sentiment label and confidence score.
    """

    if _sentiment_pipeline is None:
        raise RuntimeError(
            "The sentiment model has not been loaded."
        )

    clean_text = text.strip()

    if not clean_text:
        raise ValueError("Cannot analyze an empty message.")

    raw_result = _sentiment_pipeline(
        clean_text,
        truncation=True,
    )[0]

    label = str(raw_result["label"]).upper()
    confidence = float(raw_result["score"])

    if label not in {"POSITIVE", "NEGATIVE"}:
        raise RuntimeError(
            f"Unexpected sentiment label: {label}"
        )

    return {
        "label": label,
        "confidence": confidence,
    }