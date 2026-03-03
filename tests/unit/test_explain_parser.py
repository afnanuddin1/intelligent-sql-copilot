from app.services.database.explain_parser import parse_explain_output

SAMPLE = [{
    "Plan": {
        "Node Type": "Hash Join",
        "Total Cost": 1500.0,
        "Actual Rows": 200,
        "Plans": [
            {"Node Type": "Seq Scan", "Relation Name": "flights",
             "Total Cost": 900.0, "Actual Rows": 5000, "Plans": []},
            {"Node Type": "Hash", "Total Cost": 100.0,
             "Actual Rows": 20, "Plans": []}
        ]
    },
    "Planning Time": 2.5,
    "Execution Time": 45.3
}]

def test_parse_basic():
    result = parse_explain_output(SAMPLE)
    assert result["total_cost"] == 1500.0
    assert result["planning_time_ms"] == 2.5
    assert result["execution_time_ms"] == 45.3

def test_detects_seq_scan():
    result = parse_explain_output(SAMPLE)
    assert "flights" in result["seq_scans"]

def test_detects_expensive_nodes():
    result = parse_explain_output(SAMPLE)
    assert len(result["expensive_nodes"]) > 0
