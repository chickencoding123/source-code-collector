#! /usr/bin/env python3

from datetime import datetime
import urllib3
import zipfile
import io
import os
import errno

http = urllib3.PoolManager()
branch = "master"
sourceDir = "src/dataset"


def _get_zip_gen(url: str):
  """Requests an archive and checks if it's a zip file, then extracts and returns a generator function to iterate over files in that archive"""

  archiveUrl = "%s/archive/%s.zip" % (url, branch)
  response = http.request("GET", archiveUrl)

  if response.status == 200:
    data = io.BytesIO(response.data)

    if zipfile.is_zipfile(data) == False:
      raise "Aborting because received a non-archive file from %s" % archiveUrl

    with zipfile.ZipFile(data) as f:
      for zipinfo in f.infolist():
        with f.open(zipinfo) as file:
          yield zipinfo.filename, file


def _exists(filePath: str):
  """Does file or dirctory exist"""
  return os.path.exists(filePath)


def _repo_exists(url: str):
  """Checks directory to see if repo directory exists. Archives are downloaded by their main branch so directories have -main appendix"""

  splits = url.replace("https://github.com/", "").split("/")
  repoDirectory = splits[len(splits) - 1]
  return _exists("%s/%s-%s" % (sourceDir, repoDirectory, branch))


def _save_File(text: str, filePath: str):
  """Saves file to a directory, if it does not exist already"""

  # if dir not exist then make it
  if not _exists(filePath):
    try:
      os.makedirs(os.path.dirname(filePath))
    except OSError as exc:  # Guard against race condition
      if exc.errno != errno.EEXIST:
        raise

    with open(filePath, "w") as f:
      f.write(text)


def download_repo(url: str):
  """Saves a remote repository to local system"""

  if (_repo_exists(url)):
    return

  zipGen = _get_zip_gen(url)
  [filePath, file] = next(zipGen, [None, None])
  dirToSave = None

  while filePath is not None:
    splits = filePath.split("/")

    # do not care for directories
    if len(splits) == 1 or splits[0] == "/":
      [filePath, file] = next(zipGen, [None, None])
      continue

    fileName = splits[len(splits) - 1]

    if (
        fileName.endswith(".ts")
        or fileName.endswith(".tsx")
        or fileName.startswith(".env")
        or fileName == ".env"
        or fileName == "package.json"
        or fileName == "LICENSE"
        or fileName == "LICENSE.md"
        or fileName == "LICENSE.txt"
        or fileName == "license"
        or fileName == "license.md"
        or fileName == "license.txt"
    ):
      if dirToSave == None:
        dirToSave = os.path.join(sourceDir, os.path.dirname(filePath).split("/")[0])

      saveTo = os.path.join(sourceDir, filePath)

      # sometimes weird characters in the textual files
      try:
        _save_File(file.read().decode(), saveTo)
      except:
        pass

    [filePath, file] = next(zipGen, [None, None])

  if dirToSave != None:
    _save_File(
        """
            # This repository was saved for ML training. Source is from github and source-code-collector was used to download the data
            - saved on %s
            """
        % datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        dirToSave + "/META.md",
    )
