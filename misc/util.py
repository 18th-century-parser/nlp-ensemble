from pathlib import Path
from uuid import uuid4

import aiofiles

from fastapi import UploadFile

from textract import process

from charset_normalizer import from_bytes

from misc.fb2_processor import process_fb2
from misc.config import Paths


def get_temp_file_path(extension: str = None) -> Path:
    return Path(
        Paths.temp_dir,
        str(uuid4()) + ("" if extension.startswith(".") else ".") + (extension if extension else "")
    )


def get_plain_text(path: Path) -> str:
    if path.suffix == ".fb2":
        return process_fb2(path)
    else:
        return process(str(path), output_encoding="utf-8").decode("utf-8").replace(chr(160), " ")


async def process_files(files: list[UploadFile]) -> Path:
    async with aiofiles.open(text_file_path := get_temp_file_path("txt"), "a", encoding="utf-8") as text_file:
        for file in files:
            temp_file_path = get_temp_file_path(suffix := Path(file.filename).suffix)
            if suffix in (".docx", ".odt", ".pdf", ".epub", ".htm", ".html"):
                async with aiofiles.open(temp_file_path, "wb") as temp_file:
                    await temp_file.write(await file.read())
            else:
                async with aiofiles.open(temp_file_path, "w", encoding="utf-8") as temp_file:
                    await temp_file.write(str(from_bytes(await file.read()).best()))

            await text_file.write(get_plain_text(temp_file_path) + "\n")

    return text_file_path


async def save_text(text: str) -> Path:
    async with aiofiles.open(text_file_path := get_temp_file_path("txt"), "w", encoding="utf-8") as text_file:
        await text_file.write(text)

    return text_file_path
