import logging
import sys

MODEL_VISION = 'qwen3-vl:8b'
PHOTOS_DIR = 'photos'
NOTES_DIR = 'notes'
LOG_FILE = 'lectura_assistant.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(module)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("Lectura")