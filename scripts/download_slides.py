import json
import os
import sys
import urllib.request
import urllib.error

META_FILE = "data/slides_meta.json"
SLIDES_DIR = "slides"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://hwdc.ithome.com.tw/2026/slide"
}

def verify_pdf(file_path):
    if not os.path.exists(file_path):
        return False, "檔案不存在"
    size = os.path.getsize(file_path)
    if size < 1024:
        return False, f"檔案過小 ({size} bytes)"
    try:
        with open(file_path, "rb") as f:
            header = f.read(5)
            if header.startswith(b"%PDF"):
                return True, f"有效 PDF ({size / (1024*1024):.2f} MB)"
            else:
                return False, f"非 PDF 檔頭 ({header})"
    except Exception as e:
        return False, str(e)

def download_file(url, target_path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp, open(target_path, "wb") as out_file:
        chunk_size = 64 * 1024
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)

def main():
    if not os.path.exists(META_FILE):
        print(f"錯誤：找不到中繼檔案 {META_FILE}，請先執行 fetch_meta.py")
        sys.exit(1)

    os.makedirs(SLIDES_DIR, exist_ok=True)

    with open(META_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    pdf_sessions = [s for s in meta.get("sessions", []) if s.get("is_pdf")]
    total = len(pdf_sessions)
    print(f"==================================================")
    print(f"準備下載 HWDC 2026 簡報 PDF，共 {total} 份")
    print(f"目標目錄: {SLIDES_DIR}/")
    print(f"==================================================")

    success_count = 0
    skipped_count = 0
    failed_items = []

    for idx, item in enumerate(pdf_sessions, 1):
        filename = item["local_filename"]
        target_path = os.path.join(SLIDES_DIR, filename)
        url = item["orig_slide_url"]
        title = item["title"]
        speaker = item["speaker_display"]

        # 檢查是否已下載過且驗證合法
        is_valid, msg = verify_pdf(target_path)
        if is_valid:
            print(f"[{idx}/{total}] [略過] {title} ({speaker}) -> 已存在且驗證合法 ({msg})")
            skipped_count += 1
            success_count += 1
            continue

        print(f"[{idx}/{total}] [下載中] {title} ({speaker})...")
        print(f"   來源: {url}")
        
        # 嘗試下載（最多重試 2 次）
        download_success = False
        for attempt in range(1, 3):
            try:
                download_file(url, target_path)
                valid, check_msg = verify_pdf(target_path)
                if valid:
                    print(f"   -> 成功！{check_msg}")
                    download_success = True
                    success_count += 1
                    break
                else:
                    print(f"   -> 下載內容驗證失敗 (嘗試 {attempt}): {check_msg}")
                    if os.path.exists(target_path):
                        os.remove(target_path)
            except Exception as e:
                print(f"   -> 下載錯誤 (嘗試 {attempt}): {e}")
                if os.path.exists(target_path):
                    os.remove(target_path)

        if not download_success:
            print(f"   [失敗] 無法下載 {title}")
            failed_items.append((idx, title, speaker, url))

    print("\n==================================================")
    print(f"下載作業統計：")
    print(f"總目標: {total}")
    print(f"成功: {success_count} (其中略過現有: {skipped_count})")
    print(f"失敗: {len(failed_items)}")
    if failed_items:
        print("失敗清單:")
        for fid, ftitle, fspeaker, furl in failed_items:
            print(f"  - #{fid} {ftitle} ({fspeaker}): {furl}")
    print("==================================================")

    if failed_items:
        sys.exit(1)

if __name__ == "__main__":
    main()
