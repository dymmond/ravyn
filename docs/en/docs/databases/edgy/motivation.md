# Edgy

Everyone uses in one way or another an ORM while working with SQLDatabases.

Django, for example, is widely used by a lot of companies and people out there, the ORM it is simply
amazing and simplistic in the way you can simply focus on what it matters to you and not in the
small details.

SQL Alchemy is another one widely used and loved by the majority of the python community.

[Edgy](https://edgy.dymmond.com) is from the same author of Ravyn so is expected to be
supported (not natively) by the framework by providing some out-of-the-box built-in that can simply
be used

!!! Tip
    Although Ravyn supports out of the box some integrations with Edgy it does not necessarily mean the framework
    is only coupled with it. You are entirely free to use a completely different ORM or even ignore this section and
    implement your own Edgy integration.

## Motivation

* **100% Pydantic**
* Declaring tables
* Querying models
* Declaring relationships
* Managers
* Asynchronous
* Fast
* SQL Alchemy core

## How to use

Using Edgy is as easy installing edgy and an async capable database driver for sqlalchemy.
The rest is handled by edgy and databasez.

If there is no capable driver you can try to use the generic dbapi2 driver of databasez and adapt any dbapi2 driver.
But sometimes there is not even a suitable dbapi2 driver.

Don't worry: you can use JDBC too (with a working java installation):

```shell
$ pip install edgy[jdbc]
# or manually
$ pip install edgy jpype1

```
There are some other database connection shortcuts like:

`edgy[postres]` or `edgy[sqlite]`

## Documentation and more details

Since Ravyn supports Edgy, the best place to understand how to use all the powerful features given by it you can simply
use its [documentation](https://edgy.dymmond.com/) and learn more how to leverage it.
