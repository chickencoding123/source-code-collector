from os import path, system

"""
  Setup this project by creating a venv module and installing dependencies
"""

if (not path.exists('.env')):
  envFile = open('.env', 'w')
  envFile.write('API_KEY=')
  envFile.close()

if (not path.exists('.venv/bin/activate')):
  system('python3 -m venv .venv')

system('. .venv/bin/activate && pip install -r requirements.txt')
