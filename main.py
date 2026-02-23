import uvicorn
from app.config import logger

if __name__ == "__main__":
    logger.info("🚀 Запуск Lectura OCR Service...")

    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=True)