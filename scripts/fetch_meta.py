import urllib.request
import json
import re
import os

QUERY = """
query gets {
  getProject: HWDC2026(lang: tw) {
    sessions {
      id
      type
      started_at
      finished_at
      title
      classroom {
        tw_name
        floor
      }
      slides {
        slide_cover {
          url
        }
        slide_file {
          url
        }
        supply
      }
      relatedSpeakers {
        speaker {
          public_name
          photo {
            url
          }
          companies {
            name
            dept_title
          }
        }
        type
      }
    }
  }
}
"""

def sanitize_filename(name):
    # 去除特殊字元
    cleaned = re.sub(r'[\\/*?:"<>|]', '', name)
    cleaned = cleaned.replace('\n', ' ').replace('\r', '').strip()
    # 限制長度避免路徑過長
    if len(cleaned) > 80:
        cleaned = cleaned[:80]
    return cleaned

def fetch_and_save_meta():
    req = urllib.request.Request(
        "https://ccmsapi.ithome.com.tw",
        data=json.dumps({"query": QUERY}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        sessions = res.get("data", {}).get("getProject", {}).get("sessions", [])

    print(f"Total sessions fetched from API: {len(sessions)}")

    # 按照前端的篩選與排序邏輯
    # 1. 排除特定無效 id ("5033", "5037")
    # 2. 必須有 slides 且 slides[0].supply === "提供"
    filtered = []
    for s in sessions:
        if s.get("id") in ["5033", "5037"]:
            continue
        slides = s.get("slides") or []
        if slides and len(slides) > 0 and slides[0].get("supply") == "提供":
            filtered.append(s)

    # 排序：先依開始時間，再依標題
    filtered.sort(key=lambda x: (x.get("started_at", ""), x.get("title", "")))

    print(f"Filtered visible sessions: {len(filtered)}")

    items = []
    pdf_count = 0
    non_pdf_count = 0

    for idx, s in enumerate(filtered, 1):
        started_at = s.get("started_at", "")
        finished_at = s.get("finished_at", "")
        date_str = started_at.split("T")[0] if "T" in started_at else ""
        start_time = started_at.split("T")[1] if "T" in started_at else ""
        end_time = finished_at.split("T")[1] if "T" in finished_at else ""

        title = s.get("title", "").strip()
        classroom = s.get("classroom", {}).get("tw_name", "") if s.get("classroom") else ""

        speakers = []
        speaker_names = []
        company_titles = []

        for rel in s.get("relatedSpeakers", []):
            sp = rel.get("speaker")
            if not sp:
                continue
            name = sp.get("public_name", "").strip()
            photo = sp.get("photo", {}).get("url") if sp.get("photo") else ""
            comp_list = []
            for comp in (sp.get("companies") or []):
                if not comp:
                    continue
                cname = (comp.get("name") or "").strip()
                dtitle = (comp.get("dept_title") or "").strip()
                combined = f"{cname} {dtitle}".strip()
                if combined:
                    comp_list.append(combined)
            comp_str = " / ".join(comp_list)
            speakers.append({
                "name": name,
                "photo": photo,
                "company": comp_str
            })
            if name:
                speaker_names.append(name)
            if comp_str:
                company_titles.append(comp_str)

        speaker_display = "、".join(speaker_names) if speaker_names else "大會"
        company_display = "；".join(dict.fromkeys(company_titles))

        slides = s.get("slides", [])
        cover_url = slides[0].get("slide_cover", {}).get("url") if slides[0].get("slide_cover") else ""
        orig_slide_url = slides[0].get("slide_file", {}).get("url") if slides[0].get("slide_file") else ""

        # 判斷是否為 PDF 連結
        is_pdf = bool(orig_slide_url and ".pdf" in orig_slide_url.lower())

        if is_pdf:
            pdf_count += 1
            # 建立規範化檔案名稱
            time_tag = start_time.replace(":", "")
            date_tag = date_str.replace("-", "")
            safe_speaker = sanitize_filename(speaker_display)
            safe_title = sanitize_filename(title)
            filename = f"{date_tag}_{time_tag}_{safe_speaker}_{safe_title}.pdf"
            local_rel_path = f"slides/{filename}"
        else:
            non_pdf_count += 1
            filename = None
            local_rel_path = None

        items.append({
            "index": idx,
            "id": s.get("id"),
            "date": date_str,
            "start_time": start_time,
            "end_time": end_time,
            "classroom": classroom,
            "title": title,
            "speaker_display": speaker_display,
            "company_display": company_display,
            "speakers": speakers,
            "cover_url": cover_url,
            "orig_slide_url": orig_slide_url,
            "is_pdf": is_pdf,
            "local_filename": filename,
            "local_path": local_rel_path
        })

    result_data = {
        "event": "Hello World Dev Conference 2026",
        "total_sessions": len(items),
        "pdf_sessions": pdf_count,
        "external_sessions": non_pdf_count,
        "sessions": items
    }

    os.makedirs("data", exist_ok=True)
    with open("data/slides_meta.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(items)} sessions to data/slides_meta.json")
    print(f"  - PDF files: {pdf_count}")
    print(f"  - External links: {non_pdf_count}")

if __name__ == "__main__":
    fetch_and_save_meta()
