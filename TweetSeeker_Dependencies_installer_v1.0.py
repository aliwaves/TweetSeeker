############################################################################
#   DEPENDANCY INSTALLER SCRIPT FOR TWEETSEEKER
#---------------------------------------------------------------------------
# Written On: 4/5/2023
# Written by: Austin Daigle
# Version: 1.0
# 
# This is a script that install the required dependancies 
# for TwitterSeeker_core_v.1.0.py. Run this script before 
# running the program.
############################################################################

import importlib
import subprocess

packages = ['importlib', 'subprocess', 'requests', 'tweepy', 'csv', 'datetime', 'os']
# installation method
def installPackagesIfNeeded():
    # for every package in the list
    for package in packages:
        # check to see if the package exits and print that it is installed
        try:
            importlib.import_module(package)
            print(f'{package} already installed')
        # if the package is not there, then install it automatically to pip
        except ImportError:
            print(f'{package} not found, installing...')
            subprocess.check_call(['pip', 'install', package])

installPackagesIfNeeded()