import requests, json

BASE = "http://127.0.0.1:8000"
UID  = 651758569380904961  # <- your Discord user id

def jprint(obj): print(json.dumps(obj, indent=2, ensure_ascii=False))

def start():
    r = requests.post(f"{BASE}/session/start", params={"user_id": UID})
    r.raise_for_status(); return r.json()

def cont():
    r = requests.post(f"{BASE}/story/continue", params={"user_id": UID})
    r.raise_for_status(); return r.json()

def submit(value: str):
    r = requests.post(f"{BASE}/story/submit", json={"user_id": UID, "value": value})
    r.raise_for_status(); return r.json()

def choose(option_id: str):
    r = requests.post(f"{BASE}/story/choose", json={"user_id": UID, "option_id": option_id})
    r.raise_for_status(); return r.json()

def run():
    step = start()
    while True:
        kind = step.get("kind")
        print(f"\n== Step [{kind}] ==")
        if kind == "narration":
            text = step.get("text") or ""
            print(text)
            if step.get("can_continue"):
                input("\nPress Enter to Continue…")
                step = cont()
            else:
                print("\n[End of this path]")
                break

        elif kind == "modal":
            prompt = step.get("prompt") or "Enter value"
            val = input(f"{prompt}: ").strip()
            step = submit(val)

        elif kind in ("choice", "dyn_choice"):
            print(step.get("prompt") or "Choose:")
            opts = step.get("options") or []
            for i,o in enumerate(opts, 1):
                print(f"  {i}. {o['label']}   (id: {o['id']})")
            while True:
                sel = input("Type the id to choose: ").strip()
                if any(o["id"] == sel for o in opts):
                    step = choose(sel); break
                print("Invalid id. Copy one of the ids exactly as shown.")

        else:
            print("Under construction or unknown step type.")
            break

if __name__ == "__main__":
    run()
