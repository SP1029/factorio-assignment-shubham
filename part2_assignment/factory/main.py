from helpers import *
import numpy as np
from scipy.optimize import linprog

TOL = 1e-9
linprog_options = {
    "tol":TOL
}

def get_obj_rcp_prod_rate(obj, recipe_info, machines):
    machine_type = recipe_info["machine"]
    prod = machines[machine_type].get("prod", 0.0)
    speed = machines[machine_type].get("speed", 0.0)
    time_s = recipe_info["time_s"]
    eff_craft_per_min = machines[machine_type]["crafts_per_min"] * (1 + speed) * 60 / time_s

    obj_prod_rate = 0.0

    if obj in recipe_info["in"]:
        obj_prod_rate -= recipe_info["in"][obj] * eff_craft_per_min

    if obj in recipe_info["out"]:
        obj_prod_rate += recipe_info["out"][obj] * eff_craft_per_min * (1+prod)

    return obj_prod_rate

def get_obj_eqn(obj, recipes, machines):
    R = len(recipes)
    eqn = np.zeros(R)
    for i, recipe in enumerate(recipes):
        recipe_info = recipes[recipe]
        eqn[i] = get_obj_rcp_prod_rate(obj, recipe_info, machines)
    return eqn

def create_equations(data):
    # Process the data
    recipes = data["recipes"]
    R = len(recipes)
    machine_types = list(data["machines"].keys())
    M = len(machine_types)
    supplies = list(data["limits"]["raw_supply_per_min"].keys())
    S = len(supplies)
    target = data["target"]["item"]
    target_rate = data["target"]["rate_per_min"]
    modules = data["modules"]

    objects = set()
    for recipe_info in recipes.values():
        objects.update(recipe_info["in"].keys())
        objects.update(recipe_info["out"].keys())

    intermediates = objects - set(supplies) - set([target])
    I = len(intermediates)

    machines = data["machines"]
    for machine in machines:
        prod = 0.0
        speed = 0.0
        if machine in modules:
            prod = modules[machine].get("prod", 0.0)
            speed = modules[machine].get("speed", 0.0)
        machines[machine]["prod"] = prod
        machines[machine]["speed"] = speed

    # Setup the equations
    # Steady state for intermediates and target
    A_eq = np.zeros((I+1, R))
    b_eq = np.zeros(I+1)
    
    for i, obj in enumerate(intermediates):
        A_eq[i,:] = get_obj_eqn(obj, recipes, machines)
        b_eq[i] = 0.0

    A_eq[I,:] = get_obj_eqn(target, recipes, machines)
    b_eq[I] = target_rate

    # Upper bounds for supplies and machines
    A_ub = np.zeros((S+M, R))
    b_ub = np.zeros(S+M)

    for i, obj in enumerate(supplies):
        A_ub[i,:] = -get_obj_eqn(obj, recipes, machines)
        b_ub[i] = data["limits"]["raw_supply_per_min"][obj]

    for i, machine_type in enumerate(machine_types):
        for j, recipe_info in enumerate(recipes.values()):
            if recipe_info["machine"] == machine_type:
                A_ub[S+i, j] = 1.0
        b_ub[S+i] = data["limits"]["max_machines"][machine_type]

    # Objective to minimize total machines
    c = np.ones(R)

    return c, A_ub, b_ub, A_eq, b_eq, recipes, supplies, machines, machine_types

def is_feasible(c, A_ub, b_ub, A_eq, b_eq, target):
    b_eq[-1] = target
    result = linprog(c, A_ub, b_ub, A_eq, b_eq, method="highs-ds", options=linprog_options)
    return result.success

def binary_search_target(c, A_ub, b_ub, A_eq, b_eq):
    target = TOL
    while is_feasible(c, A_ub, b_ub, A_eq, b_eq, target*2):
        target *= 2
    step = target / 2
    while step >= TOL:
        if is_feasible(c, A_ub, b_ub, A_eq, b_eq, target + step)    :
            target += step
        step /= 2
    return target


def create_solution(x, A_ub, recipes, supplies, machines, machine_types):
    S = len(supplies)
    soln = {}
    soln["status"] = "ok"

    soln["per_recipe_crafts_per_min"] = {}
    for i, obj in enumerate(recipes):
        recipe_info = recipes[obj]
        machine_type = recipe_info["machine"]
        prod = machines[machine_type].get("prod", 0.0)
        speed = machines[machine_type].get("speed", 0.0)
        time_s = recipe_info["time_s"]
        eff_craft_per_min = machines[machine_type]["crafts_per_min"] * (1 + speed) * 60 / time_s * (1 + prod)
        rate = eff_craft_per_min * x[i]
        soln["per_recipe_crafts_per_min"][obj] = rate

    soln["per_machine_counts"] = {}
    for i, machine_type in enumerate(machine_types):
        count = A_ub[S+i:S+i+1,:] @ x
        soln["per_machine_counts"][machine_type] = count[0]

    soln["raw_consumption_per_min"] = {}
    for i, obj in enumerate(supplies):
        rate = A_ub[i,:] @ x
        soln["raw_consumption_per_min"][obj] = rate

    return soln

def get_bottleneck_hint(c, A_ub, b_ub, A_eq, b_eq, target):
    # Create max possible
    b_eq[-1] = target
    result = linprog(c, A_ub, b_ub, A_eq, b_eq, method="highs-ds", options=linprog_options)
    x = result.x
    soln = create_solution(result.x, A_ub, recipes, supplies, machines, machine_types)
    bottleneck_hint = []

    # Check machine and supply at full capacity 
    for machine in machine_types:
        used_count = soln["per_machine_counts"][machine]
        max_count = data["limits"]["max_machines"][machine]
        if abs(used_count - max_count) < 1e-3:
            bottleneck_hint.append(f"{machine} cap")

    for supply in supplies:
        used_rate = soln["raw_consumption_per_min"][supply]
        max_rate = data["limits"]["raw_supply_per_min"][supply]
        if abs(used_rate - max_rate) < 1e-3:
            bottleneck_hint.append(f"{supply} supply")

    return bottleneck_hint

def create_max_feasible_solution(c, A_ub, b_ub, A_eq, b_eq):
    soln = {}
    soln["status"] = "infeasible"
    max_target = binary_search_target(c, A_ub, b_ub, A_eq, b_eq)
    soln["max_feasible_target_per_min"] = max_target
    soln["bottleneck_hint"] = get_bottleneck_hint(c, A_ub, b_ub, A_eq, b_eq, max_target)
    return soln

if __name__=="__main__":
    data = scan_input()
    c, A_ub, b_ub, A_eq, b_eq, recipes, supplies, machines, machine_types = create_equations(data)

    if is_feasible(c, A_ub, b_ub, A_eq, b_eq, data["target"]["rate_per_min"]):
        result = linprog(c, A_ub, b_ub, A_eq, b_eq, method="highs-ds", options=linprog_options)
        x = result.x
        soln = create_solution(result.x, A_ub, recipes, supplies, machines, machine_types)
    else:
        soln = create_max_feasible_solution(c, A_ub, b_ub, A_eq, b_eq)
    
    print_soln(soln)
