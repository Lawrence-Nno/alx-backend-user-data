#!/usr/bin/env python3
"""A func called filter_datum that returns the log message obfuscated"""
import re
from typing import List, Optional
import logging
import mysql.connector as myc
import os


PII_FIELDS: List = ['name', 'email', 'phone', 'ssn', 'password']


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]) -> None:
        super(RedactingFormatter, self).__init__(self.FORMAT)
        
    def format(self, record: logging.LogRecord) -> str:
        NotImplementedError


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """This func returns log message obfuscated"""
    for field in fields:
        message = re.sub(f'{field}=(.*?){separator}',
                         f'{field}={redaction}{separator}',
                         message)
    return message


def get_logger() -> logging.Logger:
    """This func returns logging.Logger object"""
    userDataLogger: logging.Logger = logging.getLogger('user_data')
    userDataLogger.setLevel(logging.INFO)
    userDataLogger.propagate = False
    streamHandler: logging.StreamHandler = logging.StreamHandler()
    streamHandler.setFormatter(RedactingFormatter(PII_FIELDS))
    userDataLogger.addHandler(streamHandler)
    return userDataLogger


def get_db() -> myc.connection.MySQLConnection:
    """This func returns MySQLConnection object"""
    user: Optional[str] = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    password: Optional[str] = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    host: Optional[str] = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    dbName: Optional[str] = os.getenv('PERSONAL_DATA_DB_NAME')
    cnx: myc.connection.MySQLConnection = myc.connect(
        user=user,
        password=password,
        host=host,
        database=dbName
    )
    return cnx


def main() -> None:
    """This func gets data"""
    logger = get_logger()
    cnx = get_db()
    cursor = cnx.cursor()
    cursor.execute('SELECT * FROM users;')
    for (name, email, phone, ssn, password) in cursor:
        logger.info(';'.join([name, email, phone, ssn, password]) + ';')
    cursor.close()
    cnx.close()


if __name__ == "__main__":
    main()
