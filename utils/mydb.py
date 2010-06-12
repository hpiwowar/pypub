from pysqlite2 import dbapi2 as db
from mylog import mylog

__all__ = ["MyDb", "get_cursor", "free"]

LOG_FILE_NAME = "info.log"

class MyDb(object):
    def __init__(self, dbname):
        self.conn = None
        self.active_cursor = None
        self.dbname = dbname
        
    def get_cursor(self):
        if not self.conn:
            try:
                self.conn = db.connect(self.dbname, isolation_level=None)
                self.active_cursor = self.conn.cursor()
            except Exception, e:
                mylog.info(e)
        return self.active_cursor
    
    def free(self):
        try:
            self.conn.commit()  # Should be superfluous since set up with isolation_level=None
            self.active_cursor.close()
            self.conn.close()
            self.conn = None
            self.active_cursor = None
        except Exception, e:
            mylog.info(e)


