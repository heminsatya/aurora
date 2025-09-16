################
# Dependencies #
################
import importlib
config = importlib.import_module('config')


###################
# Database Engine #
###################
debug = getattr(config, "DEBUG")
db_engine = getattr(config, 'DB_ENGINE').lower()
db_engines = ['aurorasql']

# Check Database Engine
if not db_engine in db_engines:
    error = '''Unsupported Database Engine!\n'''
    error += f'''Supported Database Engines: {', '.join(db_engines)}'''

    # Check debug mode
    if debug:
        # Raise error
        raise Exception(error)

    else:
        # Print error
        print(error)
        exit()


################
# Database API #
################
db_system  = getattr(config, 'DB_SYSTEM').lower()
db_systems = ['sqlite', 'sqlite3', 'mysql', 'mariadb', 'postgres', 'postgresql']

# Check Database System then import the database class
# SQLite Database
if db_system in ('sqlite', 'sqlite3'):
    try:
        import sqlite3 as _sqlite
        DatabaseAPI   = _sqlite
        DatabaseError = _sqlite.Error

    except:
        pass

# MySQL Database
elif db_system in ('mysql', 'mariadb'):
    try:
        from mysql import connector as DatabaseAPI
        from mysql.connector import Error as DatabaseError

    except:
        pass

    # Prefer mysql-connector-python
    try:
        import mysql.connector as _mysql
        DatabaseAPI   = _mysql
        DatabaseError = _mysql.Error

    except Exception:
        # Fallback: MySQLdb
        try:
            import MySQLdb as _mysqldb
            DatabaseAPI   = _mysqldb
            DatabaseError = _mysqldb.Error

        # Fallback: PyMySQL
        except Exception:
            import pymysql as _pymysql
            DatabaseAPI   = _pymysql
            DatabaseError = _pymysql.MySQLError

# Postgres Database
elif db_system in ('postgres', 'postgresql'):
    try:
        import psycopg2 as _pg
        DatabaseAPI   = _pg
        DatabaseError = _pg.Error
        DatabaseDict  = _pg.extras

    except:
        pass

# Raise error
else:
    error = '''Unsupported Database System!\n'''
    error += f'''Supported Database Systems: {', '.join(db_systems)}'''

    # Check debug mode
    if debug:
        # Raise error
        raise Exception(error)

    else:
        # Print error
        print(error)
        exit()
