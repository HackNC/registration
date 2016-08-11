from registration import app, models
import sys

# TODO: use argparse here
debug = "debug" in sys.argv
migrate = "migrate" in sys.argv

# Make the migrations if we need to
if migrate:
    models.make_migrations(app)

app.run(debug=debug, port=8080, host="0.0.0.0")
