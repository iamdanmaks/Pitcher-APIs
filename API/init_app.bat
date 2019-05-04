pip install -r requirements.txt
set FLASK_APP=ML-API/app.py
flask db init
flask db migrate
flask db upgrade
set FLASK_APP=Analyser-API/app.py
flask db migrate
flask db upgrade
start cmd /k python Analyser-API/app.py
start cmd /k python ML-API/app.py
start cmd /k python Scraper-API/main.py