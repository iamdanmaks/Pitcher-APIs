from app import app
import os

app.run(
        host='0.0.0.0',
        port=8000,
        debug=True, 
        access_log=True, 
        auto_reload=False
    )
