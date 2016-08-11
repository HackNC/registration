from registration import app, models
import sys

# TODO: use argparse here
debug = "debug" in sys.argv
migrate = "migrate" in sys.argv

# Where should the server listen
host = '0.0.0.0' if debug else '127.0.0.1'
port = 8000 if debug else 9000

# Make the migrations if we need to
if migrate:
    models.make_migrations(app)

app.run(debug=debug, port=port, host=host)
