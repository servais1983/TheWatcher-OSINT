#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TheWatcher - Routes API
Ce module définit les routes REST pour l'application
"""

import os
import json
import time
import uuid
import logging
from flask import Blueprint, request, jsonify, send_file, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from models import db, User, SearchHistory, SearchResult
from modules.facial_recognition import FaceDetector
from modules.reverse_search import ReverseImageSearch
from modules.social_osint import SocialOSINT
from modules.data_aggregator import DataAggregator
from utils.legal_check import validate_use_case
from utils.logging import audit_log

# Configuration du logger
logger = logging.getLogger(__name__)

# Déclarer le blueprint principal
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Créer le répertoire pour les téléchargements d'images
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Extensions autorisées pour les images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """
    Vérifie si le fichier a une extension autorisée
    Args:
        filename: Nom du fichier à vérifier
    Returns:
        bool: True si l'extension est autorisée, False sinon
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_routes(app):
    """
    Enregistre les routes dans l'application Flask
    Args:
        app: Application Flask
    """
    # Enregistrer le blueprint principal
    app.register_blueprint(api_bp)
    
    # Configurer les limitations
    max_content_length = app.config.get('MAX_IMAGE_SIZE', 5 * 1024 * 1024)
    app.config['MAX_CONTENT_LENGTH'] = max_content_length
    
    logger.info("Routes API enregistrées")

# Routes pour l'authentification
@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Route pour l'authentification"""
    data = request.json
    
    # Vérifier les données requises
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Nom d'utilisateur et mot de passe requis"}), 400
    
    # Rechercher l'utilisateur
    user = User.query.filter_by(username=data['username']).first()
    
    # Vérifier le mot de passe
    if not user or not user.check_password(data['password']):
        # Journaliser la tentative échouée
        audit_log(None, 'login_failure', 'auth', request.remote_addr, {'username': data['username']}, 'failure')
        return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect"}), 401
    
    # Vérifier si l'utilisateur est actif
    if not user.is_active:
        audit_log(user.id, 'login_failure', 'auth', request.remote_addr, {'reason': 'inactive'}, 'denied')
        return jsonify({"error": "Compte désactivé"}), 403
    
    # Générer le token
    from flask_jwt_extended import create_access_token, create_refresh_token
    
    # Mettre à jour la date de dernière connexion
    user.last_login = db.func.now()
    db.session.commit()
    
    # Journaliser la connexion réussie
    audit_log(user.id, 'login_success', 'auth', request.remote_addr, None, 'success')
    
    # Retourner les tokens
    return jsonify({
        "message": "Authentification réussie",
        "access_token": create_access_token(identity=user.id),
        "refresh_token": create_refresh_token(identity=user.id),
        "user": user.to_dict()
    }), 200

# Routes pour la recherche par photo
@api_bp.route('/search/photo', methods=['POST'])
@jwt_required(optional=True)
def search_by_photo():
    """Route pour la recherche par photo"""
    # Récupérer l'identité de l'utilisateur connecté (si disponible)
    current_user_id = get_jwt_identity()
    
    # Vérifier que le consentement éthique est présent
    if request.headers.get('X-Ethical-Consent', '').lower() != 'true':
        audit_log(current_user_id, 'search_denied', 'search/photo', request.remote_addr, {'reason': 'no_consent'}, 'denied')
        return jsonify({"error": "Consentement éthique requis"}), 403
    
    # Vérifier le cas d'usage
    use_case = request.headers.get('X-Use-Case')
    if not validate_use_case(use_case):
        audit_log(current_user_id, 'search_denied', 'search/photo', request.remote_addr, {'reason': 'invalid_use_case', 'use_case': use_case}, 'denied')
        return jsonify({"error": "Cas d'usage non valide"}), 403
    
    # Vérifier si un fichier est présent
    if 'image' not in request.files:
        return jsonify({"error": "Aucune image fournie"}), 400
    
    file = request.files['image']
    
    # Vérifier si le fichier est valide
    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400
    
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Type de fichier non autorisé"}), 400
    
    # Sauvegarder le fichier avec un nom sécurisé
    filename = secure_filename(file.filename)
    unique_filename = f"{str(uuid.uuid4())}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        file.save(file_path)
        logger.info(f"Image téléchargée avec succès: {file_path}")
        
        # Mesurer le temps d'exécution
        start_time = time.time()
        
        # Créer une entrée dans l'historique des recherches
        search_history = SearchHistory(
            user_id=current_user_id,
            search_type='photo',
            search_term=file.filename,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            consent_given=True,
            use_case=use_case,
            search_parameters=request.form.to_dict()
        )
        db.session.add(search_history)
        db.session.commit()
        
        # Initialiser les modules OSINT
        face_detector = FaceDetector()
        reverse_search = ReverseImageSearch()
        
        # Options de recherche
        search_engines = request.form.get('search_engines', 'all')
        detect_faces = request.form.get('detect_faces', 'true').lower() in ('true', '1', 't')
        
        results = {}
        
        # Détection de visages si demandé
        if detect_faces:
            face_results = face_detector.detect_faces(file_path)
            results['face_detection'] = {
                'faces_count': len(face_results),
                'face_locations': face_results
            }
            
            # Extraction des visages si des visages sont détectés
            if face_results:
                faces_dir = os.path.join(os.path.dirname(file_path), 'faces')
                os.makedirs(faces_dir, exist_ok=True)
                
                extracted_faces = face_detector.extract_faces(file_path, faces_dir)
                results['face_detection']['extracted_faces'] = extracted_faces
                
                # Analyse faciale AWS si configuré
                if hasattr(face_detector, 'rekognition') and face_detector.rekognition:
                    aws_results = face_detector.aws_face_analysis(file_path)
                    results['face_detection']['aws_analysis'] = aws_results
        
        # Recherche d'image inversée
        if search_engines == 'all':
            image_search_results = reverse_search.search_all(file_path)
        else:
            image_search_results = {}
            engines = search_engines.split(',')
            if 'google' in engines and hasattr(reverse_search, 'google_search'):
                image_search_results['google'] = reverse_search.google_search(file_path)
            if 'google_api' in engines and hasattr(reverse_search, 'google_search_api'):
                image_search_results['google_api'] = reverse_search.google_search_api(file_path)
            if 'yandex' in engines and hasattr(reverse_search, 'yandex_search'):
                image_search_results['yandex'] = reverse_search.yandex_search(file_path)
            if 'tineye' in engines and hasattr(reverse_search, 'tineye_search'):
                image_search_results['tineye'] = reverse_search.tineye_search(file_path)
        
        results['image_search'] = image_search_results
        
        # Fermer les ressources
        reverse_search.close()
        
        # Calculer le temps d'exécution
        execution_time = int((time.time() - start_time) * 1000)  # En millisecondes
        
        # Mettre à jour l'historique des recherches
        search_history.execution_time = execution_time
        search_history.results_count = len(str(results).split(','))
        db.session.commit()
        
        # Créer des entrées pour les résultats
        for source, result in results.items():
            search_result = SearchResult(
                search_id=search_history.id,
                result_type=source,
                source='TheWatcher',
                confidence=90,
                data=result
            )
            db.session.add(search_result)
        
        db.session.commit()
        
        # Journaliser la recherche réussie
        audit_log(current_user_id, 'search_success', 'search/photo', request.remote_addr, {'file': file.filename}, 'success')
        
        # Ajouter des informations sur le temps d'exécution
        results['metadata'] = {
            'execution_time': execution_time,
            'search_id': str(search_history.id),
            'filename': unique_filename
        }
        
        return jsonify({
            "message": "Recherche terminée avec succès",
            "results": results
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement de l'image: {str(e)}")
        
        # Journaliser l'erreur
        audit_log(current_user_id, 'search_error', 'search/photo', request.remote_addr, {'error': str(e)}, 'failure')
        
        return jsonify({
            "error": "Erreur lors du traitement de l'image",
            "details": str(e)
        }), 500
    finally:
        # Nettoyer les ressources si nécessaire
        pass

# Routes pour la recherche par nom
@api_bp.route('/search/person', methods=['POST'])
@jwt_required(optional=True)
def search_by_person():
    """Route pour la recherche par nom de personne"""
    # Récupérer l'identité de l'utilisateur connecté (si disponible)
    current_user_id = get_jwt_identity()
    
    # Vérifier que le consentement éthique est présent
    if request.headers.get('X-Ethical-Consent', '').lower() != 'true':
        audit_log(current_user_id, 'search_denied', 'search/person', request.remote_addr, {'reason': 'no_consent'}, 'denied')
        return jsonify({"error": "Consentement éthique requis"}), 403
    
    # Vérifier le cas d'usage
    use_case = request.headers.get('X-Use-Case')
    if not validate_use_case(use_case):
        audit_log(current_user_id, 'search_denied', 'search/person', request.remote_addr, {'reason': 'invalid_use_case', 'use_case': use_case}, 'denied')
        return jsonify({"error": "Cas d'usage non valide"}), 403
    
    # Récupérer les données du formulaire
    data = request.json
    
    # Vérifier si le nom est présent
    if not data or not data.get('name'):
        return jsonify({"error": "Nom requis"}), 400
    
    name = data.get('name')
    location = data.get('location')
    company = data.get('company')
    
    try:
        # Mesurer le temps d'exécution
        start_time = time.time()
        
        # Créer une entrée dans l'historique des recherches
        search_history = SearchHistory(
            user_id=current_user_id,
            search_type='person',
            search_term=name,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            consent_given=True,
            use_case=use_case,
            search_parameters=data
        )
        db.session.add(search_history)
        db.session.commit()
        
        # Initialiser le module OSINT social
        social_osint = SocialOSINT()
        
        # Effectuer la recherche
        results = social_osint.search_person(name, location, company)
        
        # Fermer les ressources
        social_osint.close()
        
        # Calculer le temps d'exécution
        execution_time = int((time.time() - start_time) * 1000)  # En millisecondes
        
        # Mettre à jour l'historique des recherches
        search_history.execution_time = execution_time
        search_history.results_count = sum(len(profiles) for platform, profiles in results.get('profiles', {}).items())
        db.session.commit()
        
        # Journaliser la recherche réussie
        audit_log(current_user_id, 'search_success', 'search/person', request.remote_addr, {'name': name}, 'success')
        
        # Ajouter des informations sur le temps d'exécution
        results['metadata'] = {
            'execution_time': execution_time,
            'search_id': str(search_history.id)
        }
        
        return jsonify({
            "message": "Recherche terminée avec succès",
            "results": results
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de personne: {str(e)}")
        
        # Journaliser l'erreur
        audit_log(current_user_id, 'search_error', 'search/person', request.remote_addr, {'error': str(e)}, 'failure')
        
        return jsonify({
            "error": "Erreur lors de la recherche de personne",
            "details": str(e)
        }), 500

# Routes pour la recherche par nom d'utilisateur
@api_bp.route('/search/username', methods=['POST'])
@jwt_required(optional=True)
def search_by_username():
    """Route pour la recherche par nom d'utilisateur"""
    # Récupérer l'identité de l'utilisateur connecté (si disponible)
    current_user_id = get_jwt_identity()
    
    # Vérifier que le consentement éthique est présent
    if request.headers.get('X-Ethical-Consent', '').lower() != 'true':
        audit_log(current_user_id, 'search_denied', 'search/username', request.remote_addr, {'reason': 'no_consent'}, 'denied')
        return jsonify({"error": "Consentement éthique requis"}), 403
    
    # Vérifier le cas d'usage
    use_case = request.headers.get('X-Use-Case')
    if not validate_use_case(use_case):
        audit_log(current_user_id, 'search_denied', 'search/username', request.remote_addr, {'reason': 'invalid_use_case', 'use_case': use_case}, 'denied')
        return jsonify({"error": "Cas d'usage non valide"}), 403
    
    # Récupérer les données du formulaire
    data = request.json
    
    # Vérifier si le nom d'utilisateur est présent
    if not data or not data.get('username'):
        return jsonify({"error": "Nom d'utilisateur requis"}), 400
    
    username = data.get('username')
    
    try:
        # Mesurer le temps d'exécution
        start_time = time.time()
        
        # Créer une entrée dans l'historique des recherches
        search_history = SearchHistory(
            user_id=current_user_id,
            search_type='username',
            search_term=username,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            consent_given=True,
            use_case=use_case,
            search_parameters=data
        )
        db.session.add(search_history)
        db.session.commit()
        
        # Initialiser le module OSINT social
        social_osint = SocialOSINT()
        
        # Effectuer la recherche
        results = social_osint.search_username(username)
        
        # Fermer les ressources
        social_osint.close()
        
        # Calculer le temps d'exécution
        execution_time = int((time.time() - start_time) * 1000)  # En millisecondes
        
        # Mettre à jour l'historique des recherches
        search_history.execution_time = execution_time
        search_history.results_count = len(results.get('accounts', {}))
        db.session.commit()
        
        # Journaliser la recherche réussie
        audit_log(current_user_id, 'search_success', 'search/username', request.remote_addr, {'username': username}, 'success')
        
        # Ajouter des informations sur le temps d'exécution
        results['metadata'] = {
            'execution_time': execution_time,
            'search_id': str(search_history.id)
        }
        
        return jsonify({
            "message": "Recherche terminée avec succès",
            "results": results
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de nom d'utilisateur: {str(e)}")
        
        # Journaliser l'erreur
        audit_log(current_user_id, 'search_error', 'search/username', request.remote_addr, {'error': str(e)}, 'failure')
        
        return jsonify({
            "error": "Erreur lors de la recherche de nom d'utilisateur",
            "details": str(e)
        }), 500

# Route pour générer un rapport
@api_bp.route('/report/<search_id>', methods=['GET'])
@jwt_required(optional=True)
def generate_report(search_id):
    """Route pour générer un rapport à partir d'une recherche"""
    # Récupérer l'identité de l'utilisateur connecté (si disponible)
    current_user_id = get_jwt_identity()
    
    # Rechercher l'historique de recherche
    search_history = SearchHistory.query.get(search_id)
    
    if not search_history:
        return jsonify({"error": "Recherche non trouvée"}), 404
    
    # Vérifier les permissions (si l'utilisateur est connecté, il ne peut voir que ses propres recherches)
    if current_user_id and search_history.user_id != current_user_id:
        audit_log(current_user_id, 'report_denied', f'report/{search_id}', request.remote_addr, {'reason': 'unauthorized'}, 'denied')
        return jsonify({"error": "Non autorisé"}), 403
    
    try:
        # Récupérer les résultats de recherche
        search_results = SearchResult.query.filter_by(search_id=search_id).all()
        
        if not search_results:
            return jsonify({"error": "Aucun résultat trouvé pour cette recherche"}), 404
        
        # Compiler les résultats
        combined_results = {}
        for result in search_results:
            combined_results[result.result_type] = result.data
        
        # Initialiser l'agrégateur de données
        data_aggregator = DataAggregator()
        
        # Générer le rapport en fonction du type de recherche
        if search_history.search_type == 'person':
            # Pour une recherche par nom
            person_data = combined_results.get('person_search', {})
            
            # Générer le rapport HTML
            html, report_file = data_aggregator.generate_report(person_data)
            
            # Journaliser la génération du rapport
            audit_log(current_user_id, 'report_generated', f'report/{search_id}', request.remote_addr, {'file': report_file}, 'success')
            
            # Retourner le rapport
            return send_file(report_file, as_attachment=True, download_name=os.path.basename(report_file))
        
        elif search_history.search_type == 'username':
            # Pour une recherche par nom d'utilisateur
            username_data = combined_results.get('username_search', {})
            
            # Générer le rapport HTML
            html, report_file = data_aggregator.generate_report(username_data)
            
            # Journaliser la génération du rapport
            audit_log(current_user_id, 'report_generated', f'report/{search_id}', request.remote_addr, {'file': report_file}, 'success')
            
            # Retourner le rapport
            return send_file(report_file, as_attachment=True, download_name=os.path.basename(report_file))
        
        elif search_history.search_type == 'photo':
            # Pour une recherche par photo
            # Le traitement est plus complexe car il faut agréger différentes sources
            aggregated_data = {
                'name': search_history.search_term,
                'social_profiles': {},
                'images': [],
                'metadata': {
                    'sources': ['image_search'],
                    'confidence': 50
                }
            }
            
            # Ajouter les résultats de la recherche d'image
            if 'image_search' in combined_results:
                image_results = combined_results['image_search']
                
                # Traiter chaque moteur de recherche
                for engine, results in image_results.items():
                    if engine == 'google' and 'similar_images' in results:
                        for image in results['similar_images']:
                            aggregated_data['images'].append({
                                'url': image.get('url', ''),
                                'source': engine
                            })
                    
                    if engine == 'yandex' and 'similar_images' in results:
                        for image in results['similar_images']:
                            aggregated_data['images'].append({
                                'url': image.get('url', ''),
                                'source': engine
                            })
            
            # Générer le rapport HTML
            html, report_file = data_aggregator.generate_report(aggregated_data)
            
            # Journaliser la génération du rapport
            audit_log(current_user_id, 'report_generated', f'report/{search_id}', request.remote_addr, {'file': report_file}, 'success')
            
            # Retourner le rapport
            return send_file(report_file, as_attachment=True, download_name=os.path.basename(report_file))
        
        else:
            return jsonify({"error": "Type de recherche non pris en charge pour la génération de rapport"}), 400
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        
        # Journaliser l'erreur
        audit_log(current_user_id, 'report_error', f'report/{search_id}', request.remote_addr, {'error': str(e)}, 'failure')
        
        return jsonify({
            "error": "Erreur lors de la génération du rapport",
            "details": str(e)
        }), 500

# Route pour l'historique des recherches
@api_bp.route('/history', methods=['GET'])
@jwt_required()
def search_history():
    """Route pour récupérer l'historique des recherches de l'utilisateur"""
    # Récupérer l'identité de l'utilisateur connecté
    current_user_id = get_jwt_identity()
    
    # Paramètres de pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limiter le nombre de résultats par page
    per_page = min(per_page, 50)
    
    try:
        # Récupérer l'historique de recherche
        history = SearchHistory.query.filter_by(user_id=current_user_id).order_by(
            SearchHistory.created_at.desc()
        ).paginate(page=page, per_page=per_page)
        
        # Formater les résultats
        results = []
        for item in history.items:
            results.append({
                'id': str(item.id),
                'search_type': item.search_type,
                'search_term': item.search_term,
                'created_at': item.created_at.isoformat(),
                'results_count': item.results_count,
                'execution_time': item.execution_time
            })
        
        return jsonify({
            'history': results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': history.total,
                'pages': history.pages
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {str(e)}")
        return jsonify({
            "error": "Erreur lors de la récupération de l'historique",
            "details": str(e)
        }), 500
