################
# Dependencies #
################
import os
import re
import platform
import importlib
from .connector import DatabaseAPI, DatabaseError
from .helpers import dict_factory, real_dict, check_file, delete_chars, clean_key, delete_file


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
    # @param {str}  database - Required database name (file -- SQLite)
    # @param {bool} debug    - Optional debug mode
    #
    # @property {object} conn   - SQLite connection
    # @property {object} cur    - connection cursor
    # @property {str}    debug  - The debug mode
    # @property {module} config - the app config module
    ##
    def __init__(self, error:bool = True):

        # Import the configuration file
        self.config = importlib.import_module('config')

        # Public properties
        self.conn = None
        self.cur = None
        self.sp_char = None
        self.development = getattr(self.config, "DEVELOPMENT")
        self.debug = getattr(self.config, 'DEBUG') if error else False
        self.db_system = getattr(self.config, 'DB_SYSTEM')
        self.app_path = getattr(self.config, "ROOT_PATH")

        # Check platform system
        # Windows
        if platform.system() == 'Windows':
            self.sep = '\\'

        # Unix
        else:
            self.sep = '/'

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

        # Postgres
        elif  self.db_system == 'Postgres':
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


    ##
    # @desc Destructor method
    ##
    def __del__(self):
        # Check the database connection
        if self.conn:
            try:
                # Commit query result
                self.conn.commit()

                # Close the connection
                self.conn.close()

            except:
                pass

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
    # @param {str}  sql       -- Required SQL statement (ex. "SELECT * FROM users")
    # @param {list} data_bind -- Optional data to bind to the sql safely
    #
    # @var result: object -- Database query
    #
    # @return {any}
    ##
    def query(self, sql:str, data_bind:list=[]):

        # Check required params
        if not sql:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['sql']")

            # Production mode
            else:
                print("You must provide the required parameters: ['sql']")
                return False

        # Try to query to the database
        try:
            # Return the query result
            self.cur.execute(sql, data_bind)

            return self.cur

        # Catch error
        except DatabaseError as err:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(err)

            # Production mode
            else:
                print(err)
                return False


    #################
    # Exist Methods #
    #################
    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Checks if a column is a foreign key
    #
    # @param {str} table -- Required table name
    # @param {str} col   -- Required column name
    # 
    # @var {str} sql       -- The sql statement
    # @var {dict} fk_fetch -- The query for SQLite
    #
    # @return {bool}
    ##
    def _exist_fk(self, table:str, column:str):

        # Check development
        if not self.development:
            return True

        # Check required params
        if not table or not column:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'column']")
                return False

        # Prepare sql statements
        # SQLite
        if self.db_system == 'SQLite':
            # Prepare sql
            sql = f'''PRAGMA foreign_key_list('{table}');'''

            # Check foreign key
            fk_fetch = self.query(sql).fetchall()
            for x in fk_fetch:
                # Foreign key exists
                if column == x['from']:
                    return True

            # Foreign key not exists
            return False
        
        # MySQL
        elif self.db_system == 'MySQL':
            # Prepare sql
            sql = f'''
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
            '''

        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''
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
            '''

        # Check foreign key (Postgres and MySQL)
        # Foreign key exists
        if self.query(sql).fetchone():
            return True
        
        # Foreign key not exists
        else:
            return False


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Checks if a column exists
    #
    # @param {str} table  -- Required table name
    # @param {str} column -- Required column name
    # 
    # @var {str} sql -- The sql statement
    #
    # @return {bool}
    ##
    def _exist_column(self, table:str, column:str):

        # Check development
        if not self.development:
            return True

        # Check required params
        if not table or not column:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'column']")
                return False

        # Prepare sql
        # SQLite
        if self.db_system == 'SQLite':
            # Prepare sql
            sql = f'''SELECT COUNT(*) AS '{column}' FROM pragma_table_info('{table}') WHERE name='{column}';'''
            
            # Return result (SQLite)
            # Column exists
            if self.query(sql).fetchone()[column]:
                return True

            # Column not exists
            else:
                return False

        # MySQL
        elif self.db_system == 'MySQL':
            # Prepare sql
            sql = f'''SHOW COLUMNS FROM `{table}` LIKE '{column}';'''

        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''SELECT column_name FROM information_schema.columns WHERE table_name='{table}' and column_name='{column}';'''
            
        # Return result (Postgres and MySQL)
        # Column exists
        if self.query(sql).fetchone():
            return True

        # Column not exists
        else:
            return False


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Checks if a table exist
    #
    # @param {str} table -- Required table name
    # 
    # @var {str}    sql -- The sql statement
    # @var {object} cur - The custom connection cursor for Postgres
    #
    # @return {bool}
    ##
    def _exist_table(self, table:str):

        # Check development
        if not self.development:
            return True
        
        # Check required params
        if not table:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table']")
                return False

        # Prepare sql
        # SQLite
        if self.db_system == 'SQLite':
            # Prepare sql
            sql = f'''SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';'''

            # Table exists
            if self.query(sql).fetchone():
                return True
        
            # Table not exists
            else:
                return False

        # MySQL
        elif self.db_system == 'MySQL':
            # Prepare sql
            sql = f'''SHOW TABLES LIKE '{table}';'''

            # Table exists
            if self.query(sql=sql).fetchall():
                return True
        
            # Table not exists
            else:
                return False
        
        # Postgres 
        elif self.db_system == 'Postgres':
            sql = f'''SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{table}');'''

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


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Checks if a database (file - SQLite) exists
    #
    # @param {str} database -- Required database name (file - SQLite)
    # 
    # @var {str} sql     -- The sql statement
    # @var {object} conn -- The custom database connection for MySQL and Postgres
    # @var {object} cur  -- The custom connection cursor for MySQL and Postgres
    #
    # @return {bool}
    ##
    def _exist_database(self, database:str=None):

        # Check development
        if not self.development:
            return True

        # Check the required params
        if not database:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['database']")

            # Production mode
            else:
                print("You must provide the required parameters: ['database']")
                return False

        # SQLite
        if self.db_system == 'SQLite':

            # Database exists
            if os.path.isfile(self.app_path + self.sep + database):
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
            sql = f'''SELECT EXISTS(SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{database}');'''

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
        
        # Postgres
        elif self.db_system == 'Postgres':

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
            sql = f'''SELECT EXISTS(SELECT datname FROM pg_catalog.pg_database WHERE datname='{database}');'''

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
    # @param {str}  table -- Required Table name (ex. "users")
    # @param {dict} data  -- Required data (ex. {"username": "john-doe", "password": "123456"})
    #
    # @var {str}  sql          -- The sql statement
    # @var {list} data_bind    -- Data binding against SQL Injection
    # @var {list} data_key
    # @var {list} data_value
    # @var {str}  sql_inserted -- SQL statement for the last inserted id
    #
    # @return {int|bool} -- Last inserted id on success | False on error
    ##
    def create(self, table:str, data:dict):
        # Check required params
        if not table or not data:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'data']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'data']")
                return False

        # Default variables
        data_bind = []
        data_key = []
        data_value = []

        # Prepare sql statement
        # SQLite
        if self.db_system == 'SQLite':
            # Prepare data
            for key, value in data.items():
                data_key.append(f"'{key}'")
                data_value.append(self.sp_char)
                data_bind.append(value)

            data_key = ', '.join(data_key)
            data_value = ', '.join(data_value)

            sql = f'''INSERT INTO '{table}' ({data_key}) VALUES({data_value});'''
        
        # MySQL
        elif self.db_system == 'MySQL':
            # Prepare data
            for key, value in data.items():
                data_key.append(f'`{key}`')
                data_value.append(self.sp_char)
                data_bind.append(value)

            data_key = ', '.join(data_key)
            data_value = ', '.join(data_value)

            sql = f'''INSERT INTO `{table}` ({data_key}) VALUES({data_value});'''
        
        # Postgres
        elif self.db_system == 'Postgres':
            # Prepare data
            for key, value in data.items():
                data_key.append(f'"{key}"')
                data_value.append(self.sp_char)
                data_bind.append(value)

            data_key = ', '.join(data_key)
            data_value = ', '.join(data_value)

            sql = f'''INSERT INTO "{table}" ({data_key}) VALUES({data_value}) RETURNING id;'''

        # Return result
        if self.query(sql, data_bind):
            # Last inserted id sql
            # SQLite
            if self.db_system == 'SQLite':
                return self.cur.lastrowid
            
            # Postgres
            elif self.db_system == 'Postgres':
                result = self.cur.fetchone()

                # Check 'id' existence
                if self._exist_column(table=table, column='id'):
                    return result['id']
                else:
                    return result
            
            # MySQL
            elif self.db_system == 'MySQL':
                return self.cur.lastrowid

        else:
            return False


    ##
    # @desc Inserts multi rows
    #
    # @param {str}  table -- Required Table name (ex. "users")
    # @param {list} data  -- Required data (ex. [{...}, {...}, ...])
    # 
    # @return {int} -- Last inserted id
    ##
    def create_multi(self, table:str, data:list):
        # Check required params
        if not table or not data:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'data']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'data']")
                return False

        # Loop data
        i = 1
        for x in data:
            # Excecute the create query and return last inserted id
            if i == len(data):
                return self.create(table=table, data=x)

            # Excecute the create query
            else:
                self.create(table=table, data=x)

            i += 1


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Adds a foreign key to an existing column (MySQL and Postgres)
    #
    # @param {str} table     -- Required table name
    # @param {str} column    -- Required column name
    # @param {str} r_table   -- Required reference table name
    # @param {str} r_column  -- Required reference column name
    # @param {str} fk_symbol -- Optional foreign key symbol
    # @param {str} on_update -- Optional ON UPDATE statement
    # @param {str} on_delete -- Optional ON DELETE statement
    # 
    # @var {str} sql -- The sql statement
    #
    # @return {bool}
    ##
    def _create_fk(self, table:str, column:str, r_table:str, r_column:str, fk_symbol:str=None, on_update:str='CASCADE', on_delete:str='CASCADE'):
        
        # Check development
        if not self.development:
            return True

        # Check the development
        if not self.development:
            alert = '''----------------------------------------------------------\n'''
            alert += '''INFO!\n'''
            alert += '''This method is only available in development!\n'''
            alert += '''----------------------------------------------------------'''

            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check the database system
        if not self.db_system == 'Postgres' and not self.db_system == 'MySQL':
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception('The "create_fk" method only works with MySQL and Postgres!')

            # Production mode
            else:
                print('The "create_fk" method only works with MySQL and Postgres!')
                return False

        # Check required params
        if not table or not column or not r_table or not r_column:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column', 'r_table', 'r_column']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'column', 'r_table', 'r_column']")
                return False

        # Tables not exist
        if not self._exist_table(table) and self._exist_table(r_table):
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Tables "{table}" and/or "{r_table}" do not exist!')

            # Production mode
            else:
                print(f'Tables "{table}" and/or "{r_table}" do not exist!')
                return False

        # Columns not exists
        if not self._exist_column(table, column) or not self._exist_column(r_table, r_column):
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Columns "{column}" and/or "{r_column}" do not exist!')

            # Production mode
            else:
                print(f'Columns "{column}" and/or "{r_column}" do not exist!')
                return False

        # Foreign key already exists
        if self._exist_fk(table, column):
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception('The foreign key already exists!')

            # Production mode
            else:
                print('The foreign key already exists!')
                return False

        # Check on_update & on_delete
        if on_update or on_delete:
            valid_rel = ['RESTRICT', 'CASCADE', 'SET NULL', 'NO ACTION', 'SET DEFAULT']

            if not on_update.upper() in valid_rel or not on_delete.upper() in valid_rel:
                # Prepare the alert message
                alert = f'''The "on_update" and/or "on_delete" parameters are invalid!\n'''
                alert += f'Valid characters are: {valid_rel}'
                
                # Developer mode
                if self.debug:
                    # Raise error
                    raise TypeError(alert)

                # Production mode
                else:
                    print(alert)
                    return False

        # Everything is OK
        # Foreign key symbol
        if not fk_symbol:
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

        # MySQL
        if self.db_system == 'MySQL':
            sql = f'''
                ALTER TABLE `{table}`
                ADD CONSTRAINT `{fk_symbol}`
                FOREIGN KEY (`{column}`)
                REFERENCES `{r_table}`(`{r_column}`)
                {on_update + on_delete};
            '''

        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''
                ALTER TABLE "{table}"
                ADD CONSTRAINT "{fk_symbol}"
                FOREIGN KEY ("{column}")
                REFERENCES "{r_table}"("{r_column}")
                {on_update + on_delete};
            '''

        # Attempt to add the foreign key
        try:
            # Add the foreign key
            self.query(sql)

            # Return the result
            return True

        # Handle errors
        except NameError as err:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(err)

            # Production mode
            else:
                print(err)
                return False


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Adds a new column
    #
    # @param {str} table       -- Required table name
    # @param {str} col_data    -- Required column and it's data
    # @param {str} datatype    -- Required datatype of the column
    # @param {str} constraints -- Optional column constraints 
    #
    # @var {str} sql             -- The sql statement
    # @var {str} table_existance -- SQL statement for sqlite_master
    #
    # @return {bool}
    ##
    def _create_column(self, table:str, column:str, datatype:str, constraints:str=None):

        # Check development
        if not self.development:
            return True

        # Check the development
        if not self.development:
            alert = '''----------------------------------------------------------\n'''
            alert += '''INFO!\n'''
            alert += '''This method is only available in development!\n'''
            alert += '''----------------------------------------------------------'''

            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check required params
        if not table or not column or not datatype:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column', 'datatype']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'column', 'datatype']")
                return False

        # Check constraints
        if constraints:
            constraints = f' {constraints}'
        else:
            constraints = ''

        # Prepare sql statements
        # SQLite
        if self.db_system == 'SQLite':
            sql = f'''
                ALTER TABLE '{table}'
                ADD '{column}' {datatype + constraints};
            '''
        # MySQL
        elif self.db_system == 'MySQL':
            sql = f'''
                ALTER TABLE `{table}`
                ADD `{column}` {datatype + constraints};
            '''
        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''
                ALTER TABLE "{table}"
                ADD "{column}" {datatype + constraints};
            '''

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
                # Developer mode
                if self.debug:
                    # Raise error
                    raise Exception(f'Column "{column}" already exists!')

                # Production mode
                else:
                    print(f'Column "{column}" already exists!')
                    return False

        # Table not exists
        else:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" doesn\'t exist!')

            # Production mode
            else:
                print(f'Table "{table}" doesn\'t exist!')
                return False


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Creates a table if not exists.
    #
    # @Syntax:
    # foreign_key = {
    #   'user_id': {
    #       'r_table':   'users',
    #       'r_column':  'id',
    #       'on_update': RESTRICT | CASCADE | SET NULL | NO ACTION | SET DEFAULT,
    #       'on_delete': RESTRICT | CASCADE | SET NULL | NO ACTION | SET DEFAULT,
    #   },
    # }
    #
    # @param {str}  table       -- Required table name
    # @param {dict} col_type    -- Required column names and datatypes
    # @param {str}  primary_key -- Optional PRIMARY KEY column
    # @param {list} unique      -- Optional UNIQUE Constraint columns
    # @param {list} not_null    -- Optional NOT NULL Constraint columns
    # @param {dict} default     -- Optional DEFAULT Constraint columns
    # @param {dict} check       -- Optional CHECK Constraint for the table
    # @param {dict} foreign_key -- Optional FOREIGN KEY Constraints
    #
    # @var {str}  sql             -- The sql statement
    # @var {list} data_list       -- SQL data as list
    # @var {str}  data_sql        -- The sql data
    # @var {str}  table_existance -- SQL statement for sqlite_master
    # @var {str}  pk_col          -- The PRIMARY KEY sql statement
    # @var {str}  unique_col      -- The UNIQUE sql statement
    # @var {str}  null_col        -- The NOT NULL sql statement
    # @var {str}  default_col     -- The DEFAULT sql statement
    # @var {str}  check_col       -- The CHECK sql statement
    # @var {str}  auto_increment  -- The AUTO_INCREMENT sql statement for MySQL
    # @var {str}  r_table         -- The reference table name for the foreign key
    # @var {str}  r_column        -- The reference column name for the foreign key
    # @var {str}  fk_symbol       -- The foreign key symbol for Postgres and MySQL
    # @var {str}  on_update       -- ON UPDATE statement for the foreign key
    # @var {str}  on_delete       -- ON DELETE statement for the foreign key
    #
    # @return {bool}
    ##
    def _create_table(self, table:str, col_type:dict, primary_key:str=None, unique:list=[], not_null:list=[], 
        default:dict={}, check:dict={}, foreign_key:dict={}):

        # Check development
        if not self.development:
            return True

        # Check the development
        if not self.development:
            alert = '''----------------------------------------------------------\n'''
            alert += '''INFO!\n'''
            alert += '''This method is only available in development!\n'''
            alert += '''----------------------------------------------------------'''

            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Placeholders
        data_list = []
        data_sql = ''
        
        # Check required params
        if not table or not col_type:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'col_type']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'col_type']")
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

            # Postgres AUTO_INCREMENT
            if self.db_system == 'Postgres' and pk_col:
                # data_list.append(f'{key} SERIAL')
                if not value.upper() in ['SMALLSERIAL', 'SERIAL', 'BIGSERIAL']:
                    value = 'SERIAL'

            # SQLite
            if self.db_system == 'SQLite':
                data_list.append(f''''{key}' {value.upper() + pk_col + unique_col + null_col + default_col + check_col}''')

            # MySQL
            elif self.db_system == 'MySQL':
                data_list.append(f'''`{key}` {value.upper() + pk_col + unique_col + null_col + default_col + check_col}''')

            # Postgres
            elif self.db_system == 'Postgres':
                data_list.append(f'''"{key}" {value.upper() + pk_col + unique_col + null_col + default_col + check_col}''')

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

                on_update = f' ON UPDATE {on_update}' if on_update else ''
                on_delete = f' ON DELETE {on_delete}' if on_delete else ''
                
                # SQLite
                if self.db_system == 'SQLite':
                    data_list.append(f'''FOREIGN KEY ('{key}') REFERENCES '{r_table}'('{r_column}'){on_update + on_delete}''')

                # MySQL
                elif self.db_system == 'MySQL':
                    data_list.append(f'''CONSTRAINT {fk_symbol} FOREIGN KEY (`{key}`) REFERENCES `{r_table}`(`{r_column}`){on_update + on_delete}''')

                # Postgres
                elif self.db_system == 'Postgres':
                    data_list.append(f'''CONSTRAINT {fk_symbol} FOREIGN KEY ("{key}") REFERENCES "{r_table}"("{r_column}"){on_update + on_delete}''')

        # Prepare sql data
        data_sql = ',\n    '.join(data_list)

        # Prepare final sql statements
        # SQLite
        if self.db_system == 'SQLite':
            sql = f'''CREATE TABLE '{table}' (\n    '''
            sql += data_sql
            sql += '''\n);'''

        # MySQL
        elif self.db_system == 'MySQL':
            sql = f'''CREATE TABLE `{table}` (\n    '''
            sql += data_sql
            sql += '''\n);'''

        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''CREATE TABLE "{table}" (\n    '''
            sql += data_sql
            sql += '''\n);'''

        # Table not exists
        if not self._exist_table(table):
            # Create the table
            self.query(sql)

            # Return the result
            return True
            
        # Table already exists
        else:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" already exists!')

            # Production mode
            else:
                print(f'Table "{table}" already exists!')
                return False


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Creates a new database (file - SQLite)
    #
    # @param {str} database -- Required database name (file - SQLite)
    # 
    # @var {str}    sql   -- The sql statement
    # @var {str}    err   -- The error message for SQLite
    # @var {object} conn  -- The custom database connection for Postgres and MySQL
    # @var {object} cur:  -- The custom connection cursor for Postgres and MySQL
    #
    # @return {bool}
    ##
    def _create_database(self, database:str=None):

        # Check development
        if not self.development:
            return True

        # Check the development
        if not self.development:
            alert = '''----------------------------------------------------------\n'''
            alert += '''INFO!\n'''
            alert += '''This method is only available in development!\n'''
            alert += '''----------------------------------------------------------'''

            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check the required params
        if not database:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['database']")

            # Production mode
            else:
                print("You must provide the required parameters: ['database']")
                return False

        # Database already exists
        if self._exist_database(database=database):
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Database "{database}" already exists!')

            # Production mode
            else:
                print(f'Database "{database}" already exists!')
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
                        # Developer mode
                        if self.debug:
                            # Raise error
                            raise Exception('Cannot create the database!')

                        # Production mode
                        else:
                            print('Cannot create the database!')
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
                    sql = f'''CREATE DATABASE `{database}`;'''
                    
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
                    # Developer mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Production mode
                    else:
                        print(err)
                        return False

            # Postgres
            elif self.db_system == 'Postgres':
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
                    sql = f'''CREATE DATABASE "{database}";'''

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
                    # Developer mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Production mode
                    else:
                        print(err)
                        return False


    ################
    # Read Methods #
    ################
    ##
    # @desc Selects rows
    #
    # @param {str}  table    -- Required Table name (ex. "users")
    # @param {list} cols     -- Optional Columns (ex. ["id", "first_name", "last_name"])
    # @param {dict} where    -- Optional WHERE statement (ex. {"id": "2", "username": "admin"})
    # @param {dict} order_by -- Optional ORDER BY statement (ex. {"id": "ASC", "date": "DESC"})
    # @param {str}  group_by -- Optional GROUP BY statement (ex. 'country')
    # @param {int}  limit    -- Optional LIMIT statement (ex. "10")
    # @param {int}  offset   -- Optional OFFSET statement (ex. "10")
    #
    # @var {str}  sql: str     -- The sql statement
    # @var {list} data_bind    -- Data binding against SQL Injection
    # @var {list} where_sql    -- A placeholder for the WHERE clause
    # @var {list} order_by_sql -- A placeholder for the ORDER BY clause
    # @var {list} in_bind      -- A placeholder IN operator
    # @var {str}  in_sql       -- The sql statement for IN operator
    #
    # @return {class}
    ##
    def read(self, table:str, cols:list=[], where:dict={}, order_by:dict={}, group_by:str=None, limit:int=None, offset:int=None):

        # Check required params
        if not table:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table']")
                return False

        # The default variables
        data_col = []
        data_bind = []
        where_sql = []
        order_by_sql = []

        # Check cols
        if not cols or cols == ['*'] or cols == ["*"]:
            cols = '*'
        else:
            # SQLite
            if self.db_system == 'SQLite':
                for col in cols:
                    data_col.append(f'"{col}"')
                    # data_col.append(f"'{col}'")

                cols = ', '.join(data_col)

            # MySQL
            elif self.db_system == 'MySQL':
                for col in cols:
                    data_col.append(f'`{col}`')

                cols = ', '.join(data_col)
                
            # Postgres
            elif self.db_system == 'Postgres':
                for col in cols:
                    data_col.append(f'"{col}"')

                cols = ', '.join(data_col)

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

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`={self.sp_char}')

                    data_bind.append(value)

                # Not equal to
                elif re.search('--not-equal$', key) or re.search('--ne$', key):
                    key = key.replace('--not-equal', '')
                    key = key.replace('--ne', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"<>{self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`<>{self.sp_char}')

                    data_bind.append(value)

                # Greater than
                elif re.search('--greater-than$', key) or re.search('--gt$', key):
                    key = key.replace('--greater-than', '')
                    key = key.replace('--gt', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}">{self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`>{self.sp_char}')
                    
                    data_bind.append(value)

                # Greater than or equal to
                elif re.search('--greater-equal$', key) or re.search('--ge$', key):
                    key = key.replace('--greater-equal', '')
                    key = key.replace('--ge', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}">={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`>={self.sp_char}')

                    data_bind.append(value)

                # Less than
                elif re.search('--less-than$', key) or re.search('--lt$', key):
                    key = key.replace('--less-than', '')
                    key = key.replace('--lt', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"<{self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`<{self.sp_char}')

                    data_bind.append(value)

                # Less than or equal to
                elif re.search('--less-equal$', key) or re.search('--le$', key):
                    key = key.replace('--less-equal', '')
                    key = key.replace('--le', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"<={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`<={self.sp_char}')
                        
                    data_bind.append(value)

                # LIKE
                elif re.search('--like$', key) or re.search('--l$', key):
                    key = key.replace('--like', '')
                    key = key.replace('--l', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" LIKE {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` LIKE {self.sp_char}')

                    data_bind.append(value)
                    
                # NOT LIKE
                elif re.search('--not-like$', key) or re.search('--nl$', key):
                    key = key.replace('--not-like', '')
                    key = key.replace('--nl', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" NOT LIKE {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`  NOT LIKE {self.sp_char}')

                    data_bind.append(value)
                
                # BETWEEN
                elif re.search('--between$', key) or re.search('--b$', key):
                    key = key.replace('--between', '')
                    key = key.replace('--b', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" BETWEEN {self.sp_char} AND {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` BETWEEN {self.sp_char} AND {self.sp_char}')

                    data_bind.append(value[0])
                    data_bind.append(value[1])
                
                # NOT BETWEEN
                elif re.search('--not-between$', key) or re.search('--nb$', key):
                    key = key.replace('--not-between', '')
                    key = key.replace('--nb', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" NOT BETWEEN {self.sp_char} AND {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` NOT BETWEEN {self.sp_char} AND {self.sp_char}')
                        
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

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" IN ({in_sql})')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` IN ({in_sql})')

                # NOT IN
                elif re.search('--not-in$', key) or re.search('--ni$', key):
                    key = key.replace('--not-in', '')
                    key = key.replace('--ni', '')
                    for x in value:
                        in_bind.append(self.sp_char)
                        data_bind.append(x)

                    in_sql =','.join(in_bind)

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" NOT IN ({in_sql})')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` NOT IN ({in_sql})')

                # Equal to (default)
                else:
                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`={self.sp_char}')

                    data_bind.append(value)

            # Prepare the where SQL
            where = ' WHERE '

            # Check column prefixes (and/or)
            i = 0
            for x in where_sql:
                ch = ''

                if re.search('^or--', clean_key(x)) or re.search('^o--', clean_key(x)):
                    x = x.replace('or--', '')
                    x = x.replace('o--', '')
                    if i > 0:
                        ch = 'OR '

                    where_sql[i] = f'{ch + x}'
                
                elif re.search('^and--', clean_key(x)) or re.search('^a--', clean_key(x)):
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
                # SQLite and Postgres
                if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                    order_by_sql.append(f'"{key}" {value.upper()}')

                # MySQL
                elif self.db_system == 'MySQL':
                    order_by_sql.append(f'`{key}` {value.upper()}')

            order_by = ' ORDER BY ' + ', '.join(order_by_sql)

        else:
            order_by = ''

        # Check group_by
        if group_by:
            # SQLite and Postgres
            if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                group_by = f' GROUP BY "{group_by}"'

            # MySQL
            elif self.db_system == 'MySQL':
                group_by = f' GROUP BY `{group_by}`'

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
        # SQLite
        if self.db_system == 'SQLite':
            sql = f'''SELECT {cols} FROM '{table}'{where + order_by + group_by + limit + offset};'''
            
        # MySQL
        elif self.db_system == 'MySQL':
            sql = f'''SELECT {cols} FROM `{table}`{where + order_by + group_by + limit + offset};'''
            
        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''SELECT {cols} FROM "{table}"{where + order_by + group_by + limit + offset};'''

        # Return result
        return Read(self, sql, data_bind)


    ##
    # @desc Joins related tables
    #
    # @param {str}  table     -- Required main Table (ex. "table_1")
    # @param {list} f_keys    -- Required foreign keys (ex. ["user_id", "flight_id"])
    # @param {list} f_tables  -- Required foreign tables (ex. ["table_2", "table_3"])
    # @param {list} p_keys    -- Required primary keys (ex. ["pk_2", "pk_3"])
    # @param {list} cols      -- Optional Columns (ex. ["table.id", "table_2.name", "table_3.address"])
    #
    # @param {str}  join_stmt -- The join statement:
    #        SQLite: INNER JOIN, LEFT JOIN, CROSS JOIN (Learn More: https://www.sqlitetutorial.net/sqlite-join/)
    #        MySQL: INNER JOIN, LEFT JOIN, RIGHT JOIN, CROSS JOIN (Learn More: https://www.w3schools.com/mysql/mysql_join.asp)
    #        Postgres: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN (Learn More: https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-joins/)
    #        JOIN vs INNER JOIN: https://stackoverflow.com/questions/565620/difference-between-join-and-inner-join
    #
    # @param {dict} where    -- Optional WHERE statement (ex. {"table.id": "2", "table_2.name": "John"})
    # @param {dict} order_by -- Optional ORDER BY statement (ex. {"table.id": "ASC", "table.date": "DESC"})
    # @param {str}  group_by -- Optional GROUP BY statement (ex. 'table.country')
    # @param {int}  limit    -- Optional LIMIT statement (ex. "10")
    # @param {int}  offset   -- Optional OFFSET statement (ex. "10")
    #
    # @var {str}  sql: str     -- The sql statement
    # @var {list} data_bind    -- Data binding against SQL Injection
    # @var {list} where_sql    -- A placeholder for the WHERE clause
    # @var {list} order_by_sql -- A placeholder for the ORDER BY clause
    # @var {list} in_bind      -- A placeholder IN operator
    # @var {str}  in_sql       -- The sql statement for IN operator
    #
    # @return {class}
    ##
    def join(self, table:str, f_keys:list, f_tables:list, p_keys:list, cols:list=[], join_stmt:str='INNER JOIN', where:dict={}, order_by:dict={}, group_by:str=None, limit:int=None, offset:int=None):

        # Check required params
        if not table and not f_keys and not f_tables and not p_keys:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: 'main_table', 'join_tables'")

            # Production mode
            else:
                print("You must provide the required parameters: 'main_table', 'join_tables'")
                return False

        # The default variables
        data_col = []
        data_bind = []
        join_sql = ""
        where_sql = []
        order_by_sql = []

        # Check cols
        if not cols or cols == ['*'] or cols == ["*"]:
            cols = '*'
        else:
            # SQLite
            if self.db_system == 'SQLite':
                for col in cols:
                    # Check the key
                    if not '.' in col:
                        data_col.append(f'"{col}"')
                    else:
                        data_col.append(f'{col}')

            # MySQL
            elif self.db_system == 'MySQL':
                for col in cols:
                    # Check the key
                    if not '.' in col:
                        data_col.append(f'`{col}`')
                    else:
                        data_col.append(f'{col}')

            # Postgres
            elif self.db_system == 'Postgres':
                for col in cols:
                    # Check the key
                    if not '.' in col:
                        data_col.append(f'"{col}"')
                    else:
                        data_col.append(f'{col}')

            cols = ', '.join(data_col)

        # Prepare Join statement
        for i in range(len(f_tables)):
            fk = f_keys[i]
            f_table = f_tables[i]
            f_pk = p_keys[i]

            # SQLite and Postgres
            if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                join_sql += f' {join_stmt.upper()} "{f_table}" ON "{table}"."{fk}" = "{f_table}"."{f_pk}" '

            # MySQL
            elif self.db_system == 'MySQL':
                join_sql += f' {join_stmt.upper()} `{f_table}` ON `{table}`.`{fk}` = `{f_table}`.`{f_pk}` '

        join = join_sql

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

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}"={self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}`={self.sp_char}')

                    else:
                        where_sql.append(f'{key}={self.sp_char}')

                    data_bind.append(value)

                # Not equal to
                elif re.search('--not-equal$', key) or re.search('--ne$', key):
                    key = key.replace('--not-equal', '')
                    key = key.replace('--ne', '')

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}"<>{self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}`<>{self.sp_char}')
                    else:
                        where_sql.append(f'{key}<>{self.sp_char}')

                    data_bind.append(value)

                # Greater than
                elif re.search('--greater-than$', key) or re.search('--gt$', key):
                    key = key.replace('--greater-than', '')
                    key = key.replace('--gt', '')

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}">{self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}`>{self.sp_char}')
                    else:
                        where_sql.append(f'{key}>{self.sp_char}')
                    
                    data_bind.append(value)

                # Greater than or equal to
                elif re.search('--greater-equal$', key) or re.search('--ge$', key):
                    key = key.replace('--greater-equal', '')
                    key = key.replace('--ge', '')

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}">={self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}`>={self.sp_char}')
                    else:
                        where_sql.append(f'{key}>={self.sp_char}')

                    data_bind.append(value)

                # Less than
                elif re.search('--less-than$', key) or re.search('--lt$', key):
                    key = key.replace('--less-than', '')
                    key = key.replace('--lt', '')

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}"<{self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}`<{self.sp_char}')
                    else:
                        where_sql.append(f'{key}<{self.sp_char}')

                    data_bind.append(value)

                # Less than or equal to
                elif re.search('--less-equal$', key) or re.search('--le$', key):
                    key = key.replace('--less-equal', '')
                    key = key.replace('--le', '')

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}"<={self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}`<={self.sp_char}')
                    else:
                        where_sql.append(f'{key}<={self.sp_char}')
                        
                    data_bind.append(value)

                # LIKE
                elif re.search('--like$', key) or re.search('--l$', key):
                    key = key.replace('--like', '')
                    key = key.replace('--l', '')

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}" LIKE {self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}` LIKE {self.sp_char}')
                    else:
                        where_sql.append(f'{key} LIKE {self.sp_char}')

                    data_bind.append(value)
                    
                # NOT LIKE
                elif re.search('--not-like$', key) or re.search('--nl$', key):
                    key = key.replace('--not-like', '')
                    key = key.replace('--nl', '')

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}" NOT LIKE {self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}`  NOT LIKE {self.sp_char}')
                    else:
                        where_sql.append(f'{key}  NOT LIKE {self.sp_char}')

                    data_bind.append(value)
                
                # BETWEEN
                elif re.search('--between$', key) or re.search('--b$', key):
                    key = key.replace('--between', '')
                    key = key.replace('--b', '')

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}" BETWEEN {self.sp_char} AND {self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}` BETWEEN {self.sp_char} AND {self.sp_char}')
                    else:
                        where_sql.append(f'{key} BETWEEN {self.sp_char} AND {self.sp_char}')

                    data_bind.append(value[0])
                    data_bind.append(value[1])
                
                # NOT BETWEEN
                elif re.search('--not-between$', key) or re.search('--nb$', key):
                    key = key.replace('--not-between', '')
                    key = key.replace('--nb', '')

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}" NOT BETWEEN {self.sp_char} AND {self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}` NOT BETWEEN {self.sp_char} AND {self.sp_char}')
                    else:
                        where_sql.append(f'{key} NOT BETWEEN {self.sp_char} AND {self.sp_char}')
                        
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

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}" IN ({in_sql})')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}` IN ({in_sql})')
                    else:
                        where_sql.append(f'{key} IN ({in_sql})')

                # NOT IN
                elif re.search('--not-in$', key) or re.search('--ni$', key):
                    key = key.replace('--not-in', '')
                    key = key.replace('--ni', '')
                    for x in value:
                        in_bind.append(self.sp_char)
                        data_bind.append(x)

                    in_sql =','.join(in_bind)

                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}" NOT IN ({in_sql})')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}` NOT IN ({in_sql})')
                    else:
                        where_sql.append(f'{key} NOT IN ({in_sql})')

                # Equal to (default)
                else:
                    # Check the key
                    if not '.' in key:
                        # SQLite and Postgres
                        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                            where_sql.append(f'"{key}"={self.sp_char}')

                        # MySQL
                        elif self.db_system == 'MySQL':
                            where_sql.append(f'`{key}`={self.sp_char}')
                    else:
                        where_sql.append(f'{key}={self.sp_char}')

                    data_bind.append(value)

            # Prepare the where SQL
            where = ' WHERE '

            # Check column prefixes (and/or)
            i = 0
            for x in where_sql:
                ch = ''

                if re.search('^or--', clean_key(x)) or re.search('^o--', clean_key(x)):
                    x = x.replace('or--', '')
                    x = x.replace('o--', '')
                    if i > 0:
                        ch = 'OR '

                    where_sql[i] = f'{ch + x}'
                
                elif re.search('^and--', clean_key(x)) or re.search('^a--', clean_key(x)):
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
                # Check the key
                if not '.' in key:
                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        order_by_sql.append(f'"{key}" {value.upper()}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        order_by_sql.append(f'`{key}` {value.upper()}')
                else:
                    order_by_sql.append(f'{key} {value.upper()}')

            order_by = ' ORDER BY ' + ', '.join(order_by_sql)

        else:
            order_by = ''

        # Check group_by
        if group_by:
            # Check the key
            if not '.' in key:
                # SQLite and Postgres
                if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                    group_by = f' GROUP BY "{group_by}"'

                # MySQL
                elif self.db_system == 'MySQL':
                    group_by = f' GROUP BY `{group_by}`'
            else:
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
        # SQLite
        if self.db_system == 'SQLite':
            sql = f'''SELECT {cols} FROM '{table}'{join + where + order_by + group_by + limit + offset};'''
            
        # MySQL
        elif self.db_system == 'MySQL':
            sql = f'''SELECT {cols} FROM `{table}`{join + where + order_by + group_by + limit + offset};'''
            
        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''SELECT {cols} FROM "{table}"{join + where + order_by + group_by + limit + offset};'''

        # Return result
        return Join(self, sql, data_bind)


    ##################
    # Update Methods #
    ##################
    ##
    # *CAUTION! If you ignore the 'where' parameter, it may updates the columns for all records! (must confirm)
    #
    # @desc Updates row(s)
    #
    # @param {str}  table   -- Required Table name (ex. "users")
    # @param {dict} data    -- Required data (ex. {"first_name": "John", "last_name": "Doe"})
    # @param {dict} where   -- Optional (*CAUTION!) WHERE statement (ex. {"id": "2", "username": "admin"})
    # @param {bool} confirm -- Optional|Required confirm (if not where it will be Required)
    #
    # @var {str}  sql       -- The sql statement
    # @var {list} data_bind -- Data binding against SQL Injection
    # @var {list} data_sql  -- A placeholder for the update data
    # @var {list} where_sql -- A placeholder for the WHERE clause
    # @var {list} in_bind   -- A placeholder IN operator
    # @var {str}  in_sql    -- The sql statement for IN operator
    #
    # @return {bool}
    ##
    def update(self, table:str, data:dict={}, where:dict={}, confirm:bool=False):

        # Check the confirm if the where clase not set
        if not where and not confirm:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception('For update without the where clause you must confirm the command.')

            # Production mode
            else:
                print('For update without the where clause you must confirm the command.')
                return False

        # The default variables
        data_bind = []
        data_sql = []
        where_sql = []

        # Check required params
        if not table or not data:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['']")

            # Production mode
            else:
                print("You must provide the required parameters: ['']")
                return False

        # Prepare data
        # SQLite and Postgres
        if self.db_system == 'SQLite' or self.db_system == 'Postgres':
            for key, value in data.items():
                data_sql.append(f'"{key}"={self.sp_char}')
                data_bind.append(value)

            data = ', '.join(data_sql)
        
        # MySQL
        elif self.db_system == 'MySQL':
            for key, value in data.items():
                data_sql.append(f'`{key}`={self.sp_char}')
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

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`={self.sp_char}')

                    data_bind.append(value)

                # Not equal to
                elif re.search('--not-equal$', key) or re.search('--ne$', key):
                    key = key.replace('--not-equal', '')
                    key = key.replace('--ne', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"<>{self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`<>{self.sp_char}')

                    data_bind.append(value)

                # Greater than
                elif re.search('--greater-than$', key) or re.search('--gt$', key):
                    key = key.replace('--greater-than', '')
                    key = key.replace('--gt', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}">{self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`>{self.sp_char}')
                    
                    data_bind.append(value)

                # Greater than or equal to
                elif re.search('--greater-equal$', key) or re.search('--ge$', key):
                    key = key.replace('--greater-equal', '')
                    key = key.replace('--ge', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}">={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`>={self.sp_char}')

                    data_bind.append(value)

                # Less than
                elif re.search('--less-than$', key) or re.search('--lt$', key):
                    key = key.replace('--less-than', '')
                    key = key.replace('--lt', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"<{self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`<{self.sp_char}')

                    data_bind.append(value)

                # Less than or equal to
                elif re.search('--less-equal$', key) or re.search('--le$', key):
                    key = key.replace('--less-equal', '')
                    key = key.replace('--le', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"<={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`<={self.sp_char}')
                        
                    data_bind.append(value)

                # LIKE
                elif re.search('--like$', key) or re.search('--l$', key):
                    key = key.replace('--like', '')
                    key = key.replace('--l', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" LIKE {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` LIKE {self.sp_char}')

                    data_bind.append(value)
                    
                # NOT LIKE
                elif re.search('--not-like$', key) or re.search('--nl$', key):
                    key = key.replace('--not-like', '')
                    key = key.replace('--nl', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" NOT LIKE {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`  NOT LIKE {self.sp_char}')

                    data_bind.append(value)
                
                # BETWEEN
                elif re.search('--between$', key) or re.search('--b$', key):
                    key = key.replace('--between', '')
                    key = key.replace('--b', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" BETWEEN {self.sp_char} AND {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` BETWEEN {self.sp_char} AND {self.sp_char}')

                    data_bind.append(value[0])
                    data_bind.append(value[1])
                
                # NOT BETWEEN
                elif re.search('--not-between$', key) or re.search('--nb$', key):
                    key = key.replace('--not-between', '')
                    key = key.replace('--nb', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" NOT BETWEEN {self.sp_char} AND {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` NOT BETWEEN {self.sp_char} AND {self.sp_char}')
                        
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

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" IN ({in_sql})')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` IN ({in_sql})')

                # NOT IN
                elif re.search('--not-in$', key) or re.search('--ni$', key):
                    key = key.replace('--not-in', '')
                    key = key.replace('--ni', '')
                    for x in value:
                        in_bind.append(self.sp_char)
                        data_bind.append(x)

                    in_sql =','.join(in_bind)

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" NOT IN ({in_sql})')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` NOT IN ({in_sql})')

                # Equal to (default)
                else:
                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`={self.sp_char}')

                    data_bind.append(value)

            # Prepare the where SQL
            where = ' WHERE '

            i = 0
            for x in where_sql:
                ch = ''

                if re.search('^or--', clean_key(x)) or re.search('^o--', clean_key(x)):
                    x = x.replace('or--', '')
                    x = x.replace('o--', '')
                    if i > 0:
                        ch = 'OR '

                    where_sql[i] = f'{ch + x}'
                
                elif re.search('^and--', clean_key(x)) or re.search('^a--', clean_key(x)):
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
        # SQLite
        if self.db_system == 'SQLite':
            sql = f'''UPDATE "{table}" SET {data + where};'''
            
        # MySQL
        elif self.db_system == 'MySQL':
            sql = f'''UPDATE `{table}` SET {data + where};'''
            
        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''UPDATE "{table}" SET {data + where};'''

        # Update was successfull
        if self.query(sql, data_bind):
            # Return result
            return True

        # Update failed
        else:
            # Return result
            return False


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Updates a column
    #
    # @param {str} table       -- Required table name
    # @param {str} old_col     -- Required old column name
    # @param {str} new_col     -- Required new column name
    # @param {str} datatype    -- Required new column data
    # @param {str} constraints -- Optional new column constraints
    # 
    # @var {str}  sql             -- The sql statement
    # @var {str}  table_existance -- SQL statement for sqlite_master
    # @var {bool} recursion       -- For recursion the method
    #
    # @return {bool}
    ##
    def _update_column(self, table:str, old_col:str, new_col:str, datatype:str, constraints:str=None):

        # Check development
        if not self.development:
            return True

        # Check the development
        if not self.development:
            alert = '''----------------------------------------------------------\n'''
            alert += '''INFO!\n'''
            alert += '''This method is only available in development!\n'''
            alert += '''----------------------------------------------------------'''

            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check required params
        if not table  or not old_col or not new_col or not datatype:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'old_col', 'new_col', 'datatype']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'old_col', 'new_col', 'datatype']")
                return False

        # Check the FOREIGN KEY
        if self._exist_fk(table=table, column=old_col):
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception('You cannot change a foreign key with "_update_column" method!')

            # Production mode
            else:
                print('You cannot change a foreign key with "_update_column" method!')
                return False

        # Check the column names
        if old_col == new_col:
            recursion = True
            new_col += '__temp'
        else:
            recursion = False

        # Fetch the old column data
        old_data = self.read(table=table, cols=[old_col]).all()

        # Table exists
        if self._exist_table(table):
            # Add the new column
            self._create_column(table=table, column=new_col, datatype=datatype, constraints=constraints)

            # Update new column data
            for x in old_data:
                self.update(table=table, data={new_col:x[old_col]}, where={old_col:x[old_col]})

            # Commit the changes so far
            self.conn.commit()

            # Drop the old column
            self._delete_column(table=table, column=old_col, confirm=True)

            # Check the column names
            if recursion:
                # Recursion
                return self._update_column(table, old_col=new_col, new_col=old_col, datatype=datatype, constraints=constraints)

            # Return the result
            return True

        # Table not exists
        else:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" doesn\'t exist')

            # Production mode
            else:
                print(f'Table "{table}" doesn\'t exist')
                return False


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Renames a table if exists
    #
    # @param {str} old_table -- Required table old name
    # @param {str} new_table -- Required table new name
    #
    # @var {str} sql             -- The sql statement
    # @var {str} table_existance -- SQL statement for sqlite_master
    #
    # @return {bool}
    ##
    def _update_table(self, old_table:str, new_table:str):

        # Check development
        if not self.development:
            return True

        # Check the development
        if not self.development:
            alert = '''----------------------------------------------------------\n'''
            alert += '''INFO!\n'''
            alert += '''This method is only available in development!\n'''
            alert += '''----------------------------------------------------------'''

            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check required params
        if not old_table or not new_table:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['old_table', 'new_table']")

            # Production mode
            else:
                print("You must provide the required parameters: ['old_table', 'new_table']")
                return False

        # Table exists
        if self._exist_table(old_table):
            # Prepare sql statements
            # SQLite
            if self.db_system == 'SQLite':
                sql = f'''
                    ALTER TABLE '{old_table}'
                    RENAME TO '{new_table}';
                '''

            # MySQL
            elif self.db_system == 'MySQL':
                sql = f'''
                    ALTER TABLE `{old_table}`
                    RENAME TO `{new_table}`;
                '''
                
            # Postgres
            elif self.db_system == 'Postgres':
                sql = f'''
                    ALTER TABLE "{old_table}"
                    RENAME TO "{new_table}";
                '''

            # Alter the table
            self.query(sql)

            # Return the result
            return True

        # Table not exists
        else:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{old_table}" doesn\'t exist')

            # Production mode
            else:
                print(f'Table "{old_table}" doesn\'t exist')
                return False


    ##################
    # Delete Methods #
    ##################
    ##
    # *WARNING! If you ignore the 'where' parameter, it will deletes all the records inside your table! (must confirm)
    #
    # @desc Deletes row(s)
    #
    # @param {str}  table   -- Required Table name (ex. "users")
    # @param {dict} where   -- Optional (*WARNING!) WHERE statement (ex. {"id": "2", "username": "admin"})
    # @param {bool} confirm -- Optional|Required confirm (if not where it will be Required)
    #
    # @var {str}  sql       -- The sql statement
    # @var {list} data_bind -- Data binding against SQL Injection
    # @var {list} where_sql -- A placeholder for the WHERE clause
    # @var {list} in_bind   -- A placeholder IN operator
    # @var {str}  in_sql    -- The sql statement for IN operator
    #
    # @return {bool}
    ##
    def delete(self, table:str, where:dict={}, confirm:bool=False):
        
        # Check the confirm if the where clase not set
        if not where and not confirm:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception('For delete without the where clause you must confirm the command.')

            # Production mode
            else:
                print('For delete without the where clause you must confirm the command.')
                return False

        # The default variables
        data_bind = []
        where_sql = []

        # Check required params
        if not table:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table']")
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

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`={self.sp_char}')

                    data_bind.append(value)

                # Not equal to
                elif re.search('--not-equal$', key) or re.search('--ne$', key):
                    key = key.replace('--not-equal', '')
                    key = key.replace('--ne', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"<>{self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`<>{self.sp_char}')

                    data_bind.append(value)

                # Greater than
                elif re.search('--greater-than$', key) or re.search('--gt$', key):
                    key = key.replace('--greater-than', '')
                    key = key.replace('--gt', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}">{self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`>{self.sp_char}')
                    
                    data_bind.append(value)

                # Greater than or equal to
                elif re.search('--greater-equal$', key) or re.search('--ge$', key):
                    key = key.replace('--greater-equal', '')
                    key = key.replace('--ge', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}">={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`>={self.sp_char}')

                    data_bind.append(value)

                # Less than
                elif re.search('--less-than$', key) or re.search('--lt$', key):
                    key = key.replace('--less-than', '')
                    key = key.replace('--lt', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"<{self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`<{self.sp_char}')

                    data_bind.append(value)

                # Less than or equal to
                elif re.search('--less-equal$', key) or re.search('--le$', key):
                    key = key.replace('--less-equal', '')
                    key = key.replace('--le', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"<={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`<={self.sp_char}')
                        
                    data_bind.append(value)

                # LIKE
                elif re.search('--like$', key) or re.search('--l$', key):
                    key = key.replace('--like', '')
                    key = key.replace('--l', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" LIKE {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` LIKE {self.sp_char}')

                    data_bind.append(value)
                    
                # NOT LIKE
                elif re.search('--not-like$', key) or re.search('--nl$', key):
                    key = key.replace('--not-like', '')
                    key = key.replace('--nl', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" NOT LIKE {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`  NOT LIKE {self.sp_char}')

                    data_bind.append(value)
                
                # BETWEEN
                elif re.search('--between$', key) or re.search('--b$', key):
                    key = key.replace('--between', '')
                    key = key.replace('--b', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" BETWEEN {self.sp_char} AND {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` BETWEEN {self.sp_char} AND {self.sp_char}')

                    data_bind.append(value[0])
                    data_bind.append(value[1])
                
                # NOT BETWEEN
                elif re.search('--not-between$', key) or re.search('--nb$', key):
                    key = key.replace('--not-between', '')
                    key = key.replace('--nb', '')

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" NOT BETWEEN {self.sp_char} AND {self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` NOT BETWEEN {self.sp_char} AND {self.sp_char}')
                        
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

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" IN ({in_sql})')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` IN ({in_sql})')

                # NOT IN
                elif re.search('--not-in$', key) or re.search('--ni$', key):
                    key = key.replace('--not-in', '')
                    key = key.replace('--ni', '')
                    for x in value:
                        in_bind.append(self.sp_char)
                        data_bind.append(x)

                    in_sql =','.join(in_bind)

                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}" NOT IN ({in_sql})')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}` NOT IN ({in_sql})')

                # Equal to (default)
                else:
                    # SQLite and Postgres
                    if self.db_system == 'SQLite' or self.db_system == 'Postgres':
                        where_sql.append(f'"{key}"={self.sp_char}')

                    # MySQL
                    elif self.db_system == 'MySQL':
                        where_sql.append(f'`{key}`={self.sp_char}')

                    data_bind.append(value)

            # Prepare the where SQL
            where = ' WHERE '

            i = 0
            for x in where_sql:
                ch = ''

                if re.search('^or--', clean_key(x)) or re.search('^o--', clean_key(x)):
                    x = x.replace('or--', '')
                    x = x.replace('o--', '')
                    if i > 0:
                        ch = 'OR '

                    where_sql[i] = f'{ch + x}'
                
                elif re.search('^and--', clean_key(x)) or re.search('^a--', clean_key(x)):
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
        # SQLite
        if self.db_system == 'SQLite':
            sql = f'''DELETE FROM '{table}'{where};'''
            
        # MySQL
        elif self.db_system == 'MySQL':
            sql = f'''DELETE FROM `{table}`{where};'''
            
        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''DELETE FROM "{table}"{where};'''

        # Deletion was successfull
        if self.query(sql, data_bind):
            # Return result
            return True

        # Deletion failed
        else:
            # Return result
            return False


    ##
    # CAUTION! Use this methods only in development.
    #
    # @desc Drops a foreign key from an existing table (MySQL and Postgres)
    #
    # @param {str} table     -- Required table name
    # @param {str} table     -- Required column name
    # @param {str} fk_symbol -- Required foreign key symbol
    # 
    # @var {str} sql -- The sql statement
    #
    # @return {bool}
    ##
    def _delete_fk(self, table:str, column:str, fk_symbol:str, confirm:bool=False):

        # Check development
        if not self.development:
            return True

        # Check the development
        if not self.development:
            alert = '''----------------------------------------------------------\n'''
            alert += '''INFO!\n'''
            alert += '''This method is only available in development!\n'''
            alert += '''----------------------------------------------------------'''

            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check the database system
        if not self.db_system == 'Postgres' and not self.db_system == 'MySQL':
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception('The "delete_fk" method only works with MySQL and Postgres!')

            # Production mode
            else:
                print('The "delete_fk" method only works with MySQL and Postgres!')
                return False

        # Check required params
        if not table or not column or not fk_symbol or not confirm:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column', 'fk_symbol', 'confirm']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'column', 'fk_symbol', 'confirm']")
                return False

        # Tables not exist
        if not self._exist_table(table):
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" doesn\'t exist!')

            # Production mode
            else:
                print(f'Table "{table}" doesn\'t exist!')
                return False

        # Foreign key not exists
        if not self._exist_fk(table, column):
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'The foreign key not exists!')

            # Production mode
            else:
                print(f'The foreign key not exists!')
                return False

        # Everything is OK
        # MySQL
        if self.db_system == 'MySQL':
            sql = f'''
                ALTER TABLE `{table}`
                DROP FOREIGN KEY `{fk_symbol}`;
            '''

        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''
                ALTER TABLE "{table}"
                DROP CONSTRAINT "{fk_symbol}";
            '''

        # Attempt to drop the foreign key
        try:
            # Drop the foreign key
            self.query(sql)

            # Return the result
            return True

        # Handle errors
        except NameError as err:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(err)

            # Production mode
            else:
                print(err)
                return False


    ##
    # DANGER! Be super careful. This method drops your column permanently.
    #
    # CAUTION! Use this methods only in development.
    #
    # @desc Drops a column from a table
    #
    # @param {str}  table   -- Required table name
    # @param {str}  column  -- Required column name
    # @param {bool} confirm -- Required confirmation
    # 
    # @var {str} sql             -- The sql statement
    # @var {str} table_existance -- SQL statement for sqlite_master
    #
    # @return {bool}
    ##
    def _delete_column(self, table:str, column:str, confirm:bool=False):

        # Check development
        if not self.development:
            return True

        # Check the development
        if not self.development:
            alert = '''----------------------------------------------------------\n'''
            alert += '''INFO!\n'''
            alert += '''This method is only available in development!\n'''
            alert += '''----------------------------------------------------------'''

            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check required params
        if not table or not column or not confirm:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'column', 'confirm']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'column', 'confirm']")
                return False


        # Check the FOREIGN KEY
        if self._exist_fk(table=table, column=column):
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception('You cannot drop a foreign key with "_delete_column" method!')

            # Production mode
            else:
                print('You cannot drop a foreign key with "_delete_column" method!')
                return False

        # Prepare sql statements
        # SQLite
        if self.db_system == 'SQLite':
            sql = f'''
                ALTER TABLE '{table}'
                DROP COLUMN '{column}';
            '''
            
        # MySQL
        elif self.db_system == 'MySQL':
            sql = f'''
                ALTER TABLE `{table}`
                DROP COLUMN `{column}`;
            '''
            
        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''
                ALTER TABLE "{table}"
                DROP COLUMN "{column}";
            '''

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
                # Developer mode
                if self.debug:
                    # Raise error
                    raise Exception(f'Column "{column}" does\'nt exists!')

                # Production mode
                else:
                    print(f'Column "{column}" does\'nt exists!')
                    return False

        # Table not exists
        else:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" doesn\'t exist')

            # Production mode
            else:
                print(f'Table "{table}" doesn\'t exist')
                return False


    ##
    # DANGER! Be super careful. This method drops your table permanently.
    #
    # CAUTION! Use this methods only in development.
    #
    # @desc Drops a table if exists
    #
    # @param {str}  table   -- Required table name
    # @param {bool} confirm -- Required confirmation
    # 
    # @var {str} sql             -- The sql statement
    # @var {str} table_existance -- SQL statement for sqlite_master
    #
    # @return {bool}
    ##
    def _delete_table(self, table:str, confirm:bool=False):

        # Check development
        if not self.development:
            return True

        # Check the development
        if not self.development:
            alert = '''----------------------------------------------------------\n'''
            alert += '''INFO!\n'''
            alert += '''This method is only available in development!\n'''
            alert += '''----------------------------------------------------------'''

            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check required params
        if not table or not confirm:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['table', 'confirm']")

            # Production mode
            else:
                print("You must provide the required parameters: ['table', 'confirm']")
                return False

        # Prepare sql statements
        # SQLite
        if self.db_system == 'SQLite':
            sql = f'''DROP TABLE '{table}';'''
            
        # MySQL
        elif self.db_system == 'MySQL':
            sql = f'''DROP TABLE `{table}`;'''
            
        # Postgres
        elif self.db_system == 'Postgres':
            sql = f'''DROP TABLE "{table}";'''

        # Table exists
        if self._exist_table(table):
            # Drop the table
            self.query(sql)

            # Return the result
            return True
            
        else:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Table "{table}" doesn\'t exist')

            # Production mode
            else:
                print(f'Table "{table}" doesn\'t exist')
                return False


    ##
    # DANGER! Be super careful. This method drops your database permanently.
    #
    # CAUTION! Use this methods only in development.
    #
    # @desc Drops a database (Removes a database file for SQLite)
    #
    # @param {str}  database -- Required database name (file -- SQLite)
    # @param {bool} confirm  -- Required confirmation
    # 
    # @var {str}    sql  -- The sql statement
    # @var {object} conn -- The custom database connection form Postgres and MySQL
    # @var {object} cur  -- The custom connection cursor form Postgres and MySQL
    #
    # @return {bool}
    ##
    def _delete_database(self, database:str=None, confirm:str=False):
        
        # Check development
        if not self.development:
            return True

        # Check the development
        if not self.development:
            alert = '''----------------------------------------------------------\n'''
            alert += '''INFO!\n'''
            alert += '''This method is only available in development!\n'''
            alert += '''----------------------------------------------------------'''

            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check the required params
        if not database or not confirm:
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception("You must provide the required parameters: ['database', 'confirm']")

            # Production mode
            else:
                print("You must provide the required parameters: ['database', 'confirm']")
                return False

        # Database not exists
        if not self._exist_database(database=database):
            # Developer mode
            if self.debug:
                # Raise error
                raise Exception(f'Database "{database}" not exists!')

            # Production mode
            else:
                print(f'Database "{database}" not exists!')
                return False

        # Database exists
        else:
            # Close the database connection
            self.conn.close()

            # SQLite
            if self.db_system == 'SQLite':
                # Attempt the process
                try:
                    # Remove the database file
                    delete_file(self.app_path + self.sep + database)

                    # Return the result
                    return True

                # Handle the errors
                except NameError as err:
                    # Developer mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Production mode
                    else:
                        print(err)
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
                    sql = f'''DROP DATABASE `{database}`;'''
                    
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
                    # Developer mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Production mode
                    else:
                        print(err)
                        return False

            # Postgres
            elif self.db_system == 'Postgres':
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
                    sql = f'''DROP DATABASE "{database}";'''

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
                    # Developer mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Production mode
                    else:
                        print(err)
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
    # @param {class} parent    -- The Database Class
    # @param {str}   sql       -- The sql query string
    # @param {list}  data_bind -- The data to bind
    #
    # @property {str}    sql       -- the sql query string
    # @property {object} data_bind -- the data to bind
    # @property {method} query     -- the query method of the Database class
    # @property {str}    regex     -- the regular expression for the select statement
    # @property {str}    col       -- the first column extracted from the match
    #
    # @var {str}  regex -- the regular expression for the select statement
    # @var {str}  match -- the regular expression match
    # @var {list} cols  -- the columns list extracted from the match
    ##
    def __init__(self, parent, sql, data_bind):
        # Regular expression
        regex = f'''SELECT.*?FROM'''
        
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
    # @return {dict}
    ##
    def first(self):
        if self.all():
            return self.all()[0]
        else:
            return False


    ##
    # @desc Fetches the last row
    #
    # @return {dict}
    ##
    def last(self):
        if self.all()[self.count()-1]:
            return self.all()[self.count()-1]
        else:
            return False


    ##
    # @desc Fetches all the rows
    #
    # @return {list}
    ##
    def all(self):
        # Postgres
        if self.db_system == 'Postgres':
            return real_dict(self.query(self.sql, self.data_bind).fetchall())

        # SQLite or MySQL
        elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
            return self.query(self.sql, self.data_bind).fetchall()


    ##
    # @desc Counts the number of rows
    #
    # @return {int}
    ##
    def count(self):
        return len(self.all())


    ##
    # @desc Fetches the minimum of the first given column (must be of type int or float)
    #
    # @param {int} option -- Optional -- 0(@return int|float) 1(@return dict) 2 (@return list)
    #
    # @return {int|float|dict|list}
    ##
    def min(self, option=0):
        # Prepare the sql query
        sql = re.sub(self.regex, f'''SELECT min({self.col}) as {self.col} FROM''', self.sql)

        # Return the first match as a dictionary
        if option == 1:
            # Postgres
            if self.db_system == 'Postgres':
                return real_dict(self.query(sql, self.data_bind).fetchall())[0]

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchone()

        # Return the matches as a list
        elif option == 2:
            # Postgres
            if self.db_system == 'Postgres':
                return real_dict(self.query(sql, self.data_bind).fetchall())

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchall()

        # Return the first match result as the number (default)
        else:
            # Produce final column
            col = delete_chars(self.col, "'")
            col = delete_chars(col, "`")
            col = delete_chars(col, '"')

            return self.query(sql, self.data_bind).fetchone()[col]


    ##
    # @desc Fetches the maximum of the first given column (must be of type int or float)
    #
    # @param {int} option -- Optional -- 0(@return int|float) 1(@return dict) 2 (@return list)
    #
    # @return {int|float|dict|list}
    ##
    def max(self, option=0):
        # Prepare the sql query
        sql = re.sub(self.regex, f'''SELECT max({self.col}) as {self.col} FROM''', self.sql)

        # Return the first match as a dictionary
        if option == 1:
            # Postgres
            if self.db_system == 'Postgres':
                return real_dict(self.query(sql, self.data_bind).fetchall())[0]

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchone()

        # Return the matches as a list
        elif option == 2:
            # Postgres
            if self.db_system == 'Postgres':
                return real_dict(self.query(sql, self.data_bind).fetchall())

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchall()

        # Return the first match result as the number (default)
        else:
            # Produce final column
            col = delete_chars(self.col, "'")
            col = delete_chars(col, "`")
            col = delete_chars(col, '"')

            return self.query(sql, self.data_bind).fetchone()[col]


    ##
    # @desc Fetches the average of the first given column (must be of type int or float)
    #
    # @param {int} option -- Optional -- 0(@return float) 1(@return dict)
    #
    # @return {float}
    ##
    def avg(self, option=0):
        # Prepare the sql query
        sql = re.sub(self.regex, f'''SELECT avg({self.col}) as {self.col} FROM''', self.sql)

        # Return the first match as a dictionary
        if option == 1:
            # Postgres
            if self.db_system == 'Postgres':
                return real_dict(self.query(sql, self.data_bind).fetchall())[0]

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchone()

        # Return the first match result as the number (default)
        else:
            # Produce final column
            col = delete_chars(self.col, "'")
            col = delete_chars(col, "`")
            col = delete_chars(col, '"')

            return self.query(sql, self.data_bind).fetchone()[col]


    ##
    # @desc Fetches the summary of the first given column (must be of type int or float)
    #
    # @param {int} option -- Optional -- 0(@return int|float) 1(@return dict)
    #
    # @return {int|float}
    ##
    def sum(self, option=0):
        # Prepare the sql query
        sql = re.sub(self.regex, f'''SELECT sum({self.col}) as {self.col} FROM''', self.sql)

        # Return the first match as a dictionary
        if option == 1:
            # Postgres
            if self.db_system == 'Postgres':
                return real_dict(self.query(sql, self.data_bind).fetchall())[0]

            # SQLite or MySQL
            elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
                return self.query(sql, self.data_bind).fetchone()

        # Return the first match result as the number (default)
        else:
            # Produce final column
            col = delete_chars(self.col, "'")
            col = delete_chars(col, "`")
            col = delete_chars(col, '"')

            return self.query(sql, self.data_bind).fetchone()[col]


##############
# Join Class #
##############
##
# @desc Provides several methods for join methods of the Database class
##
class Join:
    ##
    # @desc Constructor method
    #
    # @param {class} parent    -- The Database Class
    # @param {str}   sql       -- The sql query string
    # @param {list}  data_bind -- The data to bind
    #
    # @property {str}    sql       -- the sql query string
    # @property {object} data_bind -- the data to bind
    # @property {method} query     -- the query method of the Database class
    # @property {str}    regex     -- the regular expression for the select statement
    # @property {str}    col       -- the first column extracted from the match
    #
    # @var {int}  regex -- the regular expression for the select statement
    # @var {int}  match -- the regular expression match
    # @var {list} cols  -- the columns list extracted from the match
    ##
    def __init__(self, parent, sql, data_bind):
        # Class properties
        self.sql = sql
        self.data_bind = data_bind
        self.query = parent.query
        self.db_system = parent.db_system


    ##
    # @desc Fetches the first row
    #
    # @return {dict}
    ##
    def first(self):
        if self.all():
            return self.all()[0]
        else:
            return False


    ##
    # @desc Fetches the last row
    #
    # @return {dict}
    ##
    def last(self):
        if self.all()[self.count()-1]:
            return self.all()[self.count()-1]
        else:
            return False


    ##
    # @desc Fetches all the rows
    #
    # @return {list}
    ##
    def all(self):
        # Postgres
        if self.db_system == 'Postgres':
            return real_dict(self.query(self.sql, self.data_bind).fetchall())

        # SQLite or MySQL
        elif self.db_system == 'SQLite' or self.db_system == 'MySQL':
            return self.query(self.sql, self.data_bind).fetchall()


    ##
    # @desc Counts the number of rows
    #
    # @return {int}
    ##
    def count(self):
        return len(self.all())
