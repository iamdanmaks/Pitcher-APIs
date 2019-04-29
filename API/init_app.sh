pip install -r requirements.txt
cd ML-API
export FLASK_APP=app.py
sudo flask db init
sudo flask db migrate
sudo flask db upgrade
cd ../Analyser-API
export FLASK_APP=app.py
sudo flask db init
mkdir migrations
cd ../ML-API
cp -a /migrations. ../Analyser-API/migrations
cd ../Analyser-API
sudo flask db migrate
sudo flask db upgrade
terminal -e python app.py
cd ../ML-API
terminal -e python app.py
cd ../Scraper-API
terminal -e python main.py