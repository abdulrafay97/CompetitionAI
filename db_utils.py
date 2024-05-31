import pyodbc
import os

from datetime import datetime
from datetime import datetime, timedelta
from dotenv import load_dotenv
from general_utils import *
load_dotenv()

sql_server_name = os.getenv('SQL_HOST')
sql_database_name = os.getenv('DATABASE')
sql_username = os.getenv('USERID')
sql_password = os.getenv('PASSWORD')


def connect_DB():
    try:
        server_name = sql_server_name
        database_name = sql_database_name
        username = sql_username
        password = sql_password

        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password}'

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        return cursor, conn
    except Exception as e:
        pass


def email_exists(email, cursor):
    select_sql = "SELECT COUNT(*) FROM UserDetails WHERE Email = ?"
    cursor.execute(select_sql, email)
    count = cursor.fetchone()[0]
    return count > 0


def insert_User(first_name, last_name, email, hashed_password, company, position, cursor, conn):
    if email_exists(email, cursor):
        return False
    
    insert_sql = "INSERT INTO UserDetails (FirstName, LastName, Email, Password, Company, Position, Validity, IsActive, Role, CreatedDate, IsRejected, IsVerified) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    try:
        cursor.execute(insert_sql, first_name, last_name, email, hashed_password, company, position, False, False, 2, datetime.now(), False, False)
        conn.commit()
        if update_verification_bit(email, cursor, conn):
            return True
        else:
            return False
    except pyodbc.Error as e:
        conn.rollback() 
        return False


def add_verification_code(email, verification_code, cursor, conn):
    insert_sql = "INSERT INTO verification (email, verification_code, date) VALUES (?, ?, ?)"

    try:
        cursor.execute(insert_sql, email, verification_code, datetime.now())
        conn.commit()
        return True
    except pyodbc.Error as e:
        conn.rollback() 
        return False
    

def verify_Signup(email, verification_code, cursor, conn):
    query = f"SELECT TOP 1 * FROM verification WHERE email = '{email}' ORDER BY Date Desc;"

    try:
        cursor.execute(query)
        data = cursor.fetchone()
        
        if (datetime.now() - data[3]).total_seconds() < 100:
            if (data[2] == str(verification_code)):
                return True
            else:
                return False
        else:
            return False
    except:
        return False
    

def update_verification_bit(email, cursor, conn):
    update_sql = f"Update UserDetails set IsVerified = 1 where email = '{email}'"

    try:
        cursor.execute(update_sql)
        conn.commit()
        return True
    except pyodbc.Error as e:
        conn.rollback() 
        return False

    
def login_user(email, password, cursor):
    query = f"SELECT * FROM UserDetails WHERE Email = '{email}' and Password = '{password}' and Validity = 1 and IsActive = 1 and IsRejected = 0 and IsVerified = 1"
    try:
        cursor.execute(query)
        data = cursor.fetchone()
    
        return data
    except:
        return False


def update_login_details(user_id, cursor, conn):
    insert_sql = "INSERT INTO LoginDetails (UserId, LoginDate) VALUES (?, ?)"

    try:
        cursor.execute(insert_sql, user_id, datetime.now())
        conn.commit()
        return True
    except pyodbc.Error as e:
        conn.rollback() 
        return False

def get_specified_users(bit, cursor):
    query = f"SELECT * FROM UserDetails WHERE Validity = '{bit}' and IsRejected = 0 and Role = 2 and IsVerified = 1"
    
    try:
        cursor.execute(query)
        data = cursor.fetchall()

        my_list = list()
    
        for i in data:
            my_dict = {}
            my_dict["UserId"] = i[0]
            my_dict["Name"] = i[1] +" "+ i[2]
            my_dict["Email"] = i[3]
            my_dict["Company"] = i[5]
            my_dict["Position"] = i[6]
            my_dict["Created Date"] = str(i[8])
            my_dict["Logged In"] = get_logged_In_details(int(i[0]), cursor)
            my_dict["Searched"] = get_searched_for_details(int(i[0]), cursor)

            my_list.append(my_dict)
        return my_list
    except:
        return False


def get_logged_In_details(user_id, cursor):
    query = f"SELECT UserId, COUNT(*) AS LoginCount FROM LoginDetails where userid = '{user_id}' GROUP BY UserId"
    try:
        cursor.execute(query)
        data = cursor.fetchone()
        
        return data[1]
    except:
        return False
    
def get_searched_for_details(user_id, cursor):
    query = f"SELECT UserId, COUNT(*) AS SearchCount FROM QueryDetails WHERE USERiD = '{user_id}' GROUP BY UserId"
    try:
        cursor.execute(query)
        data = cursor.fetchone()
        
        return data[1]
    except:
        return False

def update_validity(user_id, cursor, conn):
    update_sql = f"Update UserDetails set Validity = 1, IsActive = 1 where UserId = '{user_id}'"

    try:
        cursor.execute(update_sql)
        conn.commit()
        if grant_queries(user_id, cursor, conn):
            return True
        else:
            return False
    except pyodbc.Error as e:
        conn.rollback() 
        return False


def grant_queries(user_id, cursor, conn):
    insert_sql = "INSERT INTO UserQueries (UserId, QueryNumber, QueryStartingDate, QueryEndingDate) VALUES (?, ?, ?, ?)"

    try:
        cursor.execute(insert_sql, user_id, 15, str(datetime.now().date()), str(datetime.now().date() + timedelta(days=7)))
        conn.commit()
        return True
    except pyodbc.Error as e:
        conn.rollback() 
        return False
    

def check_queries(user_id, cursor):
    query = f"SELECT * FROM UserQueries WHERE UserId = '{user_id}'"
    try:
        cursor.execute(query)
        data = cursor.fetchone()
        my_dict = {}
        my_dict["Number_of_Queries"] = data[2]
        my_dict["Ending_Date"] = str(data[4])

        return my_dict
    except:
        return False
    

def get_last_entered_id(cursor, user_id):
    query = f"SELECT TOP 1 id FROM QueryDetails where userid = '{user_id}' ORDER BY id DESC "
    try:
        cursor.execute(query)
        data = cursor.fetchone()

        return data[0]
    except:
        return False 


def add_query_details(user_id, query, query_answer, number_of_queries, sources_and_response, vectorstore, cursor, conn):
    insert_sql = "INSERT INTO QueryDetails (UserId, Query, QueryAnswer, Vectorstore) VALUES (?, ?, ?, ?)"

    try:
        cursor.execute(insert_sql, user_id, query, query_answer, vectorstore)
        conn.commit()
        update_number_of_queries(user_id, number_of_queries, cursor, conn)
        add_query_with_source_and_response(user_id, sources_and_response, conn, cursor)
        add_query_db_details(user_id, vectorstore, cursor, conn)
        return True
    except pyodbc.Error as e:
        conn.rollback() 
        return False
    

def add_query_with_source_and_response(userId, sources_and_response, conn, cursor):

    for i in sources_and_response:
        insert_sql = "INSERT INTO UserQuerySource (UserId, queryId, source, text) VALUES (?, ?, ?, ?)"

        try:
            cursor.execute(insert_sql, userId, get_last_entered_id(cursor, userId), i['Source'], i['Text'])
            conn.commit()
        except Exception as e:
            conn.rollback()  
            return False
    return True
    

def update_number_of_queries(user_id, number_of_queries, cursor, conn):
    update_sql = f"Update UserQueries set QueryNumber = '{number_of_queries}' where UserId = '{user_id}'"

    try:
        cursor.execute(update_sql)
        conn.commit()
        return True
    except pyodbc.Error as e:
        conn.rollback()  
        return False
    

def add_query_db_details(userid, vectorstore, cursor, conn):
    insert_sql = "INSERT INTO query_db_details (userId, db_Name, CreatedDate) VALUES (?, ?, ?)"

    try:
        cursor.execute(insert_sql, userid, vectorstore, datetime.now().date())
        conn.commit()
        return True
    except Exception as e:
        conn.rollback() 
        return False
    

def my_cron_job(cursor, conn):
    update_sql = f"Update UserQueries set QueryNumber = 15, QueryStartingDate = '{datetime.now().date()}', QueryEndingDate = '{str(datetime.now().date() + timedelta(days=7))}' where QueryEndingDate = '{datetime.now().date()}'"

    try:
        cursor.execute(update_sql)
        conn.commit()
        return True
    except pyodbc.Error as e:
        conn.rollback() 
        return False
    

def user_deletion(userid, cursor, conn):
    update_sql = f"Update UserDetails set IsActive = 0 where userId = '{userid}'"

    try:
        cursor.execute(update_sql)
        conn.commit()
        return True
    except pyodbc.Error as e:
        conn.rollback() 
        return False
    

def reject_user(userid, cursor, conn):
    update_sql = f"Update UserDetails set IsRejected = 1 where userId = '{userid}'"

    try:
        cursor.execute(update_sql)
        conn.commit()
        return True
    except pyodbc.Error as e:
        conn.rollback() 
        return False


def get_query_history(vectorstore, cursor):
    query = f"SELECT id, Query, QueryAnswer FROM QueryDetails WHERE Vectorstore = '{vectorstore}'"

    try:
        cursor.execute(query)
        data = cursor.fetchall()

        my_list = list()

        for i in data:
            my_dict = {}
            my_dict["queryId"] = i[0]
            my_dict["query"] = i[1]
            my_dict["queryAnswer"] = i[2]

            data1 = get_source_and_text(i[0], cursor)

            nested_list = []
            for index, j in enumerate(data1):
                nested_dict = {}
                nested_dict["Source " + str(index)] = j[0]
                nested_dict["text " + str(index)] = j[1]
                nested_list.append(nested_dict)

            my_dict["Sources_and_text"] = nested_list
            my_list.append(my_dict)

        return my_list
    except Exception as e:
        return e



def get_source_and_text(queryid, cursor):
    query = f"SELECT source, text FROM UserQuerySource WHERE queryId = '{queryid}'"
    
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    except Exception as ex:
        return ex
    

def get_user_query_history(userid, cursor):
    query = f"SELECT id, Query, QueryAnswer FROM QueryDetails WHERE UserId = '{userid}'"

    try:
        cursor.execute(query)
        data = cursor.fetchall()

        my_list = list()

        for i in data:
            my_dict = {}
            my_dict["queryId"] = i[0]
            my_dict["query"] = i[1]
            my_dict["queryAnswer"] = i[2]

            data1 = get_source_and_text_with_user(userid, i[0], cursor)

            nested_list = []
            for index, j in enumerate(data1):
                nested_dict = {}
                nested_dict["Source " + str(index)] = j[0]
                nested_dict["text " + str(index)] = j[1]
                nested_list.append(nested_dict)

            my_dict["Sources_and_text"] = nested_list
            my_list.append(my_dict)

        return my_list
    except Exception as e:
        return e



def get_source_and_text_with_user(userid , queryid, cursor):
    query = f"SELECT source, text FROM UserQuerySource WHERE UserId = '{userid}' and queryId = '{queryid}'"
    
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    except Exception as ex:
        return ex


def get_usage_of_db_with_timeline(timeline, cursor):
    query = f"""
        SELECT 
        db_Name,
        ROUND(CAST((COUNT(*) * 100.0) / 
            (SELECT COUNT(*) 
                FROM query_db_details
                WHERE CreatedDate >= DATEADD(DAY, -{timeline}, GETDATE())
            ) AS DECIMAL(10, 2)), 2) AS value_percentage
    FROM query_db_details
    WHERE CreatedDate >= DATEADD(DAY, -{timeline}, GETDATE())
    GROUP BY db_Name;
    """
    
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        
        db_name = list()
        db_usage = list()

        for i in data:
           db_name.append(i[0])
           db_usage.append(float(i[1]))

        my_dict = {}

        my_dict["DB_Name"] = db_name
        my_dict["DB_Usage"] = db_usage

        return my_dict
    except:
        return False
    

def get_usage_of_db_without_timeline(cursor):
    query = f"""
            SELECT 
        db_Name,
        ROUND(CAST((COUNT(*) * 100.0) / 
            (SELECT COUNT(*) 
                FROM query_db_details
            ) AS DECIMAL(10, 2)), 2) AS value_percentage
    FROM query_db_details
    GROUP BY db_Name;
    """
    
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        
        db_name = list()
        db_usage = list()

        for i in data:
           db_name.append(i[0])
           db_usage.append(float(i[1]))

        my_dict = {}

        my_dict["DB_Name"] = db_name
        my_dict["DB_Usage"] = db_usage

        return my_dict
    except:
        return False
