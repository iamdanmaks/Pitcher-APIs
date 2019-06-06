pip3 install -r requirements.txt
export FLASK_APP=ML-API/app.py
flask db init
flask db migrate
flask db upgrade
export FLASK_APP=Analyser-API/app.py
flask db migrate
flask db upgrade 
python3 Analyser-API/app.py &
python3 ML-API/app.py &
python3 Scraper-API/main.py