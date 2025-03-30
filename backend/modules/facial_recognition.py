#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TheWatcher - Module de reconnaissance faciale
Ce module gère les fonctionnalités de détection et reconnaissance faciale
"""

import os
import cv2
import logging
import numpy as np
import face_recognition
import boto3
from botocore.exceptions import ClientError
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

from config import active_config

# Configuration du logger
logger = logging.getLogger(__name__)

class FaceDetector:
    """Classe pour la détection et reconnaissance faciale"""
    
    def __init__(self, config=None):
        """
        Initialise le détecteur facial
        Args:
            config: Configuration à utiliser (par défaut: active_config)
        """
        self.config = config or active_config
        self.face_match_threshold = self.config.FACE_MATCH_THRESHOLD
        
        # Initialiser le client AWS Rekognition si nécessaire
        if self.config.AWS_ACCESS_KEY_ID and self.config.AWS_SECRET_ACCESS_KEY:
            try:
                self.rekognition = boto3.client(
                    'rekognition',
                    aws_access_key_id=self.config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=self.config.AWS_SECRET_ACCESS_KEY,
                    region_name=self.config.AWS_REGION
                )
                logger.info("Client AWS Rekognition initialisé")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du client AWS Rekognition: {str(e)}")
                self.rekognition = None
        else:
            self.rekognition = None
            logger.warning("Clés AWS non configurées, la reconnaissance faciale via Rekognition ne sera pas disponible")
    
    def detect_faces(self, image_path):
        """
        Détecte les visages dans une image et renvoie leurs positions
        Args:
            image_path: Chemin vers l'image à analyser
        Returns:
            list: Liste des visages détectés [(top, right, bottom, left), ...]
        """
        try:
            # Charger l'image et détecter les visages
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            
            logger.info(f"Détection de {len(face_locations)} visages dans l'image")
            return face_locations
        
        except Exception as e:
            logger.error(f"Erreur lors de la détection des visages: {str(e)}")
            return []
    
    def recognize_faces(self, image_path, reference_images):
        """
        Compare les visages d'une image avec des images de référence
        Args:
            image_path: Chemin vers l'image à analyser
            reference_images: Liste de chemins vers des images de référence
        Returns:
            list: Liste des correspondances avec leur score de confiance
        """
        try:
            # Charger l'image cible
            unknown_image = face_recognition.load_image_file(image_path)
            unknown_encodings = face_recognition.face_encodings(unknown_image)
            
            if not unknown_encodings:
                logger.warning(f"Aucun visage détecté dans l'image à analyser: {image_path}")
                return []
            
            matches = []
            
            # Parcourir les images de référence
            for ref_path in reference_images:
                try:
                    # Charger l'image de référence
                    ref_image = face_recognition.load_image_file(ref_path)
                    ref_encodings = face_recognition.face_encodings(ref_image)
                    
                    if not ref_encodings:
                        logger.warning(f"Aucun visage détecté dans l'image de référence: {ref_path}")
                        continue
                    
                    # Comparer les visages
                    for unknown_encoding in unknown_encodings:
                        for ref_encoding in ref_encodings:
                            # Calculer la distance faciale (plus c'est petit, plus c'est similaire)
                            face_distance = face_recognition.face_distance([ref_encoding], unknown_encoding)[0]
                            
                            # Convertir en pourcentage de confiance (0-100)
                            confidence = (1 - face_distance) * 100
                            
                            if confidence >= self.face_match_threshold:
                                matches.append({
                                    'reference_image': ref_path,
                                    'confidence': confidence,
                                    'face_distance': face_distance
                                })
                
                except Exception as e:
                    logger.error(f"Erreur lors de l'analyse de l'image de référence {ref_path}: {str(e)}")
            
            # Trier les correspondances par confiance (décroissante)
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            return matches
        
        except Exception as e:
            logger.error(f"Erreur lors de la reconnaissance faciale: {str(e)}")
            return []
    
    def aws_face_analysis(self, image_path):
        """
        Analyse faciale avancée via AWS Rekognition
        Args:
            image_path: Chemin vers l'image à analyser
        Returns:
            dict: Résultats de l'analyse faciale
        """
        if not self.rekognition:
            logger.warning("AWS Rekognition n'est pas configuré")
            return {'error': 'AWS Rekognition non configuré'}
        
        try:
            # Lire l'image
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
            
            # Détecter les visages et attributs
            response = self.rekognition.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )
            
            logger.info(f"Analyse faciale AWS réussie: {len(response.get('FaceDetails', []))} visages détectés")
            return response
        
        except ClientError as e:
            logger.error(f"Erreur AWS Rekognition: {str(e)}")
            return {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse faciale AWS: {str(e)}")
            return {'error': str(e)}
    
    def compare_faces_with_public_db(self, image_path, collection_id=None):
        """
        Compare les visages avec une collection de référence dans AWS Rekognition
        Note: Cette fonction nécessite une collection préalablement créée
        Args:
            image_path: Chemin vers l'image à analyser
            collection_id: ID de la collection à utiliser
        Returns:
            list: Liste des correspondances trouvées
        """
        if not self.rekognition:
            logger.warning("AWS Rekognition n'est pas configuré")
            return []
        
        if not collection_id:
            logger.warning("Aucune collection spécifiée pour la comparaison faciale")
            return []
        
        try:
            # Lire l'image
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
            
            # Rechercher des correspondances dans la collection
            response = self.rekognition.search_faces_by_image(
                CollectionId=collection_id,
                Image={'Bytes': image_bytes},
                MaxFaces=10,
                FaceMatchThreshold=self.face_match_threshold
            )
            
            # Extraire les correspondances
            matches = []
            for match in response.get('FaceMatches', []):
                matches.append({
                    'face_id': match['Face']['FaceId'],
                    'confidence': match['Similarity'],
                    'external_image_id': match['Face'].get('ExternalImageId', 'unknown')
                })
            
            logger.info(f"Comparaison faciale: {len(matches)} correspondances trouvées")
            return matches
        
        except ClientError as e:
            logger.error(f"Erreur AWS Rekognition: {str(e)}")
            return []
        
        except Exception as e:
            logger.error(f"Erreur lors de la comparaison faciale: {str(e)}")
            return []
    
    def extract_faces(self, image_path, output_dir):
        """
        Extrait les visages d'une image et les sauvegarde dans des fichiers séparés
        Args:
            image_path: Chemin vers l'image à analyser
            output_dir: Répertoire de sortie pour les visages extraits
        Returns:
            list: Liste des chemins vers les visages extraits
        """
        try:
            # S'assurer que le répertoire de sortie existe
            os.makedirs(output_dir, exist_ok=True)
            
            # Charger l'image
            image = face_recognition.load_image_file(image_path)
            pil_image = Image.fromarray(image)
            
            # Détecter les visages
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                logger.warning(f"Aucun visage détecté dans l'image: {image_path}")
                return []
            
            # Extraire et sauvegarder chaque visage
            extracted_faces = []
            for i, (top, right, bottom, left) in enumerate(face_locations):
                # Ajouter une marge autour du visage (20%)
                height = bottom - top
                width = right - left
                
                top = max(0, top - int(height * 0.2))
                bottom = min(image.shape[0], bottom + int(height * 0.2))
                left = max(0, left - int(width * 0.2))
                right = min(image.shape[1], right + int(width * 0.2))
                
                # Extraire le visage
                face_image = pil_image.crop((left, top, right, bottom))
                
                # Générer un nom de fichier
                face_path = os.path.join(output_dir, f"face_{i+1}.jpg")
                
                # Sauvegarder le visage
                face_image.save(face_path)
                extracted_faces.append(face_path)
            
            logger.info(f"Extraction de {len(extracted_faces)} visages réussie")
            return extracted_faces
        
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des visages: {str(e)}")
            return []
