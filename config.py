import os

class Config:
    # VULN 1: SECRET_KEY yang sangat lemah dan hardcoded
    # Seharusnya diambil dari environment variable dan sangat kuat
    SECRET_KEY = 'inisecretkeyyangsangatlemahsekali'
    
    # Konfigurasi Database (SQLite untuk kemudahan demo)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vulnerable_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # VULN 2: JWT_SECRET_KEY yang lemah dan hardcoded
    # Seharusnya diambil dari environment variable dan sangat kuat
    JWT_SECRET_KEY = 'inijwtsecretkeyyanglemah'