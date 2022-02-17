################
# Dependencies #
################
import importlib
from .helpers import snake_case
config = importlib.import_module('config')


###################
# Database Engine #
###################
debug = getattr(config, "DEBUG")
db_engine = getattr(config, 'DB_ENGINE') 
db_engines = ['AuroraSQL']

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
db_system = getattr(config, 'DB_SYSTEM')
db_systems = ['SQLite', 'Postgres', 'MySQL']

# Check Database System
if db_system in db_systems:
    # Import the database class
    # SQLite Database
    if db_system == 'SQLite':
        try:
            import sqlite3 as DatabaseAPI
            from sqlite3 import Error as DatabaseError

        except:
            pass
    
    # MySQL Database
    elif db_system == 'MySQL':
        try:
            from mysql import connector as DatabaseAPI
            from mysql.connector import Error as DatabaseError

        except:
            pass
    
    # Postgres Database
    elif db_system == 'Postgres':
        try:
            import psycopg2 as DatabaseAPI
            import psycopg2.extras as DatabaseDict
            from psycopg2 import DatabaseError

        except:
            pass

# Raise error
else:
    error = ''' Unsupported Database System!\n'''
    error += f'''Supported Database Systems: {', '.join(db_systems)}'''

    # Check debug mode
    if debug:
        # Raise error
        raise Exception(error)

    else:
        # Print error
        print(error)
        exit()
