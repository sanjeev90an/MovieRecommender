import itertools
from psycopg2.pool import ThreadedConnectionPool


class DatabaseManager:
    """
    This class provides abstraction over underlying database.
    """
    
    
    def __init__(self, db_name="test_db", db_pass="", host="127.0.0.1" , port="5432"):
        self.connection_pool = ThreadedConnectionPool(10, 50, database=db_name, user="postgres", \
                                                       password=db_pass, host=host, port=port)
        

    def __execute_query(self, query):
        connection = self.connection_pool.getconn()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        self.connection_pool.putconn(connection)

    """
    Inserts multiple rows in table_name. column_headers contain tuple of table headers.
    rows contain the list of tuples where each tuple has values for each rows. The values in 
    tuple are ordered according to column_headers tuple.
    """
    def insert_batch(self, table_name, column_headers, rows):
        query = "INSERT INTO {} {} VALUES {}".format(table_name, str(column_headers), str(rows)[1:-1])
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
        self.execute_query(query)
    
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
        for x, y in itertools.izip(column_names, values):
            result[x] = y
        self.connection_pool.putconn(connection)
        return result
    
    def fetch(self, query):
        pass
