#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration de TheWatcher
Ce module gère la configuration de l'application en chargeant les variables 
d'environnement depuis le fichier .env ou les variables d'environnement du système.
"""

import os
import secrets
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Config:
    """
    Configuration de base pour l'application
    """
    # Général
    APP_ENV = os.getenv('APP_ENV', 'development')
    DEBUG = APP_ENV == 'development'
    TESTING = False
    PORT = int(os.getenv('PORT', 5000))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'info')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # Sécurité
    SECRET_KEY = os.getenv('JWT_SECRET', secrets.token_hex(32))
    API_KEY = os.getenv('API_KEY', secrets.token_hex(16))
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 heure
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 jours
    MFA_REQUIRED = os.getenv('MFA_REQUIRED', 'true').lower() in ('true', '1', 't')
    
    # Base de données
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('POSTGRES_USER', 'thewatcher')}:{os.getenv('POSTGRES_PASSWORD', 'thewatcher')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'thewatcher')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Elasticsearch
    ELASTIC_URL = os.getenv('ELASTIC_URL', 'http://localhost:9200')
    
    # Redis
    REDIS_URL = f"redis://:{os.getenv('REDIS_PASSWORD', '')}@{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/0"
    
    # Limites et sécurité
    RATE_LIMIT = os.getenv('RATE_LIMIT', '60/minute')
    MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 5)) * 1024 * 1024  # En octets
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 10))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    FACE_MATCH_THRESHOLD = float(os.getenv('FACE_MATCH_THRESHOLD', 80.0))
    
    # Services externes
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'eu-west-3')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Outils OSINT
    SHERLOCK_PATH = os.getenv('SHERLOCK_PATH', '/opt/sherlock')
    MALTEGO_API_KEY = os.getenv('MALTEGO_API_KEY')
    SPIDERFOOT_URL = os.getenv('SPIDERFOOT_URL', 'http://localhost:5001/api')
    HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')
    
    # Configuration proxy
    PROXY_ENABLED = os.getenv('PROXY_ENABLED', 'false').lower() in ('true', '1', 't')
    PROXY_TYPE = os.getenv('PROXY_TYPE', 'socks5')
    PROXY_HOST = os.getenv('PROXY_HOST', 'localhost')
    PROXY_PORT = int(os.getenv('PROXY_PORT', 8888))
    PROXY_USER = os.getenv('PROXY_USER', '')
    PROXY_PASS = os.getenv('PROXY_PASS', '')
    PROXY_ROTATION = os.getenv('PROXY_ROTATION', 'true').lower() in ('true', '1', 't')
    
    # Directives éthiques
    ETHICAL_CHECK_ENABLED = os.getenv('ETHICAL_CHECK_ENABLED', 'true').lower() in ('true', '1', 't')
    SAVE_SEARCH_HISTORY = os.getenv('SAVE_SEARCH_HISTORY', 'true').lower() in ('true', '1', 't')
    PRIVACY_CONSENT_REQUIRED = os.getenv('PRIVACY_CONSENT_REQUIRED', 'true').lower() in ('true', '1', 't')
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', 30))
    
    # Localisation
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'fr')
    DEFAULT_COUNTRY = os.getenv('DEFAULT_COUNTRY', 'FR')
    
    @staticmethod
    def get_proxies():
        """
        Retourne la configuration proxy pour les requêtes
        """
        if not Config.PROXY_ENABLED:
            return {}
        
        auth = f"{Config.PROXY_USER}:{Config.PROXY_PASS}@" if Config.PROXY_USER and Config.PROXY_PASS else ""
        proxy_url = f"{Config.PROXY_TYPE}://{auth}{Config.PROXY_HOST}:{Config.PROXY_PORT}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }


class DevelopmentConfig(Config):
    """
    Configuration pour l'environnement de développement
    """
    DEBUG = True
    LOG_LEVEL = 'debug'


class TestingConfig(Config):
    """
    Configuration pour l'environnement de test
    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """
    Configuration pour l'environnement de production
    """
    DEBUG = False
    LOG_LEVEL = 'warning'
    
    # En production, ces valeurs doivent être définies via des variables d'environnement
    SECRET_KEY = os.getenv('JWT_SECRET')
    API_KEY = os.getenv('API_KEY')
    
    # Vérifier que les clés sensibles sont définies
    @classmethod
    def validate(cls):
        """
        Valide que toutes les configurations critiques sont définies
        """
        required_vars = [
            'JWT_SECRET',
            'API_KEY',
            'POSTGRES_PASSWORD',
            'REDIS_PASSWORD'
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(f"Variables d'environnement manquantes en production: {', '.join(missing)}")


# Dictionnaire pour sélectionner la configuration en fonction de l'environnement
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# Configuration active
active_config = config_by_name[os.getenv('APP_ENV', 'development')]

# Valider la configuration en production
if os.getenv('APP_ENV') == 'production':
    ProductionConfig.validate()
