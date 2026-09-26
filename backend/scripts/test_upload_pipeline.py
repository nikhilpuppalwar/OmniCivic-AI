import urllib.request
import json
import os

# Create a small dummy image file to test upload
dummy_img_path = 'dummy_test.png'
with open(dummy_img_path, 'wb') as f:
    # Minimal 1x1 pixel PNG data
    f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82')

print("1. Submitting a new report using multipart/form-data upload...")

# Build multipart request body manually in pure Python to avoid extra library dependencies
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = []

fields = {
    'description': 'A large deep pothole in the middle of the road causing traffic blockage.',
    'latitude': '19.1190',
    'longitude': '72.8470',
    'location_name': 'Chakala Junction, Andheri East',
    'citizen_name': 'Test Citizen',
    'phone': '+91-99999-88888',
    'ward': 'Ward 7 - Andheri East'
}

for name, value in fields.items():
    body.append(f'--{boundary}')
    body.append(f'Content-Disposition: form-data; name="{name}"')
    body.append('')
    body.append(value)

# Append file field
body.append(f'--{boundary}')
body.append(f'Content-Disposition: form-data; name="image"; filename="{dummy_img_path}"')
body.append('Content-Type: image/png')
body.append('')
with open(dummy_img_path, 'rb') as f:
    body.append(f.read())

body.append(f'--{boundary}--')
body.append('')

# Combine body bytes
body_bytes = b''
for item in body:
    if isinstance(item, str):
        body_bytes += item.encode('utf-8') + b'\r\n'
    else:
        body_bytes += item + b'\r\n'

req = urllib.request.Request(
    'http://127.0.0.1:8000/reports',
    data=body_bytes,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body_bytes))
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req) as r:
        response_data = json.loads(r.read().decode())
        print("Submission success response:", json.dumps(response_data, indent=2))
        
        report_id = response_data['report_id']
        print(f"\n2. Submitting report ID {report_id} to the analysis pipeline...")
        
        req_analyze = urllib.request.Request(
            f'http://127.0.0.1:8000/analyze/{report_id}',
            method='POST'
        )
        with urllib.request.urlopen(req_analyze) as r_analyze:
            analysis_data = json.loads(r_analyze.read().decode())
            print("\nPipeline execution completed successfully!")
            print(f"Incident ID created: {analysis_data.get('incident_id')}")
            
            # Print perception stage details
            stages = analysis_data.get('stages', {})
            perception = stages.get('perception', {})
            perception_result = perception.get('result', {})
            print("\nPerception Stage Result:")
            print(f"  Issue Type: {perception_result.get('issue_type')}")
            print(f"  Severity: {perception_result.get('severity')}")
            print(f"  Confidence: {perception_result.get('confidence')}")
            print(f"  Visual Evidence Observations:")
            for obs in perception_result.get('visual_evidence', []):
                print(f"    - {obs}")
                
except Exception as e:
    print("Error executing pipeline test:", e)
finally:
    # Cleanup dummy file
    if os.path.exists(dummy_img_path):
        os.remove(dummy_img_path)
