## System Overview

OPeraTE (Optimized Personnel and Inmate Tracking Efficiency) is a centralized, web-based system developed to enhance data management and security for the Philippine National Police (PNP) in Clarin, Bohol. The system streamlines personnel and inmate profiling, reduces inefficiencies caused by manual processes, and ensures secure and fast data retrieval.

### Key Features
* Face Search: Powered by a Siamese Neural Network (SNN) with Triplet Loss for profile matching using images.
* Profile Management: Enables creating, editing, searching, and archiving personnel and inmate profiles.

## System Requirements
### Hardware Requirements:
* Storage: At least 500mb free space.

### Software Requirements
* Operating System: Windows 10 or higher (Linux not tested)
* Python 3.12.3
* Dependencies listed in `requirements.txt`


## Installation Guide

### Get repository link

1. Open this link: https://github.com/bluery0206/operate/tree/main

2. Check if you're on the main branch
    <br/> ![branches](https://github.com/user-attachments/assets/429b2ad0-6cf3-408e-8bc4-2362e00e4e71)
    <br/> If it doesn't says `main`, click on the dropdown button, and select `main`
    <br/> ![select_main_branch](https://github.com/user-attachments/assets/1f670ade-08cf-4638-98a9-13599767ac6e)

3. Copy the link: https://github.com/bluery0206/operate.git
    <br/> ![copy_link](https://github.com/user-attachments/assets/9930f525-3d31-4ff1-950e-d915f5f705f5)

### Download using Command Line (CMD)

1. Open cmd 
   <br/> ![cmd](https://github.com/user-attachments/assets/5c3665a3-0090-4918-ae94-e187b18777ee)

2. Change directory `cd PATH` where `PATH` is your desired directory to download/clone the repository. e.g. `cd documents`
   <br/> ![cd_document](https://github.com/user-attachments/assets/047d7a02-2cf9-452a-a7d8-132c3b3f83e7)
   <br/> Result:
   <br/> ![cd_document_result](https://github.com/user-attachments/assets/97f6c72c-cddb-405b-babf-abdf08386841)

3. Clone the repository `git clone https://github.com/bluery0206/operate.git`.
   <br/> ![git_clone](https://github.com/user-attachments/assets/f159dfd7-619a-4b50-aedc-57e8dbb76b60)
   <br/> Result:
   <br/> ![git_clone_result](https://github.com/user-attachments/assets/9d9c3b08-5197-48e8-a275-dfcc835053ad)

4. Change directory `cd operate` after download, assuming that you haven't closed cmd after download.
   <br/> ![cd_operate](https://github.com/user-attachments/assets/0fe856b4-02a1-4d01-8d57-b2bdfbf7755a)
   <br/> Result:
   <br/> ![cd_operate_result](https://github.com/user-attachments/assets/3351a332-13ac-4d3c-a39c-73921cf8c47a)

5. Create python environment `py -m venv venv`
   <br/> ![create_venv_result](https://github.com/user-attachments/assets/693359e3-4d0c-4340-8fe8-5324c173e673)

6. Activate environment `venv\scripts\activate`
   <br/> ![activate_venv](https://github.com/user-attachments/assets/121080e5-9930-4b95-bb97-b6ae7faa058c)

7. Install all dependencies `pip install -r requirements.txt`
   <br/> ![install_requirements](https://github.com/user-attachments/assets/97bc4073-95bf-49c4-956a-2e733cb09fef)
   <br/> After installation:
   <br/> ![install_requirements_result](https://github.com/user-attachments/assets/eccc98bd-aedc-4e44-aa69-49bf1b366e65)

8. Prepare database `py manage.py makemigrations`
   <br/> ![makemigrations](https://github.com/user-attachments/assets/6a80ca95-7079-46eb-85dd-2241402b0718)

9. Initialize database `py manage.py migrate`
   <br/> ![migrate](https://github.com/user-attachments/assets/3a8aedb8-d8dc-42a5-8e0a-a246a6f18acf)
   <br/> After migration:
   <br/> ![migrate_result](https://github.com/user-attachments/assets/ea0a24c5-75f5-45d1-b0c2-20ff2cdc3f02)

10. Create your own admin account `py manage.py createsuperuser`
   <br/> ![createsuperuser](https://github.com/user-attachments/assets/8cdb0ab1-3a8f-4fda-a145-2f99c34ff966)

11. Run server `py manage.py runserver`
   <br/> ![image](https://github.com/user-attachments/assets/29ce2a46-a06a-4979-9fd4-ffed65089e2a)

12. Open this link in the browser: `http://127.0.0.1:8000/`
   <br/> ![image](https://github.com/user-attachments/assets/6c32b5f1-6cff-4e53-8c72-242fbff855c0)

13. Done


### Download using VS Code
1. Open Source Control Panel and click `Clone Repository`
   <br/> ![image](https://github.com/user-attachments/assets/286e8970-ed39-4715-aff8-92d6d8c0bb7b)

2. Paste the link
   <br/> ![image](https://github.com/user-attachments/assets/114c5ddc-0c58-4b43-8fee-ba7b8efba7d7)

3. Select the destination folder wherever you want
   <br/> ![image](https://github.com/user-attachments/assets/9058f9ff-076d-4827-9173-f586b0c08246)

4. Wait 'till finished
   <br/> ![image](https://github.com/user-attachments/assets/1e1c9fd1-7608-4fc5-a246-c66c3dbb5c83)

5. Done
   <br/>  ![image](https://github.com/user-attachments/assets/7989aab7-462d-4e29-8b3e-340096560cb2)

#### Install
1. Open cmd 
   <br/> ![cmd](https://github.com/user-attachments/assets/5c3665a3-0090-4918-ae94-e187b18777ee)

2. Change directory `cd PATH` where `PATH` is the actual full path to operate folder. E.g. `cd documents\operate`
   <br/>  ![image](https://github.com/user-attachments/assets/f859a93f-8761-420c-9a8b-1531cc54c6e0)

3. Create python environment `py -m venv venv`
   <br/> ![create_venv_result](https://github.com/user-attachments/assets/693359e3-4d0c-4340-8fe8-5324c173e673)

4. Activate environment `venv\scripts\activate`
   <br/> ![activate_venv](https://github.com/user-attachments/assets/121080e5-9930-4b95-bb97-b6ae7faa058c)

5. Install all dependencies `pip install -r requirements.txt`
   <br/> ![install_requirements](https://github.com/user-attachments/assets/97bc4073-95bf-49c4-956a-2e733cb09fef)
   <br/> After installation:
   <br/> ![install_requirements_result](https://github.com/user-attachments/assets/eccc98bd-aedc-4e44-aa69-49bf1b366e65)

6. Prepare database `py manage.py makemigrations`
   <br/> ![makemigrations](https://github.com/user-attachments/assets/6a80ca95-7079-46eb-85dd-2241402b0718)

7. Initialize database `py manage.py migrate`
   <br/> ![migrate](https://github.com/user-attachments/assets/3a8aedb8-d8dc-42a5-8e0a-a246a6f18acf)
   <br/> After migration:
   <br/> ![migrate_result](https://github.com/user-attachments/assets/ea0a24c5-75f5-45d1-b0c2-20ff2cdc3f02)

8. Create your own admin account `py manage.py createsuperuser`
   <br/> ![createsuperuser](https://github.com/user-attachments/assets/8cdb0ab1-3a8f-4fda-a145-2f99c34ff966)

9. Run server `py manage.py runserver`
   <br/> ![image](https://github.com/user-attachments/assets/29ce2a46-a06a-4979-9fd4-ffed65089e2a)

10. Open this link in the browser: `http://127.0.0.1:8000/`
   <br/> ![image](https://github.com/user-attachments/assets/6c32b5f1-6cff-4e53-8c72-242fbff855c0)

11. Done
