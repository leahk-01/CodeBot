from pydantic import BaseModel
from typing import Optional

class CodeRequest(BaseModel):
    code: str


class GenerateRequest(BaseModel):
    description: str
    language: str  # Desired output language


class TranslateRequest(BaseModel):
    code: str
    target_language: str

class StylePreferences(BaseModel):
    indentation: Optional[int] = 4
    naming_convention: Optional[str] = "snake_case"
