#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import venv

def run_command(command):
    """Exécute une commande système."""
    try:
        result = subprocess.run(command, shell=True, check=True, 
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
    
    if system == 'linux':
        # Pour Debian/Ubuntu/Kali
        run_command('sudo apt-get update')
        run_command('sudo apt-get install -y python3-pip python3-venv docker docker-compose git build-essential')
    
    elif system == 'windows':
        # Pour Windows, on suppose que Python et pip sont déjà installés
        run_command('pip install --upgrade pip')
        print("Assurez-vous d'avoir Docker Desktop installé.")
    
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

def activate_venv(venv_path):
    """Active l'environnement virtuel."""
    if platform.system().lower() == 'windows':
        activate_this = os.path.join(venv_path, 'Scripts', 'activate_this.py')
    else:
        activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')
    
    exec(open(activate_this).read(), {'__file__': activate_this})

def install_python_dependencies():
    """Installe les dépendances Python."""
    run_command('pip install -r requirements.txt')
    
def setup_docker():
    """Configure et lance les services Docker."""
    run_command('docker-compose up -d')

def main():
    print("🚀 Installation de TheWatcher-OSINT 🚀")
    
    install_system_dependencies()
    venv_path = create_virtual_env()
    activate_venv(venv_path)
    install_python_dependencies()
    setup_docker()
    
    print("\n✅ Installation terminée avec succès !")
    print("Lancez l'application avec : python backend/app.py")

if __name__ == '__main__':
    main()
