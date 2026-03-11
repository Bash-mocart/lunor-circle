from fastapi import HTTPException, status


class AppError(HTTPException):
    """Base application error with a code and message."""

    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail={"code": code, "message": message})
