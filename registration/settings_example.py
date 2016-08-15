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
    "redirect_uri": "CALLBACK_URL_HERE"
}

SECRET_KEY = "SECRET_KEY_HERE" # Anything you want.  Should be hard to guess.

CALLBACK_URI = "CALLBACK_URL_HERE" # MLH CALLBACK URL

AUTH_URL = "https://my.mlh.io/oauth/authorize?client_id={client_id}&redirect_uri={callback_uri}&response_type=code"

MLH_EDIT_LINK = "https://my.mlh.io/edit"

DEFAULT_REGISTRATION_STATUS = "o" # Open

# Resume Config

UPLOAD_FOLDER = "ROOT_FOLDER_PATH_HERE/resumes"

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'otd'])

# State config

ACCEPTING_NEW = True

DEFAULT_USER_STATUS = 'o'