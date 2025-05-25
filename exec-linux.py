"""

Date: May 25, 2025
Author: Mark Ryan I. Hilario
Description:
    Derived from the originial `exec.py` to support linux.
Usage:
    In the operate folder terminal and run `python3 exec-linux.py`

"""

import webbrowser
import subprocess
import time
import os
from pathlib import Path

cwd = Path(__file__).parent
print(f"{cwd=}")

venv = cwd.joinpath("venv/bin/python")
mnge = cwd.joinpath("manage.py")
pkgs = list(cwd.glob("venv/lib/python3.12/site-packages/*"))
print(f"{venv=}")

commands = []

if not venv.exists():
    commands.append(["python", "-m", "venv", "venv"])

# The 3 is to excempt pip packages.
# So if only pip packages are in the packages, then the commands below
#   will be added to the list of commands to execute.
if len(pkgs) < 3:
    commands.append( [str(venv), "-m", "pip", "install", "-r", "requirements.txt"])
    commands.append([str(venv), str(mnge), "makemigrations"])
    commands.append([str(venv), str(mnge), "migrate"])
    commands.append([str(venv), str(mnge), "createsuperuser"])

commands.append([str(venv), str(mnge), "runserver"])

for idx, command in enumerate(commands):
    # Open browser after a set time when the last command is to be executed
    if idx + 1 == len(commands):
        time.sleep(3)

        # Open browser
        webbrowser.open("http://localhost:8000/")

    process = subprocess.run(command, cwd=cwd)
