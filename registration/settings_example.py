import datetime

DATE_OF_HACKATHON = datetime.date(2016, 10, 29)
SECRET_KEY = "SECRET_KEY_HERE" # Anything you want.  Should be hard to guess.  UUIDs are good.
UPLOAD_FOLDER = "ROOT_FOLDER_PATH_HERE/resumes"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'otd'])
DEFAULT_REGISTRATION_STATUS = "o" # Open
ACCEPTING_NEW = True

DATABASE = {
    "drivername": "DB_DRIVER",
    "host": "localhost",
    "port": "PORT_HERE",
    "username": "USER_HERE",
    "password": "PASSWORD_HERE",
    "database": "DATABASE_HERE"
}

MYMLH = {
    "app_id": "CLIENT_ID_HERE",
    "secret": "SECRET_KEY_HERE",
    "redirect_uri": "CALLBACK_URL_HERE",
    "auth_url": "https://my.mlh.io/oauth/authorize?client_id={client_id}&redirect_uri={callback_uri}&response_type=code",
    "edit_link": "https://my.mlh.io/edit"
}

# If you intend to use transactional email for anything
SPARKPOST = {
    "secret_key": "SPARKPOST_API_KEY"  
}