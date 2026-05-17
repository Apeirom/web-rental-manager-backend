from fastapi import HTTPException

class BaseAppException(HTTPException):
    def __init__(self, status_code: int, code: str, message_en: str, message_pt: str, **kwargs):
        detail = {
            "code": code,
            "message": message_en.format(**kwargs),
            "translation": message_pt.format(**kwargs)
        }
        super().__init__(status_code=status_code, detail=detail)