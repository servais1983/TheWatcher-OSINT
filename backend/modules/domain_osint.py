#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TheWatcher - Module OSINT pour domaines
Ce module gère les fonctionnalités d'analyse OSINT pour les domaines web
"""

import os
import logging
import requests
import dns.resolver
import shodan
import whois
from datetime import datetime
from urllib.parse import urlparse

from config import active_config

# Configuration du logger
logger = logging.getLogger(__name__)

class DomainInvestigator:
    """Classe pour l'investigation de domaines et adresses IP"""
    
    def __init__(self, config=None):
        """
        Initialise l'investigateur de domaines
        Args:
            config: Configuration à utiliser (par défaut: active_config)
        """
        self.config = config or active_config
        
        # Initialiser l'API Shodan si la clé est disponible
        if self.config.SHODAN_API_KEY:
            try:
                self.shodan_api = shodan.Shodan(self.config.SHODAN_API_KEY)
                logger.info("API Shodan initialisée")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation de l'API Shodan: {str(e)}")
                self.shodan_api = None
        else:
            self.shodan_api = None
            logger.warning("Clé API Shodan non configurée, les fonctionnalités Shodan seront désactivées")
    
    def analyze_domain(self, domain):
        """
        Effectue une analyse OSINT complète d'un domaine
        Args:
            domain: Nom de domaine à analyser
        Returns:
            dict: Résultats de l'analyse du domaine
        """
        if not domain:
            return {}
        
        # Nettoyer le domaine (supprimer le protocole et le chemin)
        clean_domain = self._clean_domain(domain)
        
        try:
            results = {
                "domain": clean_domain,
                "timestamp": datetime.now().isoformat(),
                "whois": self.get_whois_info(clean_domain),
                "dns_records": self.get_dns_records(clean_domain),
                "subdomains": self.find_subdomains(clean_domain),
                "security_headers": self.check_security_headers(domain),
                "http_info": self.get_http_info(domain),
            }
            
            # Ajouter les infos Shodan si disponibles
            if self.shodan_api:
                results["shodan_info"] = self.get_shodan_info(clean_domain)
            
            logger.info(f"Analyse complète du domaine {clean_domain} terminée")
            return results
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du domaine {clean_domain}: {str(e)}")
            return {"domain": clean_domain, "error": str(e)}
    
    def _clean_domain(self, url):
        """
        Extrait le nom de domaine d'une URL
        Args:
            url: URL à nettoyer
        Returns:
            str: Nom de domaine nettoyé
        """
        try:
            # Ajouter http:// si nécessaire pour l'analyse
            if not url.startswith(('http://', 'https://')): 
                url = 'http://' + url
            
            # Extraire le domaine
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Supprimer le port si présent
            if ':' in domain:
                domain = domain.split(':')[0]
            
            return domain
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du domaine {url}: {str(e)}")
            return url
    
    def get_whois_info(self, domain):
        """
        Récupère les informations WHOIS d'un domaine
        Args:
            domain: Nom de domaine à analyser
        Returns:
            dict: Informations WHOIS formatées
        """
        try:
            w = whois.whois(domain)
            
            # Formater les résultats pour une meilleure lisibilité
            whois_info = {
                "registrar": w.registrar,
                "creation_date": self._format_date(w.creation_date),
                "expiration_date": self._format_date(w.expiration_date),
                "updated_date": self._format_date(w.updated_date),
                "name_servers": w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else [],
                "status": w.status if isinstance(w.status, list) else [w.status] if w.status else [],
                "emails": w.emails if isinstance(w.emails, list) else [w.emails] if w.emails else [],
                "dnssec": w.dnssec
            }
            
            logger.info(f"Informations WHOIS récupérées pour {domain}")
            return whois_info
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations WHOIS pour {domain}: {str(e)}")
            return {"error": "Impossible de récupérer les informations WHOIS"}
    
    def _format_date(self, date):
        """
        Formate une date pour l'affichage
        Args:
            date: Date à formater (peut être une liste, un objet datetime ou None)
        Returns:
            str ou list: Date(s) formatée(s) ou None
        """
        if not date:
            return None
        
        if isinstance(date, list):
            return [d.isoformat() if isinstance(d, datetime) else str(d) for d in date]
        
        if isinstance(date, datetime):
            return date.isoformat()
        
        return str(date)
    
    def get_dns_records(self, domain):
        """
        Récupère les enregistrements DNS d'un domaine
        Args:
            domain: Nom de domaine à analyser
        Returns:
            dict: Enregistrements DNS par type
        """
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
        results = {}
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                results[record_type] = [str(rdata) for rdata in answers]
            except Exception as e:
                logger.debug(f"Aucun enregistrement DNS de type {record_type} pour {domain}: {str(e)}")
                results[record_type] = []
        
        logger.info(f"Enregistrements DNS récupérés pour {domain}")
        return results
    
    def find_subdomains(self, domain, use_bruteforce=False):
        """
        Trouve les sous-domaines d'un domaine
        Args:
            domain: Nom de domaine à analyser
            use_bruteforce: Utiliser la méthode de force brute (plus long mais plus complet)
        Returns:
            list: Sous-domaines découverts
        """
        subdomains = []
        
        # Méthode DNS (enregistrements NS)
        try:
            ns_records = dns.resolver.resolve(domain, 'NS')
            for ns in ns_records:
                subdomains.append(str(ns).rstrip('.'))
        except Exception as e:
            logger.debug(f"Erreur lors de la récupération des enregistrements NS pour {domain}: {str(e)}")
        
        # Méthode par force brute si activée
        if use_bruteforce and self.config.SUBDOMAIN_WORDLIST_PATH:
            try:
                if os.path.exists(self.config.SUBDOMAIN_WORDLIST_PATH):
                    with open(self.config.SUBDOMAIN_WORDLIST_PATH, 'r') as f:
                        for line in f:
                            subdomain = f"{line.strip()}.{domain}"
                            try:
                                dns.resolver.resolve(subdomain, 'A')
                                subdomains.append(subdomain)
                            except:
                                pass  # Ignorer les sous-domaines qui ne résolvent pas
            except Exception as e:
                logger.error(f"Erreur lors de la recherche de sous-domaines par force brute: {str(e)}")
        
        logger.info(f"{len(subdomains)} sous-domaines trouvés pour {domain}")
        return list(set(subdomains))  # Supprimer les doublons
    
    def check_security_headers(self, domain):
        """
        Vérifie les en-têtes de sécurité HTTP d'un domaine
        Args:
            domain: Nom de domaine à analyser
        Returns:
            dict: État des en-têtes de sécurité
        """
        security_headers = {
            'Strict-Transport-Security': False,  # HSTS
            'Content-Security-Policy': False,    # CSP
            'X-Content-Type-Options': False,
            'X-Frame-Options': False,
            'X-XSS-Protection': False,
            'Referrer-Policy': False
        }
        
        url = domain if domain.startswith(('http://', 'https://')) else 'https://' + domain
        
        try:
            response = requests.get(url, timeout=10)
            headers = response.headers
            
            # Vérifier chaque en-tête de sécurité
            for header in security_headers.keys():
                if header.lower() in (h.lower() for h in headers.keys()):
                    security_headers[header] = headers[header]
            
            logger.info(f"En-têtes de sécurité vérifiés pour {url}")
            return security_headers
        
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des en-têtes de sécurité pour {url}: {str(e)}")
            return security_headers
    
    def get_http_info(self, domain):
        """
        Récupère les informations HTTP d'un domaine
        Args:
            domain: Nom de domaine à analyser
        Returns:
            dict: Informations HTTP
        """
        url = domain if domain.startswith(('http://', 'https://')) else 'https://' + domain
        http_info = {}
        
        try:
            response = requests.get(url, timeout=10)
            
            http_info = {
                "status_code": response.status_code,
                "server": response.headers.get('Server', 'Unknown'),
                "redirect": response.url != url,
                "final_url": response.url,
                "content_type": response.headers.get('Content-Type', 'Unknown'),
                "powered_by": response.headers.get('X-Powered-By', None),
                "https": response.url.startswith('https://'),
                "cookies": [{'name': c.name, 'domain': c.domain, 'secure': c.secure, 'httponly': c.has_nonstandard_attr('httponly')} for c in response.cookies]
            }
            
            logger.info(f"Informations HTTP récupérées pour {url}")
            return http_info
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations HTTP pour {url}: {str(e)}")
            return {"error": str(e)}
    
    def get_shodan_info(self, domain):
        """
        Récupère les informations Shodan pour un domaine
        Args:
            domain: Nom de domaine à analyser
        Returns:
            dict: Informations Shodan
        """
        if not self.shodan_api:
            return {"error": "API Shodan non configurée"}
        
        try:
            # Rechercher le domaine dans Shodan
            results = self.shodan_api.search(f"hostname:{domain}")
            
            # Formater les résultats
            shodan_info = {
                "total_results": results['total'],
                "last_update": datetime.now().isoformat(),
                "ips": [],
                "ports": set(),
                "vulns": set(),
                "tags": set(),
                "hostnames": set()
            }
            
            # Traiter chaque résultat
            for result in results.get('matches', []):
                shodan_info['ips'].append(result.get('ip_str'))
                shodan_info['ports'].add(result.get('port'))
                shodan_info['hostnames'].update(result.get('hostnames', []))
                shodan_info['tags'].update(result.get('tags', []))
                
                # Extraire les vulnérabilités
                if 'vulns' in result:
                    for vuln in result['vulns']:
                        shodan_info['vulns'].add(vuln)
            
            # Convertir les ensembles en listes
            shodan_info['ports'] = list(shodan_info['ports'])
            shodan_info['vulns'] = list(shodan_info['vulns'])
            shodan_info['tags'] = list(shodan_info['tags'])
            shodan_info['hostnames'] = list(shodan_info['hostnames'])
            
            logger.info(f"Informations Shodan récupérées pour {domain}")
            return shodan_info
        
        except shodan.APIError as e:
            logger.error(f"Erreur API Shodan pour {domain}: {str(e)}")
            return {"error": str(e)}
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations Shodan pour {domain}: {str(e)}")
            return {"error": str(e)}
    
    def assess_security_risk(self, domain):
        """
        Évalue le niveau de risque de sécurité d'un domaine
        Args:
            domain: Nom de domaine à analyser
        Returns:
            dict: Évaluation du risque avec score et détails
        """
        risk_assessment = {
            "score": 0,  # 0-100, plus c'est élevé, plus le risque est grand
            "max_score": 100,
            "level": "Unknown",
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Récupérer les informations nécessaires
            security_headers = self.check_security_headers(domain)
            http_info = self.get_http_info(domain)
            whois_info = self.get_whois_info(domain)
            
            # Vérifier si HTTPS est utilisé
            if not http_info.get('https', False):
                risk_assessment["score"] += 20
                risk_assessment["issues"].append("Le site n'utilise pas HTTPS")
                risk_assessment["recommendations"].append("Activer HTTPS avec un certificat valide")
            
            # Vérifier les en-têtes de sécurité
            missing_headers = [header for header, value in security_headers.items() if value is False]
            if missing_headers:
                risk_assessment["score"] += min(5 * len(missing_headers), 30)  # Max 30 points
                risk_assessment["issues"].append(f"En-têtes de sécurité manquants: {', '.join(missing_headers)}")
                risk_assessment["recommendations"].append("Configurer les en-têtes de sécurité HTTP manquants")
            
            # Vérifier l'expiration du domaine
            if whois_info and 'expiration_date' in whois_info:
                expiration_date = whois_info['expiration_date']
                if expiration_date:
                    if isinstance(expiration_date, list):
                        expiration_date = expiration_date[0]
                    
                    try:
                        # Convertir en datetime si c'est une chaîne
                        if isinstance(expiration_date, str):
                            expiration_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
                        
                        # Calculer le temps restant avant expiration
                        time_left = expiration_date - datetime.now()
                        if time_left.days < 30:
                            risk_assessment["score"] += 15
                            risk_assessment["issues"].append("Le domaine expire dans moins de 30 jours")
                            risk_assessment["recommendations"].append("Renouveler le domaine rapidement")
                    except Exception as e:
                        logger.debug(f"Erreur lors de l'analyse de la date d'expiration: {str(e)}")
            
            # Ajouter les informations Shodan si disponibles
            if self.shodan_api:
                shodan_info = self.get_shodan_info(domain)
                if 'vulns' in shodan_info and shodan_info['vulns']:
                    risk_assessment["score"] += min(5 * len(shodan_info['vulns']), 25)  # Max 25 points
                    risk_assessment["issues"].append(f"Vulnérabilités détectées par Shodan: {', '.join(shodan_info['vulns'][:5])}" + 
                                                 (" et d'autres..." if len(shodan_info['vulns']) > 5 else ""))
                    risk_assessment["recommendations"].append("Corriger les vulnérabilités identifiées")
            
            # Cookies non sécurisés
            if 'cookies' in http_info:
                insecure_cookies = [cookie for cookie in http_info['cookies'] if not cookie.get('secure') or not cookie.get('httponly')]
                if insecure_cookies:
                    risk_assessment["score"] += min(5 * len(insecure_cookies), 10)  # Max 10 points
                    risk_assessment["issues"].append(f"{len(insecure_cookies)} cookies sans attributs de sécurité adéquats")
                    risk_assessment["recommendations"].append("Configurer les attributs 'Secure' et 'HttpOnly' pour les cookies")
            
            # Déterminer le niveau de risque
            if risk_assessment["score"] < 20:
                risk_assessment["level"] = "Low"
            elif risk_assessment["score"] < 50:
                risk_assessment["level"] = "Medium"
            elif risk_assessment["score"] < 80:
                risk_assessment["level"] = "High"
            else:
                risk_assessment["level"] = "Critical"
            
            logger.info(f"Evaluation du risque de sécurité terminée pour {domain}: {risk_assessment['level']} ({risk_assessment['score']}/{risk_assessment['max_score']})")
            return risk_assessment
        
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation du risque de sécurité pour {domain}: {str(e)}")
            risk_assessment["issues"].append(f"Erreur lors de l'analyse: {str(e)}")
            return risk_assessment
