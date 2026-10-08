import json
import urllib.request

BASE = "http://localhost:5000/api"
EMAIL = "EMAIL_PLACEHOLDER"
PASSWORD = "PASSWORD_PLACEHOLDER"

GRADES = [
    "Playgroup", "PP1", "PP2",
    "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6",
    "Grade 7", "Grade 8", "Grade 9",
]
STREAMS = ["Stream A", "Stream B"]


def call(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, method=method, data=data, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


login = call("POST", "/auth/login", {"smartmark_email": EMAIL, "password": PASSWORD})
token = login["access_token"]

for i, name in enumerate(GRADES):
    grade = call("POST", "/grades", {"name": name, "order_index": i}, token)
    for stream_name in STREAMS:
        call("POST", "/streams", {"name": stream_name, "grade_id": grade["id"]}, token)
    print(f"Created {name} with streams {STREAMS}")

print("Done.")
