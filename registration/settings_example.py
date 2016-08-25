import datetime

DATE_OF_HACKATHON = datetime.date(2016, 10, 29)
DAYS_TO_RSVP = 7  # How many days after an acceptance to allow RSVP to happen
MAX_UPLOAD_SIZE_MB = 10
SECRET_KEY = "SECRET_KEY" # Anything you want.  Should be hard to guess.
UPLOAD_FOLDER = "/path/to/resumes_folder"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'odt'])
DEFAULT_REGISTRATION_STATUS = "o" # Open
NULL_PENDING_STATUS = "x"  # The state to default pending_state to
BATCH_PENDING_STATUS= "p"  # The state to move open applications to while they are processed
ACCEPTING_NEW = True  # Override all application acceptance states without modifying the object model
DEFAULT_VIEW="apply" # Which page to show newly logged in users
ALLOWED_PAGES=['apply', 'dashboard', 'admin', 'admin_update'] # What pages can users route to?

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

SLACK = {
    "callback_url": "CALLBACK_URL"
}