from os import path, system

"""
  Setup this project by installing dependencies and setting up files/directories.
"""

if (not path.exists('.secrets')):
  envFile = open('.secrets', 'w')
  envFile.write('API_KEY=')
  envFile.close()

system('pip install pipenv')
system('pipenv update')
