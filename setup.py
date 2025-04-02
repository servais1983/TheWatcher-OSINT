from setuptools import setup, find_packages

def get_version():
    return "0.1.0"

setup(
    name="thewatcher-osint",
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        # Ajoutez ici les dépendances de requirements.txt
    ],
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
