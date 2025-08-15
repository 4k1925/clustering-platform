# server/app/config.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent  # 项目根目录

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/database/clustering.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 其他配置项...