# Shell Support

This is a simple support for an interactive shell with Ravyn. This directive simply loads some
of the defaults such as `Gateway`, `Router`, `Include`, `OpenAPIResponse`, `settings` and some others by
default (like Pydantic `BaseModel`, `FieldInfo`...) saving you time every time you need to use an
interactive shell to test some ad-hoc processes.

Ravyn gives you that possibility completely out of the box and ready to use with your
application.

## Important

Before reading this section, you should get familiar with the ways Ravyn handles the discovery
of the applications.

The following examples and explanations will be using the [auto discovery](./discovery.md#auto-discovery)
but [--app and environment variables](./discovery.md#environment-variables) approach but the
is equally valid and works in the same way.

## How does it work

Ravyn ecosystem is complex internally but simpler to the user. Ravyn will use the application
discovery to understand some of your defaults and events and start the shell.

### Requirements

To run any of the available shells you will need `ipython` or `ptpython` or both installed.

**IPython**

```shell
$ pip install ipython
```

or

```shell
$ pip install ravyn[ipython]
```

**PTPython**

```shell
$ pip install ptpython
```

or

```shell
$ pip install ravyn[ptpyton]
```

### How to call it

#### With [auto discovery](./discovery.md#auto-discovery)

**Default shell**

```shell
$ ravyn shell
```

**PTPython shell**

```shell
$ ravyn shell --kernel ptpython
```

#### With [--app and environment variables](./discovery.md#environment-variables)

**--app**

```shell
$ ravyn --app myproject.main:app shell
```

**Environment variables**

```shell
$ export RAVYN_DEFAULT_APP=--app myproject.main:app
$ ravyn shell --kernel ptpython
```

#### If you want to use your custom RavynSettings

Sometimes you want to use your application settings as well while loading the shell. You can see
[more details](../application/settings.md) about the settings and [how to use them](../application/settings.md).

=== "MacOS & Linux"

    ```shell
    $ export RAVYN_SETTINGS_MODULE=MyCustomSettings
    $ export RAVYN_DEFAULT_APP=--app myproject.main:app
    $ ravyn shell # default
    $ ravyn shell --kernel ptpython # start with ptpython
    ```

=== "Windows"

    ```shell
    $ $env:RAVYN_SETTINGS_MODULE=="MyCustomSettings"
    $ $env:RAVYN_DEFAULT_APP=--app myproject.main:app
    $ ravyn shell # default
    $ ravyn shell --kernel ptpython # start with ptpython
    ```

### How does it look like

Ravyn doesn't want to load all python globals and locals for you. Instead loads all the
essentials and some python packages automatically for you but you can still import others.

It looks like this:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1689763288/esmerald/shell/shell_q0fdyi.png" alt='Shell Example'>

Of course the `RAVYN-VERSION`, `YOUR-APPLICATION-TITLE` and `YOUR-APPLICATION-VERSION`
are replaced automatically by the version you are using.

Pretty cool, right? Then it is a normal python shell where you can import whatever you want and
need as per normal python shell interaction.
