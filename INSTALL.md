# Guide d'Installation Simplifié pour TheWatcher-OSINT

## 🐧 Installation sur Kali Linux

### Prérequis
- Kali Linux mis à jour
- Python 3.8+
- Docker et Docker Compose

### Installation Étape par Étape

1. Mettre à jour le système
```bash
sudo apt update && sudo apt upgrade -y
```

2. Installer les dépendances système
```bash
sudo apt install -y python3 python3-pip python3-venv docker docker-compose git build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev
```

3. Configurer Docker
```bash
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

4. Cloner le dépôt
```bash
git clone https://github.com/servais1983/TheWatcher-OSINT.git
cd TheWatcher-OSINT
```

5. Configurer l'environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. Résoudre les problèmes potentiels de dépendances
```bash
pip install --upgrade pip setuptools wheel
pip install dlib
```

7. Configurer les services
```bash
cp .env.example .env
docker-compose up -d
```

8. Lancer l'application
```bash
source venv/bin/activate
cd backend
python app.py
```

## 🪟 Installation sur Windows (CMD)

### Prérequis
- Windows 10/11
- Python 3.8+ 
- Docker Desktop
- Git

### Installation Étape par Étape

1. Installer Python
- Télécharger depuis python.org
- Cocher "Ajouter Python au PATH"

2. Installer Docker Desktop
- Télécharger depuis docker.com
- Activer la virtualisation dans le BIOS si nécessaire

3. Ouvrir CMD en mode Administrateur

4. Cloner le dépôt
```cmd
git clone https://github.com/servais1983/TheWatcher-OSINT.git
cd TheWatcher-OSINT
```

5. Créer un environnement virtuel
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

6. Configurer Docker
```cmd
docker-compose up -d
```

7. Lancer l'application
```cmd
cd backend
python app.py
```

## 🛠️ Dépannage

### Problèmes courants
- Vérifier les versions de Python et des bibliothèques
- S'assurer que Docker tourne correctement
- Consulter les logs Docker et Python

### Contactez le support
- Ouvrez une issue sur GitHub
- Incluez votre configuration système et les logs d'erreur

*Utilisez toujours cet outil de manière éthique et légale.*
