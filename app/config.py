import logging
import sys
import os

MODEL_VISION = 'qwen3-vl:2b'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')
NOTES_DIR = os.path.join(BASE_DIR, 'notes')
LOG_FILE = os.path.join(BASE_DIR, 'lectura_assistant.log')

SYSTEM_PROMPT = (
    "ACT AS AN EXPERT OCR. Look closely at the projector screen in the center. "
    "Ignore the walls and the blackboard. "
    "Transcribe all text from the screen. "
    "For all variables like P_n, C_n, W_n, k=3, use LaTeX: $P_n$, $C_n$, $W_n$, $k=3$. "
    "If you see a graph name, write it. "
    "OUTPUT ONLY THE TEXT. NO DESCRIPTIONS."
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