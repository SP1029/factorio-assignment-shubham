import pytest
from helpers import compare_json, run_program

TEST_CASES = [
    pytest.param(
        {
          "nodes": {
            "a": {},
            "t": {}
          },
          "edges": [
            {"from": "s1", "to": "a", "lo": 0, "hi": 50},
            {"from": "s2", "to": "a", "lo": 0, "hi": 50},
            {"from": "a", "to": "t", "lo": 0, "hi": 100}
          ],
          "sources": {
            "s1": 50,
            "s2": 30
          },
          "sink": "t"
        },
        {
          "status": "ok",
          "max_flow_per_min": 80,
          "flows": [
            {"from": "s1", "to": "a", "flow": 50},
            {"from": "s2", "to": "a", "flow": 30},
            {"from": "a", "to": "t", "flow": 80}
          ]
        },
        id="case_1_simple_feasible_multi_source"
    ),
    pytest.param(
        {
          "nodes": {
            "a": {},
            "b": {},
            "t": {}
          },
          "edges": [
            {"from": "s1", "to": "a", "lo": 0, "hi": 100},
            {"from": "a", "to": "b", "lo": 0, "hi": 70},
            {"from": "b", "to": "t", "lo": 0, "hi": 100}
          ],
          "sources": {
            "s1": 100
          },
          "sink": "t"
        },
        {
          "status": "infeasible",
          "cut_reachable": ["s1", "a"],
          "deficit": {
            "demand_balance": 30,
            "tight_nodes": [],
            "tight_edges": [
              {"from": "a", "to": "b"}
            ]
          }
        },
        id="case_2_infeasible_edge_upper_bound"
    ),
    pytest.param(
        {
          "nodes": {
            "a": {"cap": 80},
            "t": {}
          },
          "edges": [
            {"from": "s1", "to": "a", "lo": 0, "hi": 100},
            {"from": "s2", "to": "a", "lo": 0, "hi": 100},
            {"from": "a", "to": "t", "lo": 0, "hi": 100}
          ],
          "sources": {
            "s1": 50,
            "s2": 50
          },
          "sink": "t"
        },
        {
          "status": "infeasible",
          "cut_reachable": ["a", "s1", "s2"],
          "deficit": {
            "demand_balance": 20,
            "tight_nodes": ["a"],
            "tight_edges": []
          }
        },
        id="case_3_infeasible_node_capacity"
    ),
    pytest.param(
        {
          "nodes": {
            "a": {},
            "b": {},
            "c": {},
            "t": {}
          },
          "edges": [
            {"from": "s1", "to": "a", "lo": 0, "hi": 100},
            {"from": "a", "to": "b", "lo": 70, "hi": 80},
            {"from": "a", "to": "c", "lo": 0, "hi": 50},
            {"from": "b", "to": "t", "lo": 0, "hi": 80},
            {"from": "c", "to": "t", "lo": 0, "hi": 50}
          ],
          "sources": {
            "s1": 100
          },
          "sink": "t"
        },
        {
          "status": "ok",
          "max_flow_per_min": 100,
          "flows": [
            {"from": "s1", "to": "a", "flow": 100},
            {"from": "a", "to": "b", "flow": 80},
            {"from": "a", "to": "c", "flow": 20},
            {"from": "b", "to": "t", "flow": 80},
            {"from": "c", "to": "t", "flow": 20}
          ]
        },
        id="case_4_feasible_with_lower_bounds"
    ),
    pytest.param(
        {
          "nodes": {
            "a": {},
            "b": {},
            "c": {"cap": 130},
            "d": {},
            "e": {},
            "t": {}
          },
          "edges": [
            {"from": "s1", "to": "a", "lo": 0, "hi": 60},
            {"from": "s2", "to": "b", "lo": 0, "hi": 60},
            {"from": "a", "to": "c", "lo": 50, "hi": 70},
            {"from": "b", "to": "c", "lo": 50, "hi": 70},
            {"from": "c", "to": "d", "lo": 0, "hi": 100},
            {"from": "c", "to": "e", "lo": 0, "hi": 100},
            {"from": "d", "to": "t", "lo": 0, "hi": 100},
            {"from": "e", "to": "t", "lo": 0, "hi": 100}
          ],
          "sources": {
            "s1": 60,
            "s2": 60
          },
          "sink": "t"
        },
        {
          "status": "ok",
          "max_flow_per_min": 120,
          "flows": [
            {"from": "s1", "to": "a", "flow": 60},
            {"from": "s2", "to": "b", "flow": 60},
            {"from": "a", "to": "c", "flow": 60},
            {"from": "b", "to": "c", "flow": 60},
            {"from": "c", "to": "d", "flow": 100},
            {"from": "c", "to": "e", "flow": 20},
            {"from": "d", "to": "t", "flow": 100},
            {"from": "e", "to": "t", "flow": 20}
          ]
        },
        id="case_5_complex_feasible_node_cap_and_lower_bounds"
    ),
    pytest.param(
        {
          "nodes": {
            "a": {},
            "b": {},
            "t": {}
          },
          "edges": [
            {"from": "s1", "to": "a", "lo": 0, "hi": 100},
            {"from": "a", "to": "b", "lo": 50, "hi": 150},
            {"from": "b", "to": "a", "lo": 20, "hi": 20},
            {"from": "b", "to": "t", "lo": 0, "hi": 150}
          ],
          "sources": {
            "s1": 100
          },
          "sink": "t"
        },
        {
          "status": "ok",
          "max_flow_per_min": 100,
          "flows": [
            {"from": "s1", "to": "a", "flow": 100},
            {"from": "a", "to": "b", "flow": 120},
            {"from": "b", "to": "a", "flow": 20},
            {"from": "b", "to": "t", "flow": 100}
          ]
        },
        id="case_6_feasible_with_cycle_and_fixed_flow"
    )
]

@pytest.mark.parametrize("input_json, output_json", TEST_CASES)
def test_belt(input_json, output_json):
    result = run_program("belts/main.py", input_json)
    compare_json(result, output_json)
