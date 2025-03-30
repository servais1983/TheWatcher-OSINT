#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TheWatcher - Module OSINT pour les réseaux sociaux
Ce module gère les recherches d'informations sur les réseaux sociaux
"""

import os
import re
import json
import time
import logging
import requests
import subprocess
import random
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

from config import active_config

# Configuration du logger
logger = logging.getLogger(__name__)

class SocialOSINT:
    """Classe pour les recherches OSINT sur les réseaux sociaux"""
    
    def __init__(self, config=None):
        """
        Initialise le moteur de recherche sociale
        Args:
            config: Configuration à utiliser (par défaut: active_config)
        """
        self.config = config or active_config
        self.proxies = self.config.get_proxies() if self.config.PROXY_ENABLED else {}
        self.timeout = self.config.REQUEST_TIMEOUT
        self.sherlock_path = self.config.SHERLOCK_PATH
        self.hunter_api_key = self.config.HUNTER_API_KEY
        
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
    
    def run_sherlock(self, username):
        """
        Exécute Sherlock pour trouver des comptes sur les réseaux sociaux
        Args:
            username: Nom d'utilisateur à rechercher
        Returns:
            dict: Résultats de la recherche
        """
        if not os.path.exists(self.sherlock_path):
            logger.error(f"Sherlock non trouvé dans {self.sherlock_path}")
            return {'error': 'Sherlock non trouvé'}
        
        try:
            # Préparer le répertoire de sortie
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sherlock')
            os.makedirs(output_dir, exist_ok=True)
            
            result_file = os.path.join(output_dir, f"{username}.json")
            
            # Exécuter Sherlock
            cmd = [
                'python3', 
                os.path.join(self.sherlock_path, 'sherlock.py'), 
                username,
                '--timeout', str(self.timeout),
                '--print-found',
                '--output', result_file,
                '--json'
            ]
            
            # Ajouter le proxy si configuré
            if self.config.PROXY_ENABLED:
                proxy_url = f"{self.config.PROXY_TYPE}://"
                if self.config.PROXY_USER and self.config.PROXY_PASS:
                    proxy_url += f"{self.config.PROXY_USER}:{self.config.PROXY_PASS}@"
                proxy_url += f"{self.config.PROXY_HOST}:{self.config.PROXY_PORT}"
                cmd.extend(['--proxy', proxy_url])
            
            logger.info(f"Exécution de Sherlock pour '{username}'")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=300)  # 5 minutes max
            
            if process.returncode != 0:
                logger.error(f"Erreur lors de l'exécution de Sherlock: {stderr.decode('utf-8')}")
                return {'error': f"Erreur lors de l'exécution de Sherlock: {stderr.decode('utf-8')}"}
            
            # Lire les résultats
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    results = json.load(f)
                logger.info(f"Sherlock a trouvé {len(results)} comptes pour '{username}'")
                return {'accounts': results}
            else:
                logger.warning(f"Fichier de résultats Sherlock non trouvé: {result_file}")
                return {'accounts': {}}
        
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout lors de l'exécution de Sherlock pour '{username}'")
            return {'error': 'Timeout lors de l\'exécution de Sherlock'}
        
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de Sherlock: {str(e)}")
            return {'error': str(e)}
    
    def search_emails(self, domain):
        """
        Recherche des adresses email associées à un domaine via Hunter.io
        Args:
            domain: Domaine à rechercher (ex: example.com)
        Returns:
            dict: Résultats de la recherche
        """
        if not self.hunter_api_key:
            logger.warning("Clé API Hunter.io non configurée")
            return {'error': 'Clé API Hunter.io non configurée'}
        
        try:
            # Préparer la requête
            api_url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.hunter_api_key}"
            
            # Envoyer la requête
            response = requests.get(
                api_url,
                headers=self.headers,
                proxies=self.proxies,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur API Hunter.io: {response.status_code} - {response.text}")
                return {'error': f"Erreur API Hunter.io: {response.status_code}"}
            
            # Traiter les résultats
            data = response.json()
            
            # Structurer les résultats
            results = {
                'domain': domain,
                'emails': data.get('data', {}).get('emails', []),
                'pattern': data.get('data', {}).get('pattern', None),
                'organization': data.get('data', {}).get('organization', None),
                'meta': {
                    'results': data.get('meta', {}).get('results', 0),
                    'limit': data.get('meta', {}).get('limit', 0)
                }
            }
            
            logger.info(f"Recherche Hunter.io réussie: {results['meta']['results']} emails trouvés pour '{domain}'")
            return results
        
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la requête à Hunter.io: {str(e)}")
            return {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'emails: {str(e)}")
            return {'error': str(e)}
    
    def search_linkedin(self, name, company=None):
        """
        Recherche des profils LinkedIn
        Args:
            name: Nom de la personne
            company: Entreprise (facultatif)
        Returns:
            dict: Résultats de la recherche
        """
        if not self.selenium_enabled:
            logger.warning("Selenium non disponible pour la recherche LinkedIn")
            return {'error': 'Selenium non disponible'}
        
        try:
            # Construire la requête
            query = f"{name}"
            if company:
                query += f" {company}"
            
            # Accéder à Google Search (pour éviter les limites de LinkedIn)
            search_url = f"https://www.google.com/search?q=site:linkedin.com/in/ {quote_plus(query)}"
            
            # Délai aléatoire pour éviter la détection
            time.sleep(random.uniform(1, 3))
            
            # Charger la page
            self.driver.get(search_url)
            
            # Attendre les résultats
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            # Extraire les résultats
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            results = []
            
            # Récupérer les liens de profils LinkedIn
            for g in soup.select('.g'):
                link_elem = g.select_one('a')
                title_elem = g.select_one('h3')
                description_elem = g.select_one('.VwiC3b')
                
                if link_elem and title_elem:
                    url = link_elem['href']
                    # Vérifier que c'est bien un profil LinkedIn
                    if 'linkedin.com/in/' in url:
                        profile = {
                            'name': title_elem.get_text(),
                            'url': url,
                            'description': description_elem.get_text() if description_elem else None
                        }
                        results.append(profile)
            
            logger.info(f"Recherche LinkedIn réussie: {len(results)} profils trouvés pour '{query}'")
            return {'profiles': results}
        
        except TimeoutException as e:
            logger.error(f"Timeout lors de la recherche LinkedIn: {str(e)}")
            return {'error': 'Timeout lors de la recherche'}
        
        except WebDriverException as e:
            logger.error(f"Erreur Selenium lors de la recherche LinkedIn: {str(e)}")
            return {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Erreur lors de la recherche LinkedIn: {str(e)}")
            return {'error': str(e)}
    
    def search_facebook(self, name, location=None):
        """
        Recherche des profils Facebook
        Args:
            name: Nom de la personne
            location: Localisation (facultatif)
        Returns:
            dict: Résultats de la recherche
        """
        if not self.selenium_enabled:
            logger.warning("Selenium non disponible pour la recherche Facebook")
            return {'error': 'Selenium non disponible'}
        
        try:
            # Construire la requête
            query = f"{name}"
            if location:
                query += f" {location}"
            
            # Accéder à Google Search (pour éviter les limites de Facebook)
            search_url = f"https://www.google.com/search?q=site:facebook.com {quote_plus(query)}"
            
            # Délai aléatoire pour éviter la détection
            time.sleep(random.uniform(1, 3))
            
            # Charger la page
            self.driver.get(search_url)
            
            # Attendre les résultats
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            # Extraire les résultats
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            results = []
            
            # Récupérer les liens de profils Facebook
            for g in soup.select('.g'):
                link_elem = g.select_one('a')
                title_elem = g.select_one('h3')
                description_elem = g.select_one('.VwiC3b')
                
                if link_elem and title_elem:
                    url = link_elem['href']
                    # Vérifier que c'est bien un profil ou une page Facebook
                    if 'facebook.com/' in url and not 'facebook.com/search' in url:
                        profile = {
                            'name': title_elem.get_text(),
                            'url': url,
                            'description': description_elem.get_text() if description_elem else None
                        }
                        results.append(profile)
            
            logger.info(f"Recherche Facebook réussie: {len(results)} profils trouvés pour '{query}'")
            return {'profiles': results}
        
        except TimeoutException as e:
            logger.error(f"Timeout lors de la recherche Facebook: {str(e)}")
            return {'error': 'Timeout lors de la recherche'}
        
        except WebDriverException as e:
            logger.error(f"Erreur Selenium lors de la recherche Facebook: {str(e)}")
            return {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Erreur lors de la recherche Facebook: {str(e)}")
            return {'error': str(e)}
    
    def search_twitter(self, name, username=None):
        """
        Recherche des profils Twitter
        Args:
            name: Nom de la personne
            username: Nom d'utilisateur (facultatif)
        Returns:
            dict: Résultats de la recherche
        """
        if not self.selenium_enabled:
            logger.warning("Selenium non disponible pour la recherche Twitter")
            return {'error': 'Selenium non disponible'}
        
        try:
            # Construire la requête
            query = f"{name}"
            if username:
                query += f" {username}"
            
            # Accéder à Google Search
            search_url = f"https://www.google.com/search?q=site:twitter.com {quote_plus(query)}"
            
            # Délai aléatoire pour éviter la détection
            time.sleep(random.uniform(1, 3))
            
            # Charger la page
            self.driver.get(search_url)
            
            # Attendre les résultats
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            # Extraire les résultats
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            results = []
            
            # Récupérer les liens de profils Twitter
            for g in soup.select('.g'):
                link_elem = g.select_one('a')
                title_elem = g.select_one('h3')
                description_elem = g.select_one('.VwiC3b')
                
                if link_elem and title_elem:
                    url = link_elem['href']
                    # Vérifier que c'est bien un profil Twitter
                    if 'twitter.com/' in url and not any(x in url for x in ['twitter.com/search', 'twitter.com/hashtag']):
                        profile = {
                            'name': title_elem.get_text(),
                            'url': url,
                            'description': description_elem.get_text() if description_elem else None
                        }
                        results.append(profile)
            
            logger.info(f"Recherche Twitter réussie: {len(results)} profils trouvés pour '{query}'")
            return {'profiles': results}
        
        except TimeoutException as e:
            logger.error(f"Timeout lors de la recherche Twitter: {str(e)}")
            return {'error': 'Timeout lors de la recherche'}
        
        except WebDriverException as e:
            logger.error(f"Erreur Selenium lors de la recherche Twitter: {str(e)}")
            return {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Erreur lors de la recherche Twitter: {str(e)}")
            return {'error': str(e)}
    
    def search_instagram(self, name, username=None):
        """
        Recherche des profils Instagram
        Args:
            name: Nom de la personne
            username: Nom d'utilisateur (facultatif)
        Returns:
            dict: Résultats de la recherche
        """
        if not self.selenium_enabled:
            logger.warning("Selenium non disponible pour la recherche Instagram")
            return {'error': 'Selenium non disponible'}
        
        try:
            # Construire la requête
            query = f"{name}"
            if username:
                query += f" {username}"
            
            # Accéder à Google Search
            search_url = f"https://www.google.com/search?q=site:instagram.com {quote_plus(query)}"
            
            # Délai aléatoire pour éviter la détection
            time.sleep(random.uniform(1, 3))
            
            # Charger la page
            self.driver.get(search_url)
            
            # Attendre les résultats
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            # Extraire les résultats
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            results = []
            
            # Récupérer les liens de profils Instagram
            for g in soup.select('.g'):
                link_elem = g.select_one('a')
                title_elem = g.select_one('h3')
                description_elem = g.select_one('.VwiC3b')
                
                if link_elem and title_elem:
                    url = link_elem['href']
                    # Vérifier que c'est bien un profil Instagram
                    if 'instagram.com/' in url and not 'instagram.com/p/' in url:
                        profile = {
                            'name': title_elem.get_text(),
                            'url': url,
                            'description': description_elem.get_text() if description_elem else None
                        }
                        results.append(profile)
            
            logger.info(f"Recherche Instagram réussie: {len(results)} profils trouvés pour '{query}'")
            return {'profiles': results}
        
        except TimeoutException as e:
            logger.error(f"Timeout lors de la recherche Instagram: {str(e)}")
            return {'error': 'Timeout lors de la recherche'}
        
        except WebDriverException as e:
            logger.error(f"Erreur Selenium lors de la recherche Instagram: {str(e)}")
            return {'error': str(e)}
        
        except Exception as e:
            logger.error(f"Erreur lors de la recherche Instagram: {str(e)}")
            return {'error': str(e)}
    
    def search_person(self, name, location=None, company=None):
        """
        Recherche complète d'une personne sur tous les réseaux sociaux
        Args:
            name: Nom de la personne
            location: Localisation (facultatif)
            company: Entreprise (facultatif)
        Returns:
            dict: Résultats combinés de toutes les recherches
        """
        results = {
            'name': name,
            'location': location,
            'company': company,
            'profiles': {}
        }
        
        # Recherche sur LinkedIn
        linkedin_results = self.search_linkedin(name, company)
        if 'profiles' in linkedin_results:
            results['profiles']['linkedin'] = linkedin_results['profiles']
        
        # Pause pour éviter la détection
        time.sleep(random.uniform(2, 5))
        
        # Recherche sur Facebook
        facebook_results = self.search_facebook(name, location)
        if 'profiles' in facebook_results:
            results['profiles']['facebook'] = facebook_results['profiles']
        
        # Pause pour éviter la détection
        time.sleep(random.uniform(2, 5))
        
        # Recherche sur Twitter
        twitter_results = self.search_twitter(name)
        if 'profiles' in twitter_results:
            results['profiles']['twitter'] = twitter_results['profiles']
        
        # Pause pour éviter la détection
        time.sleep(random.uniform(2, 5))
        
        # Recherche sur Instagram
        instagram_results = self.search_instagram(name)
        if 'profiles' in instagram_results:
            results['profiles']['instagram'] = instagram_results['profiles']
        
        # Calculer les statistiques
        total_profiles = sum(len(profiles) for platform, profiles in results['profiles'].items())
        results['stats'] = {
            'total_profiles': total_profiles,
            'platforms': len(results['profiles']),
        }
        
        logger.info(f"Recherche complète pour '{name}' terminée: {total_profiles} profils trouvés sur {len(results['profiles'])} plateformes")
        return results
    
    def search_username(self, username):
        """
        Recherche un nom d'utilisateur sur tous les réseaux sociaux via Sherlock
        Args:
            username: Nom d'utilisateur à rechercher
        Returns:
            dict: Résultats de la recherche
        """
        results = {
            'username': username,
            'accounts': {}
        }
        
        # Utiliser Sherlock pour une recherche complète
        sherlock_results = self.run_sherlock(username)
        if 'accounts' in sherlock_results:
            results['accounts'] = sherlock_results['accounts']
        
        # Calculer les statistiques
        results['stats'] = {
            'total_accounts': len(results['accounts']),
            'platforms': list(results['accounts'].keys()) if isinstance(results['accounts'], dict) else []
        }
        
        logger.info(f"Recherche du nom d'utilisateur '{username}' terminée: {len(results['accounts'])} comptes trouvés")
        return results
