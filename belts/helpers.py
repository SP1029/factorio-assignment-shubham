import sys
import json 
import numpy as np

TOL = 1e-9
SCALE = 1

def scan_input():
    try:
        return json.load(sys.stdin)
    except Exception as e:
        print("Invalid Input")
        exit()

def clean_json(obj):
    if isinstance(obj, dict):
        return {key: clean_json(value) for key, value in obj.items()}
    
    if isinstance(obj, list):
        return [clean_json(item) for item in obj]
        
    if isinstance(obj, np.integer):
        return int(obj)

    if isinstance(obj, np.floating):
        return float(obj)
        
    if isinstance(obj, np.ndarray):
        return obj.tolist()
        
    return obj

def print_json(obj):
    print(json.dumps(clean_json(obj), indent=4, sort_keys=True))

def make_edge(u, v, cap):
    return {"from": u, "to": v, "cap": cap}

def make_tight_edge(u, v):
    return {"from": u, "to": v}

def in_node(node):
    return node + "_in"

def out_node(node):
    return node + "_out"

def get_in_node(node, upd_nodes):
    return in_node(node) if in_node(node) in upd_nodes else node

def get_out_node(node, upd_nodes):
    return out_node(node) if out_node(node) in upd_nodes else node

def get_node(node):
    if len(node)>3 and (node[-3:] == "_in" or node[-4:] == "_out"):
        return node[:-3] if node[-3:] == "_in" else node[:-4]
    else:
        return node
