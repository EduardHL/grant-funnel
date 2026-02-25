"""CLI entry point for the indexer: python -m indexer"""

import argparse
import logging
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from indexer.connectors.propublica import ProPublicaConnector
from indexer.loader import load_records

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Grant Funnel Indexer")
    parser.add_argument("--source", choices=["propublica"], default="propublica")
    parser.add_argument("--query", help="Search query for ProPublica")
    parser.add_argument("--eins", help="Comma-separated list of EINs to fetch")
    parser.add_argument("--max-pages", type=int, default=5, help="Max search result pages")
    args = parser.parse_args()

    if args.source == "propublica":
        ein_list = [e.strip() for e in args.eins.split(",")] if args.eins else None
        connector = ProPublicaConnector(
            search_query=args.query,
            ein_list=ein_list,
            max_pages=args.max_pages,
        )
    else:
        logger.error("Unknown source: %s", args.source)
        sys.exit(1)

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        stats = load_records(session, connector.fetch())
        logger.info("Import complete: %s", stats)


if __name__ == "__main__":
    main()
