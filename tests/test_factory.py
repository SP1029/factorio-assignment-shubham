import pytest
from helpers import compare_json, run_program

TEST_CASES = [
    pytest.param(
        {
            "machines": {
                "assembler_1": {
                    "crafts_per_min": 30
                },
                "chemical": {
                    "crafts_per_min": 60
                }
            },
            "recipes": {
                "iron_plate": {
                    "machine": "chemical",
                    "time_s": 3.2,
                    "in": {
                        "iron_ore": 1
                    },
                    "out": {
                        "iron_plate": 1
                    }
                },
                "copper_plate": {
                    "machine": "chemical",
                    "time_s": 3.2,
                    "in": {
                        "copper_ore": 1
                    },
                    "out": {
                        "copper_plate": 1
                    }
                },
                "green_circuit": {
                    "machine": "assembler_1",
                    "time_s": 0.5,
                    "in": {
                        "iron_plate": 1,
                        "copper_plate": 3
                    },
                    "out": {
                        "green_circuit": 1
                    }
                }
            },
            "modules": {
                "assembler_1": {
                    "prod": 0.1,
                    "speed": 0.15
                },
                "chemical": {
                    "prod": 0.2,
                    "speed": 0.1
                }
            },
            "limits": {
                "raw_supply_per_min": {
                    "iron_ore": 5000,
                    "copper_ore": 5000
                },
                "max_machines": {
                    "assembler_1": 300,
                    "chemical": 300
                }
            },
            "target": {
                "item": "green_circuit",
                "rate_per_min": 1800
            }
        }, 
        {
            'status': 'ok',
            'per_recipe_crafts_per_min': {
                'iron_plate': 1636.363636364,
                'copper_plate': 4909.090909091,
                'green_circuit': 1800.0
            },
            'per_machine_counts': {
                'assembler_1': 0.395256917,
                'chemical': 4.407713499
            },
            'raw_consumption_per_min': {
                'iron_ore': 1363.636363636,
                'copper_ore': 4090.909090909
            }
        },
        id="case_1_sample"
    ),
    pytest.param(
        {
            "machines": {
                "assembler": {
                    "crafts_per_min": 60
                }
            },
            "recipes": {
                "raw_to_plate": {
                    "machine": "assembler",
                    "time_s": 1,
                    "in": {
                        "raw": 1
                    },
                    "out": {
                        "plate": 1
                    }
                },
                "plate_to_target": {
                    "machine": "assembler",
                    "time_s": 2,
                    "in": {
                        "plate": 1
                    },
                    "out": {
                        "target": 1
                    }
                }
            },
            "modules": {},
            "limits": {
                "raw_supply_per_min": {
                    "raw": 1000
                },
                "max_machines": {
                    "assembler": 10
                }
            },
            "target": {
                "item": "target",
                "rate_per_min": 100
            }
        },
        {
            "status": "ok",
            "per_recipe_crafts_per_min": {
                "raw_to_plate": 100.0,
                "plate_to_target": 100.0
            },
            "per_machine_counts": {
                "assembler": 0.083333333
            },
            "raw_consumption_per_min": {
                "raw": 100.0
            }
        },
        id="case_2_no_modules_basic_chain"
    ),
    pytest.param(
        {
            "machines": {
                "assembler_1": {
                    "crafts_per_min": 30
                },
                "chemical": {
                    "crafts_per_min": 60
                }
            },
            "recipes": {
                "iron_plate": {
                    "machine": "chemical",
                    "time_s": 3.2,
                    "in": {
                        "iron_ore": 1
                    },
                    "out": {
                        "iron_plate": 1
                    }
                },
                "copper_plate": {
                    "machine": "chemical",
                    "time_s": 3.2,
                    "in": {
                        "copper_ore": 1
                    },
                    "out": {
                        "copper_plate": 1
                    }
                },
                "green_circuit": {
                    "machine": "assembler_1",
                    "time_s": 0.5,
                    "in": {
                        "iron_plate": 1,
                        "copper_plate": 3
                    },
                    "out": {
                        "green_circuit": 1
                    }
                }
            },
            "modules": {
                "assembler_1": {
                    "prod": 0.1,
                    "speed": 0.15
                },
                "chemical": {
                    "prod": 0.2,
                    "speed": 0.1
                }
            },
            "limits": {
                "raw_supply_per_min": {
                    "iron_ore": 5000,
                    "copper_ore": 5000
                },
                "max_machines": {
                    "assembler_1": 0.3,
                    "chemical": 300
                }
            },
            "target": {
                "item": "green_circuit",
                "rate_per_min": 1800
            }
        },
        {
            "status": "infeasible",
            "max_feasible_target_per_min": 1366.2,
            "bottleneck_hint": ["assembler_1 cap"]
        },
        id="case_3_infeasible_machine_cap_correct_logic"
    ),
    pytest.param(
        {
            "machines": {
                "assembler_1": {
                    "crafts_per_min": 30
                },
                "chemical": {
                    "crafts_per_min": 60
                }
            },
            "recipes": {
                "iron_plate": {
                    "machine": "chemical",
                    "time_s": 3.2,
                    "in": {
                        "iron_ore": 1
                    },
                    "out": {
                        "iron_plate": 1
                    }
                },
                "copper_plate": {
                    "machine": "chemical",
                    "time_s": 3.2,
                    "in": {
                        "copper_ore": 1
                    },
                    "out": {
                        "copper_plate": 1
                    }
                },
                "green_circuit": {
                    "machine": "assembler_1",
                    "time_s": 0.5,
                    "in": {
                        "iron_plate": 1,
                        "copper_plate": 3
                    },
                    "out": {
                        "green_circuit": 1
                    }
                }
            },
            "modules": {
                "assembler_1": {
                    "prod": 0.1,
                    "speed": 0.15
                },
                "chemical": {
                    "prod": 0.2,
                    "speed": 0.1
                }
            },
            "limits": {
                "raw_supply_per_min": {
                    "iron_ore": 5000,
                    "copper_ore": 4000
                },
                "max_machines": {
                    "assembler_1": 300,
                    "chemical": 300
                }
            },
            "target": {
                "item": "green_circuit",
                "rate_per_min": 1800
            }
        },
        {
            "status": "infeasible",
            "max_feasible_target_per_min": 1760.0,
            "bottleneck_hint": ["copper_ore supply"]
        },
        id="case_4_infeasible_raw_supply_correct_logic"
    ),
    pytest.param(
        {
            "machines": {
                "fast_m": {
                    "crafts_per_min": 100
                },
                "slow_m": {
                    "crafts_per_min": 10
                }
            },
            "recipes": {
                "C_fast": {
                    "machine": "fast_m",
                    "time_s": 1,
                    "in": {
                        "item_A": 1
                    },
                    "out": {
                        "item_C": 1
                    }
                },
                "C_slow": {
                    "machine": "slow_m",
                    "time_s": 1,
                    "in": {
                        "item_B": 1
                    },
                    "out": {
                        "item_C": 1
                    }
                },
                "A_raw": {
                    "machine": "fast_m",
                    "time_s": 1,
                    "in": {
                        "raw_A": 1
                    },
                    "out": {
                        "item_A": 1
                    }
                },
                "B_raw": {
                    "machine": "fast_m",
                    "time_s": 1,
                    "in": {
                        "raw_B": 1
                    },
                    "out": {
                        "item_B": 1
                    }
                }
            },
            "modules": {},
            "limits": {
                "raw_supply_per_min": {
                    "raw_A": 1000,
                    "raw_B": 1000
                },
                "max_machines": {
                    "fast_m": 10,
                    "slow_m": 10
                }
            },
            "target": {
                "item": "item_C",
                "rate_per_min": 100
            }
        },
        {
            "status": "ok",
            "per_recipe_crafts_per_min": {
                "C_fast": 100.0,
                "A_raw": 100.0,
                "C_slow": 0.0,
                "B_raw": 0.0
            },
            "per_machine_counts": {
                "fast_m": 0.033333333,
                "slow_m": 0.0
            },
            "raw_consumption_per_min": {
                "raw_A": 100.0,
                "raw_B": 0.0
            }
        },
        id="case_5_alternative_recipe_minimization"
    ),
    pytest.param(
        {
            "machines": {
                "machine_1": {
                    "crafts_per_min": 60
                },
                "slow_m": {
                    "crafts_per_min": 10
                }
            },
            "recipes": {
                "A_from_raw": {
                    "machine": "machine_1",
                    "time_s": 1,
                    "in": {
                        "raw": 1
                    },
                    "out": {
                        "A": 1
                    }
                },
                "A_to_B": {
                    "machine": "machine_1",
                    "time_s": 1,
                    "in": {
                        "A": 1
                    },
                    "out": {
                        "B": 1,
                        "C": 1
                    }
                },
                "B_to_A": {
                    "machine": "slow_m",
                    "time_s": 1,
                    "in": {
                        "B": 1
                    },
                    "out": {
                        "A": 1
                    }
                },
                "C_sink": {
                    "machine": "machine_1",
                    "time_s": 1,
                    "in": {
                        "C": 1
                    },
                    "out": {
                        "target": 1
                    }
                }
            },
            "modules": {},
            "limits": {
                "raw_supply_per_min": {
                    "raw": 1000
                },
                "max_machines": {
                    "machine_1": 10,
                    "slow_m": 10
                }
            },
            "target": {
                "item": "target",
                "rate_per_min": 100
            }
        },
        {
            "status": "ok",
            "per_recipe_crafts_per_min": {
                "A_from_raw": 0.0,
                "A_to_B": 100.0,
                "B_to_A": 100.0,
                "C_sink": 100.0
            },
            "per_machine_counts": {
                "machine_1": 0.055555555,
                "slow_m": 0.166666667
            },
            "raw_consumption_per_min": {
                "raw": 0.0
            }
        },
        id="case_6_cycle_and_byproduct")
]

@pytest.mark.parametrize("input_json, output_json", TEST_CASES)
def test_factory(input_json, output_json):
    result = run_program("factory/main.py", input_json)
    print(output_json, result)
    compare_json(result, output_json)
