"""Script to reset the knowledge base."""

import sys
import argparse

from app.vectorstore.chroma import get_vector_store
from app.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Reset knowledge base."""
    parser = argparse.ArgumentParser(description="Reset Teslas.ai knowledge base")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm deletion without prompt",
    )
    
    args = parser.parse_args()
    
    vector_store = get_vector_store()
    
    if not args.confirm:
        response = input(
            "⚠️  This will delete all documents in the knowledge base. Continue? (yes/no): "
        )
        if response.lower() != "yes":
            logger.info("Reset cancelled")
            sys.exit(0)
    
    try:
        logger.info("Deleting knowledge base...")
        vector_store.delete_collection()
        logger.info("✅ Knowledge base reset successfully")
        
    except Exception as e:
        logger.error(f"Reset failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
