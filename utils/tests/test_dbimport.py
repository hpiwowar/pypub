import utils
import utils.dbimport
import utils.shell
from nose.tools import assert_equals

DB_NAME = "temp.db"
TABLE_NAME = "temp_table"

data = [["header"+str(i) for i in range(5)], range(5), range(5,10)]


def teardown():
    utils.shell.run_in_shell("rm %s" %(DB_NAME))
    
def test_table_create_command():
    command = utils.dbimport.get_table_create_command(TABLE_NAME, data)
    gold_response = "CREATE TABLE IF NOT EXISTS temp_table (header0, header1, header2, header3, header4)"
    assert_equals(command, gold_response)

def test_table_insert_command():
    command = utils.dbimport.get_table_insert_command(TABLE_NAME, data)
    gold_response = 'INSERT OR REPLACE INTO temp_table VALUES (0, 1, 2, 3, 4); INSERT INTO temp_table VALUES (5, 6, 7, 8, 9); '
    assert_equals(command, gold_response)

def test_dbimport():
    response = utils.dbimport.write_to_db(DB_NAME, TABLE_NAME, data, verbose=True)
    db_response = utils.shell.run_in_sqlite(DB_NAME, "select * from " + TABLE_NAME, verbose=True)
    gold_response = '0|1|2|3|4\n5|6|7|8|9\n'
    assert_equals(db_response, gold_response)

@notimplemented
def test_dbimport_2():
    connection = get_connection()
    response = utils.dbimport.write_to_python_db(connection, TABLE_NAME, data, verbose=True)
    db_response = utils.shell.run_in_sqlite(DB_NAME, "select * from " + TABLE_NAME, verbose=True)
    gold_response = '0|1|2|3|4\n5|6|7|8|9\n'
    assert_equals(db_response, gold_response)
