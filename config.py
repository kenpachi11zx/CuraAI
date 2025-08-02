import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key-change-in-production')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    PORT = int(os.getenv('PORT', 5000))
    
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/curaai.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('CuraAI startup')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
} 