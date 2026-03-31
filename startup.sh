#!/bin/bash
cd /home/site/wwwroot

# Activate venv if Oryx created it; otherwise install packages directly
if [ -f "antenv/bin/activate" ]; then
    source antenv/bin/activate
else
    pip install -r requirements.txt --quiet
fi

exec gunicorn --bind=0.0.0.0:8000 --timeout=600 --workers=2 app:app
