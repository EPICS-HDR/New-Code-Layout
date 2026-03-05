'''
Author: Kartik Jariam
Date: 3/05/2026
Purpose: This is the backend's API. Any and all commands accessable to front end and the user will be available here.
''' 
from pathlib import Path
import os
import sys

def listAllSources():
    os.chdir('./BackEnd/SourceFiles')
    sources = []
    for file in Path('./').glob('_*.py'):
        source += file.name.replace('.py','')
    return sources

def listStations(source):
    pass




if (__name__ == "__main__"):
    listAllSources()