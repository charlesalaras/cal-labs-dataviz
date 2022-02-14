# cal-labs-dataviz
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
  
A Flask based visualization app created for Cal Labs

## Directory Overview
### src
Contains all source files for the application.
### `wsgi.py`
The direct entry point to the application. Simply run `python3 wsgi.py` to start the application on your local network. Calls `init_app()` from `src/__init__.py`. There are placeholder authentication variables that are currently not in use. The app runs in debug mode.
### `.gitignore`
The files ignored are described as follows:
- `.env`: Contains the variable for the absolute path of the database. Used in `db.py:10`
- `sample_lrs.json`: Contains the LRS data from Summer 2021 session. Currently, LRS data must be downloaded daily.
- `src/dash/templates`: Contains the HTML templates for rendering. Currently unused.
- `src/dash/layout.py`: Unused, but could be useful to define a landing page layout.
- `__pycache__`: Cache from Python, disregard.
- `venv`: (Accidentally) Stores a Python Virtual Environment. Ideally, you should create a Python Virtual Environment, install all dependencies, and clone this repository into the virtual environment. See [this link](https://flask.palletsprojects.com/en/2.0.x/installation/#virtual-environments) for more information.
- `*.pyc` - Python Cache files, disregard.
- `example.PNG` - Disregard.
- `origjson.txt` - Disregard, used as a placeholder file for old JSON. 
- `src/assets/*.PNG` - Contains all figures relevant to module questions. Currently, this does not work correctly because every figure is contained in a subfolder.
- `flaskr.db` - Contains the database with modules and related questions. Here is the basic format of the database table `modules`:

| id (INT) | name (STRING) | number (INT) | questions (JSON) | course (STRING) |
|----------|---------------|--------------|------------------|-----------------|
