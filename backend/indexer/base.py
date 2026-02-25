from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class RawOrganization:
    name: str
    registry: str
    external_id: str
    country: str | None = None
    website: str | None = None
    city: str | None = None
    region: str | None = None


@dataclass
class RawGrant:
    funder_registry: str
    funder_external_id: str
    grantee_registry: str
    grantee_external_id: str
    amount: Decimal | None = None
    year: int | None = None
    source: str = ""


@dataclass
class RawRecord:
    organizations: list[RawOrganization] = field(default_factory=list)
    grants: list[RawGrant] = field(default_factory=list)


class BaseConnector(ABC):
    @abstractmethod
    def fetch(self) -> Iterator[RawRecord]:
        """Yield raw records from the data source."""
        pass
