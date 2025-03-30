#!/bin/bash

# TheWatcher - Script de démarrage
# Ce script démarre les services nécessaires et l'application

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
echo -e "Démarrage de TheWatcher - Outil OSINT Éthique"
echo -e "Version: 0.1.0"
echo -e ""

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    warning "Fichier .env non trouvé. Création à partir de .env.example"
    cp .env.example .env
    echo "Veuillez éditer le fichier .env avec vos clés API"
fi

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    warning "Environnement virtuel non trouvé. Exécutez d'abord le script d'installation."
    exit 1
fi

# Activer l'environnement virtuel
info "Activation de l'environnement virtuel"
source venv/bin/activate || error "Impossible d'activer l'environnement virtuel"

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    warning "Docker n'est pas installé. Les services de base de données et Elasticsearch ne seront pas disponibles."
    USE_DOCKER=false
else
    USE_DOCKER=true
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    if [ "$USE_DOCKER" = true ]; then
        warning "Docker Compose n'est pas installé. Les services de base de données et Elasticsearch ne seront pas disponibles."
        USE_DOCKER=false
    fi
fi

# Démarrer les services Docker si disponibles
if [ "$USE_DOCKER" = true ]; then
    info "Démarrage des services Docker..."
    
    # Vérifier si les services sont déjà en cours d'exécution
    if docker-compose ps | grep -q "thewatcher"; then
        info "Les services Docker sont déjà en cours d'exécution"
    else
        docker-compose up -d || warning "Impossible de démarrer les services Docker"
    fi
else
    warning "Les services Docker ne seront pas démarrés. L'application utilisera SQLite à la place."
    
    # Modifier la configuration pour utiliser SQLite
    export USE_SQLITE=true
fi

# Créer les répertoires nécessaires
mkdir -p backend/logs backend/uploads backend/data/reports || warning "Impossible de créer certains répertoires"

# Vérifier les outils Selenium
info "Vérification de la configuration de Selenium..."
if ! command -v chromedriver &> /dev/null; then
    warning "ChromeDriver n'est pas installé ou n'est pas dans PATH. Certaines fonctionnalités OSINT utilisant Selenium ne fonctionneront pas."
    warning "Pour installer ChromeDriver: sudo apt install -y chromium-driver"
fi

# Vérifier la présence de Sherlock
if [ ! -d "$SHERLOCK_PATH" ]; then
    SHERLOCK_PATH="/opt/sherlock"
    if [ ! -d "$SHERLOCK_PATH" ]; then
        warning "Sherlock n'est pas installé dans le chemin par défaut (/opt/sherlock)."
        warning "Certaines fonctionnalités de recherche de nom d'utilisateur ne fonctionneront pas."
        warning "Pour installer Sherlock: git clone https://github.com/sherlock-project/sherlock.git /opt/sherlock"
    else
        export SHERLOCK_PATH="/opt/sherlock"
    fi
fi

# Fonction pour démarrer le backend
start_backend() {
    info "Démarrage du backend Flask..."
    cd backend
    python app.py &
    BACKEND_PID=$!
    cd ..
    success "Backend démarré (PID: $BACKEND_PID)"
}

# Fonction pour démarrer le frontend
start_frontend() {
    if [ -d "frontend" ]; then
        info "Démarrage du frontend..."
        cd frontend
        
        if [ -f "package.json" ]; then
            # Vérifier si node_modules existe
            if [ ! -d "node_modules" ]; then
                warning "Les dépendances frontend ne sont pas installées. Installation en cours..."
                npm install || warning "Impossible d'installer les dépendances frontend"
            fi
            
            npm start &
            FRONTEND_PID=$!
            cd ..
            success "Frontend démarré (PID: $FRONTEND_PID)"
        else
            warning "Le fichier package.json n'existe pas. Le frontend ne sera pas démarré."
            cd ..
        fi
    else
        warning "Le répertoire frontend n'existe pas. Le frontend ne sera pas démarré."
    fi
}

# Enregistrer les PIDs pour le nettoyage
echo "" > .pids

# Démarrer le backend
start_backend
echo "BACKEND_PID=$BACKEND_PID" >> .pids

# Démarrer le frontend
start_frontend
if [ -n "$FRONTEND_PID" ]; then
    echo "FRONTEND_PID=$FRONTEND_PID" >> .pids
fi

# Afficher les informations d'accès
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "TheWatcher est maintenant en cours d'exécution!"
echo ""
echo "🔍 Backend API: http://localhost:5000"
if [ -n "$FRONTEND_PID" ]; then
    echo "🌐 Frontend: http://localhost:3000"
fi
if [ "$USE_DOCKER" = true ]; then
    echo "📊 PostgreSQL: localhost:5432"
    echo "🔍 Elasticsearch: http://localhost:9200"
    echo "💾 Redis: localhost:6379"
fi
echo ""
echo "Pour arrêter l'application, exécutez: ./stop.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Attendre que l'utilisateur appuie sur Ctrl+C
trap 'echo -e "\nArrêt de TheWatcher..." && kill $BACKEND_PID 2>/dev/null && kill $FRONTEND_PID 2>/dev/null && echo "Terminé!" && exit 0' INT
while true; do sleep 1; done
