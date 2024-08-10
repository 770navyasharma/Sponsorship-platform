import os

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = None

class LocalDevelopmentConfig(Config):
    basedir = os.path.abspath(os.path.dirname(__file__))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "databease.sqlite3")
    DEBUG = True
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'db_directory', 'profile_images')
