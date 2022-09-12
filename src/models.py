from __future__ import (annotations)  # allows for return self enclosing class type as return value type hint
from typing import Tuple
from datetime import date

class ScrapeOptions(object):
  """Base class for scraping options."""

  def __init__(self, license: str, lang: str):
    """Base class for scraping options.

    Args:
        license (str): License of a repo
        lang (str): Language tag of a repo
    """

    self.license = license
    self.lang = lang

class LiveScrapeOptions(ScrapeOptions):
  """ Options class for finding and scraping live repositories """

  def __init__(self, license: str, lang: str, begin: int = None, end: int = None):
    """Pagination is important if you wish to stop the program, but continue where you left off at a later time.

    Args:
        license (str): License of a repo
        lang (str): Language tag of a repo
        begin (int, optional): Where to being fetching (page start)
        end (int, optional): Where to stop fetching (page end)
    """
    
    self.license = license
    self.lang = lang
    self.begin = begin
    self.end = end

class ArchiveScrapeOptions(ScrapeOptions):
  def __init__(self, license: str, lang: str, begin: date = None, end: date = None):
    """Begin and end dates are important if you wish to stop the program, but continue where you left off at a later time.

    Args:
        license (str): License of a repo
        lang (str): Language tag of a repo
        begin (date, optional): Where to being fetching (start date)
        end (date, optional): Where to stop fetching (end date)
    """

    self.license = license
    self.lang = lang
    self.begin = begin
    self.end = end


class CodeRepository(object):
  """ Data model for the repository database """

  def __init__(self, id: int, license: str, url: str, owner: str, name: str):
    self.id = id
    self.license = license
    self.url = url
    self.owner = owner
    self.name = name

  @classmethod
  def from_rows(self, rows: list[Tuple]):
    ret_value = list[CodeRepository]()

    # multiple results vs one
    if isinstance(rows, list):
      for row in rows:
        ret_value.append(self.from_row(row))
    else:
      ret_value.append(self.from_row(rows))

    return ret_value

  @classmethod
  def from_row(self, row: Tuple):
    return CodeRepository(
      row[0],
      row[1],
      row[2],
      row[3],
      row[4]
    )
