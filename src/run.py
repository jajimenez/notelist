"""Script to run Notelist.

Before running this script, the "NOTELIST_SECRET_KEY" and "NOTELIST_DB_URI"
environment variables must be set.
"""

from notelist import app


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
