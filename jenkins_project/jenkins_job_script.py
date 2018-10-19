import sqlite3
import uuid
import datetime
import argparse
from jenkinsapi.jenkins import Jenkins

def get_server_instance(jenkins_url, username, password):
    '''
    return Jenkins server using url, username and password
    :param jenkins_url: url to jenkins server
    :param username: name of jenkins user to login
    :param password: password for jenkins user
    :return: jenkins server object
    '''

    server = Jenkins(jenkins_url=jenkins_url, username=username, password=password)
    return server


def get_job_status(jenkins_server, jobname):
    '''
    retrive job status from given jenkins server
    :param jenkins_server: jenkins server object
    :param jobname: name of desired job
    :return: dictionary with job status {desc=string, running=bool, enabled=bool}
    '''

    job = jenkins_server.get_job(jobname)

    job_status = {
        'desc': job.get_description(),
        'running': job.is_running(),
        'enabled': job.is_enabled()
    }

    return job_status

def connect_sqlite():
    '''
    connect to sqlite database 'jenkins_database.db' and return connection object
    :return: sqlite connection object
    '''

    conn = sqlite3.connect("jenkins_database.db")
    return conn

def create_table_jobs(cursor):
    '''
    creates jobs table if not exist using cursor object of sqlite connection
    jobs table [id, name, desc, running, enabled, time]
    :param cursor: curser object of sqlite connection
    '''

    sql = '''CREATE TABLE IF NOT EXISTS Jobs ( id uniqueidentifier, name  varchar(255), desc  varchar(255), running bit, enabled bit, time datetime, PRIMARY KEY (id));'''
    cursor.execute(sql)

def record_sqlite(cursor, job_name, job_status):
    '''
    stroe record in jobs table in sqlite database
    :param cursor: cursor object of sqlite connection
    :param job_name: job name of jenkins jobs
    :param job_status: status for jenkins job {desc, running, enabled}
    '''

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


def parse_args():
    '''
    parse command-line arguments to get url, username and password for jenkins server
    or default values if no arguments specified
    :return: return tuple (url, username, password)
    '''
    parser = argparse.ArgumentParser(description="store jobs from jenkins to database")
    parser.add_argument('--url', help="url of jenkins server")
    parser.add_argument('--user', '--u', metavar='', help="username of jenkins server")
    parser.add_argument('--password', '--p', metavar='', help="password of jenkins server")

    args = parser.parse_args()

    url = args.url if args.url is not None else "http://localhost:8080"

    if sum(1 for elem in [args.user, args.password] if elem is not None) == 1:
        parser.error('--user and --password must be given together')

    user = args.user if args.user is not None else "test"
    password = args.password if args.password is not None else "test"

    return (url, user, password)

if __name__ == "__main__":

    # parse arguments
    (url, user, password) = parse_args()

    # connect to jenkins server
    jenkins_server = get_server_instance(jenkins_url=url, user_name=user, password=password)

    # connect to sqlite database
    conn = connect_sqlite()
    # cursor to use in queries
    sqlite_cursor = conn.cursor()
    # create jobs table if not exist
    create_table_jobs(sqlite_cursor)

    # loop through jenkins jobs and store its status
    for job in jenkins_server.get_jobs():
        print(job[0], get_job_status(jenkins_server, job[0]))
        # store job status
        record_sqlite(sqlite_cursor, job[0], get_job_status(jenkins_server, job[0]))

    # save database changes
    conn.commit()
    # close connection
    conn.close()

