import os
import glob
from datetime import datetime
from typing import List
from app.config import NOTES_DIR, logger

class NotesManager:
    def __init__(self):
        self.notes_dir = NOTES_DIR
        os.makedirs(self.notes_dir, exist_ok=True)

    def get_all_notes(self) -> List[dict]:
        """Получить список всех .md файлов"""
        notes = []
        if os.path.exists(self.notes_dir):
            md_files = glob.glob(os.path.join(self.notes_dir, "*.md"))
            for file_path in md_files:
                filename = os.path.basename(file_path)
                try:
                    stat = os.stat(file_path)
                    notes.append({
                        'filename': filename,
                        'path': file_path,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    })
                except Exception as e:
                    logger.error(f"Ошибка при обработке файла {filename}: {e}")
        return sorted(notes, key=lambda x: x['modified'], reverse=True)

    def read_note_content(self, filename: str) -> str:
        """Прочитать содержимое заметки"""
        if not filename.endswith('.md'):
            filename += '.md'
        file_path = os.path.join(self.notes_dir, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Ошибка чтения файла {filename}: {e}")
                return ""
        return ""

    def append_to_note(self, filename: str, content: str, separator: str = "\n\n---\n\n") -> bool:
        """Добавить контент в существующую заметку"""
        if not filename.endswith('.md'):
            filename += '.md'
        file_path = os.path.join(self.notes_dir, filename)
        try:
            if not os.path.exists(file_path):
                note_title = filename.replace('.md', '')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {note_title}\n\n")

            with open(file_path, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                f.write(f"{separator}## Добавлено {timestamp}\n\n{content}\n")

            logger.info(f"Контент добавлен в {filename}")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления в файл {filename}: {e}")
            return False

    def create_new_note(self, title: str, content: str = "") -> str:
        """Создать новую заметку"""
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title.replace(' ', '_')}.md"
        file_path = os.path.join(self.notes_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                if content:
                    f.write(content + "\n")
            logger.info(f"Создана новая заметка: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Ошибка создания файла {filename}: {e}")
            return ""

notes_manager = NotesManager()
