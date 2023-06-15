import pyhive.exc
from pyhive import hive
from dotenv import load_dotenv
import os

load_dotenv()


# function to connect to Hive from Python
def connect_to_hive():
    # create connection to Hive
    connection = hive.Connection(
        host=os.getenv("HIVE_HOST"),
        port=os.getenv("HIVE_PORT")
    )
    return connection


# abstract function to execute queries in Hive
def execute_query(query, no_use=False, partition_mode=False, transaction_mode=False):
    error_message = None
    # create connection to Hive
    connection = connect_to_hive()
    # create cursor to execute queries
    cursor = connection.cursor()
    # execute query
    try:
        if no_use is False:
            cursor.execute("USE {}".format(os.getenv("HIVE_DATABASE")))
        if partition_mode is True:
            cursor.execute("SET hive.exec.dynamic.partition.mode=nonstrict")
        if transaction_mode is True:
            cursor.execute("SET hive.txn.manager = org.apache.hadoop.hive.ql.lockmgr.DbTxnManager")
            cursor.execute("SET hive.compactor.initiator.on = true")
            cursor.execute("SET hive.compactor.worker.threads = 1")
            cursor.execute("SET hive.enforce.bucketing = true")
            cursor.execute("SET hive.support.concurrency = true")
        cursor.execute(query)
    except pyhive.exc.Error as e:
        error_message = e.args[0].status.errorMessage

    # close connection
    connection.close()

    if error_message is not None:
        print(
            "Error while executing query: {} \nError message: {}".format(
                query,
                error_message
            )
        )
        raise Exception(error_message)
    else:
        print ("Query executed successfully : {} ".format(query))
        return True


def fetchResult(query, transaction_mode=False):
    column_names = None
    error_message = None
    result = None
    # create connection to Hive
    connection = connect_to_hive()
    # create cursor to execute queries
    cursor = connection.cursor()
    # execute query
    try:
        cursor.execute("USE {}".format(os.getenv("HIVE_DATABASE")))

        if transaction_mode is True:
            cursor.execute("SET hive.txn.manager = org.apache.hadoop.hive.ql.lockmgr.DbTxnManager")
            cursor.execute("SET hive.compactor.initiator.on = true")
            cursor.execute("SET hive.compactor.worker.threads = 1")
            cursor.execute("SET hive.enforce.bucketing = true")
            cursor.execute("SET hive.support.concurrency = true")

        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]
        result = cursor.fetchall()
    except pyhive.exc.Error as e:
        error_message = e.args[0].status.errorMessage

    # close connection
    connection.close()

    if error_message is not None:
        print(
            "Error while executing query: {} \nError message: {}".format(
                query,
                error_message
            )
        )
        raise Exception(error_message)
    else:
        print ("Query executed successfully : {} ".format(query))
        return result, column_names


# function to create database in Hive
def create_database():
    query = "CREATE DATABASE IF NOT EXISTS {}".format(os.getenv("HIVE_DATABASE"))
    if execute_query(query, True) is True:
        print("Database created successfully")
        return True
    else:
        print("Database creation failed")
        return False


# function to create tables in Hive
def create_tables(table_name, columns):
    query = "CREATE TABLE IF NOT EXISTS {}.{} ({}) " \
            "ROW FORMAT " \
            "DELIMITED FIELDS TERMINATED BY '\t' " \
            "COLLECTION ITEMS TERMINATED BY ',' " \
            "LINES TERMINATED BY '\n' " \
            "STORED AS TEXTFILE " \
            "tblproperties('skip.header.line.count'='1')" \
        .format(
        os.getenv("HIVE_DATABASE"),
        table_name,
        columns
    )

    print("Execute query: {}".format(query))
    if execute_query(query) is True:
        print("Table created successfully")
        return True
    else:
        print("Table creation failed")
        return False


# function to load data from TSV files to Hive
def load_data(table_name, columns, file_path):
    # create table in Hive
    if create_tables(table_name, columns) is True:
        # load data from TSV files to Hive
        query = "LOAD DATA LOCAL INPATH '/data/{}' OVERWRITE INTO TABLE {}.{} ".format(file_path, os.getenv(
            "HIVE_DATABASE"), table_name)
        print("Execute query: {}".format(query))
        if execute_query(query) is True:
            print("Data loaded successfully")
            return True
        else:
            print("Data loading failed")
            return False
