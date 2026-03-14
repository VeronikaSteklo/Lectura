import io

import ollama

from PIL import Image, ImageOps, ImageEnhance, ImageFile
from app.config import logger, MODEL_VISION, SYSTEM_PROMPT

ImageFile.LOAD_TRUNCATED_IMAGES = True

def resize_image(image_path):
    with Image.open(image_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img = ImageOps.autocontrast(img)

        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)

        img.thumbnail((1344, 1344))

        temp_buffer = io.BytesIO()
        img.save(temp_buffer, format="JPEG", quality=90)
    return temp_buffer.getvalue()

async def process_image(image_path):
    client = ollama.AsyncClient()

    try:
        full_response = ""
        async for chunk in await client.chat(
                model=MODEL_VISION,
                messages=[
                    {
                        'role': 'system',
                        'content': SYSTEM_PROMPT
                    },
                    {
                        'role': 'user',
                        'content': 'Extract text.',
                        'images': [resize_image(image_path)]
                    }
                ],
                stream=True,
                options={'temperature': 0}
        ):
            full_response += chunk['message']['content']

        if not full_response.strip():
            logger.warning("Модель вернула пустой ответ!")
            return "Текст не обнаружен."

        return full_response.strip()
    except Exception as e:
        logger.error(f"Ошибка в async OCR: {e}")
        return None
