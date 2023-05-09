import pymysqlpool
from pymysql import cursors
pymysqlpool.logger.setLevel('DEBUG')
config ={'host':'database-1.cedn2xc6oolp.ap-northeast-2.rds.amazonaws.com','port':3306,'user':'ruddls030','password':'dlstn0722!','db':'DELIENG','autocommit':True}

def __init__():
    global pool1
    pool1 = pymysqlpool.ConnectionPool(size=20, maxsize= 100, pre_create_num=20, name='pool1', **config)

def execute_sql(sql:str):
    global pool1
    con = pool1.get_connection().cursor(cursors.DictCursor)
    with con as cur:

        def get(sql):
            cur.execute(sql)
            return cur.fetchall()
        
        def edit(sql):
            res = cur.execute(sql)
            return res

        if "SELECT" in sql or "select" in sql:
            res = get(sql)
        else:
            res = edit(sql)

        con.close()
        
        print(res)

        return res