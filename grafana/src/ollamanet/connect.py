# connect to mysql database
import mysql.connector

class database:
    def __init__(self, ip, port, user, pwd, database) -> None:
        self.conn = mysql.connector.connect(
            host = ip,
            port = port,
            user = user,
            password = pwd,
            database = database
        )
        self.cursor = self.conn.cursor()
    def exec(self, cmd: str):
        self.cursor.execute(cmd)
        result = self.cursor.fetchall()
        self.conn.commit()
        return result



if __name__ == '__main__':
    db = database(
        ip="127.0.0.1",
        port=3306,
        user="node1",
        pwd="mysql114514",
        database="grafana",
    )