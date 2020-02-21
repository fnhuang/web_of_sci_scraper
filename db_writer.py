import db_reader
import pymysql

class DbWriter():
    server = "localhost"
    username = "secret"
    password = "secret"
    database = "biblio"

    def __init__(self):
        self.connection = None

    def connect(self):
        if self.connection is None or not self.connection.open:
            self.connection = pymysql.connect(host=self.server,
                            user=self.username,
                            password=self.password,
                            db=self.database,
                            charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor,
                            autocommit=False)

    def commit(self):
        self.connection.commit()

    def close(self):
        if self.connection.open:
            self.connection.close()


    def update_crawl_progress(self, search_id, start_doc, total_doc, doc_num, percent_crawled):
        sql_statement = 'UPDATE crawl_progress SET total_doc = %s, doc_num = %s, percent_crawled = %s ' \
                        'WHERE (search_id = %s) and (start_doc = %s)'\
                        %(total_doc, doc_num, percent_crawled, search_id, start_doc)
        self.connection.cursor().execute(sql_statement)




