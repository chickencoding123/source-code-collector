#! /usr/bin/env python3

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
from dotenv import dotenv_values

from models import LiveScrapeOptions, CodeRepository
from db import Db

_db = Db()

_graphql_client = Client(
    transport=RequestsHTTPTransport(
        url="https://api.github.com/graphql",
        use_json=True,
        headers={
            "Content-Type": "application/graphql",
            "Authorization": f"Bearer {dotenv_values().get('API_KEY')}",
        },
        retries=3,
    ),
    fetch_schema_from_transport=True,
)


def _api_graphql_results(scrapeOptions: LiveScrapeOptions):
  """
    Call graphql and return results. Limitations:
    1. Total limit from github 500k.
    2. Maximum pagesize is 100. Additionally we have a rate limit of 5000 credits per hour.
  """

  # unfortunately the search api does not allow multiple lang/license per request
  queryLine = (
      """search(query: "language:%s archived:false is:public license:%s size:%s..%s", type: REPOSITORY, first: 100)"""
      % (scrapeOptions.lang, scrapeOptions.license, scrapeOptions.begin, scrapeOptions.end)
  )

  query = gql(
      """ 
            {
                %s {
                    repositoryCount
                    edges {
                        node {
                            ... on Repository {
                                name
                                url
                                owner {
                                    login
                                }
                            }
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
                rateLimit {
                    remaining
                    resetAt
                }
            }
            """
      % queryLine
  )

  return _graphql_client.execute(query)


def _api_find_repos(scrapeOptions: LiveScrapeOptions) -> None:
  rateLimited = 1
  totalPages = scrapeOptions.end - scrapeOptions.begin
  pageNumber = scrapeOptions.begin

  while rateLimited > 0 and pageNumber < totalPages:
    result = _api_graphql_results(LiveScrapeOptions(scrapeOptions.license, scrapeOptions.lang, scrapeOptions.begin, scrapeOptions.end))
    has_next_page = bool(result["search"]["pageInfo"]["hasNextPage"])
    end_cursor = result["search"]["pageInfo"]["endCursor"]
    rateLimited = int(result["rateLimit"]["remaining"])
    rateLimitResetAt = datetime.strptime(result["rateLimit"]["resetAt"], "%Y-%m-%dT%H:%M:%SZ")
    howLongToReset = datetime.now() - rateLimitResetAt

    for edge in result["search"]["edges"]:
      _db.upsert(CodeRepository(
          None,
          scrapeOptions.license,
          edge['node']['url'],
          edge['node']['owner']['login'],
          edge['node']['name']
      ))

    # commit per page
    _db.commit()

    # move to next page
    pageNumber += 1

    # hit the hourly rate limit
    if rateLimited <= 0:
      print(
          "Reached github API limit! Rate limit score is set to reset in %s minutes while its value is %s."
          % (howLongToReset.seconds / 60, rateLimited)
      )
    elif end_cursor == None and has_next_page == False:
      print("Finished finding repos for %s license!" % scrapeOptions.license)
      break


def find_repos(scrapeOptions: LiveScrapeOptions):
  """Finds repos from github live data. It's limited and will not return all available results although it should return more than 40k which is more than what github live search returns."""

  _api_find_repos(scrapeOptions)
