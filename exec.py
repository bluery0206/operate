import subprocess
from pathlib import Path

cwd = Path().cwd().resolve()
print(f"{cwd=}")

def clean_text(text:str) -> str:
    text = text.replace("\n", "")
    text = text.strip()

    return text

# subprocess.run accepts a list or arguments to run like
# ["py", "-m", "venv", "venv"]
def split_command(command:str) -> list[str]:
    command = command.split(" ")

    return command

commands = []

venv = cwd.joinpath("venv/Scripts/python.exe")
pkgs = list(cwd.glob("venv/Lib/site-packages/*"))
print(f"{venv=}")

if not venv.exists():
    commands.append(split_command("py -m venv venv"))

if len(pkgs) < 3:
    commands.append(split_command(str(venv) + " -m pip install -r requirements.txt"))
    commands.append(split_command(str(venv) + " manage.py makemigrations"))       
    commands.append(split_command(str(venv) + " manage.py migrate"))
    commands.append(split_command(str(venv) + " manage.py createsuperuser"))

commands.append(split_command(str(venv) + " manage.py runserver"))

for command in commands:
    process = subprocess.run(command)
    
    if process.returncode != 0:
        print(f"Error running command: {command}")
        break