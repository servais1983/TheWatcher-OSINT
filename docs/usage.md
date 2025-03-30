# Guide d'Utilisation de TheWatcher

Ce guide présente les fonctionnalités principales de TheWatcher et explique comment utiliser cet outil OSINT de manière efficace et responsable.

## Table des matières

1. [Introduction à l'interface](#1-introduction-à-linterface)
2. [Recherche par nom](#2-recherche-par-nom)
3. [Recherche par photo](#3-recherche-par-photo)
4. [Recherche par nom d'utilisateur](#4-recherche-par-nom-dutilisateur)
5. [Interprétation des résultats](#5-interprétation-des-résultats)
6. [Génération de rapports](#6-génération-de-rapports)
7. [Bonnes pratiques](#7-bonnes-pratiques)
8. [Dépannage](#8-dépannage)

## 1. Introduction à l'interface

### Accès à l'application

Une fois l'application installée et démarrée (voir [guide d'installation](installation.md)), vous pouvez y accéder via votre navigateur :

- Interface web: http://localhost:3000
- API REST: http://localhost:5000/api

### Authentification

1. Créez un compte depuis l'écran de connexion en cliquant sur "Créer un compte"
2. Connectez-vous avec vos identifiants
3. Une authentification à deux facteurs peut être requise selon la configuration

### Navigation principale

L'interface se compose de plusieurs sections :

- **Tableau de bord** : Vue d'ensemble et historique des recherches récentes
- **Recherche** : Interface pour les différents types de recherche
- **Rapports** : Gestion et visualisation des rapports générés
- **Paramètres** : Configuration de l'application et des préférences utilisateur
- **Aide** : Documentation et assistance

## 2. Recherche par nom

La recherche par nom permet de collecter des informations sur une personne à partir de son nom.

### Étapes de base

1. Accédez à l'onglet "Recherche" et sélectionnez "Recherche par nom"
2. Remplissez les champs :
   - **Nom** : Nom complet de la personne (obligatoire)
   - **Lieu** : Localisation géographique (facultatif, améliore la précision)
   - **Organisation** : Entreprise ou organisation associée (facultatif)
3. Sélectionnez un cas d'usage légitime dans le menu déroulant
4. Cochez la case de consentement éthique
5. Cliquez sur "Lancer la recherche"

### Options avancées

- **Plateformes** : Sélectionnez les réseaux sociaux spécifiques à analyser
- **Profondeur** : Définissez l'intensité de la recherche (standard, approfondie)
- **Filtres** : Ajoutez des filtres pour affiner les résultats (période, région, etc.)

### Exemple de recherche

Pour un professionnel nommé "Jean Dupont" travaillant chez "TechCorp" à Paris :
- Nom : Jean Dupont
- Lieu : Paris, France
- Organisation : TechCorp
- Cas d'usage : Vérification d'identité
- Plateformes : LinkedIn, Twitter, GitHub

## 3. Recherche par photo

La recherche par photo utilise la reconnaissance faciale et la recherche d'images inversée pour identifier une personne.

### Étapes de base

1. Accédez à l'onglet "Recherche" et sélectionnez "Recherche par photo"
2. Téléchargez une image via l'une des méthodes :
   - Glisser-déposer
   - Bouton "Parcourir"
   - URL d'image
3. Sélectionnez les options de recherche :
   - **Détection de visage** : Analyse les visages présents dans l'image
   - **Recherche inversée** : Cherche des occurrences similaires en ligne
4. Sélectionnez un cas d'usage légitime
5. Cochez la case de consentement éthique
6. Cliquez sur "Lancer la recherche"

### Conseils sur les images

- Utilisez des images de bonne qualité (résolution minimale de 300x300 pixels)
- Préférez les images où le visage est clairement visible et de face
- Évitez les images avec plusieurs personnes pour des résultats plus précis
- Les formats supportés sont : JPG, PNG, WebP

### Moteurs de recherche

TheWatcher utilise plusieurs moteurs pour la recherche par image :
- Google Images
- Yandex
- TinEye
- Google Vision API (si configuré)

## 4. Recherche par nom d'utilisateur

Cette fonctionnalité permet de trouver des comptes associés à un nom d'utilisateur spécifique sur différentes plateformes.

### Étapes de base

1. Accédez à l'onglet "Recherche" et sélectionnez "Recherche par nom d'utilisateur"
2. Entrez le nom d'utilisateur à rechercher
3. Sélectionnez un cas d'usage légitime
4. Cochez la case de consentement éthique
5. Cliquez sur "Lancer la recherche"

### Options avancées

- **Plateformes spécifiques** : Sélectionnez les sites à inclure dans la recherche
- **Délai entre requêtes** : Ajustez le temps entre les requêtes pour éviter les blocages

### Résultats

Les résultats afficheront :
- Liste des plateformes où le nom d'utilisateur a été trouvé
- Liens vers les profils correspondants
- Score de confiance pour chaque résultat
- Date de dernière activité (si disponible)

## 5. Interprétation des résultats

### Visualisation des résultats

Les résultats sont présentés sous forme de :
- **Tableaux** : Liste structurée des informations trouvées
- **Graphes** : Visualisation des relations entre les différentes données
- **Cartes** : Représentation géographique des informations de localisation
- **Chronologie** : Présentation temporelle des activités

### Score de confiance

Chaque résultat est accompagné d'un score de confiance :
- **90-100%** : Correspondance quasi certaine
- **70-89%** : Haute probabilité de correspondance
- **50-69%** : Correspondance probable
- **30-49%** : Correspondance possible, à vérifier
- **0-29%** : Faible probabilité, considérer comme un faux positif

### Navigation et filtrage

- Utilisez les filtres pour affiner les résultats par plateforme, date, ou type d'information
- Cliquez sur un élément pour voir les détails et métadonnées associées
- Utilisez la fonction de recherche pour trouver des éléments spécifiques dans les résultats

### Validation des informations

**Important** : Les résultats OSINT doivent toujours être vérifiés :
- Recoupez les informations avec plusieurs sources
- Vérifiez les dates de publication/mise à jour
- Tenez compte du contexte de chaque information
- N'acceptez pas les résultats comme des vérités absolues

## 6. Génération de rapports

### Types de rapports

TheWatcher peut générer plusieurs types de rapports :
- **Résumé** : Synthèse concise des informations essentielles
- **Détaillé** : Rapport complet avec toutes les informations collectées
- **Technique** : Rapport orienté données pour usage professionnel
- **Visuel** : Rapport graphique avec visualisations et diagrammes

### Création d'un rapport

1. Depuis une page de résultats, cliquez sur "Générer un rapport"
2. Sélectionnez le type de rapport souhaité
3. Choisissez les sections à inclure
4. Ajoutez éventuellement des notes personnalisées
5. Cliquez sur "Créer le rapport"

### Exportation et partage

Les rapports peuvent être exportés dans différents formats :
- HTML (visualisation web)
- PDF (document imprimable)
- JSON (données brutes)
- CSV (données tabulaires)

### Gestion des rapports

- Les rapports sont sauvegardés dans la section "Rapports"
- Vous pouvez y accéder ultérieurement, les modifier ou les supprimer
- Chaque rapport est horodaté et associé à une recherche spécifique

## 7. Bonnes pratiques

### Éthique et légalité

- Utilisez toujours TheWatcher conformément au [cadre légal](legal.md)
- Documentez clairement l'objectif de chaque recherche
- N'utilisez que des sources publiques d'information
- Respectez les limites légales de collecte de données

### Optimisation des recherches

- Commencez par des recherches larges, puis affinez progressivement
- Utilisez plusieurs variantes d'un nom ou d'un nom d'utilisateur
- Combinez différentes méthodes de recherche pour des résultats plus complets
- Enregistrez les recherches fréquentes comme modèles pour gagner du temps

### Sécurité opérationnelle

- Utilisez un VPN ou le réseau Tor pour les recherches sensibles
- Alternez entre différents moteurs de recherche
- Respectez des délais raisonnables entre les requêtes
- Ne stockez pas les informations sensibles plus longtemps que nécessaire

### Protection des données

- Chiffrez les rapports contenant des informations sensibles
- Utilisez les fonctionnalités d'anonymisation quand approprié
- Supprimez régulièrement les historiques de recherche
- Suivez les politiques de rétention de données de votre organisation

## 8. Dépannage

### Problèmes courants

#### Recherche sans résultats
- Vérifiez l'orthographe du nom ou du nom d'utilisateur
- Essayez des variantes (avec/sans accents, abréviations, etc.)
- Vérifiez votre connexion internet
- Essayez une autre méthode de recherche

#### Erreurs lors de la recherche d'image
- Vérifiez que l'image respecte les dimensions minimales
- Assurez-vous que le format de fichier est supporté
- Essayez de recadrer l'image sur le visage principale
- Réduisez la résolution si l'image est trop volumineuse

#### Lenteur des recherches
- Réduisez le nombre de plateformes à analyser
- Augmentez le délai entre les requêtes
- Fermez les applications inutilisées pour libérer des ressources
- Vérifiez votre connexion internet

### Obtenir de l'aide

- Consultez la documentation en ligne
- Vérifiez les journaux d'erreurs dans `backend/logs/`
- Créez une issue sur GitHub pour signaler un bug
- Contactez l'équipe de support pour les problèmes persistants

---

## Ressources supplémentaires

- [FAQ](faq.md) - Réponses aux questions fréquentes
- [Glossaire OSINT](glossary.md) - Terminologie et concepts clés
- [Tutoriels vidéo](https://example.com/thewatcher/tutorials) - Démonstrations visuelles
- [Communauté](https://example.com/thewatcher/community) - Forum d'entraide

---

**Rappel important** : TheWatcher est un outil puissant qui doit être utilisé de manière éthique et légale. Consultez toujours le [cadre légal](legal.md) avant d'entreprendre des recherches.