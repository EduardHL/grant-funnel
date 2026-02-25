import logging
from collections.abc import Iterator

import httpx

from indexer.base import BaseConnector, RawOrganization, RawRecord

logger = logging.getLogger(__name__)

PROPUBLICA_API = "https://projects.propublica.org/nonprofits/api/v2"


class ProPublicaConnector(BaseConnector):
    """Import nonprofits from the ProPublica Nonprofit Explorer API.

    Supports two modes:
    - search: search for orgs by keyword (paginated)
    - ein_list: fetch specific orgs by EIN
    """

    def __init__(
        self,
        search_query: str | None = None,
        ein_list: list[str] | None = None,
        max_pages: int = 5,
    ):
        self.search_query = search_query
        self.ein_list = ein_list or []
        self.max_pages = max_pages

    def fetch(self) -> Iterator[RawRecord]:
        with httpx.Client(timeout=30) as client:
            if self.ein_list:
                yield from self._fetch_by_ein(client)
            elif self.search_query:
                yield from self._fetch_by_search(client)
            else:
                logger.warning("No search_query or ein_list provided; nothing to fetch.")

    def _fetch_by_search(self, client: httpx.Client) -> Iterator[RawRecord]:
        for page in range(self.max_pages):
            url = f"{PROPUBLICA_API}/search.json"
            params = {"q": self.search_query, "page": page}
            logger.info("Searching ProPublica: query=%s page=%d", self.search_query, page)
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            orgs = data.get("organizations", [])
            if not orgs:
                break
            record = RawRecord()
            for org_data in orgs:
                record.organizations.append(self._parse_org(org_data))
            yield record

    def _fetch_by_ein(self, client: httpx.Client) -> Iterator[RawRecord]:
        for ein in self.ein_list:
            url = f"{PROPUBLICA_API}/organizations/{ein}.json"
            logger.info("Fetching ProPublica org: EIN=%s", ein)
            resp = client.get(url)
            if resp.status_code == 404:
                logger.warning("EIN %s not found in ProPublica", ein)
                continue
            resp.raise_for_status()
            data = resp.json().get("organization", {})
            record = RawRecord(organizations=[self._parse_org(data)])
            yield record

    def _parse_org(self, data: dict) -> RawOrganization:
        ein = str(data.get("ein", "")).strip()
        return RawOrganization(
            name=data.get("name", "").strip(),
            registry="IRS",
            external_id=ein,
            country="US",
            city=data.get("city", ""),
            region=data.get("state", ""),
        )
