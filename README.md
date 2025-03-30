# TheWatcher 🔍

Un outil OSINT (Open Source Intelligence) éthique conçu pour la recherche d'informations à partir de photos (reconnaissance faciale) ou de noms (recherche dans les données ouvertes).

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ⚠️ Avertissement Légal et Éthique

**TheWatcher est un outil à utiliser exclusivement dans un cadre légal et éthique.**

- Respecte les lois sur la protection des données (RGPD, CCPA, etc.)
- Ne doit pas être utilisé pour harceler, traquer ou porter atteinte à la vie privée
- Requiert le consentement approprié selon les législations en vigueur
- L'utilisateur est seul responsable de son utilisation de l'outil

## 🌟 Caractéristiques

### Recherche par Photo
- Reconnaissance faciale (AWS Rekognition, OpenCV, DLib)
- Recherche d'image inversée (Google, Yandex, TinEye)
- Analyse des métadonnées EXIF (localisation, date, appareil)

### Recherche par Nom
- Agrégation de données depuis les réseaux sociaux
- Recherche dans les bases de données publiques
- Analyse des fuites de données (avec précautions éthiques)

### Visualisation
- Cartographie des relations
- Géolocalisation des informations trouvées
- Génération de rapports détaillés

## 🛠️ Installation

### Prérequis
- Kali Linux (recommandé) ou autre distribution Linux
- Python 3.8+
- Docker et Docker Compose
- Node.js 16+ (pour le frontend)

### Installation Automatisée
```bash
git clone https://github.com/servais1983/TheWatcher-OSINT.git
cd TheWatcher-OSINT
chmod +x install.sh
./install.sh
```

### Installation Manuelle
```bash
# 1. Cloner le dépôt
git clone https://github.com/servais1983/TheWatcher-OSINT.git
cd TheWatcher-OSINT

# 2. Configurer l'environnement Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurer le frontend
cd frontend
npm install
cd ..

# 4. Lancer les services Docker
docker-compose up -d

# 5. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API
```

## 🚀 Utilisation

### Démarrer l'application
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer le backend
cd backend
python app.py

# Dans un nouveau terminal, lancer le frontend
cd frontend
npm start
```

### Interface Web
Accédez à `http://localhost:3000` pour utiliser l'interface graphique.

### API
Documentation de l'API disponible à `http://localhost:5000/api/docs`.

## 🔒 Sécurité et Conformité

TheWatcher intègre plusieurs fonctionnalités de sécurité :

- Authentification Multi-Facteurs (MFA)
- Chiffrement TLS 1.3 pour toutes les communications
- Journalisation complète des activités pour audit
- Vérification des cas d'usage avant chaque requête
- Respect des délais entre requêtes pour éviter la détection

## 📚 Documentation

Une documentation complète est disponible dans le dossier `/docs` :

- [Guide d'installation détaillé](docs/installation.md)
- [Guide d'utilisation](docs/usage.md)
- [API Reference](docs/api.md)
- [Cadre légal et éthique](docs/legal.md)
- [Bonnes pratiques](docs/best_practices.md)

## 🤝 Contribuer

Les contributions sont les bienvenues ! Veuillez consulter [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📊 Cas d'Usage Légitimes

- Sécurité informatique et pentesting (avec autorisation)
- Recherche de personnes disparues (cadre légal approprié)
- Vérification d'identité (avec consentement)
- Recherche académique sur les vulnérabilités de confidentialité

## ❌ Utilisations Proscrites

- Harcèlement ou traque
- Usurpation d'identité
- Espionnage illégal
- Toute activité violant les lois locales sur la vie privée

---

*Développé avec ❤️ pour la communauté de cybersécurité éthique.*

**Rappel** : Avec de grands pouvoirs viennent de grandes responsabilités. Utilisez cet outil de manière éthique et légale.