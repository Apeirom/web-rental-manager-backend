from fastapi import UploadFile
from src.constants.file_constants import MAX_FILE_SIZE_BYTES, PDF_MAGIC_BYTES
from src.errors.custom_errors import FileTooLargeError, InvalidFileFormatError


def validate_pdf_file(file_bytes: bytes) -> None:
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(max_size_mb=10)

    if len(file_bytes) < 4 or not file_bytes.startswith(PDF_MAGIC_BYTES):
        raise InvalidFileFormatError(expected_format="PDF")


def read_upload_file_safely(file: UploadFile) -> bytes:
    chunk_size = 1024 * 1024
    content = bytearray()
    while True:
        chunk = file.file.read(chunk_size)
        if not chunk:
            break
        content.extend(chunk)
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise FileTooLargeError(max_size_mb=10)
    return bytes(content)
