import sqlite3
from os import path
from ceac_tracker.utils.my_logging import get_logger

logger = get_logger(__file__)
db_root = path.dirname(__file__)

conn = sqlite3.connect(path.join(db_root, "data.db"))
cursor = conn.cursor()


def get_all_applications():
    global cursor
    res = cursor.execute("SELECT application_id, location, case_created, notification_email FROM application")
    return res.fetchall()


def get_all_records(application_id):
    global cursor
    res = cursor.execute("SELECT update_date, status, description FROM history WHERE application_id=? ORDER BY timestamp DESC", (application_id,))
    return res.fetchall()


def add_application(application_id, location, case_created, notification_email):
    global cursor, conn
    res = cursor.execute("INSERT INTO application(application_id, location, case_created, notification_email) VALUES(?, ?, ?, ?)", (application_id, location, case_created, notification_email))
    conn.commit()


def add_record(application_id, update_date, status, description):
    global cursor, conn
    res = cursor.execute(
        "INSERT INTO history(application_id, update_date, status, description) VALUES(?, ?, ?, ?)", (application_id, update_date, status, description)
    )
    conn.commit()


if __name__ == "__main__":
    with open(path.join(db_root, "ddl.sql"), "r") as ddl:
        sql = ddl.read()
        cursor.executescript(sql)
        conn.commit()
    add_application("AA00BHESAN", "TRT", "05-Dec-2022", "wu.hao.cz.21@gmail.com")
