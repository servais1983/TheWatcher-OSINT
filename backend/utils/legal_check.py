#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TheWatcher - Module de vérification légale
Ce module gère les vérifications éthiques et légales des requêtes
"""

import re
import logging

# Liste des cas d'usage autorisés
ALLOWED_USE_CASES = [
    'security_research',   # Recherche en sécurité informatique
    'pentest',            # Test d'intrusion (avec autorisation)
    'missing_person',     # Recherche de personne disparue
    'identity_verification',  # Vérification d'identité (avec consentement)
    'academic_research',  # Recherche académique
    'threat_intel'        # Renseignement sur les menaces
]

# Liste de mots-clés sensibles à surveiller dans les requêtes
SENSITIVE_KEYWORDS = [
    'hack', 'stalk', 'spy', 'track', 'monitor', 'girlfriend', 'boyfriend', 
    'spouse', 'wife', 'husband', 'ex', 'revenge', 'private', 'nude', 'steal'
]

# Expressions régulières pour détecter les informations personnelles sensibles
REGEX_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b(\+\d{1,3})?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',  # US SSN format
    'credit_card': r'\b(?:\d{4}[- ]?){3}\d{4}\b'
}

# Logger
logger = logging.getLogger(__name__)

def validate_use_case(use_case):
    """
    Vérifie si le cas d'usage est autorisé
    Args:
        use_case: Cas d'usage à vérifier
    Returns:
        bool: True si le cas d'usage est autorisé, False sinon
    """
    if not use_case:
        return False
    
    return use_case.lower() in ALLOWED_USE_CASES

def check_ethical_compliance(request):
    """
    Vérifie la conformité éthique d'une requête
    Args:
        request: Requête Flask à vérifier
    Returns:
        tuple: (is_compliant, reason)
    """
    # Vérifier les mots-clés sensibles dans la requête
    request_data = ''
    
    # Extraire les données de la requête
    if request.method == 'GET':
        request_data = ' '.join(request.args.values())
    elif request.is_json:
        try:
            json_data = request.get_json()
            if isinstance(json_data, dict):
                request_data = ' '.join(str(v) for v in json_data.values())
            elif isinstance(json_data, list):
                request_data = ' '.join(str(item) for item in json_data)
            else:
                request_data = str(json_data)
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction des données JSON: {str(e)}")
    elif request.form:
        request_data = ' '.join(request.form.values())
    
    # Vérifier les mots-clés sensibles
    for keyword in SENSITIVE_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', request_data.lower()):
            reason = f"Détection d'un mot-clé sensible: '{keyword}'"
            logger.warning(reason)
            return False, reason
    
    # Vérifier la présence d'informations personnelles sensibles
    for pattern_name, pattern in REGEX_PATTERNS.items():
        matches = re.findall(pattern, request_data)
        if matches:
            # Si nous sommes en mode vérification d'identité, certaines informations sont autorisées
            use_case = request.headers.get('X-Use-Case', '').lower()
            if use_case == 'identity_verification' and pattern_name in ['email', 'phone']:
                continue
                
            reason = f"Détection d'information sensible de type {pattern_name}"
            logger.warning(reason)
            return False, reason
    
    # Vérifier l'adresse IP si elle provient d'un pays restreint
    # Note: Ceci nécessiterait une librairie comme geoip2 pour la géolocalisation IP
    
    # Tout est en ordre
    return True, "Conforme"

def check_compliance_with_gdpr(data_processing_purpose, retention_period):
    """
    Vérifie la conformité avec le RGPD
    Args:
        data_processing_purpose: Finalité du traitement des données
        retention_period: Durée de conservation des données (en jours)
    Returns:
        tuple: (is_compliant, reason)
    """
    # Vérifier que la finalité est explicite
    if not data_processing_purpose or len(data_processing_purpose) < 10:
        return False, "La finalité du traitement doit être explicite et détaillée"
    
    # Vérifier que la durée de conservation est raisonnable
    if retention_period <= 0:
        return False, "La durée de conservation doit être positive"
    
    if retention_period > 365:  # 1 an
        return False, "La durée de conservation ne doit pas excéder 1 an sans justification"
    
    return True, "Conforme au RGPD"

def generate_privacy_notice(data_categories, processing_purposes, retention_period, recipient_categories):
    """
    Génère une notice de confidentialité conforme au RGPD
    Args:
        data_categories: Catégories de données traitées
        processing_purposes: Finalités du traitement
        retention_period: Durée de conservation
        recipient_categories: Catégories de destinataires
    Returns:
        str: Notice de confidentialité
    """
    notice = f"""
# Notice de Confidentialité - TheWatcher

## Données collectées
{', '.join(data_categories)}

## Finalités du traitement
{', '.join(processing_purposes)}

## Durée de conservation
{retention_period} jours

## Destinataires des données
{', '.join(recipient_categories)}

## Droits des personnes concernées
Vous disposez d'un droit d'accès, de rectification, d'effacement, de limitation, de portabilité et d'opposition
concernant vos données personnelles. Pour exercer ces droits, contactez privacy@thewatcher.example.com.
    """
    
    return notice
