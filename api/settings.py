from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = 'static/'
STATICFILES_DIRS =os.path.join(BASE_DIR,'static')
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles_build','static')
