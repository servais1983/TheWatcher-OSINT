#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import venv

def run_command(command, shell=True):
    """Exécute une commande système."""
    try:
        result = subprocess.run(command, shell=shell, check=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de {command}:")
        print(e.stderr)
        sys.exit(1)

def install_system_dependencies():
    """Installe les dépendances système selon la plateforme."""
    system = platform.system().lower()
    
    if system == 'windows':
        # Pour Windows, on utilise pip et winget si possible
        run_command('python -m pip install --upgrade pip')
        print("Assurez-vous d'avoir Docker Desktop installé.")
    
    elif system == 'linux':
        # Pour les systèmes Linux
        run_command('sudo apt-get update')
        run_command('sudo apt-get install -y python3-pip python3-venv docker docker-compose git')
    
    else:
        print(f"Système {system} non supporté.")
        sys.exit(1)

def create_virtual_env():
    """Crée un environnement virtuel Python."""
    venv_path = 'venv'
    
    if not os.path.exists(venv_path):
        print("Création de l'environnement virtuel...")
        venv.create(venv_path, with_pip=True)
    
    return venv_path

def activate_virtual_env(venv_path):
    """Active l'environnement virtuel."""
    system = platform.system().lower()
    
    if system == 'windows':
        activate_path = os.path.join(venv_path, 'Scripts', 'activate')
        return f'"{activate_path}"'
    else:
        activate_path = os.path.join(venv_path, 'bin', 'activate')
        return f'source "{activate_path}"'

def install_python_dependencies():
    """Installe les dépendances Python."""
    run_command('pip install -r requirements.txt')

def setup_docker():
    """Configure et lance les services Docker."""
    try:
        run_command('docker-compose up -d')
    except Exception as e:
        print("Erreur lors du démarrage de Docker :")
        print(str(e))
        print("Assurez-vous que Docker Desktop est installé et en cours d'exécution.")

def main():
    print("🚀 Installation de TheWatcher-OSINT 🚀")
    
    # Changement de répertoire de travail
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    install_system_dependencies()
    venv_path = create_virtual_env()
    
    # Commande d'activation de l'environnement virtuel
    activate_cmd = activate_virtual_env(venv_path)
    print(f"\nActivez l'environnement virtuel avec : {activate_cmd}")
    
    # Installation des dépendances
    install_python_dependencies()
    
    # Configuration Docker
    setup_docker()
    
    print("\n✅ Installation terminée avec succès !")
    print("Étapes suivantes :")
    print("1. Activez l'environnement virtuel")
    print("2. Lancez l'application avec : python backend/app.py")

if __name__ == '__main__':
    main()
