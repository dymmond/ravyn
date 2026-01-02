# Mongoz

There are different types of databases but let us just say that in general we can classify two types,
the SQL and **NoSQL** databases.

Interacting programatically with SQL databses, usually **ORMs** are used and to interact with
NoSQL, **ODMs** are the way to go. **ODM** extends for **Object Document Mapper**.

Depending on the needs of your project you might opt for using one or the other or even combining
both of them which happens more often than you think.

There are many types of **NoSQL** databases but one that is without a doubt that is widely adopted
and used by thousands of people and organisations, **MongoDB**.

Without going into details, **Mongoz** offers a seemless integration with MongoDB with an extremely
familiar interface to interact with.

[Mongoz](https://mongoz.tarsild.io) is from the same autor of Ravyn so is expected to be
supported (not natively) by the framework by providing some out-of-the-box built-in that can simply
be used

!!! Tip
    Although Ravyn supports out of the box some integrations with Mongoz it does not necessarily mean the framework
    is only coupled with it. You are entirely free to use a completely different ODM or even ignore this section and
    implement your own Mongoz integration.

As mentioned before, **Mongoz** is framework agnostic and Ravyn does not care if you use Mongoz
or anything else. **You are free to choose your own ODM**.

## Motivation

* **100% Pydantic**
* Declaring documents
* Querying documents
* Asynchronous
* Fast
* Built on the top of [Motor](https://motor.readthedocs.io/en/stable/)

## How to use

To use Mongoz with Ravyn you should install some requirements first.

```shell
$ pip install mongoz
```

## Documentation and more details

Since Ravyn supports Mongoz, the best place to understand how to use all the powerful features given by it you can simply
use its [documentation](https://mongoz.tarsild.io/) and learn more how to leverage it.
