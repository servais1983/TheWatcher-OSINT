#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TheWatcher - Module d'agrégation de données
Ce module combine les différentes sources de données et génère des rapports
"""

import os
import json
import logging
import datetime
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from config import active_config

# Configuration du logger
logger = logging.getLogger(__name__)

class DataAggregator:
    """Classe pour l'agrégation et l'analyse des données OSINT"""
    
    def __init__(self, config=None):
        """
        Initialise l'agrégateur de données
        Args:
            config: Configuration à utiliser (par défaut: active_config)
        """
        self.config = config or active_config
        
        # Créer le répertoire de sortie pour les rapports
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def aggregate_person_data(self, name, social_data, image_data=None, email_data=None):
        """
        Agrège les données d'une personne à partir de différentes sources
        Args:
            name: Nom de la personne
            social_data: Données des réseaux sociaux
            image_data: Données d'image (facultatif)
            email_data: Données d'email (facultatif)
        Returns:
            dict: Données agrégées
        """
        try:
            # Initialiser le dictionnaire de résultats
            aggregated_data = {
                'name': name,
                'updated_at': datetime.datetime.now().isoformat(),
                'social_profiles': {},
                'images': [],
                'emails': [],
                'locations': [],
                'possible_usernames': set(),
                'possible_aliases': set(),
                'related_people': set(),
                'organizations': set(),
                'metadata': {
                    'sources': [],
                    'confidence': 0
                }
            }
            
            # Ajouter les données sociales
            if social_data:
                aggregated_data['metadata']['sources'].append('social_media')
                
                # Ajouter les profils sociaux par plateforme
                for platform, profiles in social_data.get('profiles', {}).items():
                    if not platform in aggregated_data['social_profiles']:
                        aggregated_data['social_profiles'][platform] = []
                    
                    aggregated_data['social_profiles'][platform].extend(profiles)
                    
                    # Extraire des noms d'utilisateur possibles à partir des URLs
                    for profile in profiles:
                        url = profile.get('url', '')
                        if platform == 'twitter' and 'twitter.com/' in url:
                            username = url.split('twitter.com/')[1].split('/')[0].split('?')[0]
                            aggregated_data['possible_usernames'].add(username)
                        elif platform == 'instagram' and 'instagram.com/' in url:
                            username = url.split('instagram.com/')[1].split('/')[0].split('?')[0]
                            aggregated_data['possible_usernames'].add(username)
                        
                        # Extraire des lieux possibles à partir des descriptions
                        description = profile.get('description', '')
                        if description:
                            # Analyse simpliste - une analyse NLP serait meilleure ici
                            keywords = ['à', 'in', 'from', 'located', 'based']
                            for keyword in keywords:
                                if f" {keyword} " in f" {description} ":
                                    parts = description.split(f" {keyword} ")
                                    if len(parts) > 1:
                                        location_part = parts[1].split('.')[0].split(',')[0].strip()
                                        if len(location_part) > 2 and len(location_part) < 30:
                                            aggregated_data['locations'].append(location_part)
            
            # Ajouter les données d'image
            if image_data:
                aggregated_data['metadata']['sources'].append('image_search')
                
                # Ajouter les résultats de recherche d'images
                for search_engine, results in image_data.items():
                    if search_engine == 'google_api' and 'web_entities' in results:
                        # Ajouter les entités reconnues par Google Vision
                        for entity in results.get('web_entities', []):
                            description = entity.get('description', '')
                            score = entity.get('score', 0)
                            
                            if score > 0.7:  # Haute confiance
                                if any(word in description.lower() for word in ['person', 'people', 'celebrity']):
                                    # C'est probablement un nom de personne
                                    if description.lower() != name.lower():
                                        aggregated_data['possible_aliases'].add(description)
                                elif any(word in description.lower() for word in ['company', 'corporation', 'organization']):
                                    # C'est probablement une organisation
                                    aggregated_data['organizations'].add(description)
                    
                    # Ajouter les images trouvées
                    if search_engine in ['google', 'yandex', 'tineye'] and 'similar_images' in results:
                        for image in results.get('similar_images', []):
                            if isinstance(image, dict) and 'url' in image:
                                aggregated_data['images'].append({
                                    'url': image['url'],
                                    'source': search_engine,
                                    'page_url': image.get('page_url', None)
                                })
                    
                    # Ajouter le meilleur guess de Google
                    if search_engine == 'google' and 'best_guess' in results:
                        best_guess = results.get('best_guess')
                        if best_guess and best_guess.lower() != name.lower():
                            aggregated_data['possible_aliases'].add(best_guess)
                    
                    # Ajouter les sites web associés
                    if search_engine in ['google', 'yandex'] and 'websites' in results:
                        for website in results.get('websites', []):
                            # Analyser le titre et la description pour trouver des organisations
                            if 'title' in website:
                                title = website.get('title', '')
                                if any(word in title.lower() for word in ['company', 'inc', 'ltd', 'corporation', 'corp', 'group']):
                                    aggregated_data['organizations'].add(title)
            
            # Ajouter les données d'email
            if email_data:
                aggregated_data['metadata']['sources'].append('email_search')
                
                # Ajouter les emails trouvés
                if 'emails' in email_data:
                    for email in email_data.get('emails', []):
                        if isinstance(email, dict) and 'value' in email:
                            email_obj = {
                                'address': email['value'],
                                'confidence': email.get('confidence', 0),
                                'source': 'hunter.io'
                            }
                            aggregated_data['emails'].append(email_obj)
                            
                            # Extraire le nom d'utilisateur de l'email
                            username = email['value'].split('@')[0]
                            aggregated_data['possible_usernames'].add(username)
                
                # Ajouter l'organisation si disponible
                if 'organization' in email_data and email_data['organization']:
                    aggregated_data['organizations'].add(email_data['organization'])
            
            # Convertir les ensembles en listes
            aggregated_data['possible_usernames'] = list(aggregated_data['possible_usernames'])
            aggregated_data['possible_aliases'] = list(aggregated_data['possible_aliases'])
            aggregated_data['related_people'] = list(aggregated_data['related_people'])
            aggregated_data['organizations'] = list(aggregated_data['organizations'])
            
            # Calculer un score de confiance global
            confidence = 0
            if aggregated_data['social_profiles']:
                confidence += 20 * min(len(aggregated_data['social_profiles']), 5) / 5  # Max 20 points pour les profils sociaux
            
            if aggregated_data['images']:
                confidence += 15 * min(len(aggregated_data['images']), 10) / 10  # Max 15 points pour les images
            
            if aggregated_data['emails']:
                confidence += 25 * min(len(aggregated_data['emails']), 3) / 3  # Max 25 points pour les emails
            
            if aggregated_data['locations']:
                confidence += 15 * min(len(aggregated_data['locations']), 3) / 3  # Max 15 points pour les localisations
            
            if aggregated_data['possible_usernames']:
                confidence += 15 * min(len(aggregated_data['possible_usernames']), 5) / 5  # Max 15 points pour les usernames
            
            if aggregated_data['organizations']:
                confidence += 10 * min(len(aggregated_data['organizations']), 3) / 3  # Max 10 points pour les organisations
            
            aggregated_data['metadata']['confidence'] = min(round(confidence), 100)
            
            logger.info(f"Agrégation des données pour '{name}' terminée avec un score de confiance de {aggregated_data['metadata']['confidence']}%")
            return aggregated_data
        
        except Exception as e:
            logger.error(f"Erreur lors de l'agrégation des données: {str(e)}")
            return {
                'name': name,
                'error': str(e),
                'metadata': {
                    'sources': [],
                    'confidence': 0
                }
            }
    
    def generate_network_graph(self, person_data):
        """
        Génère un graphe de réseau pour visualiser les relations
        Args:
            person_data: Données agrégées d'une personne
        Returns:
            BytesIO: Objet contenant l'image du graphe
        """
        try:
            # Créer un graphe dirigé
            G = nx.DiGraph()
            
            # Ajouter le nœud principal
            G.add_node(person_data['name'], type='person', color='red')
            
            # Ajouter les profils sociaux
            for platform, profiles in person_data.get('social_profiles', {}).items():
                for i, profile in enumerate(profiles):
                    node_id = f"{platform}_{i}"
                    G.add_node(node_id, label=profile.get('name', platform), type='profile', color='blue')
                    G.add_edge(person_data['name'], node_id)
            
            # Ajouter les noms d'utilisateur possibles
            for username in person_data.get('possible_usernames', []):
                G.add_node(username, type='username', color='green')
                G.add_edge(person_data['name'], username)
            
            # Ajouter les emails
            for email in person_data.get('emails', []):
                email_address = email.get('address', '')
                if email_address:
                    G.add_node(email_address, type='email', color='purple')
                    G.add_edge(person_data['name'], email_address)
            
            # Ajouter les organisations
            for org in person_data.get('organizations', []):
                G.add_node(org, type='organization', color='orange')
                G.add_edge(person_data['name'], org)
            
            # Ajouter les localisations
            for location in person_data.get('locations', []):
                G.add_node(location, type='location', color='yellow')
                G.add_edge(person_data['name'], location)
            
            # Créer l'image
            plt.figure(figsize=(12, 8))
            
            # Positions des nœuds
            pos = nx.spring_layout(G)
            
            # Dessiner les nœuds avec des couleurs différentes selon le type
            node_colors = [G.nodes[n].get('color', 'gray') for n in G.nodes()]
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.8)
            
            # Dessiner les liens
            nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
            
            # Ajouter les labels
            labels = {}
            for n in G.nodes():
                if G.nodes[n].get('type') == 'profile':
                    labels[n] = G.nodes[n].get('label', n)
                else:
                    labels[n] = n
            nx.draw_networkx_labels(G, pos, labels, font_size=10, font_family='sans-serif')
            
            # Ajouter un titre
            plt.title(f"Réseau de relations pour {person_data['name']}")
            
            # Enlever les axes
            plt.axis('off')
            
            # Sauvegarder l'image dans un buffer
            img_buf = BytesIO()
            plt.savefig(img_buf, format='png', dpi=300, bbox_inches='tight')
            img_buf.seek(0)
            plt.close()
            
            return img_buf
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphe: {str(e)}")
            return None
    
    def generate_report(self, person_data, include_graph=True):
        """
        Génère un rapport complet en format HTML
        Args:
            person_data: Données agrégées d'une personne
            include_graph: Inclure un graphe de réseau
        Returns:
            str: Rapport au format HTML
        """
        try:
            # Nom sécurisé pour le fichier
            safe_name = ''.join(c if c.isalnum() else '_' for c in person_data['name'])
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(self.reports_dir, f"{safe_name}_{timestamp}.html")
            
            # Générer le graphe si demandé
            graph_data = None
            if include_graph:
                graph_buf = self.generate_network_graph(person_data)
                if graph_buf:
                    graph_data = base64.b64encode(graph_buf.getvalue()).decode('utf-8')
            
            # Générer le HTML
            html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport OSINT: {person_data['name']}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        h1, h2, h3 {{
            margin-top: 0;
        }}
        .confidence {{
            float: right;
            background-color: {'#4CAF50' if person_data['metadata']['confidence'] > 70 else '#FF9800' if person_data['metadata']['confidence'] > 40 else '#F44336'};
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
        }}
        .section {{
            background-color: #f9f9f9;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .profile {{
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }}
        .profile:last-child {{
            border-bottom: none;
        }}
        .email {{
            margin-bottom: 5px;
        }}
        .network-graph {{
            text-align: center;
            margin-top: 20px;
        }}
        .timestamp {{
            text-align: right;
            font-style: italic;
            color: #888;
            font-size: 0.8em;
            margin-top: 30px;
        }}
        footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #888;
        }}
        .legal-notice {{
            background-color: #f8f8f8;
            border-left: 4px solid #ccc;
            padding: 10px;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Rapport OSINT</h1>
            <div class="confidence">Niveau de confiance: {person_data['metadata']['confidence']}%</div>
        </header>
        
        <section class="section">
            <h2>Informations sur la personne</h2>
            <p><strong>Nom:</strong> {person_data['name']}</p>
            
            {f'<p><strong>Alias possibles:</strong> {", ".join(person_data.get("possible_aliases", []))}</p>' if person_data.get('possible_aliases') else ''}
            
            {f'<p><strong>Noms d\'utilisateur possibles:</strong> {", ".join(person_data.get("possible_usernames", []))}</p>' if person_data.get('possible_usernames') else ''}
            
            {f'<p><strong>Localisations:</strong> {", ".join(person_data.get("locations", []))}</p>' if person_data.get('locations') else ''}
            
            {f'<p><strong>Organisations:</strong> {", ".join(person_data.get("organizations", []))}</p>' if person_data.get('organizations') else ''}
        </section>
        
        <section class="section">
            <h2>Profils sur les réseaux sociaux</h2>
            
            {self._generate_social_profiles_html(person_data.get('social_profiles', {}))}
        </section>
        
        <section class="section">
            <h2>Adresses Email</h2>
            
            {self._generate_emails_html(person_data.get('emails', []))}
        </section>
        
        <section class="section">
            <h2>Images associées</h2>
            
            {self._generate_images_html(person_data.get('images', []))}
        </section>
        
        {f'''<section class="section">
            <h2>Graphe de relations</h2>
            <div class="network-graph">
                <img src="data:image/png;base64,{graph_data}" alt="Graphe de relations" style="max-width:100%;">
            </div>
        </section>''' if graph_data else ''}
        
        <div class="timestamp">
            Rapport généré le {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
        </div>
        
        <div class="legal-notice">
            <p><strong>Notice légale:</strong> Ce rapport est généré à des fins d'information dans le cadre légal applicable. 
            L'utilisation de ces informations doit respecter les lois sur la protection des données (RGPD, CCPA, etc.) 
            et ne doit pas porter atteinte à la vie privée des personnes concernées.</p>
        </div>
        
        <footer>
            <p>Généré par TheWatcher - Outil OSINT Éthique</p>
        </footer>
    </div>
</body>
</html>
"""
            
            # Sauvegarder le rapport
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Rapport généré avec succès: {report_file}")
            return html, report_file
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return f"<html><body><h1>Erreur</h1><p>{str(e)}</p></body></html>", None
    
    def _generate_social_profiles_html(self, social_profiles):
        """
        Génère le HTML pour la section des profils sociaux
        Args:
            social_profiles: Dictionnaire des profils par plateforme
        Returns:
            str: HTML généré
        """
        if not social_profiles:
            return "<p>Aucun profil social trouvé.</p>"
        
        html = ""
        
        for platform, profiles in social_profiles.items():
            html += f"<h3>{platform.capitalize()}</h3>"
            
            if not profiles:
                html += "<p>Aucun profil trouvé.</p>"
                continue
            
            for profile in profiles:
                html += f"""<div class="profile">
                    <p><strong>{profile.get('name', 'N/A')}</strong></p>
                    <p><a href="{profile.get('url', '#')}" target="_blank">{profile.get('url', 'N/A')}</a></p>
                    {f'<p>{profile.get("description", "")}</p>' if profile.get('description') else ''}
                </div>"""
        
        return html
    
    def _generate_emails_html(self, emails):
        """
        Génère le HTML pour la section des emails
        Args:
            emails: Liste des emails
        Returns:
            str: HTML généré
        """
        if not emails:
            return "<p>Aucune adresse email trouvée.</p>"
        
        html = ""
        
        for email in emails:
            confidence = email.get('confidence', 0)
            confidence_color = '#4CAF50' if confidence > 80 else '#FF9800' if confidence > 50 else '#F44336'
            
            html += f"""<div class="email">
                <p>
                    <strong>{email.get('address', 'N/A')}</strong>
                    <span style="float:right; background-color:{confidence_color}; color:white; padding:2px 5px; border-radius:3px; font-size:0.8em;">
                        {confidence}%
                    </span>
                </p>
                <p><small>Source: {email.get('source', 'N/A')}</small></p>
            </div>"""
        
        return html
    
    def _generate_images_html(self, images):
        """
        Génère le HTML pour la section des images
        Args:
            images: Liste des images
        Returns:
            str: HTML généré
        """
        if not images:
            return "<p>Aucune image trouvée.</p>"
        
        html = "<div style='display:flex; flex-wrap:wrap; gap:10px;'>"
        
        for image in images[:12]:  # Limiter à 12 images
            html += f"""<div style="width:150px; margin-bottom:10px;">
                <a href="{image.get('url', '#')}" target="_blank">
                    <img src="{image.get('url', '#')}" alt="Image" style="max-width:100%; max-height:150px; object-fit:contain;">
                </a>
                <p><small>Source: {image.get('source', 'N/A')}</small></p>
            </div>"""
        
        html += "</div>"
        
        if len(images) > 12:
            html += f"<p><em>+ {len(images) - 12} autres images non affichées</em></p>"
        
        return html
