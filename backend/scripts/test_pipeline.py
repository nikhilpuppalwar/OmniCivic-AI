import urllib.request
import json

# Test the full pipeline on report CIV-2026-1001 (water leakage, Scenario 1)
req = urllib.request.Request('http://localhost:8000/analyze/CIV-2026-1001', method='POST')
r = urllib.request.urlopen(req)
data = json.loads(r.read())

print("=== Pipeline Result ===")
print(f"Incident ID: {data.get('incident_id')}")
print()

stages = data.get('stages', {})
for k, v in stages.items():
    status = v.get('status', '')
    result = v.get('result', {})
    print(f"Stage: {k} -> {status}")
    if k == 'perception':
        print(f"  Issue: {result.get('issue_type')}, Severity: {result.get('severity')}, Confidence: {result.get('confidence')}")
    elif k == 'clustering':
        print(f"  Cluster size: {result.get('cluster_size')}, Reports: {result.get('report_ids', [])}")
    elif k == 'incident_detection':
        print(f"  Classification: {result.get('classification')}, Types: {result.get('issue_types')}")
    elif k == 'root_cause':
        print(f"  Chain: {' -> '.join(result.get('chain', []))}")
        print(f"  Confidence: {result.get('confidence')}")
    elif k == 'impact':
        print(f"  Score: {result.get('score')}/100, Priority: {result.get('priority')}")
    elif k == 'response':
        for step in result.get('steps', []):
            print(f"  Step {step['step_number']}: {step['department_name']} - {step['action']}")
    elif k == 'summary':
        print(f"  {result if isinstance(result, dict) else v}")

print("\n=== Agent Logs ===")
for log in data.get('agent_logs', []):
    print(f"  [{log.get('agent')}] {log.get('decision')} (confidence: {log.get('confidence')})")
