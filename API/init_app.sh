pip3 install -r requirements.txt
cd ML-API
export FLASK_APP=app.py
flask db init
flask db migrate
flask db upgrade
cd ../Analyser-API
flask db init
cd ../ML-API
cp -r migrations ../Analyser-API/
flask db migrate
flask db upgrade 
python3 app.py &
cd ../ML-API
python3 app.py &
cd ../Scraper-API
python3 main.py &
