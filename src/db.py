from __future__ import (annotations)
from datetime import date  # allows for return self enclosing class type as return value type hint

import sqlite3 as sl
from sqlite3.dbapi2 import Connection, IntegrityError
from models import CodeRepository

_table_name = "repos"


def _helper_make_schema(con: Connection):
  """Makes a schema if tables/objects do not exist"""

  con.executescript(
      """
          BEGIN;

          CREATE TABLE IF NOT EXISTS %s (
              id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
              license TEXT,
              url TEXT NOT NULL UNIQUE,
              owner TEXT NOT NULL,
              name TEXT NOT NULL,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
          );

          COMMIT;
      """
      % _table_name
  )


class Db(object):
  _instance = None

  def __new__(cls):
    if cls._instance is None:
      cls._instance = object.__new__(cls)

      try:
        print('connecting to database...')
        # a new sqlite connection and schema for this database
        cls.connection = sl.connect("database.db")

        # initialize the schema, if needed
        _helper_make_schema(cls.connection)

      except Exception as error:
        print('Error: connection not established {}'.format(error))
        Db._instance = None

      else:
        print('connection established!')

    return cls._instance

  def __init__(self):
    self.connection = self._instance.connection

  def select_by_date(self, begin: date, end: date):
    """ Select and return a respository by its url """

    cursor = self.connection.execute(f"SELECT * FROM {_table_name} WHERE timestamp >= 2015-01-01")

    return map(lambda row: CodeRepository.from_row(row), cursor.fetchall())

  def upsert(self, repo: CodeRepository):
    """ Insert or update a database record based on url conflict """

    self.connection.execute(
        f"""
            INSERT OR IGNORE INTO {_table_name} (license, url, owner, name) VALUES(?, ?, ?, ?)
          """,
        (repo.license, repo.url, repo.owner, repo.name),
    )

  def commit(self):
    """ Commit changes to the database file """

    self.connection.commit()

  def __del__(self):
    self.connection.close()
