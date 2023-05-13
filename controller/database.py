import pymysqlpool
from pymysql import cursors
#pymysqlpool.logger.setLevel('DEBUG')
config ={'host':'database-1.cedn2xc6oolp.ap-northeast-2.rds.amazonaws.com','port':3306,'user':'ruddls030','password':'dlstn0722!','db':'food','autocommit':True}

def __init__():
    global pool1
    pool1 = pymysqlpool.ConnectionPool(size=2, pre_create_num=2, name='pool1', **config)

def execute_sql(sql:str):
    global pool1
    con = pool1.get_connection()
    cursor = con.cursor(cursors.DictCursor)
    with cursor as cur:

        def get(sql):
            cur.execute(sql)
            try:
                con.close()
                res = cur.fetchall()
                return res
            except pymysqlpool.ReturnConnectionToPoolError:
                res = cur.fetchall()
                return res

        
        def edit(sql):
            res = cur.execute(sql)
            try:
                con.close()
                return res
            except pymysqlpool.ReturnConnectionToPoolError:
                return res
                
           

        if "SELECT" in sql or "select" in sql:
            return get(sql)
        else:
            return edit(sql)