import json
import os
from pathlib import Path
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

# Detect local bundled Tesseract if available
LOCAL_TESSERACT = BASE_DIR / "tesseract" / "tesseract.exe"
LOCAL_TESSDATA = BASE_DIR / "tesseract" / "tessdata"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Bangladesh Land Records Digitization System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'land_records.db'}"

    # Paths
    BASE_DIR: Path = BASE_DIR
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DEMO_DOCS_DIR: Path = BASE_DIR / "demo_docs"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # OCR and External Binary Paths
    TESSERACT_CMD: str = ""
    TESSDATA_PREFIX: str = ""
    POPPLER_PATH: str = ""
    DEFAULT_OCR_LANGUAGES: Union[List[str], str] = ["bn", "en"]
    MAX_UPLOAD_SIZE_MB: int = 25

    # Cloud AI / Gemini OCR configuration
    GEMINI_API_KEY: str = ""

    @field_validator("TESSERACT_CMD", mode="after")
    @classmethod
    def resolve_tesseract_cmd(cls, v: str) -> str:
        if not v or not v.strip():
            if LOCAL_TESSERACT.exists():
                return str(LOCAL_TESSERACT)
        return v

    @field_validator("TESSDATA_PREFIX", mode="after")
    @classmethod
    def resolve_tessdata_prefix(cls, v: str) -> str:
        if not v or not v.strip():
            if LOCAL_TESSDATA.exists():
                return str(LOCAL_TESSDATA)
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @field_validator("DEFAULT_OCR_LANGUAGES", mode="before")
    @classmethod
    def assemble_ocr_langs(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure TESSDATA_PREFIX is propagated to environment if configured
if settings.TESSDATA_PREFIX:
    os.environ["TESSDATA_PREFIX"] = settings.TESSDATA_PREFIX

# Ensure GEMINI_API_KEY is propagated to environment if configured
if settings.GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
