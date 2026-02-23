import time

import requests
import sys
import os

from app.config import logger

URL = "http://127.0.0.1:8000/ocr"


def run_cli():
    if len(sys.argv) < 2:
        logger.warning("Не указан путь к файлук")
        return

    img_path = sys.argv[1]

    if not os.path.exists(img_path):
        logger.error(f"Файл не найден: {img_path}")
        return

    logger.info(f"Обработка: {os.path.basename(img_path)}")
    start_time = time.time()

    try:
        with open(img_path, 'rb') as f:
            files = {'file': (os.path.basename(img_path), f, 'image/jpeg')}

            response = requests.post(URL, files=files)

            response.raise_for_status()

        if response.status_code == 200:
            result = response.json()
            duration = time.time() - start_time

            logger.info(f"Успешно распознано за {duration:.2f} сек.")
            print("\n" + "=" * 50)
            print(result.get('content', 'Текст пуст'))
            print("=" * 50 + "\n")

            if 'saved_to' in result:
                logger.info(f"Файл сохранен: {result['saved_to']}")

    except requests.exceptions.ConnectionError:
        logger.critical("Сервер Lectura не запущен!")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Ошибка сервера: {http_err}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    run_cli()