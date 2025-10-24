from helpers import *
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow, breadth_first_order

S = "SOURCE"
T = "SINK"

def transform_graph(data):
    upd_nodes = set()
    upd_edges = []
    balance = {}
    
    # Nodes
    upd_nodes.update(list(data["nodes"].keys()))
    upd_nodes.update(list(data["sources"].keys()))
    upd_nodes.update([u for edge in data["edges"] for u in [edge["from"], edge["to"]]])
    
    # Node Capacity Handling
    for node in data["nodes"]:
        node_info = data["nodes"][node]
        node_in = in_node(node)
        node_out = out_node(node)
        if len(node_info)!=0:
            node_cap = node_info["cap"]
            upd_nodes.remove(node)
            upd_nodes.add(node_in)
            upd_nodes.add(node_out)
            upd_edges.append(make_edge(node_in, node_out, node_cap))
            
    # Edge Lower Bound Handling
    for edge_info in data["edges"]:
        u = edge_info["from"]
        v = edge_info["to"]
        lo = edge_info["lo"]
        hi = edge_info["hi"]
        cap = hi - lo
        
        u_out = get_out_node(u, upd_nodes)
        v_in = get_in_node(v, upd_nodes)
        
        upd_edges.append(make_edge(u_out,v_in,cap))
        balance[u_out] = balance.get(u_out,0) - lo
        balance[v_in] = balance.get(v_in,0) + lo
        
    # Source Sink Handling
    for source, supply in data["sources"].items():
        upd_nodes.add(source)
        balance[source] = balance.get(source,0) + supply
        
    sink = data["sink"]
    upd_nodes.add(sink)
    balance[sink] = balance.get(sink,0) - sum(data["sources"].values())

    total_demand = 0
    upd_nodes.update([S, T])
    for node in upd_nodes:
        if balance.get(node,0) > 0:
            total_demand += balance[node]
            upd_edges.append(make_edge(S, node, balance[node]))
        elif balance.get(node,0) < 0:
            upd_edges.append(make_edge(node, T, -balance[node]))
    
    # Nodes to index
    index = {}
    label = {}
    idx_edges = []
    upd_nodes = sorted(list(upd_nodes))
    for i, node in enumerate(upd_nodes):
        index[node] = i
        label[i] = node
    
    for edge in upd_edges:
        u = edge["from"]
        v = edge["to"]
        cap = edge["cap"]
        idx_edges.append([index[u], index[v], cap])
    
    # Graph
    N = len(upd_nodes)
    rows, cols, capacities = zip(*idx_edges)
    graph = csr_matrix((capacities, (rows, cols)), shape=(N, N))
    return graph, index, label, total_demand, upd_nodes


def remove_negative_flows(flow):
    flow = flow.toarray()
    flow[flow < 0] = 0
    return csr_matrix(flow)

def compute_flow(result, index, data, upd_nodes):
    flow = {}
    flow["status"] = "ok"
    flow["max_flow_per_min"] = sum(data["sources"].values())
    flow["flows"] = []
    lo_lookup = {(e["from"], e["to"]): e["lo"] for e in data["edges"]}
    cur_flow = remove_negative_flows(result.flow)

    for u in index:
        u_idx = index[u]
        for v in index:
            v_idx = index[v]
            node_u = get_node(u)
            node_v = get_node(v)
            edge_flow = cur_flow[u_idx, v_idx]
            if u == get_out_node(node_u, upd_nodes) and v == get_in_node(node_v, upd_nodes) and node_u != node_v:
                edge_flow += lo_lookup.get((node_u, node_v), 0)
            if u == S or v == T or node_u == node_v:
                continue
            if edge_flow > 0:
                flow["flows"].append({"from": node_u, "to": node_v, "flow": edge_flow})
    flow["flows"] = sorted(flow["flows"], key=lambda x: (x["from"], x["to"]))
    return flow

def compute_certificate(total_demand, graph, result, index, label, upd_nodes):
    S_idx = index[S]
    T_idx = index[T]
    cert = {}
    cert["status"] = "infeasible"

    # Residual Graph
    cur_flow = remove_negative_flows(result.flow)
    residual = graph - cur_flow + cur_flow.T

    # Cut Reachable
    S_nodes, _ = breadth_first_order(residual, S_idx, directed=True)
    S_nodes = set(S_nodes)
    cut_reachable = set(S_nodes)
    cut_reachable.remove(S_idx)
    cut_reachable
    cut_reachable = [get_node(label[u]) for u in cut_reachable]
    cert["cut_reachable"] = cut_reachable

    # Tight Nodes and Edges
    cert["deficit"] = {}
    T_nodes = set(index.values()) - set(S_nodes)
    tight_nodes = []
    tight_edges = []
    lo_lookup = {(e["from"], e["to"]): e["lo"] for e in data["edges"]}

    for u in index:
        u_idx = index[u]
        for v in index:
            v_idx = index[v]
            if u_idx == S_idx or v_idx == T_idx:
                continue
            edge_cap = graph[u_idx, v_idx]
            node_u = get_node(u)
            node_v = get_node(v)
            edge_flow = cur_flow[u_idx, v_idx]
            if edge_flow < edge_cap:
                continue
            if u == get_out_node(node_u, upd_nodes) and v == get_in_node(node_v, upd_nodes):
                edge_flow += lo_lookup.get((node_u, node_v), 0)
            if u_idx in S_nodes and v_idx in T_nodes and edge_flow > 0:
                if node_u == node_v:
                    tight_nodes.append(node_u)
                else:
                    tight_edges.append(make_tight_edge(node_u, node_v))

    cert["deficit"]["demand_balance"] = total_demand - result.flow_value
    cert["deficit"]["tight_nodes"] = sorted(tight_nodes)
    cert["deficit"]["tight_edges"] = sorted(tight_edges, key=lambda x: (x["from"], x["to"]))
    return cert
    

def check_feasibility(graph, index, label, total_demand, data, upd_nodes):
    S_idx = index[S]
    T_idx = index[T]
    
    result = maximum_flow(graph, S_idx, T_idx)
    max_flow = result.flow_value
    
    if max_flow == total_demand:
        flow = compute_flow(result, index, data, upd_nodes)
        return flow     
    else:
        cert = compute_certificate(total_demand, graph, result, index, label, upd_nodes)
        return cert
            
if __name__=="__main__":
    data = scan_input()
    graph, index, label, total_demand, upd_nodes = transform_graph(data)
    resp = check_feasibility(graph, index, label, total_demand, data, upd_nodes)
    print_json(resp)
