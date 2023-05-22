"""Модуль для запуска бота."""
import os

import uvicorn
from webhook import app


HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
uvicorn.run(
    app=app,
    host=HOST,
    port=PORT,
)
