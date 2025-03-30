#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TheWatcher - Application principale
Ce module initialise l'application Flask et configure toutes les routes API
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_swagger_ui import get_swaggerui_blueprint

from config import active_config
from utils.logging import setup_logging
from utils.legal_check import validate_use_case, check_ethical_compliance
from models import db, User, SearchHistory, AuditLog
from routes import register_routes

# Configuration du logger
logger = logging.getLogger(__name__)

def create_app(config=None):
    """
    Crée et configure l'application Flask
    Args:
        config: Configuration à utiliser (par défaut: active_config)
    Returns:
        Application Flask configurée
    """
    app = Flask(__name__, static_folder='../frontend/build')
    
    # Utiliser la configuration spécifiée ou la configuration active
    app.config.from_object(config or active_config)
    
    # Configurer le logger
    setup_logging(app)
    
    # Initialiser les extensions
    CORS(app, resources={r"/api/*": {"origins": app.config['FRONTEND_URL']}})
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Initialiser le limiteur de débit
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config['RATE_LIMIT']],
        storage_uri=app.config['REDIS_URL']
    )
    
    # Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/swagger.json'
    swagger_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "TheWatcher API"
        }
    )
    app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)
    
    # Enregistrer les routes
    register_routes(app)
    
    # Route par défaut pour le swagger JSON
    @app.route('/api/swagger.json')
    def swagger():
        with open(os.path.join(app.root_path, 'swagger.json')) as f:
            return jsonify(json.load(f))
    
    # Middleware pour la vérification éthique
    @app.before_request
    def before_request():
        # Ignorer les requêtes pour des assets statiques
        if request.path.startswith('/static') or request.path.startswith('/api/docs'):
            return None
        
        # Vérification de consentement éthique pour les endpoints API
        if request.path.startswith('/api/search'):
            if app.config['ETHICAL_CHECK_ENABLED']:
                consent = request.headers.get('X-Ethical-Consent')
                use_case = request.headers.get('X-Use-Case')
                
                if not consent or consent.lower() != 'true':
                    return jsonify({
                        'error': 'Consentement éthique requis',
                        'message': 'Vous devez accepter les directives éthiques pour utiliser cette API'
                    }), 403
                
                if not validate_use_case(use_case):
                    return jsonify({
                        'error': 'Cas d\'usage non autorisé',
                        'message': 'Le cas d\'usage spécifié n\'est pas autorisé'
                    }), 403
                
                # Vérifier la conformité éthique de la requête
                is_compliant, reason = check_ethical_compliance(request)
                if not is_compliant:
                    logger.warning(f"Requête non conforme aux directives éthiques: {reason}")
                    return jsonify({
                        'error': 'Non-conformité éthique',
                        'message': reason
                    }), 403
        
        # Journaliser la requête pour audit
        if app.config['SAVE_SEARCH_HISTORY'] and request.method != 'OPTIONS':
            try:
                AuditLog.create_from_request(request)
            except Exception as e:
                logger.error(f"Erreur lors de la journalisation: {str(e)}")
        
        return None
    
    # Gestion des erreurs
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "La ressource demandée n'existe pas"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Erreur serveur: {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500
    
    # Servir l'application React en production
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Créer les tables de la base de données si elles n'existent pas
    with app.app_context():
        db.create_all()
    
    # Démarrer l'application
    app.run(host='0.0.0.0', port=active_config.PORT, debug=active_config.DEBUG)
