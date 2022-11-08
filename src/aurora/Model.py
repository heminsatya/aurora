################
# Dependencies #
################
import sys
import re
import pathlib
import importlib
from .helpers import snake_case
from .SQL import Database


###############
# Model Class #
###############
##
# @desc Instantiates the Database class of the Database API
##
class Model:
    ##
    # @desc Constructor method
    #
    # @property table: str -- The table name of the model
    #
    # @var caller_path: str -- The caller path
    # @var caller_file: str -- The caller file
    # @var caller_name: str -- The caller name (the model name)
    # @var Model: module -- The model module
    # @var Class: type -- The model class
    # @var attrs: dict -- The model class attributes
    ##
    def __init__(self):
        # Find information about the caller
        caller_path = sys._getframe().f_back.f_code.co_filename
        caller_file = pathlib.PurePath(caller_path).name
        caller_name = caller_file.replace('.py', '')

        # Model name
        self.model = caller_name

        # The table name
        self.table = snake_case(caller_name)

        # The model primary key
        self.primary_key = None

        # Repair the database (rename the columns)
        self.repair = {}
        
        # Instantiate the Database class
        Database.__init__(self)


    ##
    # @desc Destructor method
    ##
    def __del__(self):
        # Destruction method
        Database.__del__(self)


    ##
    # @desc column method - for generating sql column and its data
    # 
    # @param datatype: str -- *Required column datatype
    # @param primary_key: bool -- Optional column PRIMARY KEY constraint (False by default)
    # @param unique: bool -- Optional column UNIQUE constraint (False by default)
    # @param not_null: bool -- Optional column NOT NULL constraint (False by default)
    # @param default: any -- Optional column DEFAULT constraint (None by default)
    # @param check: str -- Optional column CHECK constraint (None by default)
    # @param foreign_key: str -- Optional column FOREIGN KEY constraint (None by default)
    # 
    # @var result: dict -- The result dictionary
    #
    # @return dict
    ##
    @staticmethod
    def column(datatype:str, size:str="md", scale:int=2, unique:bool=False, not_null:bool=False, default:any=None, check:str=None, 
        related_to:str=None, on_update:str='CASCADE', on_delete:str='CASCADE'):

        # Import the configuration file & its required attributes
        config = importlib.import_module('config')
        debug = getattr(config, 'DEBUG')
        safe_type = getattr(config, 'SAFE_TYPE')
        db_system = getattr(config, 'DB_SYSTEM')

        # Check required params
        if not datatype:
            alert = "You must provide the required parameters: ['datatype']"

            # Check debug mode
            if debug:
                # Raise error
                raise Exception(alert)

            # Return the result
            else:
                print(alert)
                return False

        # Safe type is True
        if safe_type:
            # Convert datatype to lowercase
            datatype = datatype.lower()

            # Safe datatypse
            safe_types = [
                'str', 
                'int', 
                'float', 
                'bool', 
                'date', 
                'time', 
                'datetime'
            ]

            # Safe sizes
            safe_sizes = [
                'xs', 
                'sm', 
                'md', 
                'lg', 
                'xl'
            ]

            # Check datatype
            if not datatype in safe_types:
                alert = 'Invalid datatype inserted!\n'
                alert += f'Valid safe datatypes are: {safe_types}'

                # Check debug mode
                if debug:
                    # Raise error
                    raise TypeError(alert)

                # Return the result
                else:
                    print(alert)
                    return False

            # Check size
            if not isinstance(size, str) or not size in safe_sizes:
                alert = 'Invalid size inserted!\n'
                alert += f'Valid sizes are: {safe_sizes}'

                # Check debug mode
                if debug:
                    # Raise error
                    raise TypeError(alert)

                # Return the result
                else:
                    print(alert)
                    return False

            # Check scale
            if not isinstance(scale, int) or scale < 1:
                    alert = 'Invalid scale inserted!\n'
                    alert += f'Parameter "scale" must be of type integer and greater than 0!'

                    # Check debug mode
                    if debug:
                        # Raise error
                        raise TypeError(alert)

                    # Return the result
                    else:
                        print(alert)
                        return False

            # Produce final datatype
            # str
            if datatype == "str":
                # Check DEFAULT for safe typing
                if not default == None and not re.match(r"^['].*.[']$", default):
                    default = f"""'{default}'"""
                #     # Prepare the alert message
                #     alert = f'''For "str" safe typing the DEFAULT constraint value must be wrapped in '...'.\n'''
                #     alert += f'''For example: default="'Hello World!'"'''
                    
                #     # Developer mode
                #     if debug:
                #         # Raise error
                #         raise Exception(alert)

                #     # Production mode
                #     else:
                #         print(alert)
                #         return False

                # Check database system
                if db_system == 'SQLite':
                    datatype = 'TEXT'                       # unlimitted characters

                elif db_system == 'MySQL':
                    datatypes = {
                        'xs': 'VARCHAR(50)',                # upto 50 characters
                        'sm': 'VARCHAR(500)',               # upto 500 characters
                        'md': 'VARCHAR(5000)',              # upto 5000 characters
                        'lg': 'TEXT',                       # upto 65535 characters (can't have a default value)
                        'xl': 'LONGTEXT'                    # unlimitted characters (can't have a default value)
                    }
                    datatype = datatypes[size]

                elif db_system == 'Postgres':
                    datatypes = {
                        'xs': 'VARCHAR(50)',                # upto 50 characters
                        'sm': 'VARCHAR(500)',               # upto 500 characters
                        'md': 'VARCHAR(5000)',              # upto 5000 characters
                        'lg': 'VARCHAR(65535)',             # upto 65535 characters
                        'xl': 'TEXT'                        # unlimitted characters
                    }
                    datatype = datatypes[size]

            # int
            elif datatype == "int":
                # Check DEFAULT for safe typing
                if not default == None and not isinstance(default, int):
                    # Prepare the alert message
                    alert = f'''For "int" safe typing the DEFAULT constraint value must be of type integer.\n'''
                    alert += f'For example: default=0'
                    
                    # Check debug mode
                    if debug:
                        # Raise error
                        raise Exception(alert)

                    # Return the result
                    else:
                        print(alert)
                        return False

                if db_system == 'SQLite':
                    datatype = 'INTEGER'                    # from 0 to 8 bytes depending on the value

                elif db_system == 'MySQL':
                    datatypes = {
                        'xs': 'TINYINT',                    # from -128 to 127
                        'sm': 'SMALLINT',                   # from -32768 to 32767
                        'md': 'MEDIUMINT',                  # from -8388608 to 8388607
                        'lg': 'INTEGER',                    # from -2147483648 to 2147483647
                        'xl': 'BIGINT'                      # from -2^63 to 2^63-1
                    }
                    datatype = datatypes[size]

                elif db_system == 'Postgres':
                    datatypes = {
                        'xs': 'SMALLINT',                   # from -32768 to 32767
                        'sm': 'SMALLINT',                   # from -32768 to 32767
                        'md': 'INTEGER',                    # from -2147483648 to 2147483647
                        'lg': 'BIGINT',                     # from -9223372036854775808 to 9223372036854775807
                        'xl': 'BIGINT'                      # from -9223372036854775808 to 9223372036854775807
                    }
                    datatype = datatypes[size]

            # float
            elif datatype == "float":
                # Check DEFAULT for safe typing
                if not default == None and not isinstance(default, float):
                    # Prepare the alert message
                    alert = f'''For "float" safe typing the DEFAULT constraint value must be of type float.\n'''
                    alert += f'For example: default=0.01'
                    
                    # Check debug mode
                    if debug:
                        # Raise error
                        raise Exception(alert)

                    # Return the result
                    else:
                        print(alert)
                        return False

                if db_system == 'SQLite':
                    datatype = 'REAL'                       # 8 bytes

                elif db_system == 'MySQL':
                    datatypes = {
                        'xs': f'DECIMAL(4, {scale})',       # from -99.99 to 99.99 (if scale=2)
                        'sm': f'DECIMAL(8, {scale})',       # from -999999.99 to 999999.99 (if scale=2)
                        'md': f'DECIMAL(12, {scale})',      # from -9999999999.99 to 9999999999.99 (if scale=2)
                        'lg': f'DECIMAL(16, {scale})',      # from -99999999999999.99 to 99999999999999.99 (if scale=2)
                        'xl': f'DECIMAL(20, {scale})',      # from -999999999999999999.99 to 999999999999999999.99 (if scale=2)
                    }
                    datatype = datatypes[size]

                elif db_system == 'Postgres':
                    datatypes = {
                        'xs': f'NUMERIC(4, {scale})',       # from -99.99 to 99.99 (if scale=2)
                        'sm': f'NUMERIC(8, {scale})',       # from -999999.99 to 999999.99 (if scale=2)
                        'md': f'NUMERIC(12, {scale})',      # from -9999999999.99 to 9999999999.99 (if scale=2)
                        'lg': f'NUMERIC(16, {scale})',      # from -99999999999999.99 to 99999999999999.99 (if scale=2)
                        'xl': f'NUMERIC(20, {scale})',      # from -999999999999999999.99 to 999999999999999999.99 (if scale=2)
                    }
                    datatype = datatypes[size]

            # bool
            elif datatype == "bool":
                # Check DEFAULT for safe typing
                if not default == None and not isinstance(default, bool):
                    # Prepare the alert message
                    alert = f'''For "bool" safe typing the DEFAULT constraint value must be of type bool.\n'''
                    alert += f'For example: default=True'
                    
                    # Check debug mode
                    if debug:
                        # Raise error
                        raise Exception(alert)

                    # Return the result
                    else:
                        print(alert)
                        return False

                if db_system == 'SQLite':
                    datatype = 'NUMERIC'

                elif db_system == 'MySQL' or db_system == 'Postgres':
                    datatype = 'BOOLEAN'
            
            # date, time, datetime
            elif datatype == "date" or datatype == "time" or datatype == "datetime":
                # Check DEFAULT for safe typing
                if not default == None and not isinstance(default, str):
                    # Prepare the alert message
                    alert = f'''For type safety, non-python datatypes "date", "time, and "datetime" DEFAULT constraint treated like string and must be wrapped in quotes.\n'''
                    alert += f'''For example: default="CURRENT_TIMESTAMP" or default="(datetime('now','localtime'))"'''
                    
                    # Check debug mode
                    if debug:
                        # Raise error
                        raise Exception(alert)

                    # Return the result
                    else:
                        print(alert)
                        return False

                if db_system == 'SQLite':
                    datatype = 'NUMERIC'                    # 8 bytes

                elif db_system == 'MySQL':
                    datatypes = {
                        'date': 'DATE',                     # YYYY-MM-DD
                        'time': 'TIME',                     # hh:mm:ss
                        'datetime': 'DATETIME',             # YYYY-MM-DD hh:mm:ss
                    }
                    datatype = datatypes[datatype]

                elif db_system == 'Postgres':
                    datatypes = {
                        'date': 'DATE',                     # YYYY-MM-DD
                        'time': 'TIME',                     # hh:mm:ss
                        'datetime': 'TIMESTAMP',            # YYYY-MM-DD hh:mm:ss
                    }
                    datatype = datatypes[datatype]

        # Check column params
        # datatype
        if not isinstance(datatype, str):
            alert = 'Parameter "datatype" must be of type "str"!'

            # Check debug mode
            if debug:
                # Raise error
                raise TypeError(alert)

            # Return the result
            else:
                print(alert)
                return False

        # unique
        if unique and not isinstance(unique, bool):
            alert = 'Parameter "unique" must be of type "bool"!'

            # Check debug mode
            if debug:
                # Raise error
                raise TypeError(alert)

            # Return the result
            else:
                print(alert)
                return False

        # not_null
        if not_null and not isinstance(not_null, bool):
            alert = 'Parameter "not_null" must be of type "bool"!'

            # Check debug mode
            if debug:
                # Raise error
                raise TypeError(alert)

            # Return the result
            else:
                print(alert)
                return False

        # CHECK constraint
        if check and not isinstance(check, str):
            alert = 'Parameter "check" must be of type "str"!'

            # Check debug mode
            if debug:
                # Raise error
                raise TypeError(alert)

            # Return the result
            else:
                print(alert)
                return False

        # related_to
        if related_to and not isinstance(related_to, str):
            alert = 'Parameter "related_to" must be of type "str"!'

            # Check debug mode
            if debug:
                # Raise error
                raise TypeError(alert)

            # Return the result
            else:
                print(alert)
                return False

        #  Check on_update and on_delete
        if on_update or on_delete:
            valid_rel = ['RESTRICT', 'CASCADE', 'SET NULL', 'NO ACTION', 'SET DEFAULT']

            if not on_update.upper() in valid_rel or not on_delete.upper() in valid_rel:
                # Prepare the alert message
                alert = f'''The "on_update" and/or "on_delete" parameters are invalid!\n'''
                alert += f'Valid characters are: {valid_rel}'
                
                # Check debug mode
                if debug:
                    # Raise error
                    raise TypeError(alert)

                # Return the result
                else:
                    print(alert)
                    return False

        # Result dictionary placeholder
        result = {}
        
        result['datatype'] = datatype.upper()
        result['unique'] = True if unique else False
        result['not_null'] = True if not_null else False
        result['default'] = default if not default == None else None
        result['check'] = check if check else None

        # Foreign key
        result['related_to'] = related_to if related_to else None
        result['on_update'] = on_update if related_to and on_update else None
        result['on_delete'] = on_delete if related_to and on_delete else None

        return result


    ##
    # @desc query method
    #
    # @param sql: str -- *Required SQL statement (ex. "SELECT * FROM users")
    #
    # @var result: object -- Database query
    #
    # @return any -- Query result
    ##
    def query(self, *class_args, **class_kwargs):
        return Database.query(self, *class_args, **class_kwargs)


    ##
    # @desc save method to save the changes manually
    ##
    def save(self):
        return Database.save(self)


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Checks if a column exists
    #
    # @return bool
    ##
    def _exist_column(self, *class_args, **class_kwargs):
        return Database._exist_column(self, *class_args, **class_kwargs)


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Checks if a table exist
    #
    # @return bool
    ##
    def _exist_table(self, *class_args, **class_kwargs):
        return Database._exist_table(self, *class_args, **class_kwargs)


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Checks if a database (file - SQLite) exists
    #
    # @return bool -- Query result
    ##
    def _exist_database(self, *class_args, **class_kwargs):
        return Database._exist_database(self, *class_args, **class_kwargs)


    ##
    # @desc Inserts single row
    #
    # @param data: dict -- *Required data (ex. {"username": "john-doe", "password": "123456"})
    # 
    # @return int -- Last inserted id as query result on success
    # @return False: bool -- As query result on error
    ##
    def create(self, data:dict):
        return Database.create(self, table=self.table, data=data)


    ##
    # @desc Inserts multi rows
    #
    # @param table: str -- *Required Table name (ex. "users")
    # @param data: list -- *Required data (ex. [{...}, {...}, ...])
    #
    # @return int -- Last inserted id
    ##
    def create_multi(self, data:list):
        # Loop data
        i = 1
        for x in data:
            if i == len(data):
                return self.create(data=x)

            else:
                self.create(data=x)

            i += 1


    ##
    # @desc Selects rows
    #
    # @param cols: list -- Optional Columns (ex. ["id", "first_name", "last_name"])
    # @param where: dict -- Optional WHERE statement (ex. {"id": "2", "username": "admin"})
    # @param order_by: dict -- Optional ORDER BY statement (ex. {"id": "ASC", "date": "DESC"})
    # @param limit: int -- Optional LIMIT statement (ex. "10")
    #
    # @return class: type -- Query result
    ##
    def read(self, cols:list=[], where:dict={}, order_by:dict={}, group_by:str=None, limit:int=None, offset:int=None):
        return Database.read(self, table=self.table, cols=cols, where=where, order_by=order_by, group_by=group_by, 
                              limit=limit, offset=offset)


    ##
    # @desc Joins tables
    #
    # @param Models: list -- *Required foreign tables (ex. ["Model1", "Model2"])
    # @param cols: list -- Optional Columns (ex. ["Model.*", "Model1.name", "Model2.address"])
    #
    # @param join_stmt: str -- The join statement:
    #        SQLite: INNER JOIN, LEFT JOIN, CROSS JOIN (Learn More: https://www.sqlitetutorial.net/sqlite-join/)
    #        MySQL: INNER JOIN, LEFT JOIN, RIGHT JOIN, CROSS JOIN (Learn More: https://www.w3schools.com/mysql/mysql_join.asp)
    #        Postgres: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN (Learn More: https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-joins/)
    #        JOIN vs INNER JOIN: https://stackoverflow.com/questions/565620/difference-between-join-and-inner-join
    #
    # @param where: dict -- Optional WHERE statement (ex. {"Model.id": "2", "Model1.name": "John"})
    # @param order_by: dict -- Optional ORDER BY statement (ex. {"Model.id": "ASC", "Model.date": "DESC"})
    # @param group_by: str -- Optional GROUP BY statement (ex. 'Model.country')
    # @param limit: int -- Optional LIMIT statement (ex. "10")
    # @param offset: int -- Optional OFFSET statement (ex. "10")
    #
    # @var sql: str -- The sql statement
    # @var data_bind: list -- Data binding against SQL Injection
    # @var where_sql: list -- A placeholder for the WHERE clause
    # @var order_by_sql: list -- A placeholder for the ORDER BY clause
    # @var in_bind: list -- A placeholder IN operator
    # @var in_sql: str -- The sql statement for IN operator
    #
    # @return class: type
    ##
    def join(self, models:list, cols:list=[], join_stmt:str='INNER JOIN', where:dict={}, order_by:dict={}, group_by:str=None, limit:int=None, offset:int=None):
        # Find last last migration
        migration = Database.read(self, '_migrations').last()

        # Migration module
        module = importlib.import_module(f'_migrations.{migration["version"]}')

        # Main model info
        m_model = getattr(module, self.model)
        m_foreign_key = m_model['foreign_key']

        # Foreign tables data
        f_tables = []
        p_keys = []
        f_keys = []

        # Find foreign models info
        for i in range(len(models)):
            f_model = getattr(module, models[i])

            # Update foreign tables data
            f_tables.append(f_model['table'])
            p_keys.append(f_model['primary_key'])

            # Find main model f_keys
            for key, value in m_foreign_key.items():
                if value['r_table'] == f_model['table']:
                    f_keys.append(key)

        # Refine cols
        r_col = []
        for x in cols:
            try:
                r_col.append(getattr(module, x.split('.')[0])['table'] + '.' + x.split('.')[1])
            except:
                r_col.append(x)

        # Refine where
        r_where = {}
        for key, value in where.items():
            try:
                if len(key.split('.')[0].split('--')) > 1:
                    r_where[key.split('.')[0].split('--')[0] + '--' + getattr(module, key.split('.')[0].split('--')[1])['table'] + '.' + key.split('.')[1]] = value
                    pass
                else:
                    r_where[getattr(module, key.split('.')[0])['table'] + '.' + key.split('.')[1]] = value
            except:
                r_where[key] = value

        # Refine order_by
        r_order_by = {}
        for key, value in order_by.items():
            try:
                if len(key.split('.')[0].split('--')) > 1:
                    r_order_by[key.split('.')[0].split('--')[0] + '--' + getattr(module, key.split('.')[0].split('--')[1])['table'] + '.' + key.split('.')[1]] = value
                    pass
                else:
                    r_order_by[getattr(module, key.split('.')[0])['table'] + '.' + key.split('.')[1]] = value
            except:
                r_order_by[key] = value

        # Refine group_by
        try:
            group_by = getattr(module, group_by.split('.')[0])['table'] + '.' + group_by.split('.')[1]
        except:
            pass
                
        # Return the results
        return Database.join(self, table=self.table, f_keys=f_keys, f_tables=f_tables, p_keys=p_keys, cols=r_col, join_stmt=join_stmt, 
                             where=r_where, order_by=r_order_by, group_by=group_by, limit=limit, offset=offset)


    ##
    # *CAUTION! If you ignore the 'where' parameter, it may updates the columns for all records!
    #
    # @desc Updates row(s)
    #
    # @param data: dict -- *Required data (ex. {"first_name": "John", "last_name": "Doe"})
    # @param where: dict -- Optional (*CAUTION!) WHERE statement (ex. {"id": "2", "username": "admin"})
    #
    # @return bool -- Query result
    ##
    def update(self, data:dict, where:dict={}, confirm:bool=False):
        return Database.update(self, table=self.table, data=data, where=where, confirm=confirm)


    ##
    # *WARNING! If you ignore the 'where' parameter, it will deletes all the records inside your table! (must confirm)
    #
    # @desc Deletes row(s)
    #
    # @param table: str -- *Required Table name (ex. "users")
    # @param where: dict -- Optional (*WARNING!) WHERE statement (ex. {"id": "2", "username": "admin"})
    # @param confirm: bool -- Required|Optional confirm (if not where it will be Required)
    #
    # @return bool -- Query result
    ##
    def delete(self, where:dict={}, confirm:dict=False):
        return Database.delete(self, table=self.table, where=where, confirm=confirm)

