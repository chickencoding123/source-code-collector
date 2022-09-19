#! /usr/bin/env python3

from datetime import datetime
import click

from main import find_repos, download_repos


class Union(click.ParamType):
  def __init__(self, types, name):
    self.name = name
    self.types = types

  def convert(self, value, param, ctx):
    for type in self.types:
      try:
        return type.convert(value, param, ctx)
      except click.BadParameter:
        continue

    self.fail("Didn't match any of the accepted types.")


@click.group()
def cli():
  pass

@cli.command()
@click.option("--license", type=str, help="Comma separated list of acceptable licenses.")
@click.option("--lang", type=str, help="Comma separated list of language tags.")
@click.option("--begin-page", type=Union([click.INT, click.STRING], 'INT | STRING'), help="For pagination purposes, determines the page start.")
@click.option("--end-page", type=Union([click.INT, click.STRING], 'INT | STRING'), help="For pagination purposes, determines the page end.")
def crawl(license: str, lang: str, begin_page: int | str, end_page: int | str):
  """Downloads repository information and save them locally."""

  licenseList = list(license.split(','))
  langList = list(lang.split(','))

  if (type(begin_page).__name__ == 'str'):
    begin_page = datetime.strptime(begin_page, '%Y-%m-%d').date()
  if (type(end_page).__name__ == 'str'):
    end_page = datetime.strptime(end_page, '%Y-%m-%d').date()

  find_repos(licenseList, langList, begin_page, end_page)
  
  click.echo("Finished finding repos!")

@cli.command()
@click.option("--begin-date", type=str, help="Begining date.")
@click.option("--end-date", type=str, help="End date.")
def download(begin_date: str, end_date: str):
  """Download source code using saved information."""

  begin_date = datetime.strptime(begin_date, '%Y-%m-%d').date()
  end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

  download_repos(begin_date, end_date)

  click.echo("Finished downloading repos!")


if __name__ == '__main__':
  cli()