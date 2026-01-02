# Custom Directives

Having [built-in directives](./directives.md) from Ravyn is great as it gives you a lot of
niceties for your project but having **custom directives** is what really powers up your
application and takes it to another level.

{!> ../../../docs_src/_shared/autodiscovery.md !}

## What is a custom directive?

Before jumping into that, let us go back to the roots of python.

Python was and still is heavily used as a scripting language. The scripts are isolated pieces of
code and logic that can run on every machine that has python installed and execute without too
much trouble or hurdle.

Quite simple, right?

So, what does this have to do with directives? Well, directives follow the same principle but
applied to your own project. What if you could create your own structured scripts inside your
project directly? What if you could build dependent or independent pieces of logic that could be
run using your own Ravyn application resources?

This is what a directive is.

!!! Tip
    If you are familiar with Django management commands, Ravyn directives follow the same
    principle. There is an [excelent article](https://simpleisbetterthancomplex.com/tutorial/2018/08/27/how-to-create-custom-django-management-commands.html)
    about those if you want to get familiar with.

### Examples

Imagine you need to deploy a database that will contain all the information about specific user
accesses and will manage roles of your application.

Now, once that database is deployed with your application, usually would would need somehow to
connect to your production server and manually setup a user or run a specific script or command
to create that same super user. This can be time consuming and prone to errors, right?

You can use a [directive](#directive) to do that same job for you.

Or what if you need to create specific operations to run in the background by some ops that
does not require APIs, for example, update the role of a user? Directives solve that problem as
well.

There is a world of possibilities of what you can do with directives.

## Directive

This is the main object class for **every single custom directive** you want to implement. This
is a special object with some defaults that you can use.

Directives were inspired by the management commands of Django with extra flavours and therefore
the syntax is very similar.

### Parameters

* **--directive** - The directive name (the file where the Directive was created).
Check [list all directives](./directives.md#list-available-directives) for more details in obtaining
the names.

### How to run

The syntax is very simple for a custom directive:

**With the --app parameter**

```shell
$ ravyn --app <LOCATION> run --directive <DIRECTIVE-NAME> <OPTIONS>
```

Example:

```shell
ravyn --app myproject.main:app run --directive mydirective --name ravyn
```

**With the RAVYN_DEFAULT_APP environment variable set**

```shell
$ export RAVYN_DEFAULT_APP=myproject.main:app
$ ravyn run --directive <DIRECTIVE-NAME> <OPTIONS>
```

Example:

```shell
$ export RAVYN_DEFAULT_APP=myproject.main:app
$ ravyn run --directive mydirective --name ravyn
```

The `run --directive` is **always** expecting the name of the file of your directive.

For example, you created a `createsuperuser.py` file with your `Directive` logic. The `--directive`
parameter will be `run --directive createsuperuser`.

Example:

```shell
$ export RAVYN_DEFAULT_APP=myproject.main:app
$ ravyn run --directive createsuperuser --email example@ravyn.dev
```

### How to create a directive

To create a directive you **must inherit from the BaseDiretive** class and **must call `Directive`**
to your object.

```python
from ravyn.core.directives import BaseDirective
```

**Create the Directive class**

```python hl_lines="4 7"
{!> ../../../docs_src/directives/base.py !}
```

Every single custom directive created **should be called Directive** and **must inherit** from the
`BaseDiretive` class.

Internally `ravyn` looks for a `Directive` object and verifies if is a subclass of `BaseDirective`.
If one of this conditions fails, it will raise a `DirectiveError`.

### Where should directives be placed at?

All the custom directives created **must be** inside a `directives/operations` package in order to
be discovered.

The place for the `directives/operations` can be anywhere in your application and
you can have **more than one** as well.

Example:

```shell hl_lines="10 16 22 36"
.
├── Taskfile.yaml
└── myproject
    ├── __init__.py
    ├── apps
    │   ├── accounts
    │   │   ├── directives
    │   │   │   ├── __init__.py
    │   │   │   └── operations
    │   │   │       ├── createsuperuser.py
    │   │   │       └── __init__.py
    │   ├── payroll
    │   │   ├── directives
    │   │   │   ├── __init__.py
    │   │   │   └── operations
    │   │   │       ├── run_payroll.py
    │   │   │       └── __init__.py
    │   ├── products
    │   │   ├── directives
    │   │   │   ├── __init__.py
    │   │   │   └── operations
    │   │   │       ├── createproduct.py
    │   │   │       └── __init__.py
    ├── configs
    │   ├── __init__.py
    │   ├── development
    │   │   ├── __init__.py
    │   │   └── settings.py
    │   ├── settings.py
    │   └── testing
    │       ├── __init__.py
    │       └── settings.py
    ├── directives
    │   ├── __init__.py
    │   └── operations
    │       ├── db_shell.py
    │       └── __init__.py
    ├── main.py
    ├── serve.py
    ├── tests
    │   ├── __init__.py
    │   └── test_app.py
    └── urls.py
```

As you can see from the previous example, we have four directives:

* **createsuperuser** - Inside `accounts/directives/operations`.
* **run_payroll** - Inside `payroll/directives/operations`.
* **createproduct** - Inside `products/directives/operations`.
* **db_shell** - Inside `./directives/operations`.

All of them, no matter where you put the directive, are inside a **directives/operations** where
ravyn always looks at.

### Directive functions

#### handle()

The `Diretive` logic is implemented inside a `handle` function that can be either `sync` or
`async`.

When calling a `Directive`, `ravyn` will execute the `handle()` and run the all the logic.

=== "Sync"

    ```python hl_lines="15"
    {!> ../../../docs_src/directives/sync_handler.py !}
    ```

=== "Async"

    ```python hl_lines="15"
    {!> ../../../docs_src/directives/async_handler.py !}
    ```

As you can see, Ravyn Directives also allow `async` and `sync` type of functions. This can be
particularly useful for when you need to run specific tasks in async mode, for example.

#### add_arguments()

This is the place where you add any argument needed to run your custom directive. The arguments
are `argparse` related arguments so the syntax should be familiar.

```python
{!> ../../../docs_src/directives/arguments.py !}
```

As you can see, the Directive has five parameters and all of them required.

```shell
ravyn --app teste.main:app run --directive mydirective --first-name Ravyn --last-name Framework --email example@ravyn.dev --username ravyn --password ravyn

```

## Help

There are two helps in place for the directives. The one you run the ravyn executor (run) and the
one for the `directive`.

### --help

This command **is only used for the executor help**, for example:

```shell
$ ravyn run --help
```

### -h

This flag is used to access the `directive` help and not the `run`.

```shell
$ ravyn run --directive mydirective -h
```

### Notes

The **only way to see the help of a directive** is via `-h`.

If `--help` is used, it will only show the help of the `run` and not the `directive` itself.

## Order of priority

**This is very important to understand**.

What happens if we have two custom directives with the same
name?

Let us use the following structure as example:

```shell hl_lines="10 32"
.
├── Taskfile.yaml
└── myproject
    ├── __init__.py
    ├── apps
    │   ├── accounts
    │   │   ├── directives
    │   │   │   ├── __init__.py
    │   │   │   └── operations
    │   │   │       ├── createsuperuser.py
    │   │   │       └── __init__.py
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── tests.py
    │   │   └── v1
    │   │       ├── __init__.py
    │   │       ├── schemas.py
    │   │       ├── urls.py
    │   │       └── controllers.py
    ├── configs
    │   ├── __init__.py
    │   ├── development
    │   │   ├── __init__.py
    │   │   └── settings.py
    │   ├── settings.py
    │   └── testing
    │       ├── __init__.py
    │       └── settings.py
    ├── directives
    │   ├── __init__.py
    │   └── operations
    │       ├── createsuperuser.py
    │       └── __init__.py
    ├── main.py
    ├── serve.py
    ├── tests
    │   ├── __init__.py
    │   └── test_app.py
    └── urls.py
```

This example is simulating a structure of an ravyn project with
**two custom directives with the same name**.

The first directive is inside `./directives/operations/` and the second inside
`./apps/accounts/directives/operations`.

Ravyn directives work on a **First Found First Executed** principle and that means if you have
two custom directives with the same name, ravyn will
**execute the first found directive with that given name**.

In other words, if you want to execute the `createsuperuser` from the `accounts`, the first found
directive inside `./directives/operations/` **shall have a different name** or else it will execute
it instead of the intended from `accounts`.

## Execution

Ravyn directives use the same events as the one passed in the application.

For example, if you want to execute database operations and the database connections should be
established before hand, you can do in two ways:

* Use [Lifespan](../lifespan-events.md) events and the directives will use them.
* Establish the connections (open and close) inside the Directive directly.

The [pratical example](#a-practical-example) uses the [lifespan events](../lifespan-events.md) to
execute the operations. This way you only need one place to manage the needed application events.

## A practical example

Let us run an example of a custom directive for your application. Since we keep mentioning the
`createsuperuser` often, let us then create that same directive and apply to our Ravyn application.

For this example we will be using [Edgy][edgy] since it is from the same author and will
allow us to do a complete end-to-end directive using the async approach.

This example is very simple in its own design.

For production you should have your models inside a models dedicated place and your `registry`
and `database` settings somewhere in your `settings` where you can access it anywhere in your code via
[ravyn settings](../application/settings.md), for example.

P.S.: For the registry and database strategy with [edgy][edgy], it is good to have a read
the [tips and tricks](https://edgy.dymmond.com/tips-and-tricks/) with edgy.

The design is up to you.

What we will be creating:

* **myproject/main/main.py** - The entry-point for our Ravyn application
* **createsuperuser** - Our directive.

In the end we simply run the directive.

We will be also using the [edgy support from Ravyn models](../databases/edgy/models.md)
as this will make the example simpler.

### The application entrypoint

```python title="myproject/main.py"
{!> ../../../docs_src/directives/example/app.py !}
```

The connection string should be replaced with whatever is your detail.

### The createsuperuser

Now it is time to create the directive `createsuperuser`. As mentioned [above](#where-should-directives-be-placed-at),
the directive shall be inside a `directives/operations` package.

```python title="myproject/directives/operations/createsuperuser.py"
{!> ../../../docs_src/directives/example/createsuperuser.py !}
```

And this should be it. We now have a `createsuperuser` and an application and now we can run
in the command line:

**Using the auto discover**

```shell
$ ravyn run --directive createsuperuser --first-name Ravyn --last-name Framework --email example@ravyn.dev --username ravyn --password ravyn
```

**Using the --app or RAVYN_DEFAULT_APP**

```shell
$ ravyn --app myproject.main:app run --directive createsuperuser --first-name Ravyn --last-name Framework --email example@ravyn.dev --username ravyn --password ravyn
```

Or

```shell
$ export RAVYN_DEFAULT_APP=myproject.main:app
$ ravyn run --directive createsuperuser --first-name Ravyn --last-name Framework --email example@ravyn.dev --username ravyn --password ravyn
```

After the command is executed, you should be able to see the superuser created in your database.

[edgy]: https://edgy.dymmond.com
