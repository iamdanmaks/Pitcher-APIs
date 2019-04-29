pip install -r requirements.txt
set FLASK_APP=ML-API/app.py
flask db init
flask db migrate
flask db upgrade
set FLASK_APP=Analyser-API/app.py
flask db migrate
flask db upgrade
start cmd /k Analyser-API/python app.py
start cmd /k ML-API/python app.py
start cmd /k Scraper-API/python main.py