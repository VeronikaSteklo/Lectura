import os

from config import *
from vision import process_image


def main():
    for img_name in os.listdir(PHOTOS_DIR):
        if img_name.lower().endswith(('.jpg', '.png')):
            path = os.path.join(PHOTOS_DIR, img_name)

            print(f"🔍 Анализирую {img_name}...")
            text = process_image(path)

            note_path = os.path.join(NOTES_DIR, f"{img_name}.md")
            with open(note_path, "w") as f:
                f.write(text)


if __name__ == "__main__":
    main()