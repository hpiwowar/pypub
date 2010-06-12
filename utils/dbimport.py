from pysqlite2 import dbapi2 as sqlite
import utils
import utils.shell

def get_table_create_command(table_name, data):
    command = "CREATE TABLE IF NOT EXISTS %s (" %table_name
    header_row = data[0]
    command += ", ".join(header_row)
    command += ")"
    return(command)

def get_table_insert_command(table_name, data):
    command = ""
    data_rows = data[1:]
    
    for row in data_rows:
        quoted_row = []
        for col in row:
            col_str = u"%s" %utils.unicode.clean_up_strange_unicode(col)
            #col_str = u"%u" %col
            # Sqlite escapes a single quote with two single quotes
            col_str = col_str.replace("'", "''")
            col_str = u"'%s'" %col_str
            quoted_row.append(col_str)
        command += u"INSERT OR REPLACE INTO %s VALUES (" %table_name
        command += u", ".join(quoted_row)
        command += u"); "
        
    return(command)
    
def trunc_table(db_name, table_name, verbose=False):
    trunc_command = "DELETE FROM %s; VACUUM;" %table_name
    db_response = utils.shell.run_in_sqlite(db_name, trunc_command, verbose)
    if verbose:
        print db_response
    return(None)

def drop_table(db_name, table_name, verbose=False):
    trunc_command = "DROP TABLE IF EXISTS %s; VACUUM;" %table_name
    db_response = utils.shell.run_in_sqlite(db_name, trunc_command, verbose)
    if verbose:
        print db_response
    return(None)
            
def write_to_db(db_name, table_name, data, verbose=False):
    
    table_create_command = get_table_create_command(table_name, data)
    db_response = utils.shell.run_in_sqlite(db_name, table_create_command, verbose)
    print db_response
    
    table_insert_command = get_table_insert_command(table_name, data)
    db_response = utils.shell.run_in_sqlite(db_name, table_insert_command, verbose)    
    print db_response
        
    return(None)

def get_connection(db_name=":memory:"):
    connection = sqlite.connect(db_name)
    return(connection)
    
def execute_python_db(connection, command, verbose=True):
    cursor = connection.cursor()  
    if verbose:
        print command
    cursor.executescript(command)
    connection.commit()
    return(cursor)
        
def write_to_python_db(connection, table_name, data, verbose):
    cursor = connection.cursor()  
    table_create_command = get_table_create_command(table_name, data)
    if verbose:
        print table_create_command
    cursor.execute(table_create_command)
    
    question_marks = ",".join(['?' for i in range(row)])
    if verbose:
        print table_create_command    
    cursor.execute('INSERT INTO ' + TABLE_NAME + ' VALUES (' + question_marks + ')' , row)
    connection.commit()
    return cursor

# From 
# http://code.activestate.com/recipes/457661/
# Example of use:
#    insert_dict = {'drink':'horchata', 'price':10}
#    sql = get_table_insert_command_from_dict("lq", insert_dict)
#    cursor.execute(sql, insert_dict)
def get_table_insert_command_from_dict(table, dict):
    """Take dictionary object dict and produce sql for 
    inserting it into the named table"""
    sql = 'INSERT OR REPLACE INTO ' + table
    sql += ' ('
    sql += ','.join(dict.keys())
    sql += ') VALUES ('
    sql += ','.join(map(wrap_with_strings, dict.values()))
    sql += ');'
    return sql

def wrap_with_strings(val):
    if val is None:
        return '""'
    if type(val) is str:
        val = val.replace("'", "").replace('"', "")
        wrapped = '"' + str(val) + '"'
        return wrapped
    return(str(val))

