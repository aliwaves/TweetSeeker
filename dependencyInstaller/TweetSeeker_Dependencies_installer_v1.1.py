############################################################################
#   DEPENDANCY INSTALLER SCRIPT FOR TWEETSEEKER
#---------------------------------------------------------------------------
# Written On: 4/11/2023
# Written by: Austin Daigle
# Version: 1.1
# 
# This is a script that install the required dependancies 
# for TweetSeeker_v1.0_alpha.py. Run this script before 
# running the program.
############################################################################

import importlib
import subprocess

# all of the packages found inside of TweekSeeker_v1.0_alpha
# update this list is there are more packages included into the
# TweetSeeker program and update the installer script as a 
# separate newer version.
packages = [
    'tkinter',
    'tkinter.messagebox',
    'subprocess',
    'requests',
    'tweepy',
    'csv',
    'datetime',
    'os',
    'json',
    'boto3']

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