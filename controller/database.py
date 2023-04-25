from pymysqlpool.pool import Pool

def __init__():
    global pool
    pool = Pool(host='database-1.cedn2xc6oolp.ap-northeast-2.rds.amazonaws.com',port=3306,user='ruddls030',password='dlstn0722!',db='food',autocommit=True)
    #MySQL 데이터베이스를 연결하고 변경사항이 생길때 자동으로 커밋하게 한다. 사용했던 회선을 재 사용함으로서 메모리 낭비가 발생하지 않도록 한다.
    pool.init()
    print('DB connection established')

def execute_sql(sql: str):
    connection = pool.get_conn()
    cur = connection.cursor()
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
    
    pool.release(connection)

    return res