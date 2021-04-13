# Topics Overview

## Docker

[Docker](https://docs.docker.com/get-started/) is something between a virtual
machine and a program running on your machine. Basically what it does is it
runs tiny virtual machines with your apps running inside of them.

What this accomplishes is that it means it's like its running on another 
computer, without any of the things that are a part of your development 
environment. In other words, you can mimic a production server on a development
machine, which I think is really cool. It also means if it works in the 
container running on your machine, it'll work on other containers running on
other people's machines.

## 12-Factor Applications

12-Factor is a set of principles or "factors" that make good good apps. There's
a lot going on there, but these have helped me create apps that are easy to 
deploy on multiple machines.

You can read more about those [here](https://12factor.net/). Specifically, 
we'll be looking at 2, 3, 7, and 10.

### 2. Dependencies

We're accomplishing this with [Pipenv](https://pypi.org/project/pipenv/) which
is a tool that allows us to keep track of and install our dependencies to a 
file, as well as keep things in a virtual environment on development machines
so that projects don't interfere with each other.

### 3. Config

We're accomplishing this by using environment variables. In dev, we have the 
option to use `.env` files and docker together, while in prod we can set these
directly on the host machine or again use an `.env` file. 

### 7. Port Binding

This is actually required by some web hosting providers nowadays, but we're 
accomplishing this through Docker and some of the configurations in our
Dockerfile.

### 10. Dev/prod Parity

Docker helps us accomplish this as well, since it turns our development machine
into a machine that's running a VM that looks just like the production setup.

## Postman and HTTPie

### Postman

Postman is a free tool (with a paid version) that allows you to organize 
collections of HTTP requests and run them easily. It also comes with scripting
capabilities, so you can write tests that are run on each request done.

You can find more information on Postman [here](https://www.postman.com/).

### HTTPie

For one-off requests, I tend to use HTTPie. It's a `curl` alternative that does
syntax highlighting, has sane defaults and makes working with JSON APIs really 
easy on the command line.

You can find more information on HTTPie [here](https://httpie.io/).