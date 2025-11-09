import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
COURSE_MATERIALS_DIR = DATA_DIR / "course_materials"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

# Vector database settings
CHROMA_DB_PATH = str(PROCESSED_DATA_DIR / "chroma_db")
COLLECTION_NAME = "network_security_course"

# Embedding model settings
EMBEDDING_MODEL = "multi-qa-MiniLM-L6-cos-v1"
CHUNK_SIZE = 1000  # Number of words per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks for better context
EMBEDDING_BATCH_SIZE = 128  # Optimized batch size for faster encoding (default was 32)

# GPT4All settings
LLM_MODEL_NAME = "mistral-7b-openorca.gguf2.Q4_0.gguf"  # Fallback if Gemma not available
MODEL_PATH = str(MODELS_DIR)
MAX_TOKENS = 512
TEMPERATURE = 0.1

# UI settings
APP_TITLE = "OnDemand Tutor Q&A Agent"
APP_DESCRIPTION = "Network Security Course Assistant"

# Processing settings
SUPPORTED_FILE_TYPES = [".pdf", ".docx", ".txt", ".md"]