################
# Dependencies #
################
import os
import sys
import platform
import importlib
import time
from datetime import datetime
from typing import List
from .helpers import *
from .SQL import Database

# Instantiate the Database class
db = Database()

# Aurora path
aurora_path = os.path.dirname(__file__)

# App path (the caller)
app_path = os.getcwd()

# Check platform system
# Windows
if platform.system() == 'Windows':
    sep    = '\\'
    py_cli = 'py -m'

# Unix
else:
    sep = '/'
    py_cli = 'python -m'

# Arguments
args: List[str] = sys.argv

# Available options
options = [
    '--help',
    '--version',
]

# Available commands
commands = [
    'create-app',
    'delete-app',
    'create-controller',
    'delete-controller',
    'create-view',
    'delete-view',
    'create-form',
    'delete-form',
    'create-model',
    'delete-model',
    'check-db',
    'init-db',
    'migrate-db',
    'repair-db',
    'reset-db',
]

# CLI message for invalid inputs
cli_error = f'''----------------------------------------------------------
Usage: {py_cli} manage OPTIONS | COMMANDS

Options:
    --help                  Shows the CLI help message.
    --version               Shows Aurora framework version.

Commands:
    create-app              Creates a new app with some default components if not exist.
    delete-app              Deletes an existing app and all its components.
    create-controller       Creates a controller blueprint if not exists for an existing app.
    delete-controller       Deletes an existing controller for an existing app.
    create-view             Creates a view blueprint if not exists for an existing app.
    delete-view             Deletes an existing view for an existing app.
    create-form             Creates a form blueprint if not exists for an existing app.
    delete-form             Deletes an existing form for an existing app.
    create-model            Creates a model blueprint if not exists.
    delete-model            Deletes an existing model.
    check-db                Checks the models and database for errors and changes.
    init-db                 Initializes the database if not initialized already.
    migrate-db              Migrates the model changes to the database.
    repair-db               Can be used for renaming the existing model columns and repairing corrupted tables.
    reset-db                Can be used for resetting the database, based on the current models.
----------------------------------------------------------'''

# Fetch statics
config = importlib.import_module('config')
development = getattr(config, "DEVELOPMENT")
statics = getattr(config, "STATICS")

# Fetch registered apps
apps_module = importlib.import_module('_apps')
apps = getattr(apps_module, "apps")

# Fetch registered models
models_module = importlib.import_module('models._models')
models = getattr(models_module, "models")

# Database system
db_system = getattr(config, "DB_SYSTEM")

# The database (file)
database = getattr(config, "DB_CONFIG")['database']

# Database safe typing
safe_type = getattr(config, 'SAFE_TYPE')

# Temporary migration file
temp_file = f'{app_path + sep}_migrations{sep}_temp.py'


#############
# CLI Class #
#############
##
# @desc CLI class for manage the root app and its child apps
##
class CLI:
    ##
    # @desc Constructor method
    ##
    def __init__(self):
        # Try to run the CLI application
        try:
            # Check the development
            if not development:
                alert = '''----------------------------------------------------------\n'''
                alert += '''NOTICE!\n'''
                alert += '''Aurora CLI app is only available in development!\n'''
                alert += '''----------------------------------------------------------'''

                # Alert the user
                print(alert)
                time.sleep(0.1)

                # Exit the program
                exit()

            # Check the arguments
            elif not len(args) == 2 or not args[1] in options and not args[1] in commands:
                # Alert the user
                print(cli_error)
                time.sleep(0.1)

                # Exit the program
                exit()

            # Commands are fine
            else:
                # Check options and commands
                if (args[1] == '--help'):
                    # Alert the user
                    print(cli_error)
                    time.sleep(0.1)

                    # Exit the program
                    exit()

                elif (args[1] == '--version'):
                    from . import __version__
                    
                    # Alert the user
                    print(f"""Aurora {__version__} beta""")
                    time.sleep(0.1)

                    # Exit the program
                    exit()

                elif (args[1] == 'create-app'):
                    self.create_app()

                elif (args[1] == 'delete-app'):
                    self.delete_app()

                elif (args[1] == 'create-controller'):
                    self.create_controller()

                elif (args[1] == 'delete-controller'):
                    self.delete_controller()

                elif (args[1] == 'create-view'):
                    self.create_view()

                elif (args[1] == 'delete-view'):
                    self.delete_view()

                elif (args[1] == 'create-model'):
                    self.create_model()

                elif (args[1] == 'delete-model'):
                    self.delete_model()

                elif (args[1] == 'create-form'):
                    self.create_form()

                elif (args[1] == 'delete-form'):
                    self.delete_form()

                elif (args[1] == 'check-db'):
                    self.check_db()

                elif (args[1] == 'init-db'):
                    self.init_db()

                elif (args[1] == 'migrate-db'):
                    self.migrate_db()

                elif (args[1] == 'repair-db'):
                    self.repair_db()

                elif (args[1] == 'reset-db'):
                    self.reset_db()

        # Handle errorr
        except NameError as e:
            raise Exception(e)


    ##
    # @desc Produce migration data
    # 
    # @param models: str -- The model name
    # @param reload: bool -- For reloading the model
    # 
    # @var content: str -- The model migration content
    # @var models_con: str -- The models content
    # @var Model: obj -- The model module
    # @var Class: obj -- The model class
    # @var table: str -- The model table name
    # @var attr: dict -- The model attributes as a dictionary
    # 
    # @return str
    ##
    @staticmethod
    def migration_data(models:str, reload:bool=False):
        # The migration content placeholder
        content = ''

        # The database content
        db_con = f"""DB_SYSTEM = '{db_system}'\n\n"""

        # Update migration content
        content += db_con

        # The models content
        models_con = f"""_models = {models}\n\n"""

        # Update migration content
        content += models_con

        # Loop the models
        for model in models:
            # Find the model and its class
            Model = importlib.import_module(f'models.{model}')

            # Check reload
            if reload:
                Model = importlib.reload(Model)

            Class = getattr(Model, model)

            # The table name
            table = Class().table

            # Atributes dictionary
            attrs = {}

            # Add model columns (class attributes) to attrs
            attrs.update(dict([(x,y) for x,y in Class.__dict__.items() if not x.startswith('__')]))

            # Table default parameters
            col_type = {}
            primary_key = Class().primary_key
            unique = []
            not_null = []
            default = {}
            check = {}
            foreign_key = {}

            # New attrs
            new_attrs = {}

            # Final attrs
            final_attrs = {}

            # Check primary key
            if primary_key == None:
                # Set primary key
                primary_key = 'id'

                # Check the id column
                if not 'id' in attrs:
                    # Add id to new attrs
                    new_attrs['id'] = {'datatype': 'integer', 'unique': False, 'not_null': True, 'default': None, 'check': None, 'foreign_key': None, 'on_update': None, 'on_delete': None}

            # Update new attrs
            new_attrs.update(attrs)

            # Loop the model attributes
            for x in new_attrs:

                # Column + Datatype
                col_type[x] = new_attrs[x]['datatype']

                # UNIQUE
                if new_attrs[x]['unique']:
                    unique.append(x)

                # NOT NULL
                if new_attrs[x]['not_null']:
                    not_null.append(x)

                # DEFAULT
                if not new_attrs[x]['default'] == None:
                    default[x] = new_attrs[x]['default']

                # Check
                if new_attrs[x]['check']:
                    check[x] = new_attrs[x]['check']

                # Foreign key
                if new_attrs[x]['related_to']:
                    # Find the reference model and its class
                    r_model = importlib.import_module(f"models.{new_attrs[x]['related_to']}")
                    r_class = getattr(r_model, new_attrs[x]['related_to'])

                    r_table = r_class().table
                    r_column = r_class().primary_key if r_class().primary_key else 'id'

                    foreign_key[x] = {
                        'r_table': r_table,
                        'r_column': r_column,
                        'on_update': new_attrs[x]['on_update'],
                        'on_delete': new_attrs[x]['on_delete'],
                    }

            # Produce final attrs for migrations
            final_attrs['table'] = table
            final_attrs['col_type'] = col_type
            final_attrs['primary_key'] = primary_key
            final_attrs['unique'] = unique
            final_attrs['not_null'] = not_null
            final_attrs['default'] = default
            final_attrs['check'] = check
            final_attrs['foreign_key'] = foreign_key

            # Produce the model attributes dictionary
            model_attrs = f"""{model} = {final_attrs}\n\n"""

            # Update migration content
            content += model_attrs

        # Chech the temporary migration file
        if file_exist(temp_file):
            # Write to the temporary migration file
            write_file(f'{app_path + sep}_migrations{sep}_temp.py', content)

        else:
            # Create the temporary migration file
            create_file(f'{app_path + sep}_migrations{sep}_temp.py', content)

        # Return the migration content
        return content


    ##
    # @desc Check models & database
    ##
    @staticmethod
    def check_database(pattern:str="init"):

        # Checking database connection
        print('Checking database connection...')
        time.sleep(0.1)

        # Database not exists
        if not db._exist_database(database):
            # "init" pattern
            if pattern == "init":
                # Alert the user
                print('- Database connection not found!')
                time.sleep(0.1)

            # Other patterns
            else:
                alert = '''----------------------------------------------------------\n'''
                alert += '''WARNING!\n'''
                alert += '''Database connection not found!\n'''
                alert += '''To create a connection and initialize the database run the following command:\n'''
                alert += f'''{py_cli} manage init-db\n'''
                alert += '''----------------------------------------------------------'''

                # Alert the user
                print(alert)
                time.sleep(0.1)

                # Exit the program
                exit()

        # Database already exists
        else:
            # "init" pattern
            if pattern == "init":
                alert = '''----------------------------------------------------------\n'''
                alert += '''NOTICE!\n'''
                alert += '''Database connection established successfully!\n'''
                alert += '''Database already initialized!\n'''
                alert += '''To check the database run the following command:\n'''
                alert += f'''{py_cli} manage check-db\n'''
                alert += '''----------------------------------------------------------'''
                    
                # Alert the user
                print(alert)
                time.sleep(0.1)

                # Exit the program
                exit()

            # Other patterns
            else:
                db_corrupted = False

                # Database corrupted
                if not db._exist_table('_migrations'):
                    db_corrupted = True

                    # "reset" pattern
                    if pattern == "reset":
                        # Alert the user
                        print('- Database is corrupted!')
                        time.sleep(0.1)

                    # Remain patterns
                    else:
                        alert = '''----------------------------------------------------------\n'''
                        alert += '''WARNING!\n'''
                        alert += '''Database is corrupted!\n'''
                        alert += '''To reset the database run the following command:\n'''
                        alert += f'''{py_cli} manage reset-db\n'''
                        alert += '''----------------------------------------------------------'''
                        
                        # Alert the user
                        print(alert)
                        time.sleep(0.1)

                        # Exit the program
                        exit()

                # Database is OK
                else:
                    db_changed = False
                    
                    # Fetch migration models data
                    try:
                        m_version = db.read(table="_migrations", cols=['version'], where={"current":True}).first()['version']
                        m_module = importlib.import_module(f'_migrations.{m_version}')
                        m_models = m_module._models
                        m_db_system =  m_module.DB_SYSTEM
                    except:
                        m_db_system = False

                    # Database system has been changed
                    if not db_system == m_db_system:
                        db_changed = True

                        # "reset" pattern
                        if pattern == "reset":
                            # Alert the user
                            print('- Database system has been changed!')
                            time.sleep(0.1)

                        # Remain patterns
                        else:
                            alert = '''----------------------------------------------------------\n'''
                            alert += '''WARNING!\n'''
                            alert += '''Database system has been changed, and the migrations cannot be used!\n'''
                            alert += '''You need to go back to the previous database system or reset the database using the following command:\n'''
                            alert += f'''{py_cli} manage reset-db\n'''
                            alert += '''----------------------------------------------------------'''
                            
                            # Alert the user
                            print(alert)
                            time.sleep(0.1)

                            # Exit the program
                            exit()

                    # Database is OK
                    else:
                        # Check database system change
                        if not db_changed and not db_corrupted:
                            # Alert the user
                            print('- Database connection established successfully!')
                            time.sleep(0.1)

        # Check the models
        print('Checking models for errors...')
        time.sleep(0.1)

        # Global placeholders
        tables = []

        # Loop models
        for model in models:
            # Not "init" pattern & not database changed & not database corrupted
            if not pattern == "init" and not db_changed and not db_corrupted:
                # Migration model attributes
                if model in m_models:
                    m_attrs = getattr(m_module, model)
                else:
                    m_attrs = {}

            # Local placeholders
            cols = []
            attrs = {}

            # Model class
            Model = importlib.import_module(f'models.{model}')
            Class = getattr(Model, model)

            # Model meta data
            table = Class().table
            primary_key = Class().primary_key
            repair = Class().repair

            # Update the tables list
            tables.append(table)
            
            # Check the table names
            if not table_name(table)["result"]:
                # Prepare the alert message
                alert = '''----------------------------------------------------------\n'''
                alert += '''WARNING!\n'''
                alert += f'''The "{table}" table name is invalid!\n'''
                alert += table_name(table)["message"]
                alert += '''\n----------------------------------------------------------'''
                
                # Alert the user
                print(alert)

                # Exit the program
                exit()

            # Check duplicated table names
            if list_dup(tables):
                # Prepare the alert message
                alert = '''----------------------------------------------------------\n'''
                alert += '''WARNING!\n'''
                alert += f'Duplicated "{table}" table name is detected!\n'
                alert += 'Please select unique names for your tables!\n'
                alert += '''----------------------------------------------------------'''
                
                # Alert the user
                print(alert)

                # Exit the program
                exit()

            # Add model columns (class attributes) to attrs
            attrs.update(dict([(x,y) for x,y in Class.__dict__.items() if not x.startswith('__')]))

            # Check columns
            for x in attrs:
                # Update the columns list
                cols.append(x)

                # Check the column names
                if not column_name(x)["result"]:
                    # Prepare the alert message
                    alert = '''----------------------------------------------------------\n'''
                    alert += '''WARNING!\n'''
                    alert += f'''The "{x}" column name of "{model}" model is invalid!\n'''
                    alert += column_name(x)["message"]
                    alert += '''\n----------------------------------------------------------'''
                    
                    # Alert the user
                    print(alert)

                    # Exit the program
                    exit()

                # Check column constraints
                #  Check foreign key
                if attrs[x]['related_to']:

                    # Foreign key not exists
                    if not attrs[x]['related_to'] in models:
                        # Prepare the alert message
                        alert = '''----------------------------------------------------------\n'''
                        alert += '''WARNING!\n'''
                        alert += f'''The "{attrs[x]['related_to']}" foreign key of "{model}" model is invalid!\n'''
                        alert += 'Please select a valid model name as the foreign key.\n'
                        alert += '''----------------------------------------------------------'''
                        
                        # Alert the user
                        print(alert)

                        # Exit the program
                        exit()

                    # Same foreign key as the model name
                    if attrs[x]['related_to'] == model:
                        # Prepare the alert message
                        alert = '''----------------------------------------------------------\n'''
                        alert += '''WARNING!\n'''
                        alert += f'''The "{attrs[x]['related_to']}" foreign key of "{model}" model is invalid!\n'''
                        alert += 'You cannot make relationship for a model with itself!\n'
                        alert += '''----------------------------------------------------------'''
                        
                        # Alert the user
                        print(alert)

                        # Exit the program
                        exit()

                # Not "init" pattern & not database changed and not database corrupted
                if not pattern == "init" and not db_changed and not db_corrupted and not x == primary_key:
                    # Check added columns with not null & no default
                    if m_attrs and not x in m_attrs['col_type']:
                        # Check model for data
                        if len(db.read(m_attrs['table']).all()) > 0:
                            # Check not null with no default
                            if attrs[x]['not_null'] and attrs[x]['default'] == None:
                                # Prepare the alert message
                                alert = '''----------------------------------------------------------\n'''
                                alert += '''WARNING!\n'''
                                alert += f'''The added "{x}" column of "{model}" model has a NOT NULL constraint set to True without a DEFAULT constraint!\n'''
                                alert += 'You cannot set NOT NULL to True without a DEFAULT constraint for tables with already inserted data!\n'
                                alert += 'You may set the NOT NULL constraint to False or provide a valid DEFAULT constraint!\n'
                                alert += '''----------------------------------------------------------'''
                                
                                # Alert the user
                                print(alert)

                                # Exit the program
                                exit()

            # Check the primary key
            if not primary_key in cols:
                # Prepare the alert message
                alert = '''----------------------------------------------------------\n'''
                alert += '''WARNING!\n'''
                alert += f'The "{primary_key}" primary key for "{table}" table does\'t exist!\n'
                alert += 'Please provide a valid primary key\n'
                alert += '''----------------------------------------------------------'''
                
                # Alert the user
                print(alert)

                # Exit the program
                exit()

            # Not "init" pattern and not reset pattern
            if not pattern == "init" and not pattern == "reset":
                # Check repair columns
                if repair:
                    # Check the new column for duplicate values
                    if dict_dup_val(repair):
                        # Prepare the alert message
                        alert  = '''----------------------------------------------------------\n'''
                        alert += '''WARNING!\n'''
                        alert += f'''Duplicated values for repairing "{model}" model detected!\n'''
                        alert += '''----------------------------------------------------------'''
                        
                        # Alert the user
                        print(alert)

                        # Exit the program
                        exit()

                    # Loop columns for repair
                    for x in repair:
                        #  Check column for availability
                        if not x in attrs:
                            # Prepare the alert message
                            alert = '''----------------------------------------------------------\n'''
                            alert += '''WARNING!\n'''
                            alert += f'''The repairing "{x}" column of the "{model}" model not exists!\n'''
                            alert += '''----------------------------------------------------------'''
                            
                            # Alert the user
                            print(alert)

                            # Exit the program
                            exit()

                        # Check new column values
                        elif repair[x] in attrs:
                            # Prepare the alert message
                            alert = '''----------------------------------------------------------\n'''
                            alert += '''WARNING!\n'''
                            alert += f'''The repairing "{x}" column new name ("{repair[x]}") of the "{model}" model already exists!\n'''
                            alert += '''----------------------------------------------------------'''
                            
                            # Alert the user
                            print(alert)

                            # Exit the program
                            exit()

                        # Check the new column names
                        elif not column_name(repair[x])["result"]:
                            # Prepare the alert message
                            alert = '''----------------------------------------------------------\n'''
                            alert += '''WARNING!\n'''
                            alert += f'''The repairing "{repair[x]}" column name of the "{model}" model is invalid!\n'''
                            alert += column_name(repair[x])["message"]
                            alert += '''\n----------------------------------------------------------'''
                            
                            # Alert the user
                            print(alert)

                            # Exit the program
                            exit()

                        # Column is the primary key
                        elif x == primary_key:
                            # Prepare the alert message
                            alert = '''----------------------------------------------------------\n'''
                            alert += '''WARNING!\n'''
                            alert += f'''You cannot use the repair-db command for the primary key.\n'''
                            alert += f'''For renaming the primary key:\n'''
                            alert += f'''1. Rename its attribute in it's model.\n'''
                            alert += f'''2. Set the "self.primary_key" value to the new name.\n'''
                            alert += f'''3. Run the following command:\n'''
                            alert += f'''{py_cli} manage migrate-db\n'''
                            alert += f'''----------------------------------------------------------'''
                            
                            # Alert the user
                            print(alert)

                            # Exit the program
                            exit()

                        # Column is a foreign key
                        elif attrs[x]['related_to']:
                            # Prepare the alert message
                            alert = '''----------------------------------------------------------\n'''
                            alert += '''WARNING!\n'''
                            alert += f'''You cannot use the repair-db command for a foreign key.\n'''
                            alert += f'''For renaming a foreign key:\n'''
                            alert += f'''1. Remove its "related_to" parameter, and run:\n'''
                            alert += f'''{py_cli} manage migrate-db\n'''
                            alert += f'''2. Repair it using the following command:\n'''
                            alert += f'''{py_cli} manage repair-db\n'''
                            alert += f'''3. Set the "related_to" parameter again, and rerun:\n'''
                            alert += f'''{py_cli} manage migrate-db\n'''
                            alert += f'''----------------------------------------------------------'''
                            
                            # Alert the user
                            print(alert)

                            # Exit the program
                            exit()

        # Everything is fine
        print('- Models are fine!')
        time.sleep(0.1)

        # Return the result
        return True


    ##
    # @desc Initialize the database
    ##
    @staticmethod
    def initialize_database(pattern: str = "init"):
        # "init" pattern
        if pattern == "init":
            print('Creating the database connection...')
            time.sleep(0.1)

        # Create the database (+connection)
        db._create_database(database=database)

        # Connect to the new connection
        new_db = Database()
        
        # "init" pattern
        if pattern == "init":
            print('Initializing the database...')
            time.sleep(0.1)

        # Produce "_migrations" table data
        # SQLite
        if db_system == 'SQLite':
            col_type = {
                'id': 'INTEGER',
                'version': 'TEXT',
                'current': 'NUMERIC',
                'date': 'NUMERIC',
                'comment': 'TEXT',
            }

        # MySQL
        elif db_system == 'MySQL':
            col_type = {
                'id': 'INTEGER',
                'version': 'VARCHAR(50)',
                'current': 'BOOLEAN',
                'date': 'DATETIME',
                'comment': 'VARCHAR(500)',
            }

        # Postgres
        elif db_system == 'Postgres':
            col_type = {
                'id': 'INTEGER',
                'version': 'VARCHAR(50)',
                'current': 'BOOLEAN',
                'date': 'TIMESTAMP',
                'comment': 'VARCHAR(500)',
            }

        primary_key = 'id'
        unique = ['version']
        not_null = ['version', 'current', 'date']
        default = {
            'current': False,
            'date': 'CURRENT_TIMESTAMP'
        }
        new_db._create_table(table='_migrations', col_type=col_type, primary_key=primary_key, unique=unique, not_null=not_null, default=default)

        # Migration content placeholder
        m_content = ''

        # The database content
        db_con = f"""DB_SYSTEM = '{db_system}'\n\n"""

        # Update migration content
        m_content += db_con

        # Models collection for migrations
        models_coll = f"""_models = {models}\n\n"""

        # Update migrations content
        m_content += models_coll

        # Create the models tables
        for model in models:
            # Find the model and its class
            Model = importlib.import_module(f'models.{model}')
            Class = getattr(Model, model)

            # The table name
            table = Class().table

            # Atributes dictionary
            attrs = {}

            # Add model columns (class attributes) to attrs
            attrs.update(dict([(x,y) for x,y in Class.__dict__.items() if not x.startswith('__')]))

            # Table default parameters
            col_type = {}
            primary_key = Class().primary_key
            unique = []
            not_null = []
            default = {}
            check = {}
            foreign_key = {}

            # New attrs
            new_attrs = {}

            # Final attrs
            final_attrs = {}

            # Check primary key
            if primary_key == None:
                # Set primary key
                primary_key = 'id'

                # Check the id column
                if not 'id' in attrs:
                    # Add id to new attrs
                    new_attrs['id'] = {'datatype': 'integer', 'unique': False, 'not_null': True, 'default': None, 'check': None, 'foreign_key': None, 'on_update': None, 'on_delete': None}

            # Update new attrs
            new_attrs.update(attrs)

            # Loop the model attributes
            for x in new_attrs:

                # Column + Datatype
                col_type[x] = new_attrs[x]['datatype']

                # UNIQUE
                if new_attrs[x]['unique']:
                    unique.append(x)

                # NOT NULL
                if new_attrs[x]['not_null']:
                    not_null.append(x)

                # DEFAULT
                if not new_attrs[x]['default'] == None:
                    default[x] = new_attrs[x]['default']

                # Check
                if new_attrs[x]['check']:
                    check[x] = new_attrs[x]['check']

                # Foreign key
                if new_attrs[x]['related_to']:
                    # Find the reference model and its class
                    r_model = importlib.import_module(f"models.{new_attrs[x]['related_to']}")
                    r_class = getattr(r_model, new_attrs[x]['related_to'])

                    r_table = r_class().table
                    r_column = r_class().primary_key if r_class().primary_key else 'id'

                    foreign_key[x] = {
                        'r_table': r_table,
                        'r_column': r_column,
                        'on_update': new_attrs[x]['on_update'],
                        'on_delete': new_attrs[x]['on_delete'],
                    }

            # Create the model table
            new_db._create_table(table=table, col_type=col_type, primary_key=primary_key, unique=unique, not_null=not_null, default=default, check=check, foreign_key=foreign_key)

            # Produce final attrs for migrations
            final_attrs['table'] = table
            final_attrs['col_type'] = col_type
            final_attrs['primary_key'] = primary_key
            final_attrs['unique'] = unique
            final_attrs['not_null'] = not_null
            final_attrs['default'] = default
            final_attrs['check'] = check
            final_attrs['foreign_key'] = foreign_key

            # Model dictionary for migrations
            model_dic = f"""{model} = {final_attrs}\n\n"""

            # Update migrations content
            m_content += model_dic

        # Create the initial migration
        if pattern == "init":
            print('Creating the initial migration...')
            time.sleep(0.1)

        date = datetime.now().strftime("%m-%d-%Y")
        version = f'1-{date}'

        # Insert the initial migration to database
        new_db.create(table='_migrations', data={'version':version,'current':True, 'comment':'The initial migration.'})
        
        # Check migration file
        if file_exist(f"""{app_path + sep}_migrations{sep + version}.py"""):
            delete_file(f"""{app_path + sep}_migrations{sep + version}.py""")

        # Create the migrations file
        create_file(f"""{app_path + sep}_migrations{sep + version}.py""", m_content)

        # Print the message
        if pattern == "init":
            print('- Database initialized successfully!')
            time.sleep(0.1)

        # Everything is fine
        return True


    ##
    # @desc Migrate the changes to the database
    ##
    @staticmethod
    def migrate_database(pattern: str = "migrate"):
        # Migration placeholder
        migration = False

        # Checking unmigrated changes
        print('Checking models for migrations...')
        time.sleep(0.1)

        # Find migration models info
        m_version = db.read(table="_migrations", cols=['version'], where={"current":True}).first()['version']
        m_module = importlib.import_module(f'_migrations.{m_version}')
        m_models = m_module._models

        # Create temporary migration file
        CLI.migration_data(models)

        # Find current models info
        c_module = importlib.import_module(f'_migrations._temp')
        c_models = c_module._models

        # Loop migration models (for removed models & renamed tables)
        for model in m_models:
            # Migration model attributes
            m_attrs = getattr(m_module, model)

            # Removed models
            if not model in c_models:
                migration = True

                print(f'- Removed model "{model}" detected!')
                time.sleep(0.1)

                # Check the pattern
                if pattern == "migrate":
                    print('Removing model table from the database...')
                    time.sleep(0.1)

                    # Delete the table if exists
                    if db._exist_table(m_attrs['table']):
                        db._delete_table(m_attrs['table'], True)

            # Common models
            else:
                # Current model attributes
                c_attrs = getattr(c_module, model)

                # Check for renamed tables
                if not m_attrs['table'] == c_attrs['table']:
                    migration = True

                    print(f'''- Renamed tabel "{c_attrs['table']}" for "{model}" model detected!''')
                    time.sleep(0.1)

                    # Check the pattern
                    if pattern == "migrate":
                        print('Renaming the table in the database...')
                        time.sleep(0.1)

                        # Rename the table if exists
                        if db._exist_table(m_attrs['table']):
                            db._update_table(m_attrs['table'], c_attrs['table'])

                # Table temporary columns
                t_cols = CLI.list_cols(c_attrs['table'])

                # Table current columns
                c_cols = []

                # Add existed columns to current columns
                for x in t_cols:
                    # Check removed columns
                    if x in c_attrs['col_type']:
                        c_cols.append(x)

                c_cols = ', '.join(c_cols)

                # Check migration models (for removed & modified columns)
                for col in m_attrs['col_type']:

                    # Removed columns (not primary key)
                    if not col in c_attrs['col_type'] and not col == m_attrs['primary_key'] and not col == c_attrs['primary_key']:
                        migration = True

                        print(f'''- Removed column "{col}" for "{model}" model detected!''')
                        time.sleep(0.1)

                        # Check the pattern
                        if pattern == "migrate":
                            print('Removing the column from the table...')
                            time.sleep(0.1)

                            # Column is a foreign key
                            if db._exist_fk(c_attrs['table'], col):
                                # Postgres & MySQL
                                if db_system == 'Postgres' or db_system == 'MySQL':
                                    # Foreign key symbol
                                    fk_symbol = f"fk_{c_attrs['table']}_{m_attrs['foreign_key'][col]['r_table']}"

                                    # Delete foreign key if exists
                                    if db._exist_fk(c_attrs['table'], col):
                                        db._delete_fk(c_attrs['table'], col, fk_symbol, True)

                                # Delete the column if exists
                                if db._exist_column(c_attrs['table'], col):
                                    db._delete_column(c_attrs['table'], col, True)
                                    
                                # SQLite
                                elif db_system == 'SQLite':
                                    # Delete the column
                                    try:
                                        # Rename table to a temporary table
                                        db._update_table(c_attrs['table'], f"{c_attrs['table']}__temp")

                                        # Create a new table with latest constraints & fk
                                        db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                                            c_attrs['not_null'], c_attrs['default'], c_attrs['check'], c_attrs['foreign_key'])

                                        # Insert the temp table data into the new table
                                        db.query(f"INSERT INTO {c_attrs['table']}({c_cols}) SELECT {c_cols} FROM {c_attrs['table']}__temp;")

                                        # Remove the temp table
                                        db._delete_table(f"{c_attrs['table']}__temp", True)

                                    # Pass for any errors
                                    except NameError as e:
                                        # print(e)
                                        pass

                            # Column is not a foreign key
                            else:
                                # Delete the column if exists
                                if db._exist_column(c_attrs['table'], col):
                                    # Postgres & MySQL
                                    if db_system == 'Postgres' or db_system == 'MySQL':
                                        db._delete_column(c_attrs['table'], col, True)

                                    # SQLite
                                    elif db_system == 'SQLite':
                                        # Create column
                                        try:
                                            db._delete_column(c_attrs['table'], col, True)

                                        # on error
                                        except:
                                            # Rename table to a temporary table
                                            db._update_table(c_attrs['table'], f"{c_attrs['table']}__temp")

                                            # Create a new table with latest constraints
                                            db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                                                c_attrs['not_null'], c_attrs['default'], c_attrs['check'])

                                            # Insert the temp table data into the new table
                                            db.query(f"INSERT INTO {c_attrs['table']}({c_cols}) SELECT {c_cols} FROM {c_attrs['table']}__temp;")
                                            
                                            # Update the column
                                            try:
                                                db._update_column(c_attrs['table'], col, col, c_datatype, c_constraints)
                                            except:
                                                pass

                                            # Remove the temp table
                                            db._delete_table(f"{c_attrs['table']}__temp", True)
                                                
                                            # Rename table to a temporary table again
                                            db._update_table(c_attrs['table'], f"{c_attrs['table']}__temp")

                                            # Create a new table with latest constraints & fk
                                            db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                                                c_attrs['not_null'], c_attrs['default'], c_attrs['check'], c_attrs['foreign_key'])

                                            # Insert the temp table data into the new table
                                            db.query(f"INSERT INTO {c_attrs['table']}({c_cols}) SELECT {c_cols} FROM {c_attrs['table']}__temp;")

                                            # Remove the temp table
                                            db._delete_table(f"{c_attrs['table']}__temp", True)

                    # Existed columns (not primary key)
                    elif col in c_attrs['col_type'] and not col == m_attrs['primary_key'] and not col == c_attrs['primary_key']:

                        # Produce migration model data
                        m_datatype = m_attrs['col_type'][col]

                        m_unique = " UNIQUE" if col in m_attrs['unique'] else ""
                        m_not_null = " NOT NULL" if col in m_attrs['not_null'] else ""
                        m_default = f" DEFAULT {m_attrs['default'][col]}" if col in m_attrs['default'] else ""
                        m_check = f" CHECK ({m_attrs['check'][col]})" if col in m_attrs['check'] else ""

                        m_constraints = m_unique + m_not_null + m_default + m_check

                        m_fk = ""

                        if col in m_attrs['foreign_key']:
                            m_r_table = m_attrs['foreign_key'][col]['r_table']
                            m_r_column = m_attrs['foreign_key'][col]['r_column']
                            m_on_update = m_attrs['foreign_key'][col]['on_update']
                            m_on_delete = m_attrs['foreign_key'][col]['on_delete']

                            m_fk = f" FOREIGN KEY ({col}) REFERENCES {m_r_table}({m_r_column}) ON UPDATE {m_on_update} ON DELETE {m_on_delete}"
                        
                        m_data = m_datatype + m_constraints + m_fk

                        # Produce current model data
                        c_datatype = c_attrs['col_type'][col]
                        
                        c_unique = " UNIQUE" if col in c_attrs['unique'] else ""
                        c_not_null = " NOT NULL" if col in c_attrs['not_null'] else ""
                        c_default = f" DEFAULT {c_attrs['default'][col]}" if col in c_attrs['default'] else ""
                        c_check = f" CHECK ({c_attrs['check'][col]})" if col in c_attrs['check'] else ""

                        c_constraints = c_unique + c_not_null + c_default + c_check

                        c_fk = ""

                        if col in c_attrs['foreign_key']:
                            c_r_table = c_attrs['foreign_key'][col]['r_table']
                            c_r_column = c_attrs['foreign_key'][col]['r_column']
                            c_on_update = c_attrs['foreign_key'][col]['on_update']
                            c_on_delete = c_attrs['foreign_key'][col]['on_delete']

                            c_fk = f" FOREIGN KEY ({col}) REFERENCES {c_r_table}({c_r_column}) ON UPDATE {c_on_update} ON DELETE {c_on_delete}"
                        
                        c_data = c_datatype + c_constraints + c_fk

                        # Column is modified
                        if not m_data == c_data:
                            migration = True

                            print(f'''- Modified column "{col}" for "{model}" model detected!''')
                            time.sleep(0.1)

                            # Check modified columns with not null & no default
                            if len(db.read(c_attrs['table']).all()) > 0:
                                if col in c_attrs['not_null'] and not col in c_attrs['default']:
                                    # Prepare the alert message
                                    alert = '''----------------------------------------------------------\n'''
                                    alert += '''WARNING!\n'''
                                    alert += f'''The modified "{col}" column of "{model}" model has a NOT NULL constraint set to True without a DEFAULT constraint!\n'''
                                    alert += 'You cannot set NOT NULL to True without a DEFAULT constraint for tables with already inserted data!\n'
                                    alert += 'You may set the NOT NULL constraint to False or provide a valid DEFAULT constraint!\n'
                                    alert += '''----------------------------------------------------------'''
                                    
                                    # Alert the user
                                    print(alert)

                                    # Exit the program
                                    exit()

                            # Check the pattern
                            if pattern == "migrate":
                                print('Updating column in the database...')
                                time.sleep(0.1)

                                # Postgres & MySQL
                                if db_system == 'Postgres' or db_system == 'MySQL':
                                    # Column is a foreign key
                                    if m_fk or c_fk:
                                        # Already a foreign key
                                        if m_fk:
                                            # Foreign key symbol
                                            fk_symbol = f"fk_{m_attrs['table']}_{m_r_table}"

                                            # Delete foreign key if exists
                                            if db._exist_fk(m_attrs['table'], col):
                                                db._delete_fk(m_attrs['table'], col, fk_symbol, True)

                                        # Update the column if exists
                                        if db._exist_column(c_attrs['table'], col):
                                            db._update_column(c_attrs['table'], col, col, c_datatype, c_constraints)
                                        
                                        # Currently a foreign key
                                        if c_fk:
                                            # Add foreign key if not exists
                                            if not db._exist_fk(m_attrs['table'], col):
                                                db._create_fk(c_attrs['table'], col, c_r_table, c_r_column, c_on_update, c_on_delete)

                                    # Column is not a foreign key
                                    else:
                                        # Update the column if exists
                                        if db._exist_column(c_attrs['table'], col):
                                            db._update_column(c_attrs['table'], col, col, c_datatype, c_constraints)

                                # SQLite
                                elif db_system == 'SQLite':
                                    # Update the column
                                    try:
                                        # Rename table to a temporary table
                                        db._update_table(c_attrs['table'], f"{c_attrs['table']}__temp")

                                        # Create a new table with latest constraints
                                        db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                                            c_attrs['not_null'], c_attrs['default'], c_attrs['check'])

                                        # Insert the temp table data into the new table
                                        db.query(f"INSERT INTO {c_attrs['table']}({c_cols}) SELECT {c_cols} FROM {c_attrs['table']}__temp;")
                                        
                                        # Update the column
                                        try:
                                            db._update_column(c_attrs['table'], col, col, c_datatype, c_constraints)
                                        except:
                                            pass

                                        # Remove the temp table
                                        db._delete_table(f"{c_attrs['table']}__temp", True)
                                            
                                        # Rename table to a temporary table again
                                        db._update_table(c_attrs['table'], f"{c_attrs['table']}__temp")

                                        # Create a new table with latest constraints & fk
                                        db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                                            c_attrs['not_null'], c_attrs['default'], c_attrs['check'], c_attrs['foreign_key'])

                                        # Insert the temp table data into the new table
                                        db.query(f"INSERT INTO {c_attrs['table']}({c_cols}) SELECT {c_cols} FROM {c_attrs['table']}__temp;")

                                        # Remove the temp table
                                        db._delete_table(f"{c_attrs['table']}__temp", True)

                                    # Pass for any errors
                                    except NameError as e:
                                        # print(e)
                                        pass

                # Check current models (for added columns)
                for col in c_attrs['col_type']:

                    # Check for added columns (not primary key)
                    if not col in m_attrs['col_type'] and not col == c_attrs['primary_key']:
                        migration = True

                        print(f'- Added column "{col}" for "{model}" model detected!')
                        time.sleep(0.1)

                        # Check the pattern
                        if pattern == "migrate":
                            print('Adding the column to the table...')
                            time.sleep(0.1)

                            # Produce current model data
                            c_datatype = c_attrs['col_type'][col]
                            
                            c_unique = " UNIQUE" if col in c_attrs['unique'] else ""
                            c_not_null = " NOT NULL" if col in c_attrs['not_null'] else ""
                            c_default = f" DEFAULT {c_attrs['default'][col]}" if col in c_attrs['default'] else ""
                            c_check = f" CHECK ({c_attrs['check'][col]})" if col in c_attrs['check'] else ""

                            c_constraints = c_unique + c_not_null + c_default + c_check

                            if col in c_attrs['foreign_key']:
                                c_r_table = c_attrs['foreign_key'][col]['r_table']
                                c_r_column = c_attrs['foreign_key'][col]['r_column']
                                c_on_update = c_attrs['foreign_key'][col]['on_update']
                                c_on_delete = c_attrs['foreign_key'][col]['on_delete']

                            # Column is a foreign key
                            if col in c_attrs['foreign_key']:
                                # Postgres & MySQL
                                if db_system == 'Postgres' or db_system == 'MySQL':

                                    # Create the column if not exists
                                    if not db._exist_column(c_attrs['table'], col):
                                        # Add column to the table
                                        db._create_column(c_attrs['table'], col, c_datatype, c_constraints)

                                    # Add the foreign key if not exists
                                    if not db._exist_fk(c_attrs['table'], col):
                                        db._create_fk(c_attrs['table'], col, c_r_table, c_r_column, c_on_update, c_on_delete)

                                # SQLite
                                elif db_system == 'SQLite':
                                    # Create the column
                                    try:
                                        # Rename table to a temporary table
                                        db._update_table(c_attrs['table'], f"{c_attrs['table']}__temp")

                                        # Create a new table with latest constraints & fk
                                        db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                                            c_attrs['not_null'], c_attrs['default'], c_attrs['check'], c_attrs['foreign_key'])

                                        # Insert the temp table data into the new table
                                        db.query(f"INSERT INTO {c_attrs['table']}({c_cols}) SELECT {c_cols} FROM {c_attrs['table']}__temp;")

                                        # Remove the temp table
                                        db._delete_table(f"{c_attrs['table']}__temp", True)

                                    # Pass if any error happened
                                    except NameError as e:
                                        # print(e)
                                        pass

                            # Column is not a foreign key
                            else:
                                # Create the column if not exists
                                if not db._exist_column(c_attrs['table'], col):
                                    # Postgres & MySQL
                                    if db_system == 'Postgres' or db_system == 'MySQL':
                                        db._create_column(c_attrs['table'], col, c_datatype, c_constraints)

                                    # SQLite
                                    elif db_system == 'SQLite':
                                        # Create column
                                        try:
                                            db._create_column(c_attrs['table'], col, c_datatype, c_constraints)

                                        # on error
                                        except:
                                            # Rename table to a temporary table
                                            db._update_table(c_attrs['table'], f"{c_attrs['table']}__temp")

                                            # Create a new table with latest constraints
                                            db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                                                c_attrs['not_null'], c_attrs['default'], c_attrs['check'])

                                            # Insert the temp table data into the new table
                                            db.query(f"INSERT INTO {c_attrs['table']}({c_cols}) SELECT {c_cols} FROM {c_attrs['table']}__temp;")
                                            
                                            # Update the column
                                            try:
                                                db._update_column(c_attrs['table'], col, col, c_datatype, c_constraints)
                                            except:
                                                pass

                                            # Remove the temp table
                                            db._delete_table(f"{c_attrs['table']}__temp", True)
                                                
                                            # Rename table to a temporary table again
                                            db._update_table(c_attrs['table'], f"{c_attrs['table']}__temp")

                                            # Create a new table with latest constraints & fk
                                            db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                                                c_attrs['not_null'], c_attrs['default'], c_attrs['check'], c_attrs['foreign_key'])

                                            # Insert the temp table data into the new table
                                            db.query(f"INSERT INTO {c_attrs['table']}({c_cols}) SELECT {c_cols} FROM {c_attrs['table']}__temp;")

                                            # Remove the temp table
                                            db._delete_table(f"{c_attrs['table']}__temp", True)

                    # Added primary key
                    elif not col in m_attrs['col_type'] and col == c_attrs['primary_key']:
                        migration = True

                        print(f'''- Modified primary key "{col}" for "{model}" model detected!''')
                        time.sleep(0.1)

                        # Check the pattern
                        if pattern == "migrate":
                            print('Modifying the primary key...')
                            time.sleep(0.1)

                            # Rename table to a temporary table
                            db._update_table(c_attrs['table'], f"{c_attrs['table']}__temp")

                            # Create a new table with latest constraints without fk
                            db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                                c_attrs['not_null'], c_attrs['default'], c_attrs['check'])

                            # Insert the temp table data into the new table
                            try:
                                db.query(f"INSERT INTO {c_attrs['table']}({c_cols}) SELECT {c_cols} FROM {c_attrs['table']}__temp;")
                            
                            # Pass for any errors
                            except NameError as e:
                                # print(e)
                                pass

                            # Remove the temp table
                            db._delete_table(f"{c_attrs['table']}__temp", True)

                            # Rename table to a temporary table again
                            db._update_table(c_attrs['table'], f"{c_attrs['table']}__temp")

                            # Create a new table with latest constraints with fk
                            db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                                c_attrs['not_null'], c_attrs['default'], c_attrs['check'], c_attrs['foreign_key'])

                            # Insert the temp table data into the new table
                            try:
                                db.query(f"INSERT INTO {c_attrs['table']}({c_cols}) SELECT {c_cols} FROM {c_attrs['table']}__temp;")
                            
                            # Pass for any errors
                            except NameError as e:
                                # print(e)
                                pass

                            # Remove the temp table
                            db._delete_table(f"{c_attrs['table']}__temp", True)

        # Loop current models (for added models)
        for model in c_models:
            # Current model attributes
            c_attrs = getattr(c_module, model)

            # Added models
            if not model in m_models:
                migration = True

                print(f'- New model "{model}" detected!')
                time.sleep(0.1)

                # Check the pattern
                if pattern == "migrate":
                    print('Creating the new model table...')
                    time.sleep(0.1)

                    # Create the table if not exists
                    if not db._exist_table(c_attrs['table']):
                        db._create_table(c_attrs['table'], c_attrs['col_type'], c_attrs['primary_key'], c_attrs['unique'], 
                        c_attrs['not_null'], c_attrs['default'], c_attrs['check'], c_attrs['foreign_key'])

        # New migration found
        if migration:
            # Migrate pattern
            if pattern == "migrate":
                # Prompt the user for migration comment
                migration_comment = input("Your Comment (optional): ")
                migration_comment = migration_comment if migration_comment else "Untitled"

                # Create new migration
                print('Creating a new migration...')
                time.sleep(0.1)

                date = datetime.now().strftime("%m-%d-%Y")
                inserted_id = db.read(table="_migrations").last()["id"] + 1
                version = f'{inserted_id}-{date}'

                # Set the previous migration current to false
                db.update(table='_migrations', data={'current':False}, where={'version':m_version})

                # Insert the new migration into the database
                db.create(table='_migrations', data={'version':version,'current':True, 'comment':migration_comment})

                # Produce the migration content
                content = CLI.migration_data(models)
                
                # Check migration file
                if file_exist(f"""{app_path + sep}_migrations{sep + version}.py"""):
                    delete_file(f"""{app_path + sep}_migrations{sep + version}.py""")

                # Create the migrations file
                create_file(f"""{app_path + sep}_migrations{sep + version}.py""", content)

                # Delete the temporary migration file
                delete_file(temp_file)

                # Alert the user
                print('- All changes migrated to the database.')
                time.sleep(0.1)

            # Check pattern
            elif pattern == "check":
                # Delete the temporary migration file
                delete_file(temp_file)

                # Alert the user
                alert = '''----------------------------------------------------------\n'''
                alert += '''NOTICE!\n'''
                alert += "To migrate new changes to the database run the following command:\n"
                alert += f"{py_cli} manage migrate-db\n"
                alert += '''----------------------------------------------------------'''

                print(alert)
                time.sleep(0.1)

            # Repair pattern
            elif pattern == "repair":
                # Delete the temporary migration file
                delete_file(temp_file)

                # Alert the user
                alert = '''----------------------------------------------------------\n'''
                alert += '''WARNING!\n'''
                alert += "Before repairing the database you must migrate the new changes.\n"
                alert += "To migrate new changes to the database run the following command:\n"
                alert += f"{py_cli} manage migrate-db\n"
                alert += '''----------------------------------------------------------'''

                print(alert)
                time.sleep(0.1)

            # Return result
            return True

        # No new migration found
        else:
            # Delete the temporary migration file
            delete_file(temp_file)

            # No migration
            print('- Nothing to migrate!')
            time.sleep(0.1)

            # Return result
            return False


    ##
    # @desc Repairing the database
    ##
    @staticmethod
    def repair_database(pattern: str = "repair"):
        # Only for check and repair patterns
        if pattern == "repair" or pattern == "check":
            print('Checking models for repairs...')
            time.sleep(0.1)

            # Repair placeholders
            table_repair = False
            column_repair = False

            # Find migration models info
            m_version = db.read(table="_migrations", cols=['version'], where={"current":True}).first()['version']
            m_module = importlib.import_module(f'_migrations.{m_version}')
            m_models = m_module._models

            # Looping the models
            for model in m_models:
                # Migration model attributes
                m_attrs = getattr(m_module, model)
                table = m_attrs['table']

                # Search for temporary tables
                if db._exist_table(f"{table}__temp"):
                    table_repair = True

                    print(f'- Corrupted "{table}" table for "{model}" model detected!')
                    time.sleep(0.1)

                    # For only the repair pattern
                    if pattern == "repair":
                        print(f'Repairing "{table}" table in the database...')
                        time.sleep(0.1)

                        db._delete_table(f"{table}__temp", True)

                        # Search for temporary columns
                        for col in m_attrs['col_type']:
                            if db._exist_column(table, f"{col}__temp"):
                                db._delete_column(table, f"{col}__temp", True)

                # Find the current model repair attribute
                c_model = importlib.import_module(f'models.{model}')
                c_class = getattr(c_model, model)
                repair = c_class().repair

                # Produce repairing model attributes
                r_attrs = {}
                for k, v in m_attrs.items():
                    if k == 'table':
                        r_attrs[k] = v

                    elif k == 'col_type':
                        r_col_type = {}
                        for x, y in m_attrs[k].items():
                            if x in repair:
                                r_col_type[repair[x]] = y
                            else:
                                r_col_type[x] = y

                        r_attrs[k] = r_col_type

                    elif k == 'primary_key':
                        r_attrs[k] = v
                    
                    elif k == 'unique':
                        r_unique = [None] * len(m_attrs[k])
                        for x in range(len(m_attrs[k])):
                            if m_attrs[k][x] in repair:
                                r_unique[x] = repair[m_attrs[k][x]]
                            else:
                                r_unique[x] = m_attrs[k][x]

                        r_attrs[k] = r_unique
                    
                    elif k == 'not_null':
                        r_not_null = [None] * len(m_attrs[k])
                        for x in range(len(m_attrs[k])):
                            if m_attrs[k][x] in repair:
                                r_not_null[x] = repair[m_attrs[k][x]]
                            else:
                                r_not_null[x] = m_attrs[k][x]

                        r_attrs[k] = r_not_null
                    
                    elif k == 'default':
                        r_default = {}
                        for x, y in m_attrs[k].items():
                            if x in repair:
                                r_default[repair[x]] = y
                            else:
                                r_default[x] = y

                        r_attrs[k] = r_default
                    
                    elif k == 'check':
                        r_check = {}
                        for x, y in m_attrs[k].items():
                            if x in repair:
                                r_check[repair[x]] = y
                            else:
                                r_check[x] = y

                        r_attrs[k] = r_check
                    
                    elif k == 'foreign_key':
                        r_foreign_key = {}
                        for x, y in m_attrs[k].items():
                            if x in repair:
                                r_foreign_key[repair[x]] = y
                            else:
                                r_foreign_key[x] = y

                        r_attrs[k] = r_foreign_key

                # if table == 'partials':
                #     print(m_attrs)
                #     print(r_attrs)

                # Table temporary columns
                t_cols = CLI.list_cols(m_attrs['table'])
                
                # Repair columns
                r_cols = []

                # Table current columns
                c_cols = []

                # Add existed columns to current columns
                for x in t_cols:
                    # Model cols
                    c_cols.append(x)

                    # Renamed columns
                    if x in repair:
                        r_cols.append(repair[x])

                    # Other comumns
                    else:
                        r_cols.append(x)

                c_cols = ', '.join(c_cols)
                r_cols = ', '.join(r_cols)

                # if table == 'partials':
                #     print(c_cols)
                #     print(r_cols)

                # Check the repair attribute
                if repair:
                    column_repair = True

                    # Loop the repair
                    for col in repair:
                        print(f'- Repairing "{col}" column for "{model}" model detected!')
                        time.sleep(0.1)

                        # For only the repair pattern
                        if pattern == "repair":
                            print('Repairing column in the database...')
                            time.sleep(0.1)

                            # Produce migration model data
                            m_datatype = m_attrs['col_type'][col]
                            
                            m_pk = " PRIMARY KEY" if col == m_attrs['primary_key'] else ""
                            
                            m_unique = " UNIQUE" if col in m_attrs['unique'] else ""
                            m_not_null = " NOT NULL" if col in m_attrs['not_null'] else ""
                            m_default = f" DEFAULT {m_attrs['default'][col]}" if col in m_attrs['default'] else ""
                            m_check = f" CHECK ({m_attrs['check'][col]})" if col in m_attrs['check'] else ""

                            m_constraints = m_pk + m_unique + m_not_null + m_default + m_check

                            # Repair the column
                            try:
                                db._update_column(table, col, repair[col], m_datatype, m_constraints)
                            
                            # On error
                            except:
                                # Rename table to a temporary table
                                db._update_table(table, f"{table}__temp")

                                # Create a new table with latest constraints (renamed)
                                db._create_table(table, r_attrs['col_type'], r_attrs['primary_key'], r_attrs['unique'], 
                                    r_attrs['not_null'], r_attrs['default'], r_attrs['check'], r_attrs['foreign_key'])

                                # Insert the temp table data into the new table
                                db.query(f"INSERT INTO {table}({r_cols}) SELECT {c_cols} FROM {table}__temp;")
                                
                                # Remove the temp table
                                db._delete_table(f"{table}__temp", True)
                            
                            model_file = f'{app_path + sep}models{sep + model}.py'

                            # Update the model file
                            old_str = rf"^[ ]*{col}+[ ]*[=]+[ ]*Model+\.+"
                            new_str = f"    {repair[col]} = Model."
                            replace_file_string(model_file, old_str, new_str, True)

                            old_line = rf"^[ ]*'{col}'+[ ]*[:]+[ ]*'{repair[col]}'+\,*"
                            new_line = ""
                            replace_file_line(model_file, old_line, new_line, True)

            # Column repair detected
            if column_repair and pattern == "repair":
                # Produce the migration content
                content = CLI.migration_data(models, True)

                # Prompt the user for migration comment
                migration_comment = input("Your Comment (optional): ")
                migration_comment = migration_comment if migration_comment else "Untitled"

                # Create new migration
                print('Creating a new migration...')
                time.sleep(0.1)

                date = datetime.now().strftime("%m-%d-%Y")
                inserted_id = db.read(table="_migrations").last()["id"] + 1
                version = f'{inserted_id}-{date}'

                # Set the previous migration current to false
                db.update(table='_migrations', data={'current':False}, where={'version':m_version})

                # Insert the new migration into the database
                db.create(table='_migrations', data={'version':version,'current':True, 'comment':migration_comment})
                
                # Check migration file
                if file_exist(f"""{app_path + sep}_migrations{sep + version}.py"""):
                    delete_file(f"""{app_path + sep}_migrations{sep + version}.py""")
                
                # Create the migrations file
                create_file(f"""{app_path + sep}_migrations{sep + version}.py""", content)

                # Delete the temporary migration file
                delete_file(temp_file)

                # Alert the user
                print('- Database repaired successfully, and a new migration created!')
                time.sleep(0.1)

            # Table repair detected
            elif table_repair and pattern == "repair":
                print("- Database repaired successfully!")
                time.sleep(0.1)

            # Pattern is check and repair detected
            elif (column_repair or table_repair) and pattern == "check":
                # Prepare the alert message
                alert = '''----------------------------------------------------------\n'''
                alert += '''NOTICE!\n'''
                alert += f'''To repair the database use the following command:\n'''
                alert += f'''{py_cli} manage repair-db\n'''
                alert += f'''----------------------------------------------------------'''
                
                # Alert the user
                print(alert)
                time.sleep(0.1)

            # No repair requested
            elif not column_repair and not table_repair:
                print("- Nothing to repair!")
                time.sleep(0.1)

        # Everything is fine
        return True


    ##
    # @desc List available columns for SQLite
    # 
    # @param data: str -- 'name', 'type', 'notnull', 'dflt_value', 'pk'
    # 
    # @var sql: str -- For SQL statement
    # @var col_list: list -- For storing column info based on "data" param
    # @var cols: list -- Query result as a list of dictionaries
    # 
    # @return list
    ##
    @staticmethod
    def list_cols(table:str):
        # SQLite
        if db_system == "SQLite":
            sql = f'''PRAGMA table_info(`{table}`);'''

        # MySQL
        elif db_system == "MySQL":
            sql = f'''SHOW COLUMNS FROM `{table}`;'''

        # Postgres
        elif db_system == "Postgres":
            sql = f'''SELECT column_name FROM information_schema.columns WHERE table_name='{table}';'''

        cols = db.query(sql).fetchall()
            
        col_list = []

        for col in cols:
            for x in col:
                if db_system == "SQLite" and x == 'name':
                    col_list.append(col[x])
                    
                elif db_system == "MySQL" and x == 'Field':
                    col_list.append(col[x])
                    
                elif db_system == "Postgres" and x == col[0]:
                    col_list.append(x)

        return col_list


    ##
    # @desc create_app method for creating new child apps
    # 
    # @var name: str -- The app name
    # @var url: str -- The app base URL
    ##
    def create_app(self):
        # Prompt for app name
        while True:
            app = input("App Name: ")

            # Check app name
            if app_name(app)['result']:
                # App name is taken
                if app_exists(app)['result']:
                    print(f'- The "{app}" is already registered! Try another name.')
                    time.sleep(0.1)

                # App name is OK
                else:
                    break

            # Print the error
            else:
                print(app_name(app)['message'])

        # Prompt for app URL
        while True:
            url = input("App URL: ")

            # Check app URL
            if app_url(url)['result']:
                # App URL is taken
                if app_url_exists(url):
                    print(f'- The "{url}" is already registered! Try another URL.')
                    time.sleep(0.1)

                # App URL is free
                break

            # Print the error
            else:
                print(app_url(url)['message'])
        
        # Begin the process
        try:
            print('Creating the new app...')
            time.sleep(0.1)

            # Create folders: (controllers, forms, statics, views)
            create_dir(f'{app_path + sep}controllers{sep + app}')
            create_dir(f'{app_path + sep}forms{sep + app}')
            create_dir(f'{app_path + sep + statics + sep + app}')
            create_dir(f'{app_path + sep}views{sep + app}')

            # Handle controllers blueprint (copy, unzip, delete)
            controllers_blueprint= f'{aurora_path + sep}blueprints{sep}controllers.zip'
            controllers_file = f'{app_path + sep}controllers{sep + app + sep}controllers.zip'
            controllers_dir = f'{app_path + sep}controllers{sep + app + sep}'
            copy_file(controllers_blueprint, controllers_file)
            unzip_file(controllers_file, controllers_dir)
            delete_file(controllers_file)

            # Handle forms blueprint (copy, unzip, delete)
            forms_blueprint= f'{aurora_path + sep}blueprints{sep}forms.zip'
            forms_file = f'{app_path + sep}forms{sep + app + sep}forms.zip'
            forms_dir = f'{app_path + sep}forms{sep + app + sep}'
            copy_file(forms_blueprint, forms_file)
            unzip_file(forms_file, forms_dir)
            delete_file(forms_file)

            # Handle statics blueprint (copy, unzip, delete)
            statics_blueprint= f'{aurora_path + sep}blueprints{sep}statics.zip'
            statics_file = f'{app_path + sep + statics + sep + app + sep}statics.zip'
            statics_dir = f'{app_path + sep + statics + sep + app + sep}'
            copy_file(statics_blueprint, statics_file)
            unzip_file(statics_file, statics_dir)
            delete_file(statics_file)

            # Handle views blueprint (copy, unzip, delete)
            views_blueprint= f'{aurora_path + sep}blueprints{sep}views.zip'
            views_file = f'{app_path + sep}views{sep + app + sep}views.zip'
            views_dir = f'{app_path + sep}views{sep + app + sep}'
            copy_file(views_blueprint, views_file)
            unzip_file(views_file, views_dir)
            delete_file(views_file)

            # Update layout.html
            replace_file_string(f'{app_path + sep}views{sep + app + sep}layout.html', 'app_name', app)

            # Update _apps.py
            new_line = f'''    app(name='{app}', url='{url}'),\n'''
            new_line += ''']#do-not-change-me'''
            replace_file_line(file_path=f'{app_path + sep}_apps.py', old_line=']#do-not-change-me', new_line=new_line)

            # print the message
            print('- The new app created successfully!')
            time.sleep(0.1)

        # Handle errors
        except NameError as e:
            print(e)


    ##
    # @desc delete_app method for removing child apps
    ##
    def delete_app(self):
        # Prompt for app name
        while True:
            app = input("App Name: ")

            # Check app name
            if app_name(app)['result']:
                # App not exists
                if not app_exists(app)['result']:
                    print(f'- The "{app}" doesn\'t exist!')
                    time.sleep(0.1)

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(app)['message'])
                time.sleep(0.1)
        
        # Alert the user for data loss
        alert = '''WARNING! You will loose the following data perminantly:\n'''
        alert += '''----------------------------------------------------------\n'''
        alert += f'''{app_path + sep}controllers{sep + app + sep}*\n'''
        alert += f'''{app_path + sep}forms{sep + app + sep}*\n'''
        alert += f'''{app_path + sep + statics + sep + app + sep}*\n'''
        alert += f'''{app_path + sep}views{sep + app + sep}*\n'''
        alert += f'''----------------------------------------------------------'''
        
        # Print the alert
        print(alert)
        time.sleep(0.1)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            print('Removing the app...')
            time.sleep(0.1)

            # Begin the process
            try:
                # Delete the app folders
                delete_dir(f'{app_path + sep}controllers{sep + app + sep}')
                delete_dir(f'{app_path + sep}forms{sep + app + sep}')
                delete_dir(f'{app_path + sep + statics + sep + app + sep}')
                delete_dir(f'{app_path + sep}views{sep + app + sep}')

                # Update the _apps.py
                old_line_1 = rf"""^[ ]*app+[(]+.*name='{app}'."""
                old_line_2 = rf"""^[ ]*app+[(]+.*name="{app}"."""
                replace_file_line(file_path=f'{app_path + sep}_apps.py', old_line=old_line_1, new_line='', regex=True)
                replace_file_line(file_path=f'{app_path + sep}_apps.py', old_line=old_line_2, new_line='', regex=True)
                
                print('- App deleted successfully')
                time.sleep(0.1)

            # Handle errors
            except NameError as e:
                print(e)

        # Rejected
        else:
            print('- The operation canceled!')
            exit()


    ##
    # @desc create_controller method for creating new controller
    ##
    def create_controller(self):
        # Prompt for app name
        while True:
            app = input("App Name: ")

            # Check app name
            if app_name(app)['result']:
                # App not exists
                if not app_exists(app)['result']:
                    print(f'- The "{app}" doesn\'t exist!')
                    time.sleep(0.1)

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(app)['message'])
                time.sleep(0.1)

        # Controllers info
        module = importlib.import_module(f'controllers.{app}._controllers')
        controllers = getattr(module, 'controllers')

        # Prompt for controller name
        while True:
            controller = input("Controller Name: ")

            # Check controller name
            if controller_name(controller)['result']:
                # Controller already exists
                if controller_exists(app, controller)['result']:
                    print(f'- The "{controller}" already exists!')

                # Controller not exists
                else:
                    break

            # Print the error
            else:
                print(controller_name(controller)['message'])

        # Prompt for controller url
        while True:
            url = input("Controller URL: ")

            # Check controller url
            if controller_url(url)['result']:
                # First URL can be omitted
                if len(controllers) == 0:
                    break

                # Controller url already exists
                if controller_url_exists(app, url):
                    print(f'- The "{url}" already exists!')

                # Controller url not exists
                else:
                    break

            # Print the error
            else:
                print(controller_url(url)['message'])

        # Prompt for optional methods
        while True:
            methods = input("Methods (optional): ").upper()

            # Remove spaces from methods
            methods = delete_chars(methods, ' ')
            
            # Convert methods to list 
            if methods:
                methods = methods.split(',')

            # Sort methods
            methods = sorted(methods)

            # Check methods
            if not controller_methods(methods)['result']:
                print(controller_methods(methods)['message'])

            # Break the loop
            else:
                break
        
        # Controller methods
        ctrl_methods = ''

        # POST method
        if 'POST' in methods:
            ctrl_methods += """    # POST Method\n"""
            ctrl_methods += """    def post(self):\n"""
            ctrl_methods += """        pass\n\n"""

        # GET method
        if 'GET' in methods:
            ctrl_methods += """    # GET Method\n"""
            ctrl_methods += """    def get(self):\n"""
            ctrl_methods += """        return 'Page content...'\n\n"""

        # PUT method
        if 'PUT' in methods:
            ctrl_methods += """    # PUT Method\n"""
            ctrl_methods += """    def put(self):\n"""
            ctrl_methods += """        pass\n\n"""

        # DELETE method
        if 'DELETE' in methods:
            ctrl_methods += """    # DELETE Method\n"""
            ctrl_methods += """    def delete(self):\n"""
            ctrl_methods += """        pass\n\n"""

        # Default method (GET)
        if not methods:
            ctrl_methods += """    # GET Method\n"""
            ctrl_methods += """    def get(self):\n"""
            ctrl_methods += """        return 'Page content...'\n\n"""
            
            methods = ['GET']
        
        # try the process
        try:
            # Create controller
            print('Creating the controller...')
            time.sleep(0.1)
            
            # Controller blueprint
            controller_blueprint = f'{aurora_path + sep}blueprints{sep}controller.zip'
            controller_file = f'{app_path + sep}controllers{sep + app + sep}controller.zip'
            controller_dir = f'{app_path + sep}controllers{sep + app + sep}'

            # Copy, unzip, delete blueprint
            copy_file(controller_blueprint, controller_file)
            unzip_file(controller_file, controller_dir)
            delete_file(controller_file)

            # Rename _controller.py
            controller_old = f'{app_path + sep}controllers{sep + app + sep}_controller.py'
            controller_new = f'{app_path + sep}controllers{sep + app + sep + controller}.py'
            rename_file(controller_old, controller_new)

            # Update new controller
            replace_file_string(controller_new, 'ControllerName', controller)
            replace_file_line(controller_new, '...', ctrl_methods)

            # Update _controllers.py
            controllers_file = f'{app_path + sep}controllers{sep + app + sep}_controllers.py'

            new_line = f'''    controller(name='{controller}', url='{url}', methods={methods}),\n'''
            new_line += """]#do-not-change-me"""

            replace_file_line(controllers_file, ']#do-not-change-me', new_line)

            # Print result
            print('- The new controller created successfuly!')
            time.sleep(0.1)

        # Handle errors
        except NameError as e:
            print(e)


    ##
    # @desc delete_controller method for removing an existing controller
    ##
    def delete_controller(self):
        # Prompt for app name
        while True:
            app = input("App Name: ")

            # Check app name
            if app_name(app)['result']:
                # App not exists
                if not app_exists(app)['result']:
                    print(f'- The "{app}" doesn\'t exist!')
                    time.sleep(0.1)

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(app)['message'])
                time.sleep(0.1)

        # Controllers info
        module = importlib.import_module(f'controllers.{app}._controllers')
        controllers = getattr(module, 'controllers')

        # App controllers
        if len(controllers) == 0:
            print(f'- No controllers found for "{app}" app!')
            exit()

        # Controller name
        while True:
            # Prompt for controller name
            controller = input("Controller Name: ")

            # Check controller name
            if controller_name(controller)['result']:
                # Controller exists
                if controller_exists(app, controller)['result']:
                    break

                # Controller not exists
                else:
                    print(f'- The "{controller}" does\'nt exist!')

            # Print the error
            else:
                print(controller_name(controller)['message'])
        
        # Alert the user for data loss
        alert = '''WARNING! You will loose the following data perminantly:\n'''
        alert += '''----------------------------------------------------------\n'''
        alert += f'''{app_path + sep}controllers{sep + app + sep + controller}.py\n'''
        alert += f'''----------------------------------------------------------'''
        
        # Print the alert
        print(alert)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            print('Removing the controller...')
            time.sleep(0.1)

            # Begin the process
            try:
                # Delete the controller module
                delete_file(f'{app_path + sep}controllers{sep + app + sep + controller}.py')

                # Update _controllers.py
                controllers_file = f'{app_path + sep}controllers{sep + app + sep}_controllers.py'
                
                old_line_1 = rf"""^[ ]*controller+[(]+.*name='{controller}'."""
                old_line_2 = rf"""^[ ]*controller+[(]+.*name="{controller}"."""

                replace_file_line(controllers_file, old_line_1, new_line='', regex=True)
                replace_file_line(controllers_file, old_line_2, new_line='', regex=True)
                
                print('- Controller deleted successfully!')
                time.sleep(0.1)

            # Handle errors
            except NameError as e:
                print(e)

        # Rejected
        else:
            print('- The operation canceled!')
            exit()


    ##
    # @desc create_view method for creating new view
    ##
    def create_view(self):
        # Prompt for app name
        while True:
            app = input("App Name: ")

            # Check app name
            if app_name(app)['result']:
                # App not exists
                if not app_exists(app)['result']:
                    print(f'- The "{app}" doesn\'t exist!')
                    time.sleep(0.1)

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(app)['message'])
                time.sleep(0.1)

        # Prompt for view name
        while True:
            view = input("View Name: ")

            # Check the view name
            if view_name(view)['result']:
                view_file = f'{app_path + sep}views{sep + app + sep + view}.html'

                # View exists
                if os.path.exists(view_file):
                    print(f'- The "{view}" is already exists!')

                # View not exists
                else:
                    break

            # Print the error
            else:
                print(view_name(view)['message'])

        # Begin the process
        try:
            print('Creating the new view...')
            time.sleep(0.1)
            
            # View blueprint
            view_blueprint = f'{aurora_path + sep}blueprints{sep}view.zip'
            view_file = f'{app_path + sep}views{sep + app + sep}view.zip'
            view_dir = f'{app_path + sep}views{sep + app + sep}'
            
            # Copy the view blueprint
            copy_file(view_blueprint, view_file)

            # Unzip the view blueprint
            unzip_file(view_file, view_dir)

            # Delete the view zip file
            delete_file(view_file)

            # Rename the view blueprint
            old_view = f'{app_path + sep}views{sep + app + sep}_view.html'
            new_view = f'{app_path + sep}views{sep + app + sep + view}.html'
            rename_file(old_view, new_view)

            # update the view blue print
            replace_file_string(new_view, 'app_name', app)

            # Print the result
            print('- The new view created successfully!')
            time.sleep(0.1)
        
        # Handle errors
        except NameError as e:
            print(e)


    ##
    # @desc delete_view method for removing an existing view
    ##
    def delete_view(self):
        # Prompt for app name
        while True:
            app = input("App Name: ")

            # Check app name
            if app_name(app)['result']:
                # App not exists
                if not app_exists(app)['result']:
                    print(f'- The "{app}" doesn\'t exist!')
                    time.sleep(0.1)

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(app)['message'])
                time.sleep(0.1)

        # Prompt for view name
        while True:
            view = input("View Name: ")

            # Check the view name
            if view_name(view)['result']:
                view_file = f'{app_path + sep}views{sep + app + sep + view}.html'

                # View not exists
                if not os.path.exists(view_file):
                    print(f'- The "{view}" deos\'nt exist!')

                # View exists
                else:
                    break

            # Print the error
            else:
                print(view_name(view)['message'])
        
        # Alert the user for data loss
        alert = '''WARNING! You will loose the following data perminantly:\n'''
        alert += '''----------------------------------------------------------\n'''
        alert += f'''{app_path + sep}views{sep + app + sep + view}.html\n'''
        alert += f'''----------------------------------------------------------'''
        
        # Print the alert
        print(alert)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            # Begin the process
            try:
                print('Removing the view...')
                time.sleep(0.1)

                # Delete the view file
                view_file = f'{app_path + sep}views{sep + app + sep + view}.html'
                delete_file(view_file)

                # Print the result
                print('- The view deleted successfully!')
                time.sleep(0.1)

            # Handle errors
            except NameError as e:
                print(e)

        # Rejected
        else:
            print('- The operation canceled!')
            exit()


    ##
    # @desc create_model method for creating new model
    ##
    def create_model(self):
        # Prompt for model name
        while True:
            model = input("Model Name: ")

            # Check model name
            if model_name(model)['result']:
                # Model exists
                if model in models:
                    print(f'- The "{model}" already exist!')

                # Model not exists
                else:
                    break

            # Print the error
            else:
                print(model_name(model)['message'])

        # Begin the process
        try:
            print('Creating the new model...')
            time.sleep(0.1)

            # Model blueprint
            # Check the safe type
            if safe_type:
                model_blueprint = f'{aurora_path + sep}blueprints{sep}model_safe.zip'
            else:
                model_blueprint = f'{aurora_path + sep}blueprints{sep}model.zip'

            model_file = f'{app_path + sep}models{sep}model.zip'
            model_dir = f'{app_path + sep}models{sep}'
            
            # Copy the model blueprint
            copy_file(model_blueprint, model_file)

            # Unzip the model blueprint
            unzip_file(model_file, model_dir)

            # Delete the model zip file
            delete_file(model_file)

            # Rename the _model.py
            old_model = f'{app_path + sep}models{sep}_model.py'
            new_model = f'{app_path + sep}models{sep + model}.py'
            rename_file(old_model, new_model)

            # Update the model blue print
            replace_file_string(new_model, 'ModelName', model)
            replace_file_string(new_model, '_table_name', snake_case(model))

            # Update the _models.py
            models_file = f'{app_path + sep}models{sep}_models.py'

            models_data = f"""    '{model}',\n"""
            models_data += """)#do-not-change-me"""

            replace_file_line(models_file, ')#do-not-change-me', models_data)

            # Update the __init__.py
            init_file = f'{app_path + sep}models{sep}__init__.py'

            if len(models) == 0:
                replace_file_line(init_file, '...', '')

            init_data = f"""    from .{model} import {model}\n"""
            init_data += """    #do-not-change-me\n"""

            replace_file_line(init_file, '#do-not-change-me', init_data)

            # Print the result
            print('- The new model created successfully!')
            time.sleep(0.1)
        
        # Handle errors
        except NameError as e:
            print(e)


    ##
    # @desc delete_model method for removing an existing model
    ##
    def delete_model(self):
        # Prompt for model name
        while True:
            model = input("Model Name: ")

            # Check model name
            if model_name(model)['result']:
                # Model not exists
                if not model in models:
                    print(f'- The "{model}" doesn\'t exist!')

                # Model exists
                else:
                    break

            # Print the error
            else:
                print(model_name(model)['message'])
        
        # Alert the user for data loss
        alert = '''WARNING! You will loose the following data perminantly:\n'''
        alert += '''----------------------------------------------------------\n'''
        alert += f'''{app_path + sep}models{sep + model}.py\n'''
        alert += f'''----------------------------------------------------------'''
        
        # Print the alert
        print(alert)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            # Begin the process
            try:
                print('Removing the model...')
                time.sleep(0.1)

                # Delete the model module
                model_file = f'{app_path + sep}models{sep + model}.py'
                delete_file(model_file)

                # Update the _models.py
                models_file = f'{app_path + sep}models{sep}_models.py'
                replace_file_line(models_file, f"'{model}',", '')

                # Update the __init__.py
                init_file = f'{app_path + sep}models{sep}__init__.py'

                if len(models) == 1:
                    replace_file_line(init_file, f'from .{model} import {model}', '    ...\n')
                else:
                    replace_file_line(init_file, f'from .{model} import {model}', '')

                # Print the result
                print('- The model deleted successfully!')
                time.sleep(0.1)

            # Handle errors
            except NameError as e:
                print(e)

        # Rejected
        else:
            print('- The operation canceled!')
            exit()


    ##
    # @desc create_form method for creating new form
    ##
    def create_form(self):
        # Prompt for app name
        while True:
            app = input("App Name: ")

            # Check app name
            if app_name(app)['result']:
                # App not exists
                if not app_exists(app)['result']:
                    print(f'- The "{app}" doesn\'t exist!')
                    time.sleep(0.1)

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(app)['message'])
                time.sleep(0.1)

        # Fetch registered forms for the app
        forms_module = importlib.import_module(f'forms.{app}._forms')
        forms = getattr(forms_module, "forms")
        
        # Prompt for form name
        while True:
            form = input("Form Name: ")

            # Check form name
            if form_name(form)['result']:
                # Form exists
                if form in forms:
                    print(f'- The "{form}" already exist!')

                # Form not exists
                else:
                    break

            # Print the error
            else:
                print(form_name(form)['message'])

        # Begin the process
        try:
            print('Creating the new form...')
            time.sleep(0.1)

            # Form blueprint
            form_blueprint = f'{aurora_path + sep}blueprints{sep}form.zip'
            form_file = f'{app_path + sep}forms{sep + app + sep}form.zip'
            form_dir = f'{app_path + sep}forms{sep + app + sep}'
            
            # Copy the form blueprint
            copy_file(form_blueprint, form_file)

            # Unzip the form blueprint
            unzip_file(form_file, form_dir)

            # Delete the forms zip file
            delete_file(form_file)

            # Rename the _form.py
            old_form = f'{app_path + sep}forms{sep + app + sep}_form.py'
            new_form = f'{app_path + sep}forms{sep + app + sep + form}.py'
            rename_file(old_form, new_form)

            # Update the form blue print
            replace_file_string(new_form, 'FormName', form)

            # Update the _forms.py
            forms_file = f'{app_path + sep}forms{sep + app + sep}_forms.py'

            forms_data = f"""    '{form}',\n"""
            forms_data += """)#do-not-change-me"""

            replace_file_line(forms_file, ')#do-not-change-me', forms_data)

            # Update the __init__.py
            init_file = f'{app_path + sep}forms{sep + app + sep}__init__.py'

            if len(forms) == 0:
                replace_file_line(init_file, '...', '')

            init_data = f"""    from .{form} import {form}\n"""
            init_data += """    #do-not-change-me\n"""

            replace_file_line(init_file, '#do-not-change-me', init_data)

            # Print the result
            print('- The new form created successfully!')
            time.sleep(0.1)
        
        # Handle errors
        except NameError as e:
            print(e)


    ##
    # @desc delete_form method for removing an existing form
    ##
    def delete_form(self):
        # Prompt for app name
        while True:
            app = input("App Name: ")

            # Check app name
            if app_name(app)['result']:
                # App not exists
                if not app_exists(app)['result']:
                    print(f'- The "{app}" doesn\'t exist!')
                    time.sleep(0.1)

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(app)['message'])
                time.sleep(0.1)

        # Fetch registered forms for the app
        forms_module = importlib.import_module(f'forms.{app}._forms')
        forms = getattr(forms_module, "forms")
        
        # Prompt for form name
        while True:
            form = input("Form Name: ")

            # Check form name
            if form_name(form)['result']:
                # Form not exists
                if not form in forms:
                    print(f'- The "{form}" doesn\'t exist!')

                # Form exists
                else:
                    break

            # Print the error
            else:
                print(form_name(form)['message'])
        
        # Alert the user for data loss
        alert = '''WARNING! You will loose the following data perminantly:\n'''
        alert += '''----------------------------------------------------------\n'''
        alert += f'''{app_path + sep}forms{sep + app + sep + form}.py\n'''
        alert += f'''----------------------------------------------------------'''
        
        # Print the alert
        print(alert)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            # Begin the process
            try:
                print('Removing the form...')
                time.sleep(0.1)

                # Delete the form module
                form_file = f'{app_path + sep}forms{sep + app + sep + form}.py'
                delete_file(form_file)

                # Update the _forms.py
                forms_file = f'{app_path + sep}forms{sep + app + sep}_forms.py'
                replace_file_line(forms_file, f"'{form}',", '')

                # Update the __init__.py
                init_file = f'{app_path + sep}forms{sep + app + sep}__init__.py'

                if len(forms) == 1:
                    replace_file_line(init_file, f'from .{form} import {form}', '    ...\n')
                else:
                    replace_file_line(init_file, f'from .{form} import {form}', '')

                # Print the result
                print('- The form deleted successfully!')
                time.sleep(0.1)

            # Handle errors
            except NameError as e:
                print(e)

        # Rejected
        else:
            print('- The operation canceled!')
            exit()


    ##
    # @desc check_db method for checking the database for existence and so on
    ##
    def check_db(self):
        # Check the database
        CLI.check_database(pattern="check")

        # Chech for migrations
        if not CLI.migrate_database(pattern="check"):
            # Check the database for repairs
            CLI.repair_database(pattern="check")

        # Exit the program
        exit()


    ##
    # @desc init_db method for initializing the database for the first time
    ##
    def init_db(self):
        # Check the database
        CLI.check_database(pattern="init")

        # Initialize the database
        CLI.initialize_database(pattern="init")

        # Exit the program
        exit()


    ##
    # @desc Migrates the database changes
    ##
    def migrate_db(self):
        # Check the database
        CLI.check_database(pattern="migrate")

        # Migrate the changes
        CLI.migrate_database(pattern="migrate")

        # Exit the program
        exit()


    ##
    # @desc Repair the database (rename the columns)
    ##
    def repair_db(self):
        # Check the database
        CLI.check_database(pattern="repair")

        # Chech for migrations
        if not CLI.migrate_database(pattern="repair"):
            CLI.repair_database(pattern="repair")

        # Exit the program
        exit()


    ##
    # @desc Resets the database based on the current models and removes previous migrations
    ##
    def reset_db(self):
        # Check the database
        CLI.check_database(pattern="reset")
        
        # Reset the database
        # Alert the user for data loss
        alert = '''----------------------------------------------------------\n'''
        alert += '''DANGER!:\n'''
        alert += '''By resetting the database, you will lose all migrations and the data inserted into the database permanently.\n'''
        alert += '''----------------------------------------------------------'''
        
        print(alert)
        time.sleep(0.1)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            # Begin the process
            try:
                print('Reseting the database...')
                time.sleep(0.1)

                # Delete the migrations
                migrations = db.read(table="_migrations").all()
                for migration in migrations:
                    # Delete the migration files
                    delete_file(f"""{app_path + sep}_migrations{sep + migration['version']}.py""")

                # Drop the database
                db._delete_database(database, True)

                # Initialize the database
                CLI.initialize_database(pattern="reset")

                # Print the result
                print('- Database reseted successfully!')

            # Handle errors
            except NameError as e:
                print(e)

        # Rejected
        else:
            print('- The operation canceled!')
            exit()
