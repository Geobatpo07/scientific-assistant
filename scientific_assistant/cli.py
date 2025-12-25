"""Command-line interface for the Scientific Assistant."""

import argparse
import sys
from scientific_assistant import ScientificAssistant


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scientific Assistant - High-level tools for applied mathematics and data science",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scientific-assistant --info
    Display information about available modules
  
  scientific-assistant --interactive
    Start interactive Python session with assistant loaded
        """
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Display information about available capabilities'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Start interactive Python session with assistant loaded'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    args = parser.parse_args()
    
    # Create assistant instance
    assistant = ScientificAssistant()
    
    if args.info:
        assistant.info()
        return 0
    
    if args.interactive:
        try:
            import IPython
            print("Starting interactive session...")
            print("The 'assistant' object is available with modules:")
            print("  - assistant.analysis: Mathematical analysis")
            print("  - assistant.numerical: Numerical experimentation")
            print("  - assistant.modeling: Statistical and ML modeling")
            print("  - assistant.data: Data science tools")
            print()
            IPython.embed(user_ns={'assistant': assistant})
        except ImportError:
            print("IPython not available. Starting basic Python REPL...")
            import code
            code.interact(local={'assistant': assistant})
        return 0
    
    # If no arguments, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
