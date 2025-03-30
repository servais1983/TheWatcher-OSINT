# Guide d'Installation de TheWatcher

Ce document détaille les étapes pour installer TheWatcher, outil OSINT éthique, sur différentes plateformes.

## Prérequis

### Matériel recommandé
- CPU: 2+ cœurs
- RAM: 4 Go minimum, 8 Go recommandé
- Espace disque: 2 Go minimum pour l'application et ses dépendances

### Système d'exploitation
- **Recommandé**: Kali Linux (optimisé pour les outils de sécurité et OSINT)
- **Compatible**: Ubuntu 20.04+, Debian 11+
- **Possible avec adaptations**: CentOS/RHEL, Fedora, Arch Linux
- **Windows**: Possible via WSL2 (Windows Subsystem for Linux)

### Logiciels requis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Node.js 16 ou supérieur et npm
- Docker et Docker Compose (pour les services de base de données)
- Git
- Navigateur Chrome/Chromium (pour Selenium)
- ChromeDriver (compatible avec votre version de Chrome)

## Installation automatisée

La méthode la plus simple est d'utiliser notre script d'installation :

```bash
# 1. Cloner le dépôt
git clone https://github.com/servais1983/TheWatcher-OSINT.git
cd TheWatcher-OSINT

# 2. Rendre le script exécutable
chmod +x install.sh

# 3. Exécuter le script d'installation
sudo ./install.sh
```

Le script d'installation effectuera les opérations suivantes :
- Installation des dépendances système
- Configuration d'un utilisateur dédié (thewatcher)
- Installation des dépendances Python et Node.js
- Configuration des services Docker
- Installation et configuration des outils OSINT tiers (Sherlock, etc.)

## Installation manuelle

Si vous préférez installer manuellement ou si le script automatisé ne fonctionne pas, suivez ces étapes :

### 1. Préparer le système
```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances
sudo apt install -y \
    python3 python3-pip python3-venv \
    nodejs npm \
    postgresql postgresql-contrib \
    libpq-dev \
    docker.io docker-compose \
    git \
    curl \
    libffi-dev libssl-dev \
    build-essential \
    libgl1-mesa-glx \
    cmake
```

### 2. Cloner le dépôt
```bash
git clone https://github.com/servais1983/TheWatcher-OSINT.git
cd TheWatcher-OSINT
```

### 3. Configurer l'environnement Python
```bash
# Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances Python
pip install -r requirements.txt
```

### 4. Configurer le frontend
```bash
cd frontend
npm install
cd ..
```

### 5. Configurer la base de données
```bash
# Démarrer les services Docker
docker-compose up -d
```

### 6. Configurer les outils OSINT tiers

#### Installation de Sherlock
```bash
# Cloner Sherlock
git clone https://github.com/sherlock-project/sherlock.git /opt/sherlock
cd /opt/sherlock
pip install -r requirements.txt
cd -
```

### 7. Configurer les variables d'environnement
```bash
# Créer le fichier .env à partir de l'exemple
cp .env.example .env

# Éditer le fichier avec vos clés API
nano .env
```

### 8. Rendre les scripts exécutables
```bash
chmod +x run.sh stop.sh
```

## Configuration spécifique aux OS

### Windows (via WSL2)
1. Installer WSL2 avec Ubuntu
2. Suivre la procédure d'installation pour Linux
3. Pour utiliser Selenium, installer Chrome et ChromeDriver dans WSL2

### MacOS
1. Utiliser Homebrew pour installer les dépendances :
```bash
brew install python node postgresql docker docker-compose
```
2. Suivre la procédure d'installation standard

## Configuration des clés API

TheWatcher peut utiliser plusieurs API externes pour améliorer ses capacités OSINT. Voici les services principaux que vous devriez configurer :

### AWS Rekognition (reconnaissance faciale)
- Créer un compte AWS
- Créer un utilisateur IAM avec les droits Rekognition
- Obtenir une clé d'accès et une clé secrète
- Configurer `AWS_ACCESS_KEY_ID` et `AWS_SECRET_ACCESS_KEY` dans le fichier .env

### Google Vision API (recherche d'images et analyse)
- Créer un projet dans Google Cloud Console
- Activer l'API Vision
- Créer une clé API
- Configurer `GOOGLE_API_KEY` dans le fichier .env

### Hunter.io (recherche d'e-mails)
- Créer un compte sur Hunter.io
- Obtenir une clé API
- Configurer `HUNTER_API_KEY` dans le fichier .env

## Vérification de l'installation

### Tester l'application
```bash
# Démarrer l'application
./run.sh

# Accéder à l'interface web
# Ouvrir un navigateur et aller à http://localhost:3000
```

### Vérifier les services

#### Base de données PostgreSQL
```bash
psql -h localhost -U thewatcher -d thewatcher
# Le mot de passe par défaut est dans le fichier .env
```

#### Elasticsearch
```bash
curl http://localhost:9200
```

#### Redis
```bash
redis-cli ping
# Devrait répondre "PONG"
```

## Résolution des problèmes

### Problèmes courants

1. **Erreur de connexion à PostgreSQL**
   - Vérifier que le service PostgreSQL est en cours d'exécution
   - Vérifier les informations de connexion dans le fichier .env

2. **Erreur "ModuleNotFoundError"**
   - Vérifier que l'environnement virtuel est activé
   - Réinstaller les dépendances avec `pip install -r requirements.txt`

3. **Erreur de ChromeDriver**
   - Vérifier que ChromeDriver est installé et dans le PATH
   - Vérifier que la version de ChromeDriver correspond à votre version de Chrome

4. **Erreur "Permission denied"**
   - Exécuter les commandes avec `sudo` si nécessaire
   - Vérifier les permissions des répertoires et fichiers

### Logs et diagnostics

Les logs de l'application se trouvent dans :
- Backend: `backend/logs/`
- Docker: Utiliser `docker-compose logs -f`

## Mises à jour

Pour mettre à jour TheWatcher :

```bash
# 1. Arrêter l'application
./stop.sh

# 2. Mettre à jour le code
git pull

# 3. Mettre à jour les dépendances
source venv/bin/activate
pip install -r requirements.txt
cd frontend
npm install
cd ..

# 4. Redémarrer l'application
./run.sh
```

## Désinstallation

Pour désinstaller complètement TheWatcher :

```bash
# 1. Arrêter tous les services
./stop.sh

# 2. Supprimer les conteneurs et volumes Docker
docker-compose down -v

# 3. Supprimer le répertoire de l'application
cd ..
rm -rf TheWatcher-OSINT
```

## Support

Pour obtenir de l'aide ou signaler des problèmes :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement via l'adresse e-mail de support
