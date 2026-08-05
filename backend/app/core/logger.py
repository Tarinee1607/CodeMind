import logging
import os

from app.core.config import settings

# Create logs directory if it doesn't exist
os.makedirs("backend/logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("backend/logs/codemind.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(settings.APP_NAME)