# Guide de Contribution à TheWatcher

Nous vous remercions de votre intérêt pour contribuer à TheWatcher ! Ce document présente les directives pour contribuer efficacement au projet.

## Table des matières

1. [Code de conduite](#code-de-conduite)
2. [Comment contribuer](#comment-contribuer)
   - [Signaler des bugs](#signaler-des-bugs)
   - [Suggérer des améliorations](#suggérer-des-améliorations)
   - [Proposer du code](#proposer-du-code)
3. [Style de code](#style-de-code)
4. [Processus de développement](#processus-de-développement)
5. [Structure du projet](#structure-du-projet)
6. [Tests](#tests)
7. [Documentation](#documentation)
8. [Questions fréquentes](#questions-fréquentes)

## Code de conduite

Ce projet adhère à un Code de Conduite adapté du [Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). 
En participant, vous êtes tenu de respecter ce code.

Les principes fondamentaux sont :
- Utiliser un langage accueillant et inclusif
- Respecter les différents points de vue et expériences
- Accepter gracieusement les critiques constructives
- Se concentrer sur ce qui est le mieux pour la communauté
- Faire preuve d'empathie envers les autres membres

## Comment contribuer

### Signaler des bugs

Si vous trouvez un bug dans TheWatcher, veuillez créer une issue sur GitHub avec :

1. Un titre clair et descriptif
2. Une description détaillée du problème
3. Les étapes pour reproduire le bug
4. Le comportement attendu vs observé
5. Des captures d'écran si applicable
6. Votre environnement (OS, version de Python, etc.)

Utilisez le modèle fourni lors de la création d'une issue.

### Suggérer des améliorations

Pour proposer de nouvelles fonctionnalités ou améliorations :

1. Vérifiez que votre idée n'a pas déjà été suggérée
2. Créez une issue avec le tag "enhancement"
3. Décrivez clairement la fonctionnalité et sa valeur ajoutée
4. Proposez une implémentation si possible

### Proposer du code

Pour contribuer directement au code :

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. Implémentez vos modifications
4. Ajoutez des tests pour votre code
5. Assurez-vous que tous les tests passent
6. Mettez à jour la documentation si nécessaire
7. Soumettez une Pull Request

**Important** : Toute contribution doit respecter le cadre légal et éthique du projet.

## Style de code

TheWatcher suit les conventions de style Python PEP 8 et utilise les outils suivants :

- **Python** : [Black](https://github.com/psf/black) pour le formatage
- **JavaScript** : [ESLint](https://eslint.org/) avec configuration Airbnb
- **Documentation** : [NumPy docstring format](https://numpydoc.readthedocs.io/en/latest/format.html)

Avant de soumettre votre code :
```bash
# Formater le code Python
black backend/

# Linter JavaScript
cd frontend && npm run lint
```

## Processus de développement

1. Choisissez une issue à traiter ou créez-en une nouvelle
2. Discutez de l'approche dans l'issue si nécessaire
3. Forkez et clonez le dépôt
4. Créez une branche spécifique
5. Développez votre solution
6. Testez vos modifications
7. Soumettez une Pull Request
8. Répondez aux revues de code

Les branches doivent suivre cette nomenclature :
- `feature/nom-de-la-fonctionnalite`
- `bugfix/description-du-bug`
- `docs/sujet-de-documentation`
- `refactor/composant-refactorise`

## Structure du projet

```
TheWatcher-OSINT/
├── backend/                # Code du backend Flask
│   ├── modules/            # Modules OSINT
│   ├── utils/              # Utilitaires
│   └── app.py              # Point d'entrée principal
├── frontend/               # Interface React
├── docs/                   # Documentation
├── tests/                  # Tests automatisés
└── docker-compose.yml      # Configuration Docker
```

## Tests

Tous les nouveaux codes doivent être accompagnés de tests. Nous utilisons :
- pytest pour le backend Python
- Jest pour le frontend React

Pour exécuter les tests :
```bash
# Tests backend
cd backend && pytest

# Tests frontend
cd frontend && npm test
```

La couverture de code minimale est de 70%.

## Documentation

La documentation est essentielle pour ce projet. Pour toute nouvelle fonctionnalité :

1. Ajoutez des docstrings à toutes les fonctions, classes et modules
2. Mettez à jour les guides d'utilisation pertinents
3. Documentez les API dans les fichiers swagger correspondants
4. Ajoutez des exemples d'utilisation si nécessaire

## Questions fréquentes

**Q: Comment puis-je tester sans configurer toutes les API externes ?**

R: Utilisez les mocks fournis dans le module de test. Consultez le fichier 
`tests/test_utils/api_mocks.py` pour des exemples.

**Q: Comment ajouter un nouveau module OSINT ?**

R: Créez un nouveau fichier Python dans le dossier `backend/modules/` en suivant le modèle des modules existants. Assurez-vous d'implémenter les interfaces communes et de documenter les nouvelles fonctionnalités.

**Q: Y a-t-il des directives spécifiques pour les contributions liées à la reconnaissance faciale ?**

R: Oui, toute contribution relative à la reconnaissance faciale doit être particulièrement attentive aux aspects éthiques et légaux. Consultez le document `docs/legal.md` pour plus de détails sur les limites à respecter.

**Q: Comment gérer les clés API dans mes tests et contributions ?**

R: N'incluez jamais de clés API réelles dans votre code. Utilisez le système de variables d'environnement et le fichier `.env.example` pour documenter les clés nécessaires. Pour les tests, utilisez les clés de test ou les mocks.

**Q: Comment exécuter TheWatcher en mode développement ?**

R: Utilisez la commande suivante pour le mode développement :
```bash
# Activer le mode développement
export APP_ENV=development

# Lancer l'application
./run.sh
```

## Considérations Éthiques Particulières

Étant donné la nature sensible de l'OSINT, nous avons des exigences supplémentaires pour certains types de contributions :

### Modules de Web Scraping
- Respectez les fichiers robots.txt
- Incluez des délais adaptables entre les requêtes
- Documentez clairement les sites ciblés

### Fonctionnalités de Reconnaissance Faciale
- Implémentez des options de consentement explicites
- Limitez la précision des correspondances si nécessaire
- Documentez les implications légales par juridiction

### Stockage de Données
- Respectez les principes de minimisation des données
- Implémentez des mécanismes d'expiration automatique
- Fournissez des options de chiffrement

## Communication

Pour discuter avec la communauté de développeurs :
- **Chat Discord** : Rejoignez notre serveur Discord à [https://discord.gg/thewatcher](https://discord.gg/thewatcher)
- **Mailing List** : Inscrivez-vous à [dev-list@thewatcher-osint.org](mailto:dev-list@thewatcher-osint.org)
- **Réunions** : Nous organisons des appels bimensuels (voir le calendrier sur le wiki)

## Reconnaissance des contributions

Nous valorisons toutes les contributions, grandes ou petites. Les contributeurs sont mentionnés dans :
- Le fichier CONTRIBUTORS.md à la racine du projet
- Les notes de version pour les fonctionnalités majeures
- La section "À propos" de l'application

## Ressources supplémentaires

- [Guide de développement détaillé](docs/development.md)
- [Architecture du projet](docs/architecture.md)
- [Guide de sécurité](docs/security.md)
- [Wiki du projet](https://github.com/servais1983/TheWatcher-OSINT/wiki)

---

Merci encore pour votre intérêt à contribuer à TheWatcher. Votre aide est essentielle pour faire de cet outil un projet OSINT éthique et puissant qui respecte les droits fondamentaux.
