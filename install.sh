#!/bin/bash

# TheWatcher - Script d'installation
# Ce script configure l'environnement complet pour TheWatcher

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour les messages d'erreur
error() {
    echo -e "${RED}[ERREUR]${NC} $1"
    exit 1
}

# Fonction pour les messages d'information
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Fonction pour les messages de succès
success() {
    echo -e "${GREEN}[SUCCÈS]${NC} $1"
}

# Fonction pour les messages d'avertissement
warning() {
    echo -e "${YELLOW}[AVERTISSEMENT]${NC} $1"
}

# Message de bienvenue
echo -e "${BLUE}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  _____ _          _    _       _       _                     "
echo " |_   _| |__   ___| |  | | __ _| |_ ___| |__   ___ _ __       "
echo "   | | | '_ \ / _ \ |  | |/ _\` | __/ __| '_ \ / _ \ '__|      "
echo "   | | | | | |  __/ |  | | (_| | || (__| | | |  __/ |         "
echo "   |_| |_| |_|\___|_|  |_|\__,_|\__\___|_| |_|\___|_|         "
echo "                                                               "
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"
echo -e "Installation de TheWatcher - Outil OSINT Éthique"
echo -e "Version: 0.1.0"
echo -e ""

# Vérifier si nous sommes sur Kali Linux
if [ -f /etc/os-release ]; then
    source /etc/os-release
    if [[ "$ID" == "kali" ]]; then
        success "Système d'exploitation Kali Linux détecté"
    else
        warning "Ce script est optimisé pour Kali Linux. Vous utilisez: $PRETTY_NAME"
        echo -e "L'installation peut continuer, mais certaines fonctionnalités pourraient nécessiter des ajustements."
        read -p "Continuer? (o/n): " confirm
        if [[ $confirm != "o" && $confirm != "O" ]]; then
            exit 1
        fi
    fi
fi

# Vérifier les permissions de superutilisateur
if [[ $EUID -ne 0 ]]; then
    warning "Ce script nécessite des privilèges d'administration."
    warning "Exécutez-le avec sudo ou en tant que root."
    exit 1
fi

# Créer un utilisateur dédié pour TheWatcher (plus sécurisé)
info "Création d'un utilisateur dédié pour TheWatcher..."
if id "thewatcher" &>/dev/null; then
    info "L'utilisateur thewatcher existe déjà"
else
    useradd -m -s /bin/bash thewatcher || error "Impossible de créer l'utilisateur"
    echo "thewatcher:$(openssl rand -base64 12)" | chpasswd || error "Impossible de définir le mot de passe"
    success "Utilisateur thewatcher créé"
fi

# Mise à jour du système
info "Mise à jour du système..."
apt update || error "Impossible de mettre à jour le système"
apt upgrade -y || warning "Certains paquets n'ont pas pu être mis à jour"

# Installation des dépendances
info "Installation des dépendances système..."
apt install -y \
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
    cmake || error "Impossible d'installer les dépendances système"

# Installation des outils OSINT spécifiques
info "Installation des outils OSINT..."
apt install -y \
    maltego \
    recon-ng \
    theharvester \
    spiderfoot \
    exiftool \
    libimage-exiftool-perl || warning "Certains outils OSINT n'ont pas pu être installés"

# Cloner le dépôt Sherlock si nécessaire
if [ ! -d "/opt/sherlock" ]; then
    git clone https://github.com/sherlock-project/sherlock.git /opt/sherlock
    cd /opt/sherlock
    python3 -m pip install -r requirements.txt
    cd - > /dev/null
fi

# Configuration de Docker
info "Configuration de Docker..."
systemctl start docker || error "Impossible de démarrer Docker"
systemctl enable docker || warning "Impossible d'activer Docker au démarrage"
usermod -aG docker thewatcher || warning "Impossible d'ajouter l'utilisateur au groupe docker"

# Créer la structure du projet
info "Création de la structure du projet..."
PROJECT_DIR="/opt/thewatcher"
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/backend/modules
mkdir -p $PROJECT_DIR/backend/utils
mkdir -p $PROJECT_DIR/frontend
mkdir -p $PROJECT_DIR/docs
mkdir -p $PROJECT_DIR/data

# Configuration des permissions
chown -R thewatcher:thewatcher $PROJECT_DIR

# Téléchargement des fichiers du projet
info "Téléchargement des fichiers du projet..."
cd $PROJECT_DIR
runuser -l thewatcher -c "git clone https://github.com/servais1983/TheWatcher-OSINT.git $PROJECT_DIR"

# Création de l'environnement Python
info "Configuration de l'environnement Python..."
cd $PROJECT_DIR
runuser -l thewatcher -c "python3 -m venv $PROJECT_DIR/venv"
runuser -l thewatcher -c "source $PROJECT_DIR/venv/bin/activate && pip install -r $PROJECT_DIR/requirements.txt"

# Configuration des variables d'environnement
info "Configuration du fichier .env..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp $PROJECT_DIR/.env.example $PROJECT_DIR/.env
    success "Fichier .env créé, veuillez le modifier avec vos clés API"
fi

# Configuration du frontend
info "Configuration du frontend..."
runuser -l thewatcher -c "cd $PROJECT_DIR/frontend && npm install"

# Démarrage des services Docker
info "Démarrage des services Docker..."
cd $PROJECT_DIR
docker-compose up -d || warning "Erreur lors du démarrage des services Docker"

# Finalisation
success "Installation terminée!"
echo ""
echo "🔍 TheWatcher a été installé avec succès!"
echo ""
echo "Prochaines étapes:"
echo "1. Modifiez le fichier $PROJECT_DIR/.env avec vos clés API"
echo "2. Lancez l'application avec: 'cd $PROJECT_DIR && ./run.sh'"
echo "3. Accédez à l'interface web: http://localhost:3000"
echo ""
echo "Documentation disponible dans: $PROJECT_DIR/docs"
echo ""
echo "RAPPEL: Utilisez cet outil de manière éthique et légale uniquement!"
