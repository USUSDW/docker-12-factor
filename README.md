# Docker and 12-Factor Basics

We're starting off today with a little Flask app that stores and can accept
comments, and interacts with a PostgreSQL database.

*Interested in just a topics overview with sources? Take a look at 
[the topics listing](./TOPCS.md).

## The original app

Let's take a look through the original app. This can be run with `flask run` if
you have a PostgreSQL server running on your local machine with a matching 
configuration to below, and `flask` and `psycopg2` installed in your python
path. (We'll make this run more places later)

### `app.py`
`app.py` contains the Flask code for the project and sets up a couple simple
routes, namely `GET localhost:5000/comments` and `POST localhost:5000/comments`.

```python
from flask import Flask, request

from db import CommentDatabase
from comment import Comment

app = Flask(__name__)
app.config["DEBUG"] = True

db_url = 'postgresql://comments:comment_pw@localhost/comments'

connection = CommentDatabase(db_url)

@app.route('/comments', methods=['GET'])
def getComments():
    return { 
        'comments': [comment.toDict() for comment in connection.getAllComments()]
    }

@app.route('/comments', methods=['POST'])
def addComment():
    data = request.json
    print(data)
    if not 'name' in data:
        return { 'error': 'Name is required.' }, 400
    if not 'comment' in data:
        return { 'error': 'Comment is required.' }, 400
    connection.createComment(Comment(-1, data['name'], data['comment']))
    return '', 201

if __name__ == "__main__":
    app.run()
```

### `comment.py`
`comment.py` contains a class that helps us convert comment data to and from
the database and API layers.

```python
class Comment:
    def __init__(self, id, name, comment):
        self.id = id
        self.name = name
        self.comment = comment

    def toDict(self):
        return { 'id': self.id, 'name': self.name, 'comment': self.comment }
```

### `db.py`
`db.py` creates a simple CommentDatabase class that does the SQL queries for
us.

```python
import psycopg2
from comment import Comment

class CommentDatabase():
    def __init__(self, db_url):
        print("Starting database connection...")
        self.connection = psycopg2.connect(db_url)
        print("Connected.")
        cursor = self.connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS comments (id SERIAL, name TEXT, comment TEXT);')

    def __mapComments(self, comments):
        return list(map(lambda x: Comment(*x), comments))

    def createComment(self, comment):
        if not isinstance(comment, Comment):
            return
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO comments (name, comment) VALUES (%(name)s, %(comment)s);',
            comment.toDict())

    def __lookupComments(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM comments;')
        return cursor.fetchall()

    def getAllComments(self):
        return self.__mapComments(self.__lookupComments())
```

## Takeaways

There are a couple things going through here that I don't like.

### Hardcoded Database URL

Part of the configuration for this app is right in the source files that are 
run, and there's no good way to change those without going in and editing the
individual files.

Take the `db_url` for example:
```python
db_url = 'postgresql://comments:comment_pw@localhost/comments'

connection = CommentDatabase(db_url)
```

This is bad for two reasons. One, we've exposed our *super-secure* password to
anyone that has access to version control. Two, any machine where the database
is not running on `localhost`, or the username is not `comments`, or the 
is on a different port means that we have to change this.

### No Configurable Port

When I run this app, flask lets me configure the port which is good for that
perspective, but it's not choosing that from a normally-editable source like 
the environment variables or a configuration file. If I'm uploading these files
somewhere to run, I have no choice over the port, and sometimes I only have one
port option I'm given.

### No Dependencies List

There are two dependencies used in this project that aren't built into python.
Can you spot them? They're `Flask` and `psycopg2` from my perspective, but 
there's not much that separates them from any other import.

If I were to run this on another machine, I would need to know to install both
of them which works in a team of one person, but does not in larger situations,
especially in open-source software where anyone should be able to run this.

### Production will be very different

Any difference in production means a code change, and my local development 
environment might (read: will) be running a different version of postgres, or
python, or any other minute software difference that can cause issues.

## Running on another machine

To remedy some of these issues, let's first try making this run on another
machine than mine. I'm going to use [Docker](https://www.docker.com/) for
this because it allows me to use diverse types of machines as well as doesn't
force me to use another computer.

### Creating the Dockerfile

Docker runs based on `Dockerfile`s. These are layered configuration files that
tell docker how to build the machine that we want our app to run on, one action
at a time.

It's like creating another mini computer running all on its own inside of your
computer. It has its own networking, firewall, operating system, everything.

Running virtual machines are called **containers**, while the base pieces they
come from are called **images**. The machine running the containers is called
the **host machine**.

`Dockerfile`
```dockerfile
FROM python:3.8-slim-buster

WORKDIR /code

COPY . /code/

CMD ["flask", "run", "--no-reload"]
```

We have four steps here:
1. `FROM python:3.8-slim-buster` - this picks our base image, which tells us
which operating system we're running on as well as decides how we'll need to
install libraries if we need to do so.
2. `WORKDIR /code` - this sets the working directory in the virtual machine,
which determines where commands will be run.
3. `COPY . /code/` - Copies all of the files from this directory into the 
virtual machine, and
4. `CMD ["flask", "run"]` - Sets the command that will be run when we run the
virtual machine.

We'll build this with `docker build . -t project`. This will then let us run
the image with `docker run project`. Everything should work just fine, right?

```
docker build . -t project 

Step 1/4 : FROM python:3.8-slim-buster
 ---> 5bacf0a78697
Step 2/4 : WORKDIR /code
 ---> Using cache
 ---> 5f10e4760493
Step 3/4 : COPY . /code/
 ---> b7c37f6f4ff2
Step 4/4 : CMD ["flask", "run"]
 ---> Running in 73b21bfc1f5d
Removing intermediate container 73b21bfc1f5d
 ---> 4b4a3989651b
Successfully built 4b4a3989651b
Successfully tagged project:latest

docker run project

Error response from daemon: OCI runtime create failed: container_linux.go:349: starting container process caused "exec: \"flask\": executable file not found in $PATH": unknown.
```

So it looks like the virtual machine has no idea how to run this because 
`flask` doesn't come with python. We could fix that by telling Docker to 
install flask with `pip` during the build process, but what if we wanted to run
this on another computer outside of Docker?

Enter Pipenv.

## Managing Dependencies with Pipenv

[Pipenv](https://pypi.org/project/pipenv/) is a ~~package manager~~ python
workflow built on top of python's default `pip` that allows us to create
repeatable builds by locking both the package versions that we have installed
in a project, but also helps us make builds that work the same because it
manages their dependencies, too. It also manages python versions so that we
get warned if we try to run a project on an unsupported version.

Let's install it. We already have python, so we should already also have `pip`
installed.

```
pip install pipenv
```

### Tracking our Dependencies

Now we can start pipenv tracking our dependencies by running `pipenv install`.
This creates a `Pipfile` that keeps track of our python version. It also 
creates a `Pipfile.lock` that duplicates some of that information in a more
verbose format, acting like a cache of not just dependencies that we need, but 
dependencies that those need. 

Now let's add the dependencies that we identified earlier:

```
pipenv install flack psycopg2-binary
```

Our `Pipfile` now looks like this:
```ini
[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[dev-packages]

[packages]
psycopg2-binary = "*"
flask = "*"

[requires]
python_version = "3.8"
```

If we want to run this on our host machine, we can run `pipenv shell` then run
`flask run` just as we would before. We should see no difference. We want to 
replicate this installing of dependencies in Docker, too.

### Updating our Dockerfile

Here's our new Dockerfile:

```Dockerfile
FROM python:3.8-slim-buster

WORKDIR /code

RUN pip install pipenv

COPY Pipfile Pipfile.lock /code/

RUN pipenv install --system

COPY . /code/

CMD ["flask", "run", "--no-reload"]
```

There are some familiar lines in there. We're still based on the python image
we chose above, and we still move into `/code`.

Next we have some new things:
1. `RUN pip install pipenv` - This should look familiar; we ran a similar
command when we added Pipenv to our host machine.
2. `COPY Pipfile Pipfile.lock /code/` - This moves our pipfiles to the code
folder inside of the docker image. We do this separately because Docker can
cache things in the order they're run, so we only want to run the next step
if this step changes.
3. `RUN pipenv install --system` - This installs the packages from the
Pipfile to the system of the virtual machine. We can install to the system
here because it's a brand new python installation, and the only thing it's
being used for is to run our app.

And then we run our app as we did before. We're ready to run it now, right?

```
docker build . -t project

Step 1/7 : FROM python:3.8-slim-buster
 ---> 5bacf0a78697
Step 2/7 : WORKDIR /code
 ---> Using cache
 ---> 5f10e4760493
Step 3/7 : RUN pip install pipenv
 ---> Using cache
 ---> 12d830931bf0
Step 4/7 : COPY Pipfile Pipfile.lock /code/
 ---> 55f34bba751f
Step 5/7 : RUN pipenv install --system
 ---> Running in 8978490dffbd
Installing dependencies from Pipfile.lock (92ed03)...
Removing intermediate container 8978490dffbd
 ---> 0b07c6636207
Step 6/7 : COPY . /code/
 ---> 5cd071a8e99c
Step 7/7 : CMD ["flask", "run", "--no-reload"]
 ---> Running in 3b668224045c
Removing intermediate container 3b668224045c
 ---> f5ef38116c64
Successfully built f5ef38116c64
Successfully tagged project:latest

docker run project

 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
Starting database connection...

psycopg2.OperationalError: could not connect to server: Connection refused
        Is the server running on host "localhost" (127.0.0.1) and accepting
        TCP/IP connections on port 5432?
could not connect to server: Cannot assign requested address
        Is the server running on host "localhost" (::1) and accepting
        TCP/IP connections on port 5432?
```

Looks like it can't connect to the database.

An easy answer here would be to try and connect to the host address from inside
of the container, but we're trying to make this run *anywhere*, even if it
doesn't have a PostgreSQL server running on it.

Enter Docker Compose.

## Connecting to the Database