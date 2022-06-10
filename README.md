# SABRENA'S KOFFIE CODING CHALLENGE

## Overview
This is Sabrena Beck's submission for the Koffie Backend Coding Challenge. Please follow the instructions
bellow in order to properly set up the environment and run the webapp. 
Thank you so much for your time and consideration!

## Set up virtual environment
In order to avoid package failures, please open this project in a virtual environment with the IDE of your choice. For example purposes
I will assume that you have Intellij. The following instructions to create a virtual environment are assuming you have IntelliJ. 
If you have a different IDE and need help setting one up, please contact me.

* Open Intellij. File > New > Project From Version Control 
* Enter the following under url: https://github.com/sb5829/koffielabs.git
* Open in New Window
* File > Project Structure >SDKs
* Add Python SDK > Pipenv Environment (choose your python executable)
* File > Project Structure > Project > Select new Pipenv as SDK
* File > Project Structure > Module > Fastapi 
* Mark KoffieProject as root source
* From Terminal and at project root KoffieProject, run pipenv shell (if you do not have pipenv, please run pip install pipenv)

## Install dependencies 

Install the dependencies by running the following command under KoffieProject directory:
pipenv install -v --dev --ignore-pipfile

The flag --ignore-pipfile forces to use the Pipfile.lock and all pinned version from there

## Create Fastapi running configuration 
* At the top right next to the green triangle, please click on Add Configuration
* Please select FastApi
* Application file should be: <your_root_path_where_project_is_located>/KoffieProject/main.py
* On the uvicorn command paste: --reload
* For python interpreter, please select the project's SDK 

## Run the application
Universe willing, now you should be able to press that play green triangle and the application will run on http://127.0.0.1:8000!

There are two ways you can utilize the APIs created:

* Directly search into your browser the desired route, i.e. http://127.0.0.1:8000/export/
* Go to the FastApi docs UI http://127.0.0.1:8000/docs#/ and interact with the APIs there
* Enter the request data as defined in the FastApi docs
* IMPORTANT: if it's your first time running, please call the api "create_table" to create the database
* Note: please ignore all the extra files that github generated

## Questions/Concerns

Please let me know if there are any questions/concerns by reaching out to me at sb5829@nyu.edu
Again, thank you for taking the time to look at my challenge, and I look forward to hearing back!
