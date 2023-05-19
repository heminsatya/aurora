# Aurora Framework (v0.9.1 beta)

Aurora is an MVC web framework for creating CRUD applications quickly and simply.

It is based on REST architecture. In another word it is a RESTFUL web framework.

Aurora is written in [Python](https://www.python.org/), and partially used [Flask](https://flask.palletsprojects.com/).


# Installation

You can install Aurora by running:

```
$ pip install aurora-mvc
```


# Usage

## Get Started

To get started with Aurora simply do the following steps:

1. Create the root app (project) directory:

```
$ mkdir my_app
```

> Here *my_app* is a variable name. Change it to anything of your choice at any time you want.

2. Create a python virtual environment in the same path the project directory exists:

**Linux / Mac:**

```
$ python3 -m venv venv
```

**Windows:**

```
$ py -m venv venv
```

3. Activate the virtual environment:

**Linux / Mac:**

```
$ source venv/bin/activate
```

**Windows:**

```
$ venv\scripts\activate
```

4. Navigate to the project directory:

```
(venv) cd my_app
```

> Notice that the project directory must be empty, otherwise you will get an error on the next step.

5. Initialize the root app with Aurora via python shell:

**Linux / Mac:**

```
(venv) python3
>>> from aurora import init
>>> init.start()
```

**Windows:**

```
(venv) py
>>> from aurora import init
>>> init.start()
```

> Congratulations! You successfully initialized the root app. Now you are ready to get started with Aurora.

6. To start the root app run the following command:

**Linux / Mac:**

```
(venv) python3 -m app
```

**Windows:**

```
(venv) py -m app
```


## Next Steps

Documentation: [Aurora Docs](https://github.com/heminsatya/aurora/tree/main/docs)

Changelog: [Aurora Changes](https://github.com/heminsatya/aurora/tree/main/changes)

Issues: [Aurora Bug Tracker](https://github.com/heminsatya/aurora/issues)

Source: [Aurora GitHub Repo](https://github.com/heminsatya/aurora)

PyPI: [Aurora PyPI Page](https://pypi.org/project/aurora-mvc/)


# Dependencies

## Packages:
 
- [Flask](https://pypi.org/project/Flask/)
- [WTForms](https://pypi.org/project/WTForms/) -- For WTForms & CSRF tokens.

## Database APIs:
- [sqlite3](https://docs.python.org/3/library/sqlite3.html) -- If you are using SQLite Database. *Included in the standard python library*
- [mysql.connector](https://pypi.org/project/mysql-connector-python/) -- If you are using MySQL Database.
- [psycopg2](https://pypi.org/project/psycopg2/) -- If you are using Postgres Database.


# About The Author

Hello Everyone!

I'm Hemin Satya, a freelance programmer.
Aurora framework is currently in beta version, and I'm trying my best to make it something magnificent. I hope you like it.

If you saw any bugs or mistakes, please let me know. I'll do my best to solve them asap.

Please let me know your precious comments, observations, and suggestions.
([GitHub](https://github.com/heminsatya))
([Twitter](https://twitter.com/heminsatya))

Thank you all.
