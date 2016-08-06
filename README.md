# registration
A flask app for HackNC registration using MyMLH for auth.

# Development
```
git clone https://github.com/HackNC/registration
cd registration
virtualenv -p python3 .
source bin/activate
pip install -e .
```
Note that you'll need to ask someone for a copy of settings.py to drop in the main registration directory.  It contains all our secrets!!
After that, just start the server with `python registration.py [debug]`

The server will run on port 5000.  To run in prod, it's highly recommended that you sit flask behind nginx.