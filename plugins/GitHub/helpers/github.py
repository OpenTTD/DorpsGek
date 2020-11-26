import aiohttp
import datetime
import jwt
import logging
import time

from gidgethub import (
    routing,
    sansio,
)
from gidgethub.aiohttp import GitHubAPI
from gidgethub.sansio import accept_format

from .. import settings

log = logging.getLogger(__name__)

router = routing.Router()

_github_repositories = {}
_github_installations = {}


class GitHubAPIContext:
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return GitHubAPI(self._session, "DorpsGek/1.0")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()


async def dispatch(headers, data):
    event = sansio.Event.from_http(headers, data, secret=settings.GITHUB_APP_SECRET)

    async with GitHubAPIContext() as github_api:
        await router.dispatch(event, github_api)


async def get_oauth_token(repository):
    if settings.GITHUB_APP_ID is None or settings.GITHUB_APP_PRIVATE_KEY is None:
        return None

    async with GitHubAPIContext() as github_api:
        # Lookup the installation_id from the repository name
        if repository in _github_repositories:
            installation_id = _github_repositories[repository]
        else:
            data = await github_api.getitem(
                f"/repos/{repository}/installation",
                accept=accept_format(version="machine-man-preview"),
                jwt=get_jwt(),
            )
            installation_id = data["id"]
            _github_repositories[repository] = installation_id

        # Check if we already have a token; otherwise get one
        if installation_id in _github_installations:
            expires_at, oauth_token = _github_installations[installation_id]
            if expires_at > datetime.datetime.utcnow() + datetime.timedelta(minutes=5):
                return oauth_token

        data = await github_api.post(
            f"/app/installations/{installation_id}/access_tokens",
            data="",
            accept=accept_format(version="machine-man-preview"),
            jwt=get_jwt(),
        )

        expires_at = datetime.datetime.strptime(data["expires_at"], "%Y-%m-%dT%H:%M:%SZ")
        _github_installations[installation_id] = (expires_at, data["token"])

        return data["token"]


def get_jwt():
    now = int(time.time())

    # The JWT is only valid for one minute; we often only do a single action with them, so the shorter the better.
    # This does mean the server needs to be NTP sync'd (or not drift more than a minute).
    data = {
        "iat": now,
        "exp": now + 60,
        "iss": settings.GITHUB_APP_ID,
    }

    j = jwt.encode(data, key=settings.GITHUB_APP_PRIVATE_KEY, algorithm="RS256").decode()
    return j
