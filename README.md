# Notelist
Notelist is a note taking REST API that can be used to manage **notebooks**,
**tags** and **notes**. This API is based on the Flask framework.

#### Project information:
- Version: 0.1.0<br>
- Author: Jose A. Jimenez (jajimenezcarm@gmail.com)<br>
- License: MIT License

## How to install

It's recommended to install Notelist in a Python **virtual environment**. To
create a virtual environment and activate it (in Linux or Mac OS), run the
following commands (with Python 3):

```
python -m venv env
source env/bin/activate
```

Then Notelist can be downloaded from **PyPI** and installed with **PIP**:

```
pip install notelist
```

Alternatively, you can build the **Wheel** or the **Source** package from the
source code and install any of the packages. To build and install the **Wheel**
package (preferred):

```
pip install wheel
python setup.py bdist_wheel
pip install ./dist/notelist*.whl
```

To build and install the **Source** package:

```
python setup.py sdist
pip install ./dist/notelist*.whl
```

## How to run

To run Notelist, we need first to set the following environment variables:

- `FLASK_APP`:<br>
Its value must be always the Notelist package name: `notelist`.

- `NOTELIST_SECRET_KEY`:<br>
Its value must be a **random** sequence of characters
and must be kept **secret**. E.g. `f34jgU#vcfk6&(759fg!AFj`.

- `NOTELIST_DB_URI`:<br>
Its value is the database connection string. E.g.
`sqlite:///path_to_database_file`. For certain database systems, you might need
to install additional Python packages (e.g. **Psycopg** for **PostgreSQL**)

To create the database tables:

```
flask db upgrade -d $(flask path migrations)
```

To create a user:

```
flask user create <username> <password> <admin> <enabled> <full-name> \
<e-mail> 
```

- admin = `0` (default) or `1`
- enabled = `0` (default) or `1` (if value is 0, the user won't be able to log in)
- Example for an administrator user: `flask user create admin somepassword 1 1`

To run Notelist (only in **development** or **test** environments):

```
flask run
```

To run Notelist in a **production** environment, we need to run it through a
**WSGI** server (e.g. Gunicorn). We can install **Gunicorn** from the
`requirements_pro.txt` file:

```
pip install -r requirements_pro.txt
```

And then we can run Notelist through Gunicorn (for instance, with 4 worker
processes, listening to connections from outside our computer on port 5000):

```
gunicorn -w 4 -b 0.0.0.0:5000 notelist:app
```

## How to run with Docker

You can run a Docker container with Notelist with the following command, which
downloads the Docker image from the Docker Hub repository (if the image doesn't
exist yet locally) and runs a container from the image:

```
docker container run --name notelist -d -p 5000:5000 \
-e NOTELIST_SECRET_KEY=<key> -e NOTELIST_DB_URI=<uri> notelist
```

Once the container is running, we can create the database tables with this
command:

```
docker container exec -it notelist upgrade-db
```

To create an administrator user:

```
docker container exec -it notelist create-user <username> <password> \
<admin> <enabled> <name> <email>
```

- admin: `0` (default) or `1`
- enabled: `0` (default) or `1` (if it's 0, the user won't be able to log in)
- To create an administrator user: `docker container exec -it notelist
create-user admin pw_example 1 1`

## How to run with Docker Compose

We can try Notelist using **Docker Compose** to run a Notelist container and a
PostgreSQL container to store the Notelist data. Create a file named
`docker-compose.yml`:

```yaml
version: "3.9"
services:
  notelist-api:
    image: notelist:0.1.0
    container_name: notelist-api
    ports:
      - "5000:5000"
    environment:
      - NOTELIST_SECRET_KEY=aSecretKey
      - NOTELIST_DB_URI=postgresql://notelist:somepw@notelist-db:5432/notelist

  notelist-db:
    image: postgres:13.3
    container_name: notelist-db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=notelist
      - POSTGRES_PASSWORD=somepw
      - POSTGRES_DB=notelist
```

Run the containers:

```
docker compose up -d
```

Create the database tables:

```
docker container exec -it notelist-api upgrade-db
```

Create an administrator user:

```
docker container exec -it notelist-api create-user admin somepassword 1 1
````
