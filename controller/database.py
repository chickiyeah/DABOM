from pymysqlpool.pool import Pool
config = {
    'host':"database-1.cedn2xc6oolp.ap-northeast-2.rds.amazonaws.com",
    'port':3306,
    'user':'ruddls030',
    'password':'dlstn0722!',
    'db':'food',
    'autocommit': True
}

def __init__():
    global pool
    pool = Pool(host='database-1.cedn2xc6oolp.ap-northeast-2.rds.amazonaws.com',port=3306,user='ruddls030',password='dlstn0722!',db='food',autocommit=True)
    pool.init()
    global connection
    connection = pool.get_conn()
    print('DB connection established')

def execute_sql(sql: str):
    cur = connection.cursor()
    def get(sql):
        cur.execute(sql)
        return cur.fetchall()
    
    def insert(sql):
        res = cur.execute(sql)
        return res

    if "SELECT" in sql or "select" in sql:
        res = get(sql)

    return res