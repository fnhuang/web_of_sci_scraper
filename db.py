import pymysql


server = "localhost"
username = "root"
password = "GamPoPa1209"
database = "biblio"

def getConnection():
    bibdb = pymysql.connect(host=server,
                            user=username,
                            password=password,
                            db=database,
                            charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor)
    return bibdb


def read(statement):
    bibdb = pymysql.connect(host=server,
                            user=username,
                            password=password,
                            db=database,
                            charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor)
    try:
        with bibdb.cursor() as cursor:
            # Read a single record
            cursor.execute(statement)
            results = cursor.fetchall()
            return results

    finally:
        bibdb.close()



