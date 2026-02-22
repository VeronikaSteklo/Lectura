import io

import ollama
import logging
import os
import time

from PIL import Image
from config import logger, MODEL_VISION

def resize_image(image_path):
    img = Image.open(image_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail((1024, 1024))
    temp_buffer = io.BytesIO()
    img.save(temp_buffer, format="JPEG", quality=85)
    return temp_buffer.getvalue()


def process_image(image_path):
    if not os.path.exists(image_path):
        logging.error(f"Файл не найден: {image_path}")
        return None

    logging.info(f"Обработка {os.path.basename(image_path)}...")
    start_time = time.time()

    try:
        full_response = ""
        for chunk in ollama.chat(
                model=MODEL_VISION,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a fast OCR bot. Output ONLY text/tables from images in Markdown. No thinking, no chat.'
                    },
                    {
                        'role': 'user',
                        'content': 'Extract text.',
                        'images': [resize_image(image_path)]
                    }
                ],
                stream=True,
                options={
                    'temperature': 0,
                    'num_predict': 1000
                }
        ):
            full_response += chunk['message']['content']

        content = full_response.strip()
        if "</think>" in content:
            content = content.split("</think>")[-1].strip()

        duration = time.time() - start_time
        logger.info(f"\nЗавершено за {duration:.2f} сек.")
        return content

    except Exception as e:
        logger.critical(f"Ошибка: {e}")
        return None
