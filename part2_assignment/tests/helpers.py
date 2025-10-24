import json
import subprocess

TOL = 1e-9

def compare_json(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        assert set(a.keys()) == set(b.keys())

        for k in a:
            compare_json(a[k], b[k])
            
    elif isinstance(a, list) and isinstance(b, list):
        assert len(a) == len(b)

        a = sorted(a, key=lambda x: json.dumps(x, sort_keys=True))
        b = sorted(b, key=lambda x: json.dumps(x, sort_keys=True))

        for i in range(len(a)):
            compare_json(a[i], b[i])

    elif isinstance(a, float) and isinstance(b, float):
        assert abs(a - b) < 1e-3
        
    else:
        assert a == b

def run_program(file_path, input_json):
    result = subprocess.run(
        ["python3", file_path],
        input=json.dumps(input_json),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Solver crashed for {input_json}:\n{result.stderr}")
    
    return json.loads(result.stdout)
