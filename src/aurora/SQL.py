################
# Dependencies #
################
import os
import re
import platform
import importlib
from .connector import DatabaseAPI, DatabaseError
from .helpers import dict_factory, real_dict, check_file, delete_chars, delete_file


##################
# Database Class #
##################
##
# @desc Database Class for Python Database APIs sqlite3, psycopg2, mysql-connector-python
##
class Database:

    #################
    # Basic Methods #
    #################
    ##
    # @desc Constructor method
    #
    # @param database: str - *Required database name (file -- SQLite)
    # @param debug: bool - Optional debug mode
    #
    # @property conn: object - SQLite connection
    # @property cur: object - connection cursor
    # @param debug: str - The debug mode
    # @param table: str - The table name
    # @property config: module - the app config module
    ##
    def __init__(self):

        # Import the configuration file
        self.config = importlib.import_module('config')

        # Public properties
        self.conn = None
        self.cur = None
        self.sp_char = None
        self.debug = getattr(self.config, 'DEBUG')
        self.db_system = getattr(self.config, 'DB_SYSTEM')
        self.app_path = getattr(self.config, "ROOT_PATH")

        # Check platform system
        # Windows
        if platform.system() == 'Windows':
            self.url_div = '\\'

        # Linux, Mac
        else:
            self.url_div = '/'

        # Database config attributes
        self.host = None
        self.user = None
        self.password = None
        self.database = None
        self.port = None

        # SQLite Database
        if self.db_system == 'SQLite':
            # The special character
            self.sp_char = '?'

            # The database file
            self.database = getattr(self.config, "DB_CONFIG")['database']

            # Try to create a database Connection
            try:
                # Check database file name and extension
                if (not self.database or not check_file(self.database, '.db') and not check_file(self.database, '.sqlite') 
                    and not check_file(self.database, '.sqlite3')):

                    # Prepare error message
                    err = '''Database file name and/or extension is invalid!\n'''
                    err += '''Valid Name Characters: a-z, A-Z, _\n'''
                    err += '''Valid Extensions: .sqlite3, .sqlite, .db'''

                    # Check debug mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Return the result
                    else:
                        return False

                # Database exists
                if self._exist_database(database=self.database):
                    # Create a database connection
                    self.conn = DatabaseAPI.connect(self.database)

                    # Convert rows to list of dictionaries
                    self.conn.row_factory = dict_factory   # dict_factory | sqlite3.Row (needs query(...).keys() for keys)
                    
                    # Create the connection cursor
                    self.cur = self.conn.cursor()

                    # For test
                    # print("Database Connection Created!")

            # Catch error
            except DatabaseError as err:
                print(err)

        # PostgreSQL
        elif  self.db_system == 'PostgreSQL':
            # The special character
            self.sp_char = '%s'

            # The database configurations
            self.host = getattr(self.config, "DB_CONFIG")['host']
            self.user = getattr(self.config, "DB_CONFIG")['user']
            self.password = getattr(self.config, "DB_CONFIG")['password']
            self.database = getattr(self.config, "DB_CONFIG")['database']
            self.port = getattr(self.config, "DB_CONFIG")['port']

            # Try to create a database Connection
            try:
                # Database exists
                if self._exist_database(database=self.database):
                    # Create a database connection
                    self.conn = DatabaseAPI.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                    )

                # Database not exists
                else:
                    # Create a root database connection
                    self.conn = DatabaseAPI.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                    )
                
                # Create the connection cursor
                from .connector import DatabaseDict
                self.cur = self.conn.cursor(cursor_factory=DatabaseDict.DictCursor)     # DictCursor | RealDictCursor | NamedTupleCursor

                # For test
                # print("Database Connection Created!")

            # Catch error
            except DatabaseError as err:
            # except NameError as err:
                print(err)

        # MySQL
        elif  self.db_system =='MySQL':
            # The special character
            self.sp_char = '%s'

            # The database configurations
            self.host = getattr(self.config, "DB_CONFIG")['host']
            self.user = getattr(self.config, "DB_CONFIG")['user']
            self.password = getattr(self.config, "DB_CONFIG")['password']
            self.database = getattr(self.config, "DB_CONFIG")['database']

            # Try to create a database Connection
            try:
                # Database exists
                if self._exist_database(database=self.database):
                    # Create a database connection
                    self.conn = DatabaseAPI.connect(
                        host=self.host,
                        user=self.user,
                        password=self.password,
                        database=self.database
                    )

                # Database not exists
                else:
                    # Create a root database connection
                    self.conn = DatabaseAPI.connect(
                        host=self.host,
                        user=self.user,
                        password=self.password
                    )
                
                # Create the connection cursor
                self.cur = self.conn.cursor(dictionary=True, buffered=True)

                # For test
                # print("Database Connection Created!")

            # Catch error
            except DatabaseError as err:
                print(err)


    ##
    # @desc Destructor method
    ##
    def __del__(self):
        # Check the database connection
        if self.conn:
            # Commit query result
            self.conn.commit()

            # Close the connection
            self.conn.close()

            # For test
            # print("Database Connection Closed!")


    ##
    # @desc save method to save the changes manually
    ##
    def save(self):
        # Check the database connection
        if self.conn:
            try:
                # Commit query result
                self.conn.commit()

                return True

            except:
                return False


    ##
    # @desc close method to close the connection manually
    ##
    def close(self):
        # Check the database connection
        if self.conn:
            try:
                # Close the connection
                self.conn.close()
                
                return True

            except:
                return False


    ##
    # @desc query method
    #
    # @param sql: str -- *Required SQL statement (ex. "SELECT * FROM users")
    # @param data_bind: list -- Optional data to bind to the sql safely
    #
    # @var result: object -- Database query
    #
    # @return any
    ##
    def query(self, sql:str, data_bind:list=[]):

        # Check required params
        if not sql:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['sql']")

            # Return the result
            else:
                return False

        # Try to query to the database
        try:
            # Return the query result
            self.cur.execute(sql, data_bind)

            return self.cur

        # Catch error
        except DatabaseError as err:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(err)

            # Return the result
            else:
                return False


    #################
    # Exist Methods #
    #################
    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Checks if a column is a foreign key
    #
    # @param table: str -- *Required table name
    # @param col: str -- *Required column name
    # 
    # @var sql: str -- The sql statement
    # @var fk_fetch: dict -- The query for SQLite
    #
    # @return bool
    ##
    def _exist_fk(self, table:str, column:str):

        # Check required params
        if not table or not column:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column']")

            # Return the result
            else:
                return False

        # Prepare sql statements
        # SQLite
        if self.db_system == 'SQLite':
            # Prepare sql
            sql = f'PRAGMA foreign_key_list({table});'

            # Check foreign key
            fk_fetch = self.query(sql).fetchall()
            for x in fk_fetch:
                # Foreign key exists
                if column == x['from']:
                    return True

            # Foreign key not exists
            return False

        # PostgreSQL
        elif self.db_system == 'PostgreSQL':
            sql = f"""
                SELECT
                    tc.table_schema, 
                    tc.constraint_name, 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE 
                    tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='{table}' AND kcu.column_name='{column}';
            """
        
        # MySQL
        elif self.db_system == 'MySQL':
            # Prepare sql
            sql = f"""
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                COLUMN_NAME,
                CONSTRAINT_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            where 
                TABLE_SCHEMA = '{self.database}'
                AND TABLE_NAME = '{table}'
                AND COLUMN_NAME = '{column}'
                AND REFERENCED_TABLE_NAME IS NOT NULL;
            """

        # Check foreign key for PostgreSQL or MySQL
        # Foreign key exists
        if self.query(sql).fetchone():
            return True
        
        # Foreign key not exists
        else:
            return False


    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Checks if a column exists
    #
    # @param table: str -- *Required table name
    # @param column: str -- *Required column name
    # 
    # @var sql: str -- The sql statement
    #
    # @return bool
    ##
    def _exist_column(self, table:str, column:str):

        # Check required params
        if not table or not column:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column']")

            # Return the result
            else:
                return False

        # Prepare sql
        # SQLite
        if self.db_system == 'SQLite':
            # Prepare sql
            sql = f'''SELECT COUNT(*) AS {column} FROM pragma_table_info('{table}') WHERE name='{column}';'''
            
            # Return result (SQLite)
            # Column exists
            if self.query(sql).fetchone()[column]:
                return True

            # Column not exists
            else:
                return False

        # PostgreSQL
        elif self.db_system == 'PostgreSQL':
            sql = f'''SELECT column_name FROM information_schema.columns WHERE table_name='{table}' and column_name='{column}';'''

        # MySQL
        elif self.db_system == 'MySQL':
            # Prepare sql
            sql = f'''SHOW COLUMNS FROM `{table}` LIKE '{column}';'''
            
        # Return result (PostgreSQL or MySQL)
        # Column exists
        if self.query(sql).fetchone():
            return True

        # Column not exists
        else:
            return False


    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Checks if a table exist
    #
    # @param table: str -- *Required table name
    # 
    # @var sql: str -- The sql statement
    # @var cur: object - The custom connection cursor for PostgreSQL
    #
    # @return bool
    ##
    def _exist_table(self, table:str):
        
        # Check required params
        if not table:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table']")

            # Return the result
            else:
                return False

        # Prepare sql
        # SQLite
        if self.db_system == 'SQLite':
            # Prepare sql
            sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"

            # Table exists
            if self.query(sql).fetchone():
                return True
        
            # Table not exists
            else:
                return False
        
        # PostgreSQL or MySQL
        elif self.db_system == 'PostgreSQL':
            sql = f"SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{table}');"

            cur = self.conn.cursor()

            # Excecute the query
            cur.execute(sql)

            # Check Table existence
            for x in cur:
                # Table exists
                if x[0]:
                    return True
            
                # Table not exists
                else:
                    return False

        # MySQL
        elif self.db_system == 'MySQL':
            # Prepare sql
            sql = f"""SHOW TABLES LIKE '{table}';"""

            # Table exists
            if self.query(sql=sql).fetchall():
                return True
        
            # Table not exists
            else:
                return False


    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Checks if a database (file - SQLite) exists
    #
    # @param database: str -- *Required database name (file - SQLite)
    # 
    # @var sql: str -- The sql statement
    # @var conn: object - The custom database connection for MySQL and PostgreSQL
    # @var cur: object - The custom connection cursor for MySQL and PostgreSQL
    #
    # @return bool
    ##
    def _exist_database(self, database:str=None):

        # Check the required params
        if not database:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['database']")

            # Return the result
            else:
                return False

        # SQLite
        if self.db_system == 'SQLite':

            # Database exists
            if os.path.isfile(self.app_path + self.url_div + database):
                return True

            # Database not exists
            else:
                return False
        
        # PostgreSQL
        elif self.db_system == 'PostgreSQL':

            # Create a database connection
            conn = DatabaseAPI.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
            )
            
            # Create the connection cursor
            cur = conn.cursor()

            # Prepare sql
            sql = f"SELECT EXISTS(SELECT datname FROM pg_catalog.pg_database WHERE datname='{database}');"

            # Excecute the query
            cur.execute(sql)

            # Check database existence
            for x in cur:
                # Database exists
                if x[0]:
                    return True
            
                # Database not exists
                else:
                    return False
        
        # MySQL
        elif self.db_system == 'MySQL':

            # Create a database connection
            conn = DatabaseAPI.connect(
                host=self.host,
                user=self.user,
                password=self.password,
            )
            
            # Create the connection cursor
            cur = conn.cursor()

            # Prepare sql
            sql = f"SELECT EXISTS(SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{database}');"

            # Excecute the query
            cur.execute(sql)

            # Check database existence
            for x in cur:
                # Database exists
                if x[0]:
                    return True
            
                # Database not exists
                else:
                    return False


    ##################
    # Create Methods #
    ##################
    ##
    # @desc Inserts a single row into a table
    #
    # @param table: str -- *Required Table name (ex. "users")
    # @param data: dict -- *Required data (ex. {"username": "john-doe", "password": "123456"})
    #
    # @var sql: str -- The sql statement
    # @var data_bind: list -- Data binding against SQL Injection
    # @var data_key: list
    # @var data_value: list
    # @var sql_inserted: str -- SQL statement for the last inserted id
    #
    # @return int | bool -- Last inserted id on success | False on error
    ##
    def create(self, table:str, data:dict):
        # Check required params
        if not table or not data:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'data']")

            # Return the result
            else:
                return False

        # Default variables
        data_bind = []
        data_key = []
        data_value = []

        # Prepare data
        for key, value in data.items():
            data_key.append(key)
            data_value.append(self.sp_char)
            data_bind.append(value)

        data_key = ', '.join(data_key)
        data_value = ', '.join(data_value)

        # Check database System
        if self.db_system == 'PostgreSQL':
            insert_id = ' RETURNING id'
        else:
            insert_id = ''

        # Prepare sql statement
        sql = f'INSERT INTO {table} ({data_key}) VALUES({data_value}){insert_id}'

        # Return result
        if self.query(sql, data_bind):
            # Last inserted id sql
            # SQLite
            if self.db_system == 'SQLite':
                return self.cur.lastrowid
            
            # PostgreSQL
            elif self.db_system == 'PostgreSQL':
                return self.cur.fetchone()['id']
            
            # MySQL
            elif self.db_system == 'MySQL':
                return self.cur.lastrowid

        else:
            return False


    ##
    # @desc Inserts multi rows
    #
    # @param table: str -- *Required Table name (ex. "users")
    # @param data: list -- *Required data (ex. [{...}, {...}, ...])
    # 
    # @return int -- Last inserted id
    ##
    def create_multi(self, table:str, data:list):
        # Check required params
        if not table or not data:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'list']")

            # Return the result
            else:
                return False

        # Loop data
        i = 1
        for x in data:
            if i == len(data):
                return self.create(table=table, data=x)

            else:
                self.create(table=table, data=x)

            i += 1


    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Adds a foreign key to an existing column (MySQL and PostgreSQL)
    #
    # @param table: str -- *Required table name
    # @param column: str -- *Required column name
    # @param r_table: str -- *Required reference table name
    # @param r_column: str -- *Required reference column name
    # @param on_update: str -- Optional ON UPDATE statement
    # @param on_delete: str -- Optional ON DELETE statement
    # 
    # @var sql: str -- The sql statement
    # @var fk_symbol: str -- The foreign key symbol
    #
    # @return bool
    ##
    def _create_fk(self, table:str, column:str, r_table:str, r_column:str, on_update:str=None, on_delete:str=None):
        # Check the database system
        if not self.db_system == 'PostgreSQL' or not self.db_system == 'MySQL':
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception('The "_create_fk" method only works with PostgreSQL and MySQL!')

            # Return the result
            else:
                return False

        # Check required params
        if not table or not column or not r_table or not r_column:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column', 'r_table', 'r_column']")

            # Return the result
            else:
                return False

        # Tables not exist
        if not self._exist_table(table) or self._exist_table(r_table):
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" or "{r_table}" doesn\'t exist!')

            # Return the result
            else:
                return False

        # Columns not exists
        if not self._exist_column(table, column) or not self._exist_column(r_table, r_column):
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Column "{column}" or "{r_column}" doesn\'t exist!')

            # Return the result
            else:
                return False

        # Foreign key already exists
        if self._exist_fk(table, column):
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'The foreign key already exists!')

            # Return the result
            else:
                return False

        # Everything is OK
        # Foreign key symbol
        fk_symbol = f'fk_{table}_{r_table}'

        # ON UPDATE statement
        if on_update:
            on_update = f' ON UPDATE {on_update}'
        else:
            on_update = ''

        # ON DELETE statement
        if on_delete:
            on_delete = f' ON DELETE {on_delete}'
        else:
            on_delete = ''

        sql = f"""
            ALTER TABLE {table}
            ADD CONSTRAINT {fk_symbol}
            FOREIGN KEY ({column})
            REFERENCES {r_table}({r_column})
            {on_update + on_delete};
        """

        # Attempt to add the foreign key
        try:
            # Add the foreign key
            self.query(sql)

            # Return the result
            return True

        # Handle errors
        except NameError as err:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(err)

            # Return the result
            else:
                return False


    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Adds a new column
    #
    # @var sql: str -- The sql statement
    # @param table: str -- *Required table name
    # @param col_data: str -- *Required column and it's data
    #
    # @var table_existance: str -- SQL statement for sqlite_master
    #
    # @return bool
    ##
    def _create_column(self, table:str, column:str, datatype:str, constraints:str=None):

        # Check required params
        if not table or not column or not datatype:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column', 'datatype']")

            # Return the result
            else:
                return False

        # Check constraints
        if constraints:
            constraints = f' {constraints}'
        else:
            constraints = ''

        # Prepare sql statements
        sql = f'ALTER TABLE {table}\n'
        sql += f'ADD {column} {datatype + constraints};'

        # Table exists
        if self._exist_table(table):

            # Column not exists
            if not self._exist_column(table, column):
                # Add the column
                self.query(sql)

                # Return the result
                return True

            # Table exists
            else:
                # Check debug mode
                if self.debug:
                    # Raise error
                    raise Exception(f'Column "{column}" already exists!')

                # Return the result
                else:
                    return False

        # Table not exists
        else:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" doesn\'t exist!')

            # Return the result
            else:
                return False


    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Creates a table if not exists.
    #
    # @param table: str -- *Required table name
    # @param col_type: dict -- *Required column names and datatypes
    # @param primary_key: str -- Optional PRIMARY KEY column
    # @param unique: list -- Optional UNIQUE Constraint columns
    # @param not_null: list -- Optional NOT NULL Constraint columns
    # @param default: dict -- Optional DEFAULT Constraint columns
    # @param check: str -- Optional CHECK Constraint for the table
    # @param foreign_key: dict -- Optional FOREIGN KEY Constraints
    # @Syntax: foreign_key
    # {
    #   'user_id': {
    #       'r_table': 'users',
    #       'r_column': 'id',
    #       'on_update': RESTRICT | CASCADE | SET NULL | NO ACTION | SET DEFAULT,
    #       'on_delete': RESTRICT | CASCADE | SET NULL | NO ACTION | SET DEFAULT,
    #   },
    # }
    #
    # @var sql: str -- The sql statement
    # @var data_list: list -- SQL data as list
    # @var data_sql: str -- The sql data
    # @var table_existance: str -- SQL statement for sqlite_master
    # @var pk_col: str -- The PRIMARY KEY sql statement
    # @var unique_col: str -- The UNIQUE sql statement
    # @var null_col: str -- The NOT NULL sql statement
    # @var default_col: str -- The DEFAULT sql statement
    # @var check_col: str -- The CHECK sql statement
    # @var auto_increment: str -- The AUTO_INCREMENT sql statement for MySQL
    # @var r_table: str -- The reference table name for the foreign key
    # @var r_column: str -- The reference column name for the foreign key
    # @var fk_symbol: str -- The foreign key symbol for PostgreSQL and MySQL
    # @var on_update: str -- ON UPDATE statement for the foreign key
    # @var on_delete: str -- ON DELETE statement for the foreign key
    #
    # @return bool
    ##
    def _create_table(self, table:str, col_type:str, primary_key:str=None, unique:list=[], not_null:list=[], 
        default:dict={}, check:dict={}, foreign_key:dict={}):

        # Default variables
        data_list = []
        data_sql = ''
        
        # Check required params
        if not table or not col_type:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'col_type']")

            # Return the result
            else:
                return False

        # Columns and datatypes
        for key, value in col_type.items():
            pk_col = ' PRIMARY KEY' if key == primary_key else ''
            unique_col = ' UNIQUE' if key in unique else ''
            null_col = ' NOT NULL' if key in not_null else ''
            default_col = f' DEFAULT {default[key]}' if key in default else ''
            check_col = f' CHECK ({check[key]})' if key in check else ''

            # MySQL AUTO_INCREMENT
            if self.db_system == 'MySQL' and pk_col:
                pk_col += ' AUTO_INCREMENT'

            # PostgreSQL AUTO_INCREMENT
            if self.db_system == 'PostgreSQL' and pk_col:
                # data_list.append(f'{key} SERIAL')
                if not value.upper() == 'SMALLSERIAL' or not value.upper() == 'SERIAL' or not value.upper() == 'BIGSERIAL':
                    value = 'SERIAL'

            data_list.append(f'{key} {value.upper() + pk_col + unique_col + null_col + default_col + check_col}')

        # FOREIGN KEY
        if foreign_key:
            for key, value in foreign_key.items():
                
                # Reference table and column
                r_table = value['r_table']
                r_column = value['r_column']

                # Foreign key symbol
                fk_symbol = f'fk_{table}_{r_table}'

                # Foreign key on update and delete
                try:
                    on_update = value['on_update']
                    on_delete = value['on_delete']
                except:
                    on_update = None
                    on_delete = None

                if on_update:
                    on_update = f' ON UPDATE {on_update}'
                else:
                    on_update = ''

                if on_delete:
                    on_delete = f' ON DELETE {on_delete}'
                else:
                    on_delete = ''
                
                # SQLite
                if self.db_system == 'SQLite':
                    data_list.append(f'FOREIGN KEY ({key}) REFERENCES {r_table}({r_column}){on_update + on_delete}')

                # PostgreSQL or MySQL
                elif self.db_system == 'PostgreSQL' or self.db_system == 'MySQL':
                    data_list.append(f'CONSTRAINT {fk_symbol} FOREIGN KEY ({key}) REFERENCES {r_table}({r_column}){on_update + on_delete}')

        # Prepare sql data
        data_sql = ',\n    '.join(data_list)

        # Prepare final sql statements
        sql = f'''CREATE TABLE {table} (\n    '''
        sql += data_sql
        sql += '''\n);'''

        # Table not exists
        if not self._exist_table(table):
            # Create the table
            self.query(sql)

            # Return the result
            return True
            
        # Table exists
        else:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" already exists!')

            # Return the result
            else:
                return False


    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Creates a new database (file - SQLite)
    #
    # @param database: str -- *Required database name (file - SQLite)
    # 
    # @var sql: str -- The sql statement
    # @var err: str -- The error message for SQLite
    # @var conn: object -- The custom database connection for PostgreSQL and MySQL
    # @var cur: object -- The custom connection cursor for PostgreSQL and MySQL
    #
    # @return bool
    ##
    def _create_database(self, database:str=None):

        # Check the required params
        if not database:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['database']")

            # Return the result
            else:
                return False

        # Database already exists
        if self._exist_database(database=database):
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Database "{database}" already exists!')

            # Return the result
            else:
                return False

        # Database not exists
        else:
            # SQLite
            if self.db_system == 'SQLite':
            
                # Check database file name and extension
                if not check_file(database, '.db') and not check_file(database, '.sqlite') and not check_file(database, '.sqlite3'):

                    # Prepare error message
                    err = '''Database file name and/or extension is invalid!\n'''
                    err += '''Valid Names: A-Z, a-z, _\n'''
                    err += '''Valid Extensions: .sqlite3, .sqlite, .db'''

                    # Check debug mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Return the result
                    else:
                        return False
                
                # Everything is fine
                else:
                    # Attempt the process
                    try:
                        # Create the database
                        self.conn = DatabaseAPI.connect(database)

                        # Return the result
                        return True

                    # Handle the errors
                    except NameError:
                        # Check debug mode
                        if self.debug:
                            # Raise error
                            raise Exception('Cannot create the database!')

                        # Return the result
                        else:
                            return False

            # PostgreSQL
            elif self.db_system == 'PostgreSQL':
                # Close the global connection
                self.conn.close()

                # Create a database connection
                conn = DatabaseAPI.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                )

                # Attempt the process
                try:
                    # Prepare sql
                    sql = f'CREATE DATABASE {database};'

                    # Set the transaction to autocommit
                    conn.autocommit = True
                    
                    # Create the connection cursor
                    cur = conn.cursor()

                    # Excecute the sql
                    cur.execute(sql)

                    # Close the current connection
                    conn.close()

                    # Return the result
                    return True

                # Handle the errors
                except NameError as err:
                    # Check debug mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Return the result
                    else:
                        return False


            # MySQL
            elif self.db_system == 'MySQL':
                # Create a database connection
                conn = DatabaseAPI.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                )

                # Attempt the process
                try:
                    # Prepare sql
                    sql = f'CREATE DATABASE {database};'
                    
                    # Create the connection cursor
                    cur = conn.cursor()

                    # Excecute the sql
                    cur.execute(sql)

                    # Close the current connection
                    conn.close()

                    # Return the result
                    return True

                # Handle the errors
                except NameError as err:
                    # Check debug mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Return the result
                    else:
                        return False


    ################
    # Read Methods #
    ################
    ##
    # @desc Selects rows
    #
    # @param table: str -- *Required Table name (ex. "users")
    # @param cols: list -- Optional Columns (ex. ["id", "first_name", "last_name"])
    # @param where: dict -- Optional WHERE statement (ex. {"id": "2", "username": "admin"})
    # @param order_by: dict -- Optional ORDER BY statement (ex. {"id": "ASC", "date": "DESC"})
    # @param group_by: str -- Optional GROUP BY statement (ex. 'country')
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
    def read(self, table:str, cols:list=[], where:dict={}, order_by:dict={}, group_by:str=None, limit:int=None, offset:int=None):

        # Check required params
        if not table:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table']")

            # Return the result
            else:
                return False

        # The default variables
        data_bind = []
        where_sql = []
        order_by_sql = []

        # Check cols
        if cols:
            cols = ', '.join(cols)
        else:
            cols = '*'

        # Check where
        if where:
            for key, value in where.items():
                in_bind = []

                # Remove the Ineffective characters (#)
                key = delete_chars(key, '#')
        
                # Check patterns
                # Equal to (strict)
                if re.search('--equal$', key) or re.search('--e$', key):
                    key = key.replace('--equal', '')
                    key = key.replace('--e', '')
                    where_sql.append(key + '=' + self.sp_char)
                    data_bind.append(value)

                # Not equal to
                elif re.search('--not-equal$', key) or re.search('--ne$', key):
                    key = key.replace('--not-equal', '')
                    key = key.replace('--ne', '')
                    where_sql.append(key + '<>' + self.sp_char)
                    data_bind.append(value)

                # Greater than
                elif re.search('--greater-than$', key) or re.search('--gt$', key):
                    key = key.replace('--greater-than', '')
                    key = key.replace('--gt', '')
                    where_sql.append(key + '>' + self.sp_char)
                    data_bind.append(value)

                # Greater than or equal to
                elif re.search('--greater-equal$', key) or re.search('--ge$', key):
                    key = key.replace('--greater-equal', '')
                    key = key.replace('--ge', '')
                    where_sql.append(key + '>=' + self.sp_char)
                    data_bind.append(value)

                # Less than
                elif re.search('--less-than$', key) or re.search('--lt$', key):
                    key = key.replace('--less-than', '')
                    key = key.replace('--lt', '')
                    where_sql.append(key + '<' + self.sp_char)
                    data_bind.append(value)

                # Less than or equal to
                elif re.search('--less-equal$', key) or re.search('--le$', key):
                    key = key.replace('--less-equal', '')
                    key = key.replace('--le', '')
                    where_sql.append(key + '<=' + self.sp_char)
                    data_bind.append(value)

                # LIKE
                elif re.search('--like$', key) or re.search('--l$', key):
                    key = key.replace('--like', '')
                    key = key.replace('--l', '')
                    where_sql.append(key + ' LIKE ' + self.sp_char)
                    data_bind.append(value)
                    
                # NOT LIKE
                elif re.search('--not-like$', key) or re.search('--nl$', key):
                    key = key.replace('--not-like', '')
                    key = key.replace('--nl', '')
                    where_sql.append(key + ' NOT LIKE ' + self.sp_char)
                    data_bind.append(value)
                
                # BETWEEN
                elif re.search('--between$', key) or re.search('--b$', key):
                    key = key.replace('--between', '')
                    key = key.replace('--b', '')
                    where_sql.append(key + ' BETWEEN ' + self.sp_char + ' AND ' + self.sp_char)
                    data_bind.append(value[0])
                    data_bind.append(value[1])
                
                # NOT BETWEEN
                elif re.search('--not-between$', key) or re.search('--nb$', key):
                    key = key.replace('--not-between', '')
                    key = key.replace('--nb', '')
                    where_sql.append(key + ' NOT BETWEEN ' + self.sp_char + ' AND ' + self.sp_char)
                    data_bind.append(value[0])
                    data_bind.append(value[1])
                
                # IN
                elif re.search('--in$', key) or re.search('--i$', key):
                    key = key.replace('--in', '')
                    key = key.replace('--i', '')
                    for x in value:
                        in_bind.append(self.sp_char)
                        data_bind.append(x)

                    in_sql =','.join(in_bind)

                    where_sql.append(f'{key} IN ({in_sql})')
                
                # NOT IN
                elif re.search('--not-in$', key) or re.search('--ni$', key):
                    key = key.replace('--not-in', '')
                    key = key.replace('--ni', '')
                    for x in value:
                        in_bind.append(self.sp_char)
                        data_bind.append(x)

                    in_sql =','.join(in_bind)

                    where_sql.append(f'{key} NOT IN ({in_sql})')

                # Equal to (default)
                else:
                    where_sql.append(key + '=' + self.sp_char)
                    data_bind.append(value)

            # Prepare the where SQL
            where = ' WHERE '

            i = 0
            for x in where_sql:
                ch = ''

                if re.search('^or--', x) or re.search('^o--', x):
                    x = x.replace('or--', '')
                    x = x.replace('o--', '')
                    if i > 0:
                        ch = 'OR '

                    where_sql[i] = f'{ch + x}'
                
                elif re.search('^and--', x) or re.search('^a--', x):
                    x = x.replace('and--', '')
                    x = x.replace('a--', '')
                    if i > 0:
                        ch = 'AND '

                    where_sql[i] = f'{ch + x}'
                
                else:
                    if i > 0:
                        ch = 'AND '

                    where_sql[i] = f'{ch + x}'

                i += 1

            where += ' '.join(where_sql)

        else:
            where = ''

        # Check order_by
        if order_by:
            for key, value in order_by.items():
                order_by_sql.append(key + ' ' + value.upper())

            order_by = ' ORDER BY ' + ', '.join(order_by_sql)

        else:
            order_by = ''

        # Check group_by
        if group_by:
            group_by = f' GROUP BY {group_by}'
        else:
            group_by = ''

        # Check limit
        if limit:
            limit = f' LIMIT {limit}'
        else:
            limit = ''

        # Check offset
        if offset:
            offset = f' OFFSET {offset}'
        else:
            offset = ''

        # Prepare the sql statement
        sql = f'SELECT {cols} FROM {table + where + order_by + group_by + limit + offset}'

        # Return result
        return Read(self, sql, data_bind)


    ##################
    # Update Methods #
    ##################
    ##
    # *CAUTION! If you ignore the 'where' parameter, it may updates the columns for all records! (must confirm)
    #
    # @desc Updates row(s)
    #
    # @param table: str -- *Required Table name (ex. "users")
    # @param data: dict -- *Required data (ex. {"first_name": "John", "last_name": "Doe"})
    # @param where: dict -- Optional (*CAUTION!) WHERE statement (ex. {"id": "2", "username": "admin"})
    # @param confirm: bool -- Required|Optional confirm (if not where it will be Required)
    #
    # @var sql: str -- The sql statement
    # @var data_bind: list -- Data binding against SQL Injection
    # @var data_sql: list -- A placeholder for the update data
    # @var where_sql: list -- A placeholder for the WHERE clause
    # @var in_bind: list -- A placeholder IN operator
    # @var in_sql: str -- The sql statement for IN operator
    #
    # @return bool
    ##
    def update(self, table:str, data:dict={}, where:dict={}, confirm:bool=False):

        # Check the confirm if the where clase not set
        if not where and not confirm:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception('For update without the where clause you must confirm the command.')

            # Return the result
            else:
                return False

        # The default variables
        data_bind = []
        data_sql = []
        where_sql = []

        # Check required params
        if not table or not data:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['']")

            # Return the result
            else:
                return False

        # Prepare data
        for key, value in data.items():
            data_sql.append(key + '=' + self.sp_char)
            data_bind.append(value)

        data = ', '.join(data_sql)

        # Check where
        if where:
            for key, value in where.items():
                in_bind = []

                # Remove the Ineffective characters (#)
                key = delete_chars(key, '#')
        
                # Check patterns
                # Equal to (strict)
                if re.search('--equal$', key) or re.search('--e$', key):
                    key = key.replace('--equal', '')
                    key = key.replace('--e', '')
                    where_sql.append(key + '=' + self.sp_char)
                    data_bind.append(value)

                # Not equal to
                elif re.search('--not-equal$', key) or re.search('--ne$', key):
                    key = key.replace('--not-equal', '')
                    key = key.replace('--ne', '')
                    where_sql.append(key + '<>' + self.sp_char)
                    data_bind.append(value)

                # Greater than
                elif re.search('--greater-than$', key) or re.search('--gt$', key):
                    key = key.replace('--greater-than', '')
                    key = key.replace('--gt', '')
                    where_sql.append(key + '>' + self.sp_char)
                    data_bind.append(value)

                # Greater than or equal to
                elif re.search('--greater-equal$', key) or re.search('--ge$', key):
                    key = key.replace('--greater-equal', '')
                    key = key.replace('--ge', '')
                    where_sql.append(key + '>=' + self.sp_char)
                    data_bind.append(value)

                # Less than
                elif re.search('--less-than$', key) or re.search('--lt$', key):
                    key = key.replace('--less-than', '')
                    key = key.replace('--lt', '')
                    where_sql.append(key + '<' + self.sp_char)
                    data_bind.append(value)

                # Less than or equal to
                elif re.search('--less-equal$', key) or re.search('--le$', key):
                    key = key.replace('--less-equal', '')
                    key = key.replace('--le', '')
                    where_sql.append(key + '<=' + self.sp_char)
                    data_bind.append(value)

                # LIKE
                elif re.search('--like$', key) or re.search('--l$', key):
                    key = key.replace('--like', '')
                    key = key.replace('--l', '')
                    where_sql.append(key + ' LIKE ' + self.sp_char)
                    data_bind.append(value)
                    
                # NOT LIKE
                elif re.search('--not-like$', key) or re.search('--nl$', key):
                    key = key.replace('--not-like', '')
                    key = key.replace('--nl', '')
                    where_sql.append(key + ' NOT LIKE ' + self.sp_char)
                    data_bind.append(value)
                
                # BETWEEN
                elif re.search('--between$', key) or re.search('--b$', key):
                    key = key.replace('--between', '')
                    key = key.replace('--b', '')
                    where_sql.append(key + ' BETWEEN ' + self.sp_char + ' AND ' + self.sp_char)
                    data_bind.append(value[0])
                    data_bind.append(value[1])
                
                # NOT BETWEEN
                elif re.search('--not-between$', key) or re.search('--nb$', key):
                    key = key.replace('--not-between', '')
                    key = key.replace('--nb', '')
                    where_sql.append(key + ' NOT BETWEEN ' + self.sp_char + ' AND ' + self.sp_char)
                    data_bind.append(value[0])
                    data_bind.append(value[1])
                
                # IN
                elif re.search('--in$', key) or re.search('--i$', key):
                    key = key.replace('--in', '')
                    key = key.replace('--i', '')
                    for x in value:
                        in_bind.append(self.sp_char)
                        data_bind.append(x)

                    in_sql =','.join(in_bind)

                    where_sql.append(f'{key} IN ({in_sql})')
                
                # NOT IN
                elif re.search('--not-in$', key) or re.search('--ni$', key):
                    key = key.replace('--not-in', '')
                    key = key.replace('--ni', '')
                    for x in value:
                        in_bind.append(self.sp_char)
                        data_bind.append(x)

                    in_sql =','.join(in_bind)

                    where_sql.append(f'{key} NOT IN ({in_sql})')

                # Equal to (default)
                else:
                    where_sql.append(key + '=' + self.sp_char)
                    data_bind.append(value)

            # Prepare the where SQL
            where = ' WHERE '

            i = 0
            for x in where_sql:
                ch = ''

                if re.search('^or--', x) or re.search('^o--', x):
                    x = x.replace('or--', '')
                    x = x.replace('o--', '')
                    if i > 0:
                        ch = 'OR '

                    where_sql[i] = f'{ch + x}'
                
                elif re.search('^and--', x) or re.search('^a--', x):
                    x = x.replace('and--', '')
                    x = x.replace('a--', '')
                    if i > 0:
                        ch = 'AND '

                    where_sql[i] = f'{ch + x}'
                
                else:
                    if i > 0:
                        ch = 'AND '

                    where_sql[i] = f'{ch + x}'

                i += 1

            where += ' '.join(where_sql)

        else:
            where = ''

        # Prepare the sql statement
        sql = f'UPDATE {table} SET {data + where}'

        # Update was successfull
        if self.query(sql, data_bind):
            # Return result
            return True

        # Update failed
        else:
            # Return result
            return False


    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Updates a column
    #
    # @param table: str -- *Required table name
    # @param old_col: str -- *Required old column name
    # @param new_col: str -- *Required new column name
    # @param datatype: str -- *Required new column data
    # @param constraints: str -- Optional new column constraints
    # 
    # @var sql: str -- The sql statement
    # @var table_existance: str -- SQL statement for sqlite_master
    # @var recursion: bool -- For recursion the method
    #
    # @return bool
    ##
    def _update_column(self, table:str, old_col:str, new_col:str, datatype:str, constraints:str=None):

        # Check required params
        if not table  or not old_col or not new_col or not datatype:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'old_col', 'new_col', 'datatype']")

            # Return the result
            else:
                return False

        # Check the FOREIGN KEY
        if self._exist_fk(table=table, column=old_col):
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception('You cannot change a foreign key with "_update_column" method!')

            # Return the result
            else:
                return False

        # Check the column names
        if old_col == new_col:
            recursion = True
            new_col += '__temp'
        else:
            recursion = False

        # Fetch the old column data
        old_data = self.read(table=table, cols=['id', old_col]).all()

        # Table exists
        if self._exist_table(table):
            # Add the new column
            self._create_column(table=table, column=new_col, datatype=datatype, constraints=constraints)

            # Update new column data
            for x in old_data:
                self.update(table=table, data={new_col:x[old_col]}, where={'id':x['id']})

            # Commit the changes so far
            self.conn.commit()

            # Drop the old column
            self._delete_column(table=table, col=old_col, confirm=True)

            # Check the column names
            if recursion:
                # Recursion
                return self._update_column(table, old_col=new_col, new_col=old_col, datatype=datatype)

            # Return the result
            return True

        # Table not exists
        else:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" doesn\'t exist')

            # Return the result
            else:
                return False


    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Renames a table if exists
    #
    # @param old_table: str -- *Required table old name
    # @param new_table: str -- *Required table new name
    #
    # @var sql: str -- The sql statement
    # @var table_existance: str -- SQL statement for sqlite_master
    #
    # @return bool
    ##
    def _update_table(self, old_table:str, new_table:str):

        # Check required params
        if not old_table or not new_table:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['old_table', 'new_table']")

            # Return the result
            else:
                return False

        # Table exists
        if self._exist_table(old_table):
            # Prepare sql statements
            sql = f'ALTER TABLE {old_table}\n'
            sql += f'RENAME TO {new_table};'

            # Alter the table
            self.query(sql)

            # Return the result
            return True

        # Table not exists
        else:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{old_table}" doesn\'t exist')

            # Return the result
            else:
                return False


    ##################
    # Delete Methods #
    ##################
    ##
    # *WARNING! If you ignore the 'where' parameter, it will deletes all the records inside your table! (must confirm)
    #
    # @desc Deletes row(s)
    #
    # @param table: str -- *Required Table name (ex. "users")
    # @param where: dict -- Optional (*WARNING!) WHERE statement (ex. {"id": "2", "username": "admin"})
    # @param confirm: bool -- Required|Optional confirm (if not where it will be Required)
    #
    # @var sql: str -- The sql statement
    # @var data_bind: list -- Data binding against SQL Injection
    # @var where_sql: list -- A placeholder for the WHERE clause
    # @var in_bind: list -- A placeholder IN operator
    # @var in_sql: str -- The sql statement for IN operator
    #
    # @return bool
    ##
    def delete(self, table:str, where:dict={}, confirm:bool=False):
        
        # Check the confirm if the where clase not set
        if not where and not confirm:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception('For delete without the where clause you must confirm the command.')

            # Return the result
            else:
                return False

        # The default variables
        data_bind = []
        where_sql = []

        # Check required params
        if not table:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['']")

            # Return the result
            else:
                return False
        
        # Check where
        if where:
            for key, value in where.items():
                in_bind = []

                # Remove the Ineffective characters (#)
                key = delete_chars(key, '#')
        
                # Check patterns
                # Equal to (strict)
                if re.search('--equal$', key) or re.search('--e$', key):
                    key = key.replace('--equal', '')
                    key = key.replace('--e', '')
                    where_sql.append(key + '=' + self.sp_char)
                    data_bind.append(value)

                # Not equal to
                elif re.search('--not-equal$', key) or re.search('--ne$', key):
                    key = key.replace('--not-equal', '')
                    key = key.replace('--ne', '')
                    where_sql.append(key + '<>' + self.sp_char)
                    data_bind.append(value)

                # Greater than
                elif re.search('--greater-than$', key) or re.search('--gt$', key):
                    key = key.replace('--greater-than', '')
                    key = key.replace('--gt', '')
                    where_sql.append(key + '>' + self.sp_char)
                    data_bind.append(value)

                # Greater than or equal to
                elif re.search('--greater-equal$', key) or re.search('--ge$', key):
                    key = key.replace('--greater-equal', '')
                    key = key.replace('--ge', '')
                    where_sql.append(key + '>=' + self.sp_char)
                    data_bind.append(value)

                # Less than
                elif re.search('--less-than$', key) or re.search('--lt$', key):
                    key = key.replace('--less-than', '')
                    key = key.replace('--lt', '')
                    where_sql.append(key + '<' + self.sp_char)
                    data_bind.append(value)

                # Less than or equal to
                elif re.search('--less-equal$', key) or re.search('--le$', key):
                    key = key.replace('--less-equal', '')
                    key = key.replace('--le', '')
                    where_sql.append(key + '<=' + self.sp_char)
                    data_bind.append(value)

                # LIKE
                elif re.search('--like$', key) or re.search('--l$', key):
                    key = key.replace('--like', '')
                    key = key.replace('--l', '')
                    where_sql.append(key + ' LIKE ' + self.sp_char)
                    data_bind.append(value)
                    
                # NOT LIKE
                elif re.search('--not-like$', key) or re.search('--nl$', key):
                    key = key.replace('--not-like', '')
                    key = key.replace('--nl', '')
                    where_sql.append(key + ' NOT LIKE ' + self.sp_char)
                    data_bind.append(value)
                
                # BETWEEN
                elif re.search('--between$', key) or re.search('--b$', key):
                    key = key.replace('--between', '')
                    key = key.replace('--b', '')
                    where_sql.append(key + ' BETWEEN ' + self.sp_char + ' AND ' + self.sp_char)
                    data_bind.append(value[0])
                    data_bind.append(value[1])
                
                # NOT BETWEEN
                elif re.search('--not-between$', key) or re.search('--nb$', key):
                    key = key.replace('--not-between', '')
                    key = key.replace('--nb', '')
                    where_sql.append(key + ' NOT BETWEEN ' + self.sp_char + ' AND ' + self.sp_char)
                    data_bind.append(value[0])
                    data_bind.append(value[1])
                
                # IN
                elif re.search('--in$', key) or re.search('--i$', key):
                    key = key.replace('--in', '')
                    key = key.replace('--i', '')
                    for x in value:
                        in_bind.append(self.sp_char)
                        data_bind.append(x)

                    in_sql =','.join(in_bind)

                    where_sql.append(f'{key} IN ({in_sql})')
                
                # NOT IN
                elif re.search('--not-in$', key) or re.search('--ni$', key):
                    key = key.replace('--not-in', '')
                    key = key.replace('--ni', '')
                    for x in value:
                        in_bind.append(self.sp_char)
                        data_bind.append(x)

                    in_sql =','.join(in_bind)

                    where_sql.append(f'{key} NOT IN ({in_sql})')

                # Equal to (default)
                else:
                    where_sql.append(key + '=' + self.sp_char)
                    data_bind.append(value)

            # Prepare the where SQL
            where = ' WHERE '

            i = 0
            for x in where_sql:
                ch = ''

                if re.search('^or--', x) or re.search('^o--', x):
                    x = x.replace('or--', '')
                    x = x.replace('o--', '')
                    if i > 0:
                        ch = 'OR '

                    where_sql[i] = f'{ch + x}'
                
                elif re.search('^and--', x) or re.search('^a--', x):
                    x = x.replace('and--', '')
                    x = x.replace('a--', '')
                    if i > 0:
                        ch = 'AND '

                    where_sql[i] = f'{ch + x}'
                
                else:
                    if i > 0:
                        ch = 'AND '

                    where_sql[i] = f'{ch + x}'

                i += 1

            where += ' '.join(where_sql)

        else:
            where = ''

        # Prepare the sql statement
        sql = f'DELETE FROM {table + where}'

        # Deletion was successfull
        if self.query(sql, data_bind):
            # Return result
            return True

        # Deletion failed
        else:
            # Return result
            return False


    ##
    # CAUTION! Use this methods only in developement.
    #
    # @desc Drops a foreign key from an existing table (MySQL and PostgreSQL)
    #
    # @param table: str -- *Required table name
    # @param table: str -- *Required column name
    # @param fk_symbol: str -- *Required foreign key symbol
    # 
    # @var sql: str -- The sql statement
    #
    # @return bool
    ##
    def _delete_fk(self, table:str, column:str, fk_symbol:str, confirm:bool=False):
        # Check the database system
        if not self.db_system == 'PostgreSQL' or not self.db_system == 'MySQL':
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception('The "_delete_fk" method only works with PostgreSQL and MySQL!')

            # Return the result
            else:
                return False

        # Check required params
        if not table or not column or not fk_symbol or not confirm:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column', 'fk_symbol', 'confirm']")

            # Return the result
            else:
                return False

        # Tables not exist
        if not self._exist_table(table):
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" doesn\'t exist!')

            # Return the result
            else:
                return False

        # Foreign key not exists
        if not self._exist_fk(table, column):
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'The foreign key not exists!')

            # Return the result
            else:
                return False

        # Everything is OK
        # PostgreSQL
        if self.db_system == 'PostgreSQL':
            sql = f"""
                ALTER TABLE {table}
                DROP CONSTRAINT {fk_symbol};
            """
        
        elif self.db_system == 'MySQL':
            sql = f"""
                ALTER TABLE {table}
                DROP FOREIGN KEY {fk_symbol};
            """

        # Attempt to drop the foreign key
        try:
            # Drop the foreign key
            self.query(sql)

            # Return the result
            return True

        # Handle errors
        except NameError as err:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(err)

            # Return the result
            else:
                return False


    ##
    # DANGER! Be super careful. This method drops your column permanently.
    #
    # CAUTION! Use this methods only in developement.
    #
    # @desc Drops a column from a table
    #
    # @var sql: str -- The sql statement
    # @param table: str -- *Required table name
    # @param column: str -- *Required column name
    # @param confirm: bool -- *Required confirmation
    # 
    # @var table_existance: str -- SQL statement for sqlite_master
    #
    # @return bool
    ##
    def _delete_column(self, table:str, column:str, confirm:bool=False):

        # Check required params
        if not table or not column or not confirm:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column', 'confirm']")

            # Return the result
            else:
                return False


        # Check the FOREIGN KEY
        if self._exist_fk(table=table, column=column):
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception('You cannot drop a foreign key with "_delete_column" method!')

            # Return the result
            else:
                return False

        # Prepare sql statements
        sql = f'ALTER TABLE {table}\n'
        sql += f'DROP COLUMN {column};'

        # Table exists
        if self._exist_table(table):

            # Column exists
            if self._exist_column(table, column):
                # Drop the column
                self.query(sql)

                # Return the result
                return True

            # Column not exists
            else:
                # Check debug mode
                if self.debug:
                    # Raise error
                    raise Exception(f'Column "{column}" does\'nt exists!')

                # Return the result
                else:
                    return False

        # Table not exists
        else:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" doesn\'t exist')

            # Return the result
            else:
                return False


    ##
    # DANGER! Be super careful. This method drops your table permanently.
    #
    # CAUTION! Use this methods only in developement.
    #
    # @desc Drops a table if exists
    #
    # @param table: str -- *Required table name
    # @param confirm: bool -- *Required confirmation
    # 
    # @var sql: str -- The sql statement
    # @var table_existance: str -- SQL statement for sqlite_master
    #
    # @return bool
    ##
    def _delete_table(self, table:str, confirm:bool=False):

        # Check required params
        if not table or not confirm:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'confirm']")

            # Return the result
            else:
                return False

        # Prepare sql statements
        sql = f'DROP TABLE {table};'

        # Table exists
        if self._exist_table(table):
            # Drop the table
            self.query(sql)

            # Return the result
            return True
            
        else:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" doesn\'t exist')

            # Return the result
            else:
                return False


    ##
    # DANGER! Be super careful. This method drops your database permanently.
    #
    # CAUTION! Use this methods only in developement.
    #
    # @desc Drops a database (Removes a database file for SQLite)
    #
    # @param database: str -- *Required database name (file -- SQLite)
    # @param confirm: bool -- *Required confirmation
    # 
    # @var sql: str -- The sql statement
    # @var conn: object -- The custom database connection form PostgreSQL and MySQL
    # @var cur: object -- The custom connection cursor form PostgreSQL and MySQL
    #
    # @return bool
    ##
    def _delete_database(self, database:str=None, confirm:str=False):

        # Check the required params
        if not database or not confirm:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['database', 'confirm']")

            # Return the result
            else:
                return False

        # Database not exists
        if not self._exist_database(database=database):
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(f'Database "{database}" not exists!')

            # Return the result
            else:
                return False

        # Database exists
        else:
            # Close the global connection
            self.conn.close()

            # SQLite
            if self.db_system == 'SQLite':
                # Attempt the process
                try:
                    # Remove the database file
                    delete_file(self.app_path + self.url_div + database)

                    # Return the result
                    return True

                # Handle the errors
                except NameError as err:
                    # Check debug mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Return the result
                    else:
                        return False

            # PostgreSQL
            elif self.db_system == 'PostgreSQL':
                # Create a database connection
                conn = DatabaseAPI.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                )

                # Attempt the process
                try:
                    # Prepare sql
                    sql = f'DROP DATABASE {database};'

                    # Set the transaction to autocommit
                    conn.autocommit = True
                    
                    # Create the connection cursor
                    cur = conn.cursor()

                    # Excecute the sql
                    cur.execute(sql)

                    # Close the current connection
                    conn.close()

                    # Return the result
                    return True

                # Handle the errors
                except NameError as err:
                    # Check debug mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Return the result
                    else:
                        return False


            # MySQL
            elif self.db_system == 'MySQL':
                # Create a database connection
                conn = DatabaseAPI.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                )

                # Attempt the process
                try:
                    # Prepare sql
                    sql = f'DROP DATABASE {database};'
                    
                    # Create the connection cursor
                    cur = conn.cursor()

                    # Excecute the sql
                    cur.execute(sql)

                    # Close the current connection
                    conn.close()

                    # Return the result
                    return True

                # Handle the errors
                except NameError as err:
                    # Check debug mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Return the result
                    else:
                        return False


##############
# Read Class #
##############
##
# @desc Provides several methods for the read method of the Database class
##
class Read:
    ##
    # @desc Constructor method
    #
    # @param parent: type - The Database Class
    # @param sql: str - The sql query string
    # @param data_bind: list - The data to bind
    #
    # @property sql: str - the sql query string
    # @property data_bind: object - the data to bind
    # @property query: method - the query method of the Database class
    # @property regex: str - the regular expression for the select statement
    # @property col: str - the first column extracted from the match
    #
    # @var regex: str - the regular expression for the select statement
    # @var match: str - the regular expression match
    # @var cols: list - the columns list extracted from the match
    ##
    def __init__(self, parent, sql, data_bind):
        # Regular expression
        regex = 'SELECT.*?FROM'
        
        # Find the match
        match = re.search(regex, sql).group()

        # Extract column from the match
        cols = re.sub('SELECT ', '', match)
        cols = re.sub(' FROM', '', cols)
        cols = cols.split (',')

        # Class properties
        self.sql = sql
        self.data_bind = data_bind
        self.query = parent.query
        self.db_system = parent.db_system
        self.regex = regex
        self.col = cols[0]


    ##
    # @desc Fetches the first row
    #
    # @return dict
    ##
    def first(self):
        if self.all():
            return self.all()[0]
        else:
            return False

    ##
    # @desc Fetches the last row
    #
    # @return dict
    ##
    def last(self):
        if self.all()[self.count()-1]:
            return self.all()[self.count()-1]
        else:
            return False


    ##
    # @desc Fetches all the rows
    #
    # @return list
    ##
    def all(self):
        # PostgreSQL
        if self.db_system == 'PostgreSQL':
            return real_dict(self.query(self.sql, self.data_bind).fetchall())

        # SQLite or MySQL
        elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
            return self.query(self.sql, self.data_bind).fetchall()


    ##
    # @desc Counts the number of rows
    #
    # @return int
    ##
    def count(self):
        return len(self.all())


    ##
    # @desc Fetches the minimum of the first given column (must be of type int or float)
    #
    # @param option: int -- Optional -- 0(@return int|float) 1(@return dict) 2 (@return list)
    #
    # @return int|float|dict|list
    ##
    def min(self, option=0):
        # Prepare the sql query
        sql = re.sub(self.regex, f'SELECT min({self.col}) as {self.col} FROM', self.sql)

        # Return the first match as a dictionary
        if option == 1:
            # PostgreSQL
            if self.db_system == 'PostgreSQL':
                return real_dict(self.query(sql, self.data_bind).fetchall())[0]

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchone()

        # Return the matches as a list
        elif option == 2:
            # PostgreSQL
            if self.db_system == 'PostgreSQL':
                return real_dict(self.query(sql, self.data_bind).fetchall())

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchall()

        # Return the first match result as the number (default)
        else:
            return self.query(sql, self.data_bind).fetchone()[self.col]


    ##
    # @desc Fetches the maximum of the first given column (must be of type int or float)
    #
    # @param option: int -- Optional -- 0(@return int|float) 1(@return dict) 2 (@return list)
    #
    # @return int|float|dict|list
    ##
    def max(self, option=0):
        # Prepare the sql query
        sql = re.sub(self.regex, f'SELECT max({self.col}) as {self.col} FROM', self.sql)

        # Return the first match as a dictionary
        if option == 1:
            # PostgreSQL
            if self.db_system == 'PostgreSQL':
                return real_dict(self.query(sql, self.data_bind).fetchall())[0]

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchone()

        # Return the matches as a list
        elif option == 2:
            # PostgreSQL
            if self.db_system == 'PostgreSQL':
                return real_dict(self.query(sql, self.data_bind).fetchall())

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchall()

        # Return the first match result as the number (default)
        else:
            return self.query(sql, self.data_bind).fetchone()[self.col]


    ##
    # @desc Fetches the average of the first given column (must be of type int or float)
    #
    # @param option: int -- Optional -- 0(@return float) 1(@return dict)
    #
    # @return float
    ##
    def avg(self, option=0):
        # Prepare the sql query
        sql = re.sub(self.regex, f'SELECT avg({self.col}) as {self.col} FROM', self.sql)

        # Return the first match as a dictionary
        if option == 1:
            # PostgreSQL
            if self.db_system == 'PostgreSQL':
                return real_dict(self.query(sql, self.data_bind).fetchall())[0]

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchone()

        # Return the first match result as the number (default)
        else:
            return self.query(sql, self.data_bind).fetchone()[self.col]


    ##
    # @desc Fetches the summary of the first given column (must be of type int or float)
    #
    # @param option: int -- Optional -- 0(@return int|float) 1(@return dict)
    #
    # @return int|float
    ##
    def sum(self, option=0):
        # Prepare the sql query
        sql = re.sub(self.regex, f'SELECT sum({self.col}) as {self.col} FROM', self.sql)

        # Return the first match as a dictionary
        if option == 1:
            # PostgreSQL
            if self.db_system == 'PostgreSQL':
                return real_dict(self.query(sql, self.data_bind).fetchall())[0]

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchone()

        # Return the first match result as the number (default)
        else:
            return self.query(sql, self.data_bind).fetchone()[self.col]

