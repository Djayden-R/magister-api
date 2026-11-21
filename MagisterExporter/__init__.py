import logging
import os
from dotenv import load_dotenv

load_dotenv()

log_level = os.getenv("LOG_LEVEL", "WARNING").upper()

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.getLogger(__name__).addHandler(logging.NullHandler())
