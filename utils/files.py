import os
import aiohttp
import aiofiles
from docx import Document
from utils.logger import logger


async def download_image(url, filename: str, directory: str = '.') -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(filename, 'wb') as file:
                    async for chunk in response.content.iter_any():
                        await file.write(chunk)
                logger.info(f'File {filename} downloaded successfully')
            else:
                logger.error(f'Не удалось скачать файл. HTTP-код ответа: {response.status}')
        # await delete_old_files(directory)


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[-1].lower()

    if ext in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    elif ext == ".docx":
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    else:
        raise ValueError("Unsupported file type. Only .txt, .md and .docx are allowed.")