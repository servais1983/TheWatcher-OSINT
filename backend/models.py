#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TheWatcher - Modèles de base de données
Ce module définit les modèles SQLAlchemy pour l'application
"""

import json
import uuid
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import bcrypt

# Initialiser SQLAlchemy
db = SQLAlchemy()

class Base(db.Model):
    """Classe de base pour tous les modèles"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(Base):
    """Modèle pour les utilisateurs"""
    __tablename__ = 'users'
    
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime)
    mfa_secret = Column(String(32))
    mfa_enabled = Column(Boolean, default=False)
    api_key = Column(String(64), unique=True)
    
    # Relations
    searches = relationship('SearchHistory', back_populates='user')
    
    def __init__(self, username, email, password, **kwargs):
        """
        Initialise un nouvel utilisateur avec un mot de passe hashé
        """
        super(User, self).__init__(**kwargs)
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        """
        Hash et stocke le mot de passe
        """
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, password):
        """
        Vérifie si le mot de passe fourni correspond au hash stocké
        """
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )
    
    def generate_api_key(self):
        """
        Génère une nouvelle clé API pour l'utilisateur
        """
        self.api_key = uuid.uuid4().hex
        return self.api_key
    
    def to_dict(self):
        """
        Convertit l'utilisateur en dictionnaire, en omettant les champs sensibles
        """
        data = super().to_dict()
        del data['password_hash']
        del data['mfa_secret']
        return data


class SearchHistory(Base):
    """Modèle pour l'historique des recherches"""
    __tablename__ = 'search_history'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    search_type = Column(String(20), nullable=False)  # 'name', 'photo', etc.
    search_term = Column(Text, nullable=False)
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    consent_given = Column(Boolean, default=False)
    use_case = Column(String(50))
    results_count = Column(Integer, default=0)
    execution_time = Column(Integer)  # En millisecondes
    search_parameters = Column(JSONB)
    
    # Relations
    user = relationship('User', back_populates='searches')
    results = relationship('SearchResult', back_populates='search')
    
    @staticmethod
    def create_from_request(request, user=None, search_type='', search_term='', results_count=0, execution_time=0):
        """
        Crée un nouvel enregistrement d'historique à partir d'une requête HTTP
        """
        search = SearchHistory(
            user_id=user.id if user else None,
            search_type=search_type,
            search_term=search_term,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            consent_given=request.headers.get('X-Ethical-Consent', '').lower() == 'true',
            use_case=request.headers.get('X-Use-Case', ''),
            results_count=results_count,
            execution_time=execution_time,
            search_parameters=request.json or {}
        )
        db.session.add(search)
        db.session.commit()
        return search


class SearchResult(Base):
    """Modèle pour les résultats de recherche"""
    __tablename__ = 'search_results'
    
    search_id = Column(UUID(as_uuid=True), ForeignKey('search_history.id'), nullable=False)
    result_type = Column(String(50))  # 'social_profile', 'image_match', etc.
    source = Column(String(100))  # 'facebook', 'linkedin', etc.
    confidence = Column(Integer)  # 0-100
    data = Column(JSONB)
    
    # Relations
    search = relationship('SearchHistory', back_populates='results')


class AuditLog(Base):
    """Modèle pour les logs d'audit de sécurité"""
    __tablename__ = 'audit_logs'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    action = Column(String(50), nullable=False)
    resource = Column(String(100))
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    details = Column(JSONB)
    status = Column(String(10))  # 'success', 'failure', 'denied'
    
    @staticmethod
    def create_from_request(request, action='access', resource=None, user=None, details=None, status='success'):
        """
        Crée un nouvel enregistrement d'audit à partir d'une requête HTTP
        """
        log = AuditLog(
            user_id=user.id if user else None,
            action=action,
            resource=resource or request.path,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            details=details or {
                'method': request.method,
                'params': request.args.to_dict(),
                'json': request.get_json(silent=True)
            },
            status=status
        )
        db.session.add(log)
        db.session.commit()
        return log
