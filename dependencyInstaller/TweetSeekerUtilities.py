import importlib
import subprocess

packages = ['importlib', 'subprocess', 'requests', 'tweepy', 'csv', 'datetime', 'os']

def install_packages_if_needed():
    for package in packages:
        try:
            importlib.import_module(package)
            print(f'{package} already installed')
        except ImportError:
            print(f'{package} not found, installing...')
            subprocess.check_call(['pip', 'install', package])

install_packages_if_needed()