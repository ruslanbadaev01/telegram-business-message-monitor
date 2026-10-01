import logging

from bot import build_application
from config import load_settings


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    build_application(load_settings()).run_polling()
