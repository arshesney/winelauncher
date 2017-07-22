try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'WINE wrapper',
    'author': 'Arshesney',
    'url': 'https://github.com/arshesney/winelauncher',
    'download_url': 'https://github.com/arshesney/winelauncher',
    'author_email': 'arsh79@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'winelauncher',
    'python_requires': '>=3'
}

setup(**config)

