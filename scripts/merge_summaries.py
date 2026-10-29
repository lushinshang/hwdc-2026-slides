import json
import os

def merge_summaries():
    batches = [
        "data/summary_batch_1.json",
        "data/summary_batch_2.json",
        "data/summary_batch_3.json",
        "data/summary_batch_4.json"
    ]

    all_summaries = {}
    for b in batches:
        if not os.path.exists(b):
            print(f"Error: {b} does not exist!")
            return
        with open(b, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                all_summaries[item["index"]] = item

    print(f"Total merged summaries: {len(all_summaries)}")

    with open("data/slides_meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    updated_count = 0
    for s in meta["sessions"]:
        idx = s["index"]
        if idx in all_summaries:
            sm = all_summaries[idx]
            s["summary"] = sm.get("summary", "")
            s["pain_point"] = sm.get("pain_point", "")
            s["solution"] = sm.get("solution", "")
            s["takeaways"] = sm.get("takeaways", [])
            updated_count += 1
        else:
            print(f"Warning: Index {idx} not found in summaries!")

    with open("data/slides_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Successfully enriched {updated_count} / {len(meta['sessions'])} sessions in data/slides_meta.json!")

if __name__ == "__main__":
    merge_summaries()
