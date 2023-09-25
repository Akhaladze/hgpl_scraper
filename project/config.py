import os
#basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.dirname(os.path.realpath(__file__))
print("basedir", basedir)

FLASK_APP = os.getenv("FLASK_APP", "app.py")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", 1)
FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT", 5000)
FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST", "0.0.0.0")

class DevelopmentConfig(object):
    #PROJECT_PATH = os.getenv("PROJECT_PATH", os.path.abspath(os.path.dirname(__file__)))
    PROJECT_PATH = os.getenv("PROJECT_PATH", basedir)
    APP_PATH = os.getenv("APP_PATH", os.path.abspath(os.path.dirname(__file__)))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://scraper_db:scraper_db@localhost:5432/scraper_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    TESTING = False
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://scraper:scraper@localhost:5672/scraper_app")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    CELERY_BROKER_USE_SSL = False
    CELERY_RESULT_BACKEND_USE_SSL = False
    CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
    CELERY_RESULT_EXPIRES = 3600

class ProductionConfig(DevelopmentConfig):
    DEBUG = False
    TESTING = False 


