from pathlib import Path
import os

BASEDIR = Path(__file__).resolve().parent
dotenv_path = os.path.join(BASEDIR, '.env')