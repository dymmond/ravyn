# Using docker

What is docker? Quoting them

> Docker is a set of platform as a service products that use OS-level virtualization to deliver software in packages
called containers.

## The conventional way

When you deploy usually you need to:

* Decide how many environments you will deploy (testing, staging, production...)
* Prepare the requirements.
* Prepare possible environment variables.
* Prepare secrets to be passed onto the application.
* Possibly, prepare the database accesses via those same environment variables.
* Orchestration.
* ...

And in the end, a lot of hope that everything will work flawlessly in every single environment as long as those are
exactly the same.

**This is great but prompt to human mistakes**.

## The docker way

Using docker you still need to think about infrastructure and resources for your application but reduces the
fact that you need to install the same binaries in every single environment since it will be managed by a
**container**.

Imagine a container as a zip file. You simply put together all that is needed for your Ravyn to work in one place
and "zip it" which in this case, you will "dockerize it". Which means in every single environment the binaries will
be **exactly the same** and not reliant on humans reducing the complexity.

## Ravyn and docker example

Let's assume we want to deploy a simple **Ravyn** application using docker. Assuming that external resources
are already handled and managed by you.

Let's use:

* [Nginx configuration](#nginx) - Web server.
* Supervisor - Process manager.
* Ravyn dockerized application.

**Assumptions**:

* All of configrations will be places in a folder called `/deployment`.
* The application will have a simple folder structure

    ```txt
    .
    ├── app
    │   ├── __init__.py
    │   └── main.py
    ├── Dockerfile
    ├── deployment/
    │   ├── nginx.conf
    │   └── supervisor.conf
    └── requirements.txt
    ```

* The requirements file

    ```txt
    ravyn
    uvicorn
    nginx
    supervisor
    ```

**As mentioned in these docs, we will be using uvicorn for our examples but you are free to use whatever you want**.

### The application

Let's start with a simple, single file application just to send an hello world.

```python title='app/main.py'
{!> ../../../docs_src/deployment/app.py !}
```

### Nginx

Nginx is a web server that can also be used as a reverse proxy, load balancer, mail proxy and HTTP cache.

You find more details about Nginx but exploring [their documentation](https://www.nginx.com/) and how to use it.

Let's start by building our simple nginx application.

```nginx
{!> ../../../docs_src/deployment/nginx.conf !}
```

We have created a simple `nginx` configuration with some level of security to make sure we protect the application
on every level.

### Supervisor

Supervisor is a simple, yet powerful, process manager that allows to monitor and control a number of processes
on a UNIX-like operating systems.

[Their documentation](http://supervisord.org/) will help you to understand better how to use it.

Now it is time to create a supervisor configuration.

```ini
{!> ../../../docs_src/deployment/supervisor.conf !}
```

It looks complex and big but let's translate what this configuration is actually doing.

1. Creates the initial configurations for the `supervisor` and `supervisord`.
2. Declares instructions how to start the [nginx](#nginx).
3. Declares the instructions how to start the `uvicorn` and the ravyn application.

### Dockefile

The Dockerfile is where you place all the instructions needed to start your application once it is deployed,
for example, start the [supervisor](#supervisor) which will then start all the processes declared inside.

```{ .dockerfile .annotate }
# (1)
FROM python:3.9

# (2)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libatlas-base-dev gfortran nginx supervisor nginx-extras

# (3)
WORKDIR /src

# (4)
COPY ./requirements.txt /src/requirements.txt

# (5)
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

# (6)
COPY ./app /src/app

COPY deployment/nginx.conf /etc/nginx/
COPY deployment/nginx.conf /etc/nginx/sites-enabled/default
COPY deployment/supervisord.conf /etc/

# (7)
CMD ["/usr/bin/supervisord"]
```

1. Start from an official python base image.
2. Install the minimum requirements to run the nginx and the supervisor.
3. Set the current working directory to `/src`.

    This is where you will be putting the `requirements.txt` and the `app` directory.

4. Copy the requirements for your project.

    You should only copy the requirements and not the rest of the code and the reason for it is the **cache**
    from docker. If the file doesn't change too often, then it will cache and the next time you need to rebuild
    the image, it won't repeat the same steps all the time.

5. Install the requirements.

    The `--no-cache-dir` is optional. You can simply add it to tell pip not to cache the packages locally.

    The `--upgrade` is to make sure that pip upgrades the current installed packages to the latest.

6. Copy the `./app` to the `/src` directory.

    Also copies the necessary created `nginx.conf` and `supervisor.conf` previously created to the corresponding
    system folders.

7. Tells `supervisor` to start running. The system will be using the `supervisor.conf` file created and it will
trigger the instructions declared like starting the nginx and uvicorn.

## Build the docker image

With the [Dockerfile](#dockefile) created it is now time to build the image.

```shell
$ docker build -t myapp-image .
```

### Test the image locally

You can test your image locally before deploying and see if it works as you want.

```shell
$ docker run -d --name mycontainer -p 80:80 myapp-image
```

### Verify it

After [building the image](#build-the-docker-image) and [start it locally](#test-the-image-locally) you can then
check if it works as you need it to work.

**Example**:

* [http://127.0.0.1/](http://127.0.0.1/)
* [http://127.0.0.1/users/5?q=somequery](http://127.0.0.1/users/5?q=somequery)

## Important

It was given an example of how to build some files similar to the ones needed for a given deployment.

**You should always check and change any of the examples to fit your needs and make sure it works for you**

## OpenAPI docs

Ravyn provides the [OpenAPI](../configurations/openapi/config.md) documentation ready to be used and always active
and you can acess via:

* [http://127.0.0.1/swagger](http://127.0.0.1/docs/swagger)
* [http://127.0.0.1/redoc](http://127.0.0.1/docs/redoc)
* [http://127.0.0.1/elements](http://127.0.0.1/docs/elements)
* [http://127.0.0.1/rapidoc](http://127.0.0.1/docs/rapidoc)

### Documentation in production

By design, the docs will be always available but majority of the applications will not have the documentation
available in production for many reasons.

To disable the documentation for being generated you can simply use the internal flag `enable_openapi`.

```python hl_lines="21"
{!> ../../../docs_src/deployment/flag.py !}
```

Or do it via your [custom settings](../application/settings.md#custom-settings)

```python
{!> ../../../docs_src/deployment/settings.py !}
```
