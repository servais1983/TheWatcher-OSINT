# Guide d'Installation Détaillé de TheWatcher-OSINT

## 📋 Prérequis Généraux

- Python 3.8 ou supérieur
- Docker et Docker Compose
- Git
- Connexion Internet stable

## 🐧 Installation sur Linux (Kali, Ubuntu, Debian)

### Étape 1 : Préparation du Système
```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances de base
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    docker \
    docker-compose \
    git \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev
```

### Étape 2 : Clonage du Dépôt
```bash
git clone https://github.com/servais1983/TheWatcher-OSINT.git
cd TheWatcher-OSINT
```

### Étape 3 : Installation
```bash
# Option 1 : Script d'installation automatique
python3 install.py

# Option 2 : Installation manuelle
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d
```

## 🪟 Installation sur Windows

### Étape 1 : Prérequis
1. Télécharger et installer [Python 3.8+](https://www.python.org/downloads/)
2. Télécharger et installer [Docker Desktop](https://www.docker.com/products/docker-desktop)
3. Installer [Git for Windows](https://gitforwindows.org/)

### Étape 2 : Configuration
```cmd
# Ouvrir PowerShell ou CMD en mode administrateur

# Cloner le dépôt
git clone https://github.com/servais1983/TheWatcher-OSINT.git
cd TheWatcher-OSINT

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer Docker Compose
docker-compose up -d
```

## 🔧 Résolution des Problèmes Courants

### Erreurs de Dépendances
- Assurez-vous que toutes les dépendances sont installées
- Vérifiez les versions de Python et des bibliothèques
- Utilisez `pip install --upgrade pip` si nécessaire

### Problèmes Docker
- Vérifiez que Docker Desktop est en cours d'exécution
- Redémarrez Docker si des problèmes persistent
- Consultez les logs Docker avec `docker-compose logs`

### Erreurs Python
- Utilisez toujours un environnement virtuel
- Vérifiez que vous utilisez Python 3.8+
- Installez les dépendances système manquantes

## 🚀 Démarrage de l'Application

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux
venv\Scripts\activate     # Windows

# Lancer le backend
python backend/app.py
```

## 📌 Notes Importantes

- Toujours utiliser l'outil de manière éthique et légale
- Respecter les lois sur la protection des données
- Obtenir les consentements nécessaires

## 🆘 Support

En cas de problème :
- Consultez la documentation
- Vérifiez les issues GitHub
- Contactez les mainteneurs du projet

---

*Guide mis à jour le : 02/04/2025*
