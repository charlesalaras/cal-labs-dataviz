# `src` Directory Overview
## assets
Contains external scripts, images, and CSS stylesheets necessary for the application.
- `mathjax.js`: Simple script that runs every second. It detects if there is any LaTeX equations (denoted with `\(\)`) delimiters, and updates accordingly. It also logs in the console its status (when loaded)
- `styles.css`: CSS stylesheet for the whole application. Most of it is derivative from [this styleguide](https://codepen.io/chriddyp/pen/bWLwgP).
- `/*/*.PNG`: Contains all figures related to a module's questions. The subfolder is a name of a module.
## dash
Contains all files related to data analysis, database access, rendering layout, etc. In essence, the heart of the app.
## `__init__.py`
Contains `init_app()` which initializes the Dash/Flask application. It works by first creating `app` as a Flask application. Then, using `app_context()` we import routes from `routes.py` to create application routing for URLs and pages. Then, we implement Dash within by importing the `init_dashboard(app)` function, using our Flask application as the target for Dash. Finally, we register the database by calling `db.init_app()`. This ensures that database calls are only made by the application. There is also an `init_db_command` that is not necessary unless performing first time setup.
## `db.py`
Contains functions for making database requests to `flaskr.db`. A `.env` file is required to set the `DATABASE` variable. To make a database request, the application must first call `get_db()`. It uses SQLite3 to connect to the database, and sets it up to execute requests. After the request is made, call `close_db()` to ensure that no other edits are made to the database.
## `routes.py`
Contains the URL routes for the Flask application. We import `render_templates` to use [HTML layouts](https://flask.palletsprojects.com/en/2.0.x/tutorial/templates/) on the website.
- `home()`: Returns the landing page
- `login()`: Contains unused authentication codes. Ideally, where the teacher or instructor logs in. Must redirect to the authentication application.
## `schema.sql`
Unused, but is used to initialize the database. It also has an incorrect layout.