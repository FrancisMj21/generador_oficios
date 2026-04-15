import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DOCX_DIR = BASE_DIR / "plantillas"
GENERATED_DIR = BASE_DIR / "generados"
GENERATED_DIR.mkdir(exist_ok=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
