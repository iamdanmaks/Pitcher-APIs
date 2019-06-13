from app import app
import os

app.run(host='0.0.0.0', debug=True, port=os.environ.get('PORT', 5000))
