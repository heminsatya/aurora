################
# Dependencies #
################
import sys
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

        # The table name
        self.table = snake_case(caller_name)

        # The model primary key
        self.primary_key = None
        
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
    def column(datatype:str, unique:bool=False, not_null:bool=False, default:any=None, check:str=None, 
        related_to:str=None, on_update:str='CASCADE', on_delete:str='CASCADE'):

        # Import the configuration file
        config = importlib.import_module('config')

        # Debug mode
        debug = getattr(config, 'DEBUG')

        # Check required params
        if not datatype:
            # Check debug mode
            if debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['datatype']")

            # Return the result
            else:
                print('You must provide the required parameters.')
                return False

        # Result dictionary placeholder
        result = {}
        
        result['datatype'] = datatype
        result['unique'] = True if unique == True else False
        result['not_null'] = True if not_null == True else False
        result['default'] = default if default != None else None
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
    # CAUTION! Use this methods only in developement.
    #
    # @desc Checks if a database (file - SQLite) exists
    #
    # @param database: str -- *Required database name (file - SQLite)
    #
    # @return bool -- Query result
    ##
    def _exist_database(self, *class_args, **class_kwargs):
        return Database._exist_database(self, *class_args, **class_kwargs)


    ##
    # @desc Insert single row
    #
    # @param data: dict -- *Required data (ex. {"username": "john-doe", "password": "123456"})
    # 
    # @return int -- Last inserted id as query result on success
    # @return False: bool -- As query result on error
    ##
    def create(self, data:dict):
        return Database.create(self, table=self.table, data=data)


    ##
    # @desc Insert multi rows
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
    # @desc Select rows
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
    # *CAUTION! If you ignore the 'where' parameter, it may updates the columns for all records!
    #
    # @desc Update row(s)
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
    # @desc Delete row(s)
    #
    # @param table: str -- *Required Table name (ex. "users")
    # @param where: dict -- Optional (*WARNING!) WHERE statement (ex. {"id": "2", "username": "admin"})
    # @param confirm: bool -- Required|Optional confirm (if not where it will be Required)
    #
    # @return bool -- Query result
    ##
    def delete(self, where:dict={}, confirm:dict=False):
        return Database.delete(self, table=self.table, where=where, confirm=confirm)

