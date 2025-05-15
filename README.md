![Capture d'écran 2025-05-15 142625](https://github.com/user-attachments/assets/cc33695d-67bd-475e-918d-880f4cfc218d)


# TheWatcher 🔍

Un outil OSINT (Open Source Intelligence) éthique conçu pour la recherche d'informations à partir de photos (reconnaissance faciale) ou de noms (recherche dans les données ouvertes).

![Version](https://img.shields.io/badge/version-0.1.1-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platforms](https://img.shields.io/badge/platforms-Linux%20%7C%20Windows-brightgreen.svg)

## 🚨 Avertissement Légal et Éthique

**TheWatcher est un outil à utiliser exclusivement dans un cadre légal et éthique.**

- Respecte les lois sur la protection des données
- Ne doit pas être utilisé pour harceler ou porter atteinte à la vie privée
- Requiert le consentement approprié

## 🌟 Caractéristiques Principales

- Reconnaissance faciale
- Recherche d'images inversées
- Analyse de métadonnées EXIF
- Agrégation de données depuis les réseaux sociaux
- Cartographie des relations

## 🛠️ Installation Rapide

### Prérequis
- Python 3.8+
- Docker et Docker Compose
- Git

### Installation Automatique (Linux & Windows)

```bash
# Cloner le dépôt
git clone https://github.com/servais1983/TheWatcher-OSINT.git
cd TheWatcher-OSINT

# Lancer le script d'installation
python install.py
```

### Méthodes d'Installation Alternatives

1. **Kali Linux/Debian** :
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv docker docker-compose
   ```

2. **Windows** :
   - Installer Python depuis python.org
   - Installer Docker Desktop
   - Exécuter le script d'installation

## 🚀 Démarrage Rapide

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux
venv\Scripts\activate     # Windows

# Lancer l'application
python backend/app.py
```

## 📚 Documentation Complète

- [Guide d'Installation Détaillé](INSTALL.md)
- [Spécifications Techniques](docs/requirements.md)
- [Guide d'Utilisation](docs/usage.md)

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez consulter [CONTRIBUTING.md](CONTRIBUTING.md).

## 📝 Licence

Projet sous licence MIT - Voir [LICENSE](LICENSE) pour plus de détails.

---

*Développé avec ❤️ pour la communauté de cybersécurité éthique.*

**Rappel** : Utilisez cet outil de manière responsable et éthique.
