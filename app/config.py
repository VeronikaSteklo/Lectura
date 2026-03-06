import logging
import sys
import os

MODEL_VISION = 'qwen3-vl:2b'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')
NOTES_DIR = os.path.join(BASE_DIR, 'notes')
LOG_FILE = os.path.join(BASE_DIR, 'lectura_assistant.log')

SYSTEM_PROMPT = (
    "You are a strict OCR-only engine. "
    "1. EXTRACT all visible text and mathematical formulas. "
    "2. WRAP every formula or variable in $...$. "
    "3. IGNORE and SKIP all drawings, diagrams, photos, or illustrations. Do not describe them. "
    "4. If there is a caption under a picture, extract the caption text only. "
    "5. Output ONLY the extracted Markdown text. No chat, no intro."
)

for directory in [PHOTOS_DIR, NOTES_DIR]:
    os.makedirs(directory, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(module)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("Lectura")