import os
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from app.vision import process_image
from app.config import logger, NOTES_DIR, BASE_DIR
from app.notes_manager import notes_manager

app = FastAPI(title="Lectura API")


@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Поддерживаются только JPG и PNG")

    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = await process_image(temp_path)
        if not text or not text.strip():
            text = "*OCR не обнаружил текст*"

        note_filename = f"{os.path.splitext(file.filename)[0]}.md"
        note_path = os.path.join(NOTES_DIR, note_filename)
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(f"# {os.path.splitext(file.filename)[0]}\n\n")
            f.write(text)

        return {
            "status": "success",
            "content": text,
            "saved_to": note_filename
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/ocr/append")
async def ocr_append_endpoint(
        file: UploadFile = File(...),
        target_file: str = Form(None),
        create_new: bool = Form(False),
        note_title: str = Form("")
):
    """OCR + добавление в существующую заметку или создание новой"""
    logger.info(f"Вызов ocr/append: create_new={create_new}, target_file={target_file}, note_title={note_title}")
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Поддерживаются только JPG и PNG")

    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = await process_image(temp_path)
        if not text or not text.strip():
            text = f"*OCR не обнаружил текст в файле {file.filename}*"

        filename = ""
        action = ""

        if create_new:
            title = note_title if note_title else os.path.splitext(file.filename)[0]
            filename = notes_manager.create_new_note(title, text)
            if not filename:
                raise HTTPException(status_code=500, detail="Ошибка создания новой заметки")
            action = "created"
        else:
            if not target_file:
                raise HTTPException(status_code=400, detail="Укажите целевой файл")
            success = notes_manager.append_to_note(target_file, text)
            if not success:
                raise HTTPException(status_code=500, detail="Ошибка добавления в заметку")
            filename = target_file
            action = "appended"

        return {
            "status": "success",
            "content": text,
            "saved_to": filename,
            "action": action
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/notes")
async def list_notes():
    """Получить список всех заметок"""
    return {"notes": notes_manager.get_all_notes()}


@app.get("/notes/{filename}")
async def get_note(filename: str):
    """Получить содержимое конкретной заметки"""
    content = notes_manager.read_note_content(filename)
    if content == "" and not os.path.exists(
            os.path.join(NOTES_DIR, filename if filename.endswith('.md') else filename + '.md')):
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return {"filename": filename, "content": content}


@app.post("/notes/search")
async def search_notes(query: str):
    """Поиск по заметкам"""
    return {"query": query, "message": "Поиск пока не реализован"}


app.mount("/css", StaticFiles(directory=os.path.join(BASE_DIR, "static", "css")), name="css")
app.mount("/scripts", StaticFiles(directory=os.path.join(BASE_DIR, "static", "scripts")), name="js")
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="static")
