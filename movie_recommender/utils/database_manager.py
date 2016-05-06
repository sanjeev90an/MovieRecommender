import itertools
from psycopg2._psycopg import ProgrammingError, IntegrityError
from psycopg2.pool import ThreadedConnectionPool
from movie_recommender.utils.logging_utils import get_logger


class DatabaseManager:
    """
    This class provides abstraction over underlying database.
    """
    
    def __init__(self, db_name="test_db", db_pass="", host="127.0.0.1" , port="5432"):
        self.connection_pool = ThreadedConnectionPool(10, 50, database=db_name, user="postgres", \
                                                       password=db_pass, host=host, port=port)
        self.logger = get_logger()
        

    def __execute_query(self, query):
        connection = self.connection_pool.getconn()
        cursor = connection.cursor()
        self.logger.debug("Going to execute query {}".format(query))
        try:
            cursor.execute(query)
        except ProgrammingError:
            self.logger.error("Error occurred while executing query {}".format(query))
        except IntegrityError:
            self.logger.error("Query failed. Duplicate row for query {}".format(query))
        connection.commit()
        self.connection_pool.putconn(connection)

    """
    Inserts multiple rows in table_name. column_headers contain tuple of table headers.
    rows contain the list of tuples where each tuple has values for each rows. The values in 
    tuple are ordered according to column_headers tuple.
    """
    def insert_batch(self, table_name, column_headers, rows):
        query = "INSERT INTO {} {} VALUES {}".format(table_name, '(' + ','.join(column_headers) + ')', str(rows)[1:-1])
        self.__execute_query(query)

    """
    """
    def update(self, table_name, column_vs_value, uid):
        update_str = ''.join('{}={},'.format(key, val) for key, val in column_vs_value.items())[:-1]
        query = "UPDATE {} SET {} WHERE id = {} ".format(table_name, update_str, uid) 
        self.__execute_query(query)
    
    """
    """
    def delete_batch(self, table_name , uids):
        query = "DELETE from {} WHERE id in {}".format(table_name, str(uids))
        self.__execute_query(query)
    
    """
    """
    def get_row(self, table_name, uid):
        query = "Select * from {} where id = {}".format(table_name, uid)
        connection = self.connection_pool.getconn()
        cursor = connection.cursor()
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]
        values = cursor.fetchall()
        result = {}
        for x, y in itertools.izip(column_names, values[0]):
            result[x] = y
        self.connection_pool.putconn(connection)
        return result
    
    def get_all_values_for_attr(self, table_name, column_name):
        query = "Select distinct {} from {}".format(column_name, table_name)
        connection = self.connection_pool.getconn()
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        uids = [row[0] for row in rows]
        self.connection_pool.putconn(connection)
        return uids
    
    def get_all_rows(self, table_name, where_clause, limit=20):
        query = "Select * from {} where {} limit {}".format(table_name, where_clause, limit)
        connection = self.connection_pool.getconn()
        cursor = connection.cursor()
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result_row = {}
            for x, y in itertools.izip(column_names, row):
                result_row[x] = str(y)
            result.append(result_row)
        self.connection_pool.putconn(connection)
        return result
    
    """
    Gets a new connection from the pool and returns the connection object.
    """
    def get_connection(self):
        return self.connection_pool.getconn()
        
    """
    Releases the connection back to pool.
    """
    def release_connection(self, connection):
        self.connection_pool.putconn(connection)

db_manager = DatabaseManager(db_name="movie_recommender")
"""
Returns the db manger object. Everyone should access the same db manager object.
"""    
def get_db_manager():
    return db_manager
    
