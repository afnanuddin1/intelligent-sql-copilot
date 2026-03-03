def parse_explain_output(explain_json: list) -> dict:
    if not explain_json:
        return {}

    plan = explain_json[0]
    root = plan.get("Plan", {})
    seq_scans = []
    all_nodes = []
    expensive_nodes = []

    def walk(node: dict):
        ntype    = node.get("Node Type", "")
        relation = node.get("Relation Name", node.get("Alias", ""))
        cost     = node.get("Total Cost", 0.0)
        rows     = node.get("Actual Rows", 0)
        is_seq   = ntype == "Seq Scan"

        if is_seq and relation:
            seq_scans.append(relation)
        if cost > 1000:
            expensive_nodes.append(f"{ntype} on {relation} (cost={cost})")

        all_nodes.append({
            "node_type": ntype,
            "relation": relation,
            "total_cost": cost,
            "actual_rows": rows,
            "is_seq_scan": is_seq,
        })
        for child in node.get("Plans", []):
            walk(child)

    walk(root)

    return {
        "total_cost":       root.get("Total Cost", 0.0),
        "planning_time_ms": plan.get("Planning Time", 0.0),
        "execution_time_ms":plan.get("Execution Time", 0.0),
        "nodes":            all_nodes,
        "seq_scans":        list(set(seq_scans)),
        "expensive_nodes":  expensive_nodes,
    }
