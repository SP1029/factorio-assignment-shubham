import json
import sys

def scan_input():
    try:
        return json.load(sys.stdin)
    except Exception as e:
        print("Invalid Input")
        exit()

def print_soln(soln):
    print(json.dumps(format_floats(soln), indent=4))

def format_floats(obj):
    if isinstance(obj, float):
        return float(f"{obj:.9f}")
    elif isinstance(obj, dict):
        return {k: format_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [format_floats(v) for v in obj]
    return obj
