pip install -r requirements.txt
cd ML-API
set FLASK_APP=app.py
flask db init
flask db migrate
flask db upgrade
cd ../Analyser-API
set FLASK_APP=app.py
flask db init
mkdir migrations
cd ../ML-API
xcopy /S /E "%cd%/migrations" "../Analyser-API/migrations"
cd ../Analyser-API
flask db migrate
flask db upgrade
start cmd /k python app.py
cd ../ML-API
start cmd /k python app.py
cd ../Scraper-API
start cmd /k python main.py