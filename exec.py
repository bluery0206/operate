import webbrowser
import subprocess
import time
import os
from pathlib import Path

cwd = Path(__file__).parent
print(f"{cwd=}")

venv = cwd.joinpath("venv/Scripts/python.exe")
mnge = cwd.joinpath("manage.py")
pkgs = list(cwd.glob("venv/Lib/site-packages/*"))
print(f"{venv=}")

# Set environment to project's environment
env = os.environ.copy()
env['PATH'] = f"{cwd / 'venv/Scripts'};{env['PATH']}"

commands = []

if not venv.exists():
    commands.append(["py", "-m", "venv", "venv"])

# The 3 is to excempt pip packages.
# So if only pip packages are in the packages, then the commands below
#   will be added to the list of commands to execute.
if len(pkgs) < 3:
    commands.append(
        [str(venv), "-m", "pip", "install", "-r", "requirements.txt"],
        [str(venv), str(mnge), "makemigrations"],
        [str(venv), str(mnge), "migrate"],
        [str(venv), str(mnge), "createsuperuser"])

commands.append(str(venv) + " " + str(mnge) + " runserver")

for idx, command in enumerate(commands):
    # Open browser after a set time when the last command is to be executed
    if idx + 1 == len(commands):
        time.sleep(3)

        # Open browser
        webbrowser.open("http://localhost:8000/")

    process = subprocess.run(command, cwd=cwd, env=env)
    
