# Run your Python startup script
python setup/startup.py

# Then start Uvicorn server
exec uvicorn api:app --host 0.0.0.0 --port 5057 --reload