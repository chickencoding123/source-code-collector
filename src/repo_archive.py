#! /usr/bin/env python3

from datetime import timedelta
import urllib3
import gzip
import json

from models import ArchiveScrapeOptions, CodeRepository
from db import Db


_http = urllib3.PoolManager()
_db = Db()


def _get_urls(scrapeOptions: ArchiveScrapeOptions, year: int, month: str, day: str, segment: int):
  url = """https://data.gharchive.org/%s-%s-%s-%s.json.gz""" % (year, month, day, segment)
  r = _http.request("GET", url)

  if r.status == 200:
    uncompressed = gzip.decompress(r.data)
    decoded = uncompressed.decode()
    lines = decoded.split("\n")
    targetLines = list()

    # filter for a specific language
    for line in lines:
      if line and line.lower().find(scrapeOptions.lang) > -1:
        targetLines.append(line)

    # save results
    if len(targetLines) > 0:
      for line in targetLines:
        json_obj = json.loads(line)
        splits = json_obj["repo"]["name"].split("/")

        _db.upsert(CodeRepository(
            None,
            scrapeOptions.license,
            "https://github.com/%s/%s" % (splits[0], splits[1]),
            splits[0],
            splits[1]
        ))

      _db.commit()

  elif r.status == 404:
    pass

  else:
    print("Aborting because received error from https://gharchive.org")
    exit(1)


def _api_find_repos(scrapeOptions: ArchiveScrapeOptions):
  segment = 0
  now = scrapeOptions.begin
  delta = timedelta(days=1)

  while now <= scrapeOptions.end:
    s = segment

    while s < 24:
      _get_urls(scrapeOptions, now.year, "%02d" % now.month, "%02d" % now.day, s)
      s += 1

    segment = 0
    now += delta


def find_repos(scrapeOptions: ArchiveScrapeOptions):
  """Finds repos from github archive."""

  _api_find_repos(scrapeOptions)
