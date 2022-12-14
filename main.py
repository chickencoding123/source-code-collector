

from datetime import date

from src.models import ArchiveScrapeOptions, LiveScrapeOptions
from src.repo_live import find_repos as find_repos_live
from src.repo_archive import find_repos as find_repos_archive
from src.download import download_repo
from src.db import Db


def find_repos(licenseList: list[str], langList: list[str], beginPage: int | date, endPage: int | date):
  """Find matching repositories and save their information locally. Does not download source code."""

  if licenseList is None or langList is None or beginPage is None or endPage is None or len(licenseList) == 0 or len(langList) == 0:
    raise Exception('Missing one or more required parameters.')

  for license in licenseList:
    for lang in langList:
      if (type(beginPage).__name__ == 'date'):
        find_repos_archive(ArchiveScrapeOptions(license, lang, beginPage, endPage))
      else:
        find_repos_live(LiveScrapeOptions(license, lang, beginPage, endPage))


def download_repos(beginDate: date, endDate: date):
  """Download source code for the given timeframe by using previously saved information"""

  if beginDate is None or endDate is None:
    raise Exception('Missing one or more required parameters.')

  db = Db()
  repos = db.select_by_date(beginDate, endDate)

  for repo in repos:
    download_repo(repo.url)
