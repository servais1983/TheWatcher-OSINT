from setuptools import setup, find_packages

def get_version():
    return "0.1.0"

setup(
    name="thewatcher-osint",
    version="0.1.0",  # Version explicite
    packages=find_packages(),
    install_requires=[
        # Framework web
        'Flask==2.3.3',
        'Flask-RESTful==0.3.10',
        'Flask-Cors==4.0.0',
        'Flask-JWT-Extended==4.5.3',
        'gunicorn==21.2.0',
        'Werkzeug==2.3.7',

        # Base de données
        'psycopg2-binary==2.9.7',
        'SQLAlchemy==2.0.22',
        'elasticsearch==7.17.9',
        'redis==5.0.1',
        'Flask-SQLAlchemy==3.1.1',
        'alembic==1.12.0',

        # Sécurité
        'PyJWT==2.8.0',
        'bcrypt==4.0.1',
        'cryptography==41.0.4',
        'python-dotenv==1.0.0',
        'python-decouple==3.8',
        'Flask-Limiter==3.5.0',
        'pyotp==2.9.0',
        'authlib==1.2.1',

        # Image et reconnaissance faciale
        'opencv-python==4.8.1.78',
        'face-recognition==1.3.0',
        'dlib==19.24.2',
        'Pillow==10.0.1',
        'exifread==3.0.0',
        'boto3==1.28.53',

        # Web scraping et OSINT
        'beautifulsoup4==4.12.2',
        'requests==2.31.0',
        'requests-html==0.10.0',
        'Scrapy==2.11.0',
        'selenium==4.13.0',
        'google-api-python-client==2.99.0',
        'googlesearch-python==1.2.3',
        'PySocks==1.7.1',
        'shodan==1.30.1',

        # Analyse de données
        'pandas==2.1.1',
        'numpy==1.26.0',
        'networkx==3.1',
        'matplotlib==3.8.0',
        'pydotplus==2.0.2',

        # Traitement du langage naturel
        'nltk==3.8.1',
        'spacy==3.7.1',
        'textblob==0.17.1',

        # Validation et schémas
        'marshmallow==3.20.1',
        'jsonschema==4.19.1',
        'pydantic==2.4.2',

        # Utilitaires
        'tqdm==4.66.1',
        'python-magic==0.4.27',
        'python-whois==0.8.0',
        'pytz==2023.3.post1',
        'geopy==2.4.0',
        'geoip2==4.7.0',
        'phonenumbers==8.13.22',
        'python-Levenshtein==0.21.1',
        'python-dateutil==2.8.2',
        'validators==0.22.0',
    ],
    extras_require={
        'dev': [
            # Documentation
            'Sphinx==7.2.6',
            'Flask-Swagger-UI==4.11.1',
            'apispec==6.3.0',

            # Tests
            'pytest==7.4.2',
            'pytest-cov==4.1.0',
        ]
    },
    author="servais1983",
    description="Un outil OSINT éthique pour la recherche d'informations",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/servais1983/TheWatcher-OSINT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
