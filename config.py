import os
import datetime

BASE_URLS = {
    "local": os.getcwd(),
    "production": "https://example.com",
}

SITE_ENV = os.environ.get("SITE_ENV", "local")
BASE_URL = BASE_URLS[SITE_ENV]
ROOT_DIR = "pages"
LAYOUTS_BASE_DIR = "_layouts"
SITE_DIR = "_site"
HOOKS = {
    "template_filters": {"hooks": ["transform_date_to_day_name_date"]},
}

SITE_STATE = {
    "date_as_str": (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d"),
}