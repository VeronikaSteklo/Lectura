import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from app.vision import process_image
from app.config import logger, NOTES_DIR, BASE_DIR
from app.notes_manager import notes_manager

app = FastAPI(title="Lectura API")


@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...), save: bool = Form(False)):
    """Унифицированный эндпоинт для создания новой заметки через OCR"""
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Поддерживаются только JPG и PNG")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
    temp_path = tmp.name

    try:
        shutil.copyfileobj(file.file, tmp)
        tmp.close()

        text = await process_image(temp_path)

        if not text or not text.strip():
            text = "*OCR не обнаружил текст*"

        if not save:
            return {"status": "success", "content": text, "saved_to": None}

        title = os.path.splitext(file.filename)[0]
        note_filename = notes_manager.create_new_note(title, text)

        if not note_filename:
            raise HTTPException(status_code=500, detail="Ошибка при создании заметки")

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
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Поддерживаются только JPG и PNG")

    suffix = os.path.splitext(file.filename)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_path = tmp.name

    try:
        shutil.copyfileobj(file.file, tmp)
        tmp.close()

        text = await process_image(temp_path)
        if not text or not text.strip():
            text = f"*OCR не обнаружил текст в файле {file.filename}*"

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
    if not content and not os.path.exists(
            os.path.join(NOTES_DIR, filename if filename.endswith('.md') else filename + '.md')):
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return {"filename": filename, "content": content}


@app.post("/notes/search")
async def search_notes(query: str = Form(...)):
    """Полнотекстовый поиск по всем заметкам"""
    results = notes_manager.search_notes(query)
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }


app.mount("/css", StaticFiles(directory=os.path.join(BASE_DIR, "static", "css")), name="css")
app.mount("/scripts", StaticFiles(directory=os.path.join(BASE_DIR, "static", "scripts")), name="js")
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="static")
