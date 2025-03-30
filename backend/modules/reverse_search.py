#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TheWatcher - Module de recherche inversée
Ce module gère les fonctionnalités de recherche d'images inversée
"""

import os
import re
import json
import time
import logging
import requests
import base64
from urllib.parse import urlencode, quote_plus
from PIL import Image
from io import BytesIO
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from config import active_config

# Configuration du logger
logger = logging.getLogger(__name__)

class ReverseImageSearch:
    """Classe pour la recherche d'images inversée"""
    
    def __init__(self, config=None):
        """
        Initialise le moteur de recherche d'images inversée
        Args:
            config: Configuration à utiliser (par défaut: active_config)
        """
        self.config = config or active_config
        self.proxies = self.config.get_proxies() if self.config.PROXY_ENABLED else {}
        self.timeout = self.config.REQUEST_TIMEOUT
        self.google_api_key = self.config.GOOGLE_API_KEY
        
        # Configurer les headers pour simuler un navigateur
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Initialiser Selenium si disponible
        self.selenium_enabled = self._init_selenium()
    
    def _init_selenium(self):
        """
        Initialise Selenium pour les recherches avancées
        Returns:
            bool: True si Selenium est initialisé avec succès, False sinon
        """
        try:
            # Configuration de Chrome en mode headless
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
            
            # Ajouter un proxy si configuré
            if self.config.PROXY_ENABLED:
                proxy_url = f"{self.config.PROXY_TYPE}://{self.config.PROXY_HOST}:{self.config.PROXY_PORT}"
                if self.config.PROXY_USER and self.config.PROXY_PASS:
                    auth = f"{self.config.PROXY_USER}:{self.config.PROXY_PASS}"
                    chrome_options.add_argument(f"--proxy-server={proxy_url}")
                    # Note: L'authentification proxy avec Selenium est plus complexe et peut nécessiter une extension
                else:
                    chrome_options.add_argument(f"--proxy-server={proxy_url}")
            
            # Initialiser le WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            logger.info("Selenium WebDriver initialisé avec succès")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Selenium: {str(e)}")
            return False
    
    def close(self):
        """Ferme les ressources"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium WebDriver fermé")
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture de Selenium: {str(e)}")
    
    def _compress_image(self, image_path, max_size=1000, quality=85):
        """
        Compresse une image pour la recherche
        Args:
            image_path: Chemin vers l'image à compresser
            max_size: Taille maximale en pixels (largeur ou hauteur)
            quality: Qualité de compression JPEG (0-100)
        Returns:
            BytesIO: Objet contenant l'image compressée
        """
        try:
            img = Image.open(image_path)
            
            # Redimensionner si nécessaire
            width, height = img.size
            if width > max_size or height > max_size:
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convertir en RGB si nécessaire (pour les images avec canal alpha)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Compresser l'image
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            return output
        
        except Exception as e:
            logger.error(f"Erreur lors de la compression de l'image: {str(e)}")
            return None
    
    def google_search_api(self, image_path):
        """
        Recherche d'image inversée via l'API Google Vision
        Args:
            image_path: Chemin vers l'image à rechercher
        Returns:
            dict: Résultats de la recherche
        """
        if not self.google_api_key:
            logger.warning("Clé API Google non configurée")
            return {'error': 'Clé API Google non configurée'}
        
        try:
            # Lire et encoder l'image
            with open(image_path, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Préparer la requête
            api_url = f"https://vision.googleapis.com/v1/images:annotate?key={self.google_api_key}"
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": encoded_image
                        },
                        "features": [
                            {
                                "type": "WEB_DETECTION",
                                "maxResults": 50
                            }
                        ]
                    }
                ]
            }
            
            # Envoyer la requête
            response = requests.post(
                api_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur API Google Vision: {response.status_code} - {response.text}")
                return {'error': f"Erreur API Google Vision: {response.status_code}"}
            
            # Traiter les résultats
            results = response.json()
            
            # Extraire les informations pertinentes
            web_detection = results.get('responses', [{}])[0].get('webDetection', {})
            
            processed_results = {
                'full_matches': web_detection.get('fullMatchingImages', []),
                'partial_matches': web_detection.get('partialMatchingImages', []),
                'pages_with_image': web_detection.get('pagesWithMatchingImages', []),
                'visually_similar': web_detection.get('visuallySimilarImages', []),
                'web_entities': web_detection.get('webEntities', [])
            }
            
            logger.info(f"Recherche Google Vision réussie: {len(processed_results['full_matches'])} correspondances complètes trouvées")
            return processed_results
        
        except Exception as e:
            logger.error(f"Erreur lors de la recherche Google Vision: {str(e)}")
            return {'error': str(e)}
    
    def google_search(self, image_path):
        """
        Recherche d'image inversée via Google Images (web scraping)
        Args:
            image_path: Chemin vers l'image à rechercher
        Returns:
            dict: Résultats de la recherche
        """
        if not self.selenium_enabled:
            logger.warning("Selenium non disponible pour la recherche Google")
            return {'error': 'Selenium non disponible'}
        
        try:
            # Délai aléatoire pour éviter la détection
            time.sleep(random.uniform(1, 3))
            
            # Accéder à Google Images
            self.driver.get('https://images.google.com/')
            
            # Cliquer sur l'icône de recherche par image
            search_by_image_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Recherche par image' or @aria-label='Search by image']"))
            )
            search_by_image_button.click()
            
            # Cliquer sur "Importer une image"
            upload_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Importer') or contains(text(), 'Upload')]"))
            )
            upload_button.click()
            
            # Trouver le champ de téléchargement de fichier
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            
            # Télécharger l'image
            file_input.send_keys(os.path.abspath(image_path))
            
            # Attendre les résultats
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            # Attendre un peu pour que tous les résultats se chargent
            time.sleep(3)
            
            # Extraire les résultats
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Analyser les résultats
            results = {
                'similar_images': [],
                'websites': [],
                'best_guess': None
            }
            
            # Récupérer les sites web contenant l'image
            website_elements = soup.select(".Psd1Cc")
            for element in website_elements:
                title_elem = element.select_one(".MLSGY")
                url_elem = element.select_one(".KjWMVd")
                description_elem = element.select_one(".VjqMgc")
                
                if title_elem and url_elem:
                    results['websites'].append({
                        'title': title_elem.get_text(),
                        'url': url_elem.get('href'),
                        'description': description_elem.get_text() if description_elem else ''
                    })
            
            # Récupérer la meilleure supposition (best guess)
            best_guess_elem = soup.select_one(".fKDtNb")
            if best_guess_elem:
                results['best_guess'] = best_guess_elem.get_text()
            
            # Récupérer les images similaires
            similar_images_elements = soup.select(".isv-r")
            for element in similar_images_elements:
                img_elem = element.select_one("img.Q4LuWd")
                link_elem = element.select_one("a")
                
                if img_elem and link_elem:
                    img_url = img_elem.get('src')
                    if img_url and not img_url.startswith('data:'):
                        results['similar_images'].append({
                            'url': img_url,
                            'page_url': link_elem.get('href') if link_elem.get('href') and link_elem.get('href').startswith('http') else None
                        })
            
            logger.info(f"Recherche Google Images réussie: {len(results['websites'])} sites web et {len(results['similar_images'])} images similaires trouvées")
            return results
        
        except TimeoutException as e:
            logger.error(f"Timeout lors de la recherche Google Images: {str(e)}")
            return {'error': 'Timeout lors de la recherche'}
        
        except WebDriverException as e:
            logger.error(f"Erreur Selenium lors de la recherche Google Images: {str(e)}")
            return {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Erreur lors de la recherche Google Images: {str(e)}")
            return {'error': str(e)}
    
    def yandex_search(self, image_path):
        """
        Recherche d'image inversée via Yandex Images
        Args:
            image_path: Chemin vers l'image à rechercher
        Returns:
            dict: Résultats de la recherche
        """
        if not self.selenium_enabled:
            logger.warning("Selenium non disponible pour la recherche Yandex")
            return {'error': 'Selenium non disponible'}
        
        try:
            # Délai aléatoire pour éviter la détection
            time.sleep(random.uniform(2, 4))
            
            # Accéder à Yandex Images
            self.driver.get('https://yandex.com/images/')
            
            # Cliquer sur l'icône de recherche par image
            search_by_image_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".icon_type_cbir"))
            )
            search_by_image_button.click()
            
            # Trouver le champ de téléchargement de fichier
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".cbir-panel__file-input"))
            )
            
            # Télécharger l'image
            file_input.send_keys(os.path.abspath(image_path))
            
            # Attendre les résultats
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".serp-list"))
            )
            
            # Attendre un peu pour que tous les résultats se chargent
            time.sleep(3)
            
            # Extraire les résultats
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Analyser les résultats
            results = {
                'similar_images': [],
                'websites': [],
                'categories': []
            }
            
            # Récupérer les sites web
            website_elements = soup.select(".serp-item")
            for element in website_elements:
                title_elem = element.select_one(".serp-item__title")
                link_elem = element.select_one(".serp-item__link")
                thumb_elem = element.select_one(".serp-item__thumb")
                
                if title_elem and link_elem:
                    site_info = {
                        'title': title_elem.get_text(),
                        'url': link_elem.get('href'),
                        'thumbnail': thumb_elem.get('src') if thumb_elem else None
                    }
                    
                    # Vérifier si c'est une image ou un site web
                    if thumb_elem and 'thumb' in str(thumb_elem):
                        results['similar_images'].append(site_info)
                    else:
                        results['websites'].append(site_info)
            
            # Récupérer les catégories suggérées
            category_elements = soup.select(".cbir-recognition__group")
            for element in category_elements:
                category_name = element.select_one(".cbir-recognition__group-title")
                category_items = element.select(".cbir-recognition__label")
                
                if category_name:
                    category = {
                        'name': category_name.get_text(),
                        'items': [item.get_text() for item in category_items if item]
                    }
                    results['categories'].append(category)
            
            logger.info(f"Recherche Yandex réussie: {len(results['websites'])} sites web et {len(results['similar_images'])} images similaires trouvées")
            return results
        
        except TimeoutException as e:
            logger.error(f"Timeout lors de la recherche Yandex: {str(e)}")
            return {'error': 'Timeout lors de la recherche'}
        
        except WebDriverException as e:
            logger.error(f"Erreur Selenium lors de la recherche Yandex: {str(e)}")
            return {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Erreur lors de la recherche Yandex: {str(e)}")
            return {'error': str(e)}
    
    def tineye_search(self, image_path):
        """
        Recherche d'image inversée via TinEye
        Args:
            image_path: Chemin vers l'image à rechercher
        Returns:
            dict: Résultats de la recherche
        """
        if not self.selenium_enabled:
            logger.warning("Selenium non disponible pour la recherche TinEye")
            return {'error': 'Selenium non disponible'}
        
        try:
            # Délai aléatoire pour éviter la détection
            time.sleep(random.uniform(2, 5))
            
            # Accéder à TinEye
            self.driver.get('https://tineye.com/')
            
            # Trouver le champ de téléchargement de fichier
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "image"))
            )
            
            # Télécharger l'image
            file_input.send_keys(os.path.abspath(image_path))
            
            # Attendre les résultats
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "match-row"))
            )
            
            # Attendre un peu pour que tous les résultats se chargent
            time.sleep(3)
            
            # Extraire les résultats
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Analyser les résultats
            results = {
                'matches': [],
                'total_results': 0,
                'domains': []
            }
            
            # Récupérer le nombre total de résultats
            total_results_elem = soup.select_one(".matches strong")
            if total_results_elem:
                try:
                    results['total_results'] = int(total_results_elem.get_text().replace(',', ''))
                except ValueError:
                    pass
            
            # Récupérer les correspondances
            match_elements = soup.select(".match-row")
            for element in match_elements:
                image_tag = element.select_one(".match-img img")
                link_tag = element.select_one(".match-details .item-link a")
                domain_tag = element.select_one(".match-details .domains a")
                size_tag = element.select_one(".match-details .image-detail-size")
                
                if image_tag and link_tag:
                    match = {
                        'thumbnail': image_tag.get('src'),
                        'url': link_tag.get('href'),
                        'domain': domain_tag.get_text() if domain_tag else None,
                        'size': size_tag.get_text() if size_tag else None
                    }
                    results['matches'].append(match)
            
            # Récupérer les domaines
            domain_elements = soup.select(".sidebar-domains .domain-link")
            for element in domain_elements:
                domain_name = element.select_one(".domain-name")
                domain_count = element.select_one(".domain-count")
                
                if domain_name and domain_count:
                    domain = {
                        'name': domain_name.get_text(),
                        'count': domain_count.get_text().strip('()')
                    }
                    results['domains'].append(domain)
            
            logger.info(f"Recherche TinEye réussie: {results['total_results']} correspondances trouvées")
            return results
        
        except TimeoutException as e:
            logger.error(f"Timeout lors de la recherche TinEye: {str(e)}")
            return {'error': 'Timeout lors de la recherche'}
        
        except WebDriverException as e:
            logger.error(f"Erreur Selenium lors de la recherche TinEye: {str(e)}")
            return {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Erreur lors de la recherche TinEye: {str(e)}")
            return {'error': str(e)}
    
    def search_all(self, image_path):
        """
        Effectue une recherche sur tous les moteurs disponibles
        Args:
            image_path: Chemin vers l'image à rechercher
        Returns:
            dict: Résultats combinés de tous les moteurs de recherche
        """
        results = {}
        
        # Google API (si clé disponible)
        if self.google_api_key:
            results['google_api'] = self.google_search_api(image_path)
        
        # Google Images (web scraping)
        if self.selenium_enabled:
            results['google'] = self.google_search(image_path)
            
            # Pause pour éviter la détection
            time.sleep(random.uniform(3, 6))
            
            results['yandex'] = self.yandex_search(image_path)
            
            # Pause pour éviter la détection
            time.sleep(random.uniform(3, 6))
            
            results['tineye'] = self.tineye_search(image_path)
        
        return results
