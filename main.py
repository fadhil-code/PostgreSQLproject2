import asyncio, psycopg2
import asyncpg
import paramiko, os

def check_pinging(host):
    res = os.system("ping " + host)
    return res
def make_iptables_conn():
    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(hostname='127.0.0.1',
               username='root',
               password='root',
               port=32)
    stin, stout, sterr = cl.exec_command('s.sh')
    cl.close()
async def insert_vals_function():
    if check_pinging("127.0.0.1") == 0:
        conn = psycopg2.connect(dbname='mypsotgaredb',
                                user='postgres',
                                password='root',
                                host='127.0.0.1')
        c = conn.cursor()
        sqlcode = 'create table mytable (id int, time time);'
        (c.execute(sqlcode))
    if check_pinging("192.168.0.2") == 0:
        conn = await asyncpg.connect(database='mypsotgaredb',
                                     user='replicant',
                                     password='root',
                                     host='192.168.0.2',
                                     command_timeout='2')
        i = 0
        try:

            while i < 1000:
                async with conn.transaction():
                    sqlcode=f"insert into mytable (id, time) VALUES ('{i}', 'now()');"
                    await conn.execute(sqlcode)
                if i == 500:
                    make_iptables_conn()
                i = i + 1
            print(f"{i} vals inserted...")
        except:
            print("Something went wrong")
        finally:
            print("The 'try except' is finished")
        return (i)
#recods=insert_vals_function()
event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(insert_vals_function())
def computing_function():
    try:

        while check_pinging("192.168.0.2") == 0:
            conn1 = psycopg2.connect(dbname='mypsotgaredb',
                                   user='replicant',
                                   password='root',
                                   host='192.168.0.2')
            c1 = conn1.cursor()
            sqlcode = 'select count(*) from mytable;'
            c1.execute(sqlcode)
            count = c1.fetchone()
            conn2 = psycopg2.connect(dbname='mypsotgaredb',
                                     user='replicant',
                                     password='root',
                                     host='192.168.0.3')
            c2 = conn2.cursor()
            c2.execute(sqlcode)
            count2 = c2.fetchone()
            print(f"({count[0]}) records In the first database. ")
            print(f"({count2[0]}) records In the second database.")
            print(f"  {(count[0]-count2[0])} errors... ")
    except:
        print("Something went wrong")
    finally:
        print("The 'try except' is finished")
computing_function()
