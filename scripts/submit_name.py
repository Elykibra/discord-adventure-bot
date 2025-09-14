import requests, json

BASE = "http://127.0.0.1:8000"
UID  = 651758569380904961   # <-- your user id
NAME = "Elyk"               # <-- the name you want to submit

r = requests.post(f"{BASE}/story/submit", json={"user_id": UID, "value": NAME})
r.raise_for_status()
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
