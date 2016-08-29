import sys
from registration import app, models

# If you defined any event triggers, import them
import callbacks

if __name__ == '__main__':
    
    # TODO: use argparse here
    debug = "debug" in sys.argv
    migrate = "migrate" in sys.argv

    # Where should the server listen
    host = '0.0.0.0' if debug else '127.0.0.1'
    port = 8002 if debug else 9002

    # Make the migrations if we need to
    if migrate:
        models.make_migrations(app)

    app.run(debug=debug, port=port, host=host)
