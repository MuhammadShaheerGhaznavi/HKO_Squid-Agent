#!/usr/bin/env python3
import sys
from config import MAX_AGENT_ITERATIONS
from agent_graph import run_query


def interactive_loop():
    print("=" * 60)
    print("  LLM Wiki Query Agent")
    print("  Type 'exit' or 'quit' to stop.")
    print("=" * 60)
    print()

    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        print()
        run_query(query)

        print("\n" + "-" * 60 + "\n")


def main():
    args = sys.argv[1:]

    if args:
        query = " ".join(args)
        run_query(query)
        print()
    else:
        interactive_loop()


if __name__ == "__main__":
    main()
