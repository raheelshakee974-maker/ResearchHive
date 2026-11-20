"""Report history: har report history/ folder mein JSON file ban kar save hoti hai."""
import json, os, time

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history")
os.makedirs(DIR, exist_ok=True)


def save_report(topic, data: dict) -> str:
    rid = time.strftime("%Y%m%d-%H%M%S")
    data = {**data, "topic": topic, "id": rid, "date": time.strftime("%d %b %Y %H:%M")}
    with open(os.path.join(DIR, rid + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return rid


def list_reports():
    out = []
    for fn in sorted(os.listdir(DIR), reverse=True):
        if fn.endswith(".json"):
            try:
                with open(os.path.join(DIR, fn), encoding="utf-8") as f:
                    d = json.load(f)
                out.append({"id": d["id"], "topic": d["topic"], "date": d["date"]})
            except Exception:
                pass
    return out


def load_report(rid):
    with open(os.path.join(DIR, rid + ".json"), encoding="utf-8") as f:
        return json.load(f)


def delete_report(rid):
    p = os.path.join(DIR, rid + ".json")
    if os.path.exists(p):
        os.remove(p)
