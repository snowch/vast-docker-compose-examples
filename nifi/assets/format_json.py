#!/usr/bin/env python3

import json
import sys

def format_json(input_file, output_file=None):
    """Deterministically formats a JSON file for easy diffing."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        formatted_json = json.dumps(
            data, 
            indent=4, 
            sort_keys=True, 
            ensure_ascii=True
        )
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(formatted_json + "\n")
        else:
            print(formatted_json)
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Format JSON for easier diffing.")
    parser.add_argument("input_file", help="Path to the input JSON file.")
    parser.add_argument("-o", "--output", help="Optional output file path.")
    
    args = parser.parse_args()
    format_json(args.input_file, args.output)

