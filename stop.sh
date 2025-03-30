#!/bin/bash

# TheWatcher - Script d'arrêt
# Ce script arrête l'application et les services

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

# Message de début
echo -e "${BLUE}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Arrêt de TheWatcher - Outil OSINT Éthique"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"

# Vérifier si le fichier .pids existe
if [ ! -f ".pids" ]; then
    warning "Fichier .pids non trouvé. Impossible de déterminer les processus à arrêter."
    
    # Tenter de trouver et arrêter les processus Python et Node.js
    info "Tentative d'arrêt des processus Python et Node.js..."
    pkill -f "python backend/app.py" || warning "Aucun processus Python trouvé"
    pkill -f "node.*start" || warning "Aucun processus Node.js trouvé"
else
    # Lire les PIDs du fichier
    source .pids
    
    # Arrêter le backend
    if [ -n "$BACKEND_PID" ]; then
        info "Arrêt du backend (PID: $BACKEND_PID)..."
        kill -15 $BACKEND_PID 2>/dev/null || warning "Impossible d'arrêter le backend, le processus n'existe peut-être plus."
    else
        warning "Aucun PID de backend trouvé dans .pids"
    fi
    
    # Arrêter le frontend
    if [ -n "$FRONTEND_PID" ]; then
        info "Arrêt du frontend (PID: $FRONTEND_PID)..."
        kill -15 $FRONTEND_PID 2>/dev/null || warning "Impossible d'arrêter le frontend, le processus n'existe peut-être plus."
    else
        warning "Aucun PID de frontend trouvé dans .pids"
    fi
    
    # Supprimer le fichier .pids
    rm .pids
fi

# Vérifier si Docker est installé
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    # Demander si l'utilisateur souhaite arrêter les services Docker
    read -p "Voulez-vous arrêter les services Docker (PostgreSQL, Elasticsearch, etc.) ? [o/N] " stop_docker
    
    if [[ $stop_docker == "o" || $stop_docker == "O" ]]; then
        info "Arrêt des services Docker..."
        docker-compose stop || warning "Impossible d'arrêter les services Docker"
    else
        info "Les services Docker restent en cours d'exécution."
    fi
fi

success "TheWatcher a été arrêté avec succès!"
