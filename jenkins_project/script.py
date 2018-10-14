import sqlite3
import uuid
import datetime
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.jobs import Job

def get_server_instance(jenkins_url, user_name, password):
    jenkins_url = jenkins_url
    server = Jenkins(jenkins_url, username=user_name, password=password)
    return server


def get_job_status(jenkins_server, jobname):
    job = jenkins_server.get_job(jobname)
    job_status = {'desc':job.get_description(), 'running':job.is_running(), 'enabled': job.is_enabled()}

    return job_status

def record_sqlite(cursor, job_name, job_status):
    sql = '''INSERT INTO Jobs VALUES(?, ?, ?, ?, ?, ?)'''
    param = [
        str(uuid.uuid4()).replace('-', ''),
        job_name,
        job_status['desc'],
        job_status['running'],
        job_status['enabled'],
        datetime.datetime.now()
    ]
    cursor.execute(sql, param)
    print("success")

def connect_sqlite():
    conn = sqlite3.connect("jenkins_database.db")
    return conn

def create_table_jobs(cursor):
    sql = '''CREATE TABLE IF NOT EXISTS Jobs ( id uniqueidentifier, name  varchar(255), desc  varchar(255), running bit, enabled bit, time datetime, PRIMARY KEY (id));'''
    cursor.execute(sql)


if __name__ == "__main__":
    jenkins_server = get_server_instance("http://localhost:8080", "test", "test")

    conn = connect_sqlite()
    sqlite_cursor = conn.cursor()

    create_table_jobs(sqlite_cursor)



    for job in jenkins_server.get_jobs():
        print(get_job_status(jenkins_server, job[0]))
        record_sqlite(sqlite_cursor, job[0], get_job_status(jenkins_server, job[0]))

    conn.commit()
    conn.close()

