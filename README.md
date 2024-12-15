## Install
1. Open cmd
2. Check if you're in the `main` branch

![branch](markdown_images/branches.jpg)

If not, select `main`

![branch](markdown_images/select_branches.jpg)

3. Clone the repo: `git clone https://github.com/bluery0206/operate.git`.
4. Change directory `cd PATH\operate` after download. Change `PATH` to actual full path to `operate` folder.
5. Create python environment `py -m venv venv`
6. Activate environment `venv\scripts\activate`
7. Install all dependencies `pip install -r requirements.txt`
8. Create your own admin account `py manage.py createsuperuser`
9. Run server `py manage.py runserver`
10. Done

## Pull
1. Open cmd
2. Change directory `cd PATH\operate`. Change `PATH` to actual full path to `operate` folder.
3. Activate environment `venv\scripts\activate`
4. Pull `git pull`
5. Done

## Push
1. Open cmd
2. Change directory `cd PATH\operate`. Change `PATH` to actual full path to `operate` folder.
3. Activate environment `venv\scripts\activate`
4. Stage all changes `git add -A`
5. Commit all changes `git commit -m MESSAGE`. Change `MESSAGE` to atual message like what have changed.
6. Done
