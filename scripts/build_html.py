import json
import html
import os

META_FILE = "data/slides_meta.json"
OUTPUT_HTML = "index.html"

def generate_awwwards_html_v4():
    with open(META_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    sessions = meta.get("sessions", [])
    total_count = len(sessions)
    pdf_sessions = [s for s in sessions if s.get("is_pdf")]
    ext_sessions = [s for s in sessions if not s.get("is_pdf")]
    
    total_size_bytes = sum(s.get("filesize_bytes", 0) for s in pdf_sessions)
    total_size_mb = total_size_bytes / (1024 * 1024)

    day1_count = sum(1 for s in sessions if "10-14" in s.get("date", ""))
    day2_count = sum(1 for s in sessions if "10-15" in s.get("date", ""))

    cards_html = []
    for s in sessions:
        idx = s.get("index")
        date = s.get("date", "")
        is_day1 = "10-14" in date
        date_short = "10/14" if is_day1 else "10/15"
        day_badge_text = "DAY 1 · 10/14 (三)" if is_day1 else "DAY 2 · 10/15 (四)"
        
        start_time = s.get("start_time", "")
        end_time = s.get("end_time", "")
        classroom = s.get("classroom", "主會場")
        
        title_raw = s.get("title", "")
        title = html.escape(title_raw)
        
        speaker_display = html.escape(s.get("speaker_display", ""))
        company_display = html.escape(s.get("company_display", ""))
        cover_url = s.get("cover_url") or "https://hwdc.ithome.com.tw/2026/img/slides.jpg"
        orig_url = s.get("orig_slide_url", "")
        is_pdf = s.get("is_pdf", False)
        filesize_str = s.get("filesize_str", "")

        # 內容精華摘要
        summary = html.escape(s.get("summary", ""))
        pain_point = html.escape(s.get("pain_point", ""))
        solution = html.escape(s.get("solution", ""))
        takeaways = s.get("takeaways", [])
        takeaways_li = "".join([f"<li>{html.escape(t)}</li>" for t in takeaways])

        # 主題標籤
        topic_tags = []
        t_lower = title_raw.lower()
        if any(k in t_lower for k in ["agent", "agentic", "skill", "mcp"]):
            topic_tags.append('<span class="topic-tag tag-agent">🤖 Agentic AI</span>')
        if any(k in t_lower for k in ["coding", "架構", "架構師", "架構設計", "structurizr"]):
            topic_tags.append('<span class="topic-tag tag-arch">📐 Architecture</span>')
        if any(k in t_lower for k in ["治理", "security", "secret", "防護", "認證", "harness"]):
            topic_tags.append('<span class="topic-tag tag-sec">🛡️ Governance</span>')
        if any(k in t_lower for k in ["測試", "o11y", "aiops", "團隊", "工作流", "敏捷", "計費"]):
            topic_tags.append('<span class="topic-tag tag-ops">⚡ Workflow</span>')
        if not topic_tags:
            topic_tags.append('<span class="topic-tag tag-general">💡 Innovation</span>')
        topic_tags_html = " ".join(topic_tags)

        # 講者資訊區塊
        speaker_chips = []
        for sp in s.get("speakers", []):
            sp_name = html.escape(sp.get("name", ""))
            sp_comp = html.escape(sp.get("company", ""))
            sp_photo = sp.get("photo") or ""
            photo_tag = f'<img src="{sp_photo}" alt="{sp_name}" class="avatar" loading="lazy">' if sp_photo else '<div class="avatar-fallback">👤</div>'
            speaker_chips.append(f"""
                <div class="speaker-chip">
                    {photo_tag}
                    <div class="speaker-info">
                        <span class="speaker-name">{sp_name}</span>
                        {f'<span class="speaker-dept">{sp_comp}</span>' if sp_comp else ''}
                    </div>
                </div>
            """)
        speakers_markup = "".join(speaker_chips)

        # 格式徽章與主下載按鈕
        if is_pdf:
            format_badge = f'<span class="badge badge-pdf"><span class="badge-dot"></span>PDF · {filesize_str}</span>'
            btn_text = "官方原網址下載 PDF"
            btn_icon = '''<svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>'''
        else:
            format_badge = '<span class="badge badge-ext"><span class="badge-dot"></span>講者線上專題</span>'
            btn_text = "開啟講者原網址專文"
            btn_icon = '''<svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z"/><path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"/></svg>'''

        card = f"""
        <article class="slide-card {'day1' if is_day1 else 'day2'} {'type-pdf' if is_pdf else 'type-ext'}" 
                 data-date="{date_short}" 
                 data-type="{'pdf' if is_pdf else 'ext'}" 
                 data-title="{title}" 
                 data-speaker="{speaker_display}"
                 data-id="{idx}">
            <div class="card-glow"></div>
            <div class="card-cover-container">
                <img src="{cover_url}" alt="{title}" class="card-cover-img" loading="lazy" onerror="this.src='https://hwdc.ithome.com.tw/2026/img/slides.jpg'">
                <div class="cover-overlay"></div>
                <div class="cover-top-bar">
                    <span class="day-chip">{day_badge_text}</span>
                    {format_badge}
                </div>
                <div class="cover-bottom-bar">
                    <span class="time-chip">⏱️ {start_time} - {end_time}</span>
                    <span class="room-chip">📍 {classroom}</span>
                </div>
            </div>
            
            <div class="card-content">
                <div class="tags-container">
                    {topic_tags_html}
                </div>
                <h3 class="card-title" title="{title}">{title}</h3>
                
                <div class="speakers-container">
                    {speakers_markup}
                </div>

                <!-- 內容精華說明區塊 -->
                <div class="digest-box">
                    <div class="digest-summary">
                        <span class="digest-icon">📌</span>
                        <p class="digest-text">{summary}</p>
                    </div>

                    <div class="digest-details">
                        <div class="digest-section">
                            <span class="digest-label label-pain">🎯 核心痛點</span>
                            <p class="digest-desc">{pain_point}</p>
                        </div>
                        <div class="digest-section">
                            <span class="digest-label label-sol">🛠️ 關鍵解法</span>
                            <p class="digest-desc">{solution}</p>
                        </div>
                        <div class="digest-section">
                            <span class="digest-label label-takeaway">💡 關鍵帶走</span>
                            <ul class="digest-list">
                                {takeaways_li}
                            </ul>
                        </div>
                    </div>
                </div>
                
                <!-- 底部按鈕區：單一官方下載主按鈕 + 複製分享 -->
                <div class="card-footer">
                    <div class="actions-grid">
                        <a href="{html.escape(orig_url)}" target="_blank" rel="noopener noreferrer" class="card-btn btn-primary" title="直連大會官方原始檔案來源">
                            {btn_icon}
                            <span>{btn_text}</span>
                        </a>
                        <button type="button" class="card-btn btn-share" onclick="copyInfo('{title}', '{speaker_display}', '{orig_url}')" title="複製標題、講者與官方原網址">
                            <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"/><path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"/></svg>
                            <span>複製分享</span>
                        </button>
                    </div>
                </div>
            </div>
        </article>
        """
        cards_html.append(card)

    cards_rendered = "\n".join(cards_html)

    full_html = f"""<!DOCTYPE html>
<html lang="zh-TW" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>HWDC 2026 演講簡報精華庫 | 官方原網址直連下載</title>
    <meta name="description" content="收錄 55 場 Hello World Dev Conference 2026 簡報內容深度精華（核心痛點、架構解法與帶走清單），直連官方原網址下載。">
    <meta name="theme-color" content="#080c14">
    
    <!-- Open Graph Metadata -->
    <meta property="og:title" content="HWDC 2026 演講簡報精華庫 | 官方原網址直連下載">
    <meta property="og:description" content="全會期 55 場前瞻架構、AI Coding、Agentic 治理演講投影片深度精華，提供直連大會官方原網址下載。">
    <meta property="og:type" content="website">

    <!-- Fonts: Inter + JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&family=Noto+Sans+TC:wght@400;500;700;800&display=swap" rel="stylesheet">

    <style>
        :root {{
            --bg-base: #080c14;
            --bg-surface: #0e1422;
            --bg-card: rgba(18, 26, 43, 0.75);
            --bg-card-hover: rgba(24, 35, 58, 0.95);
            --bg-digest: rgba(10, 16, 28, 0.6);
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(99, 102, 241, 0.45);
            --border-active: #6366f1;

            --primary: #4f46e5;
            --primary-glow: rgba(79, 70, 229, 0.4);
            --accent-cyan: #06b6d4;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-purple: #a855f7;

            --text-heading: #f8fafc;
            --text-body: #cbd5e1;
            --text-muted: #64748b;
            --text-dim: #475569;

            --radius-xl: 20px;
            --radius-lg: 14px;
            --radius-md: 10px;
            --radius-sm: 6px;

            --font-sans: 'Inter', 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }}

        [data-theme="light"] {{
            --bg-base: #f8fafc;
            --bg-surface: #ffffff;
            --bg-card: rgba(255, 255, 255, 0.95);
            --bg-card-hover: #ffffff;
            --bg-digest: #f1f5f9;
            --border-subtle: #e2e8f0;
            --border-hover: #6366f1;
            --border-active: #4f46e5;

            --text-heading: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --text-dim: #94a3b8;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }}

        #scrollProgress {{
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: linear-gradient(90deg, #4f46e5 0%, #06b6d4 50%, #10b981 100%);
            z-index: 9999;
            width: 0%;
            transition: width 0.1s ease-out;
        }}

        body {{
            background-color: var(--bg-base);
            color: var(--text-body);
            font-family: var(--font-sans);
            line-height: 1.6;
            overflow-x: hidden;
            min-height: 100vh;
            transition: background-color 0.3s, color 0.3s;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.12) 0%, transparent 60%),
                radial-gradient(circle at 10% 25%, rgba(6, 182, 212, 0.06) 0%, transparent 40%),
                radial-gradient(circle at 90% 45%, rgba(168, 85, 247, 0.06) 0%, transparent 45%);
            background-attachment: fixed;
        }}

        body::before {{
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
            z-index: 0;
        }}

        [data-theme="light"] body::before {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.02) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(0, 0, 0, 0.02) 1px, transparent 1px);
        }}

        /* =================== HERO SECTION =================== */
        .hero {{
            position: relative;
            z-index: 1;
            padding: 60px 24px 36px;
            text-align: center;
            border-bottom: 1px solid var(--border-subtle);
            background: linear-gradient(180deg, rgba(14, 20, 34, 0.6) 0%, rgba(8, 12, 20, 0.95) 100%);
            backdrop-filter: blur(12px);
        }}

        [data-theme="light"] .hero {{
            background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%);
        }}

        .hero-inner {{
            max-width: 1080px;
            margin: 0 auto;
        }}

        .brand-pill {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 16px;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.35);
            border-radius: 9999px;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            font-weight: 600;
            color: #818cf8;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
        }}

        .brand-dot {{
            width: 8px;
            height: 8px;
            background-color: #38bdf8;
            border-radius: 50%;
            box-shadow: 0 0 8px #38bdf8;
        }}

        .hero-title {{
            font-size: clamp(2rem, 4.5vw, 3.4rem);
            font-weight: 800;
            color: var(--text-heading);
            letter-spacing: -0.03em;
            line-height: 1.15;
            margin-bottom: 16px;
        }}

        .gradient-text {{
            background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 70%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        [data-theme="light"] .gradient-text {{
            background: linear-gradient(135deg, #1e1b4b 30%, #4338ca 70%, #0284c7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero-desc {{
            font-size: clamp(0.95rem, 1.8vw, 1.15rem);
            color: var(--text-muted);
            max-width: 780px;
            margin: 0 auto 24px;
            line-height: 1.7;
        }}

        .origin-banner {{
            max-width: 820px;
            margin: 0 auto 30px;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: var(--radius-md);
            padding: 12px 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-size: 0.88rem;
            color: #93c5fd;
            text-align: left;
        }}

        [data-theme="light"] .origin-banner {{
            background: #eff6ff;
            border-color: #bfdbfe;
            color: #1e40af;
        }}

        .origin-banner-icon {{
            font-size: 1.2rem;
            flex-shrink: 0;
        }}

        .origin-banner strong {{
            color: #ffffff;
            font-weight: 700;
        }}

        [data-theme="light"] .origin-banner strong {{
            color: #1e3a8a;
        }}

        .stats-dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            max-width: 880px;
            margin: 0 auto;
        }}

        .stat-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            padding: 16px 20px;
            border-radius: var(--radius-lg);
            backdrop-filter: blur(8px);
            display: flex;
            flex-direction: column;
            gap: 4px;
            transition: border-color 0.2s, transform 0.2s;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}

        .stat-card:hover {{
            border-color: rgba(99, 102, 241, 0.4);
            transform: translateY(-2px);
        }}

        .stat-num {{
            font-family: var(--font-mono);
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text-heading);
        }}

        .stat-label {{
            font-size: 0.82rem;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        /* =================== STICKY TOOLBAR =================== */
        .sticky-toolbar {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(8, 12, 20, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-subtle);
            padding: 16px 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: background 0.3s;
        }}

        [data-theme="light"] .sticky-toolbar {{
            background: rgba(255, 255, 255, 0.9);
        }}

        .toolbar-inner {{
            max-width: 1280px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        .search-row {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}

        .search-wrapper {{
            position: relative;
            flex-grow: 1;
        }}

        .search-icon {{
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            width: 18px;
            height: 18px;
            color: var(--text-muted);
            pointer-events: none;
        }}

        .search-input {{
            width: 100%;
            padding: 13px 48px 13px 46px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            color: var(--text-heading);
            font-size: 0.95rem;
            font-family: inherit;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .search-input:focus {{
            outline: none;
            border-color: #6366f1;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
        }}

        .shortcut-badge {{
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-muted);
            padding: 2px 7px;
            border-radius: 4px;
            font-family: var(--font-mono);
            font-size: 0.75rem;
            pointer-events: none;
        }}

        [data-theme="light"] .shortcut-badge {{
            background: #e2e8f0;
            border-color: #cbd5e1;
        }}

        .theme-toggle-btn {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            color: var(--text-heading);
            width: 44px;
            height: 44px;
            border-radius: var(--radius-md);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            transition: all 0.2s;
            flex-shrink: 0;
        }}

        .theme-toggle-btn:hover {{
            border-color: var(--primary);
            transform: scale(1.05);
        }}

        .results-count-chip {{
            font-family: var(--font-mono);
            font-size: 0.85rem;
            color: var(--text-muted);
            white-space: nowrap;
            padding: 0 4px;
        }}

        .results-count-chip strong {{
            color: #38bdf8;
        }}

        .filter-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .filter-group {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .pill-btn {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-subtle);
            color: var(--text-body);
            padding: 7px 14px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        [data-theme="light"] .pill-btn {{
            background: #f1f5f9;
        }}

        .pill-btn:hover {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-heading);
            border-color: rgba(255, 255, 255, 0.2);
        }}

        [data-theme="light"] .pill-btn:hover {{
            background: #e2e8f0;
        }}

        .pill-btn.active {{
            background: var(--primary);
            border-color: var(--primary);
            color: #ffffff;
            box-shadow: 0 0 16px var(--primary-glow);
        }}

        /* =================== MAIN CONTENT & BENTO GRID =================== */
        .main-container {{
            position: relative;
            z-index: 1;
            max-width: 1280px;
            margin: 0 auto;
            padding: 32px 24px 80px;
        }}

        .grid-layout {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 24px;
        }}

        /* =================== CARD =================== */
        .slide-card {{
            position: relative;
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-xl);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), 
                        border-color 0.25s, 
                        box-shadow 0.25s;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}

        .slide-card:hover {{
            transform: translateY(-4px);
            border-color: var(--border-hover);
            box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.4), 0 0 24px -5px rgba(99, 102, 241, 0.25);
        }}

        .card-cover-container {{
            position: relative;
            width: 100%;
            aspect-ratio: 16 / 9;
            background: #090e17;
            overflow: hidden;
        }}

        .card-cover-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .slide-card:hover .card-cover-img {{
            transform: scale(1.04);
        }}

        .cover-overlay {{
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, rgba(8, 12, 20, 0.2) 0%, rgba(8, 12, 20, 0.85) 100%);
            pointer-events: none;
        }}

        .cover-top-bar {{
            position: absolute;
            top: 12px;
            left: 12px;
            right: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 2;
        }}

        .day-chip {{
            font-family: var(--font-mono);
            font-size: 0.72rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 9999px;
            background: rgba(0, 0, 0, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #e2e8f0;
            backdrop-filter: blur(8px);
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-family: var(--font-mono);
            font-size: 0.72rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 9999px;
            backdrop-filter: blur(8px);
        }}

        .badge-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
        }}

        .badge-pdf {{
            background: rgba(79, 70, 229, 0.3);
            border: 1px solid rgba(99, 102, 241, 0.5);
            color: #a5b4fc;
        }}

        [data-theme="light"] .badge-pdf {{
            background: rgba(79, 70, 229, 0.12);
            color: #4338ca;
            border-color: rgba(99, 102, 241, 0.3);
        }}

        .badge-pdf .badge-dot {{
            background-color: #818cf8;
            box-shadow: 0 0 6px #818cf8;
        }}

        .badge-ext {{
            background: rgba(16, 185, 129, 0.25);
            border: 1px solid rgba(16, 185, 129, 0.5);
            color: #6ee7b7;
        }}

        [data-theme="light"] .badge-ext {{
            background: rgba(16, 185, 129, 0.12);
            color: #047857;
            border-color: rgba(16, 185, 129, 0.3);
        }}

        .badge-ext .badge-dot {{
            background-color: #34d399;
            box-shadow: 0 0 6px #34d399;
        }}

        .cover-bottom-bar {{
            position: absolute;
            bottom: 12px;
            left: 14px;
            right: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 2;
            font-size: 0.78rem;
            color: #e2e8f0;
        }}

        .time-chip, .room-chip {{
            background: rgba(8, 12, 20, 0.75);
            padding: 3px 8px;
            border-radius: var(--radius-sm);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(6px);
        }}

        /* 卡片主體 */
        .card-content {{
            padding: 20px;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }}

        .tags-container {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }}

        .topic-tag {{
            font-size: 0.72rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            letter-spacing: 0.02em;
        }}

        .tag-agent {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.25); }}
        .tag-arch {{ background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.25); }}
        .tag-sec {{ background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.25); }}
        .tag-ops {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.25); }}
        .tag-general {{ background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.25); }}

        [data-theme="light"] .tag-agent {{ background: #e0f2fe; color: #0284c7; border-color: #bae6fd; }}
        [data-theme="light"] .tag-arch {{ background: #f3e8ff; color: #7e22ce; border-color: #e9d5ff; }}
        [data-theme="light"] .tag-sec {{ background: #ffe4e6; color: #e11d48; border-color: #fecdd3; }}
        [data-theme="light"] .tag-ops {{ background: #fef3c7; color: #b45309; border-color: #fde68a; }}
        [data-theme="light"] .tag-general {{ background: #f1f5f9; color: #475569; border-color: #e2e8f0; }}

        .card-title {{
            font-size: 1.15rem;
            font-weight: 700;
            line-height: 1.45;
            color: var(--text-heading);
            margin-bottom: 12px;
            letter-spacing: -0.015em;
        }}

        .speakers-container {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 16px;
        }}

        .speaker-chip {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
            border: 1.5px solid rgba(255, 255, 255, 0.15);
            background: #182338;
            flex-shrink: 0;
        }}

        [data-theme="light"] .avatar {{
            border-color: #cbd5e1;
            background: #e2e8f0;
        }}

        .avatar-fallback {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #182338;
            border: 1.5px solid rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            flex-shrink: 0;
        }}

        [data-theme="light"] .avatar-fallback {{
            background: #e2e8f0;
            border-color: #cbd5e1;
        }}

        .speaker-info {{
            display: flex;
            flex-direction: column;
            min-width: 0;
        }}

        .speaker-name {{
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--text-heading);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .speaker-dept {{
            font-size: 0.78rem;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* =================== 內容精華說明區塊 =================== */
        .digest-box {{
            background: var(--bg-digest);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 14px;
            margin-bottom: 18px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .digest-summary {{
            display: flex;
            align-items: flex-start;
            gap: 8px;
            padding-bottom: 10px;
            border-bottom: 1px dashed var(--border-subtle);
        }}

        .digest-icon {{
            font-size: 1.1rem;
            flex-shrink: 0;
            line-height: 1.4;
        }}

        .digest-text {{
            font-size: 0.88rem;
            font-weight: 600;
            color: var(--text-heading);
            line-height: 1.5;
        }}

        .digest-details {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .digest-section {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .digest-label {{
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            display: inline-flex;
            align-items: center;
            width: fit-content;
            padding: 1px 6px;
            border-radius: 4px;
        }}

        .label-pain {{ color: #f87171; background: rgba(239, 68, 68, 0.12); }}
        .label-sol {{ color: #38bdf8; background: rgba(56, 189, 248, 0.12); }}
        .label-takeaway {{ color: #34d399; background: rgba(16, 185, 129, 0.12); }}

        .digest-desc {{
            font-size: 0.82rem;
            color: var(--text-body);
            line-height: 1.55;
        }}

        .digest-list {{
            list-style: none;
            padding: 0;
            display: flex;
            flex-direction: column;
            gap: 4px;
            margin-top: 2px;
        }}

        .digest-list li {{
            font-size: 0.8rem;
            color: var(--text-muted);
            line-height: 1.5;
            position: relative;
            padding-left: 14px;
        }}

        .digest-list li::before {{
            content: "•";
            position: absolute;
            left: 2px;
            color: #34d399;
            font-weight: bold;
        }}

        /* 卡片底部按鈕區 */
        .card-footer {{
            margin-top: auto;
            padding-top: 14px;
            border-top: 1px solid var(--border-subtle);
        }}

        .actions-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 8px;
        }}

        .card-btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 11px 14px;
            border-radius: var(--radius-md);
            font-size: 0.85rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            border: 1px solid transparent;
            white-space: nowrap;
        }}

        .btn-icon {{
            width: 16px;
            height: 16px;
            flex-shrink: 0;
        }}

        /* 唯一主按鈕：直連官方原網址下載 */
        .btn-primary {{
            background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%);
            color: #ffffff;
            box-shadow: 0 2px 10px rgba(79, 70, 229, 0.35);
        }}

        .btn-primary:hover {{
            background: linear-gradient(135deg, #3730a3 0%, #4f46e5 100%);
            box-shadow: 0 4px 16px rgba(79, 70, 229, 0.55);
            transform: translateY(-1px);
        }}

        .btn-share {{
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-body);
            border-color: var(--border-subtle);
        }}

        [data-theme="light"] .btn-share {{
            background: #f1f5f9;
        }}

        .btn-share:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-heading);
            border-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }}

        [data-theme="light"] .btn-share:hover {{
            background: #e2e8f0;
        }}

        /* =================== TOAST NOTIFICATION =================== */
        .toast {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #1e293b;
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 12px 20px;
            border-radius: var(--radius-md);
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            pointer-events: none;
        }}

        .toast.show {{
            transform: translateY(0);
            opacity: 1;
        }}

        .toast-icon {{
            color: #10b981;
            font-size: 1.1rem;
        }}

        /* =================== BACK TO TOP BUTTON =================== */
        .back-to-top {{
            position: fixed;
            bottom: 30px;
            left: 30px;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            color: var(--text-heading);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 16px rgba(0,0,0,0.3);
            z-index: 90;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s;
            pointer-events: none;
        }}

        .back-to-top.visible {{
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }}

        .back-to-top:hover {{
            border-color: var(--primary);
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3);
        }}

        /* =================== NO RESULT =================== */
        .no-result {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 80px 20px;
            display: none;
        }}

        .no-result-icon {{
            font-size: 3rem;
            margin-bottom: 12px;
        }}

        .no-result-title {{
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--text-heading);
            margin-bottom: 8px;
        }}

        .no-result-desc {{
            color: var(--text-muted);
            font-size: 0.95rem;
        }}

        /* =================== FOOTER =================== */
        footer {{
            position: relative;
            z-index: 1;
            border-top: 1px solid var(--border-subtle);
            background: var(--bg-surface);
            padding: 48px 24px;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}

        .footer-links {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}

        .footer-link {{
            color: #818cf8;
            text-decoration: none;
            transition: color 0.2s;
        }}

        .footer-link:hover {{
            color: #c7d2fe;
            text-decoration: underline;
        }}

        /* =================== MOBILE RESPONSIVE =================== */
        @media (max-width: 640px) {{
            .hero {{
                padding: 40px 16px 28px;
            }}
            .hero-title {{
                font-size: 1.75rem;
            }}
            .origin-banner {{
                flex-direction: column;
                text-align: center;
            }}
            .stats-dashboard {{
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }}
            .stat-card {{
                padding: 12px;
            }}
            .stat-num {{
                font-size: 1.4rem;
            }}
            .sticky-toolbar {{
                padding: 12px 16px;
            }}
            .main-container {{
                padding: 20px 14px 60px;
            }}
            .grid-layout {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
            .card-title {{
                font-size: 1.05rem;
            }}
            .actions-grid {{
                grid-template-columns: 1fr;
            }}
            .back-to-top {{
                bottom: 20px;
                left: 20px;
            }}
        }}
    </style>
</head>
<body>

<div id="scrollProgress"></div>

<!-- HERO HEADER -->
<header class="hero">
    <div class="hero-inner">
        <div class="brand-pill">
            <span class="brand-dot"></span>
            <span>HWDC 2026 ARCHIVE · 55 SESSIONS EXECUTIVE SUMMARY</span>
        </div>
        <h1 class="hero-title">
            <span class="gradient-text">Hello World Dev Conference 2026</span><br>
            演講簡報精華庫與官方原網址直連
        </h1>
        <p class="hero-desc">
            全會期完整收錄 55 場前瞻架構、AI Coding、Agentic 治理與效能監測之深度內容精華。
            每場皆解析<strong>核心痛點、關鍵解法與實踐結論</strong>，直連 iThome 大會官方原網址下載。
        </p>

        <!-- 官方原始網址聲明橫幅 -->
        <div class="origin-banner">
            <span class="origin-banner-icon">📌</span>
            <div>
                <strong>官方原網址直連保證：</strong>
                本站所有卡片的主按鈕<strong>「官方原網址下載」</strong>均 100% 直連 iThome HWDC 2026 大會伺服器或講者原始教材，絕非第三方修改檔；精華說明供讀者在下載前快速掌握技術乾貨。
            </div>
        </div>

        <div class="stats-dashboard">
            <div class="stat-card">
                <span class="stat-num">{total_count}</span>
                <span class="stat-label">演講精華總數</span>
            </div>
            <div class="stat-card">
                <span class="stat-num" style="color: #818cf8;">{len(pdf_sessions)}</span>
                <span class="stat-label">官方 PDF 簡報</span>
            </div>
            <div class="stat-card">
                <span class="stat-num" style="color: #38bdf8;">{total_size_mb:.1f} <small style="font-size: 0.9rem;">MB</small></span>
                <span class="stat-label">官方簡報總量</span>
            </div>
            <div class="stat-card">
                <span class="stat-num" style="color: #34d399;">{len(ext_sessions)}</span>
                <span class="stat-label">講者線上專題</span>
            </div>
        </div>
    </div>
</header>

<!-- STICKY CONTROL TOOLBAR -->
<aside class="sticky-toolbar">
    <div class="toolbar-inner">
        <div class="search-row">
            <div class="search-wrapper">
                <svg class="search-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
                </svg>
                <input type="text" id="searchInput" class="search-input" placeholder="即時篩選題目、講者姓名、任職單位、精華關鍵字 (按 / 鍵聚焦)..." autocomplete="off">
                <span class="shortcut-badge">/</span>
            </div>
            
            <button type="button" class="theme-toggle-btn" id="themeToggle" title="切換深色 / 淺色主題">
                🌓
            </button>

            <div class="results-count-chip">
                顯示 <strong id="visibleCount">{total_count}</strong> / {total_count} 場
            </div>
        </div>

        <div class="filter-row">
            <div class="filter-group">
                <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600; margin-right: 4px;">日程：</span>
                <button type="button" class="pill-btn active" data-filter="date" data-val="all">全部會期</button>
                <button type="button" class="pill-btn" data-filter="date" data-val="10/14">10/14 Day 1 ({day1_count})</button>
                <button type="button" class="pill-btn" data-filter="date" data-val="10/15">10/15 Day 2 ({day2_count})</button>
            </div>

            <div class="filter-group">
                <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600; margin-right: 4px;">格式：</span>
                <button type="button" class="pill-btn active" data-filter="type" data-val="all">所有格式</button>
                <button type="button" class="pill-btn" data-filter="type" data-val="pdf">📄 PDF 檔案 ({len(pdf_sessions)})</button>
                <button type="button" class="pill-btn" data-filter="type" data-val="ext">🌐 線上教材 ({len(ext_sessions)})</button>
            </div>
        </div>
    </div>
</aside>

<!-- MAIN CONTENT -->
<main class="main-container">
    <div class="grid-layout" id="cardsGrid">
        {cards_rendered}
        <div class="no-result" id="noResult">
            <div class="no-result-icon">🔎</div>
            <h4 class="no-result-title">未找到符合條件的演講簡報</h4>
            <p class="no-result-desc">請嘗試輸入不同的關鍵字或重設篩選條件（可按 ESC 鍵清空搜尋）。</p>
        </div>
    </div>
</main>

<!-- BACK TO TOP BUTTON -->
<button type="button" class="back-to-top" id="backToTop" onclick="scrollToTop()" title="返回頂部">
    ↑
</button>

<!-- TOAST MESSAGE -->
<div class="toast" id="toastMsg">
    <span class="toast-icon">✓</span>
    <span id="toastText">已複製分享資訊！</span>
</div>

<!-- FOOTER -->
<footer>
    <div class="footer-links">
        <a href="https://hwdc.ithome.com.tw/2026/slide" target="_blank" rel="noopener noreferrer" class="footer-link">大會官方簡報下載頁</a>
        <a href="https://hwdc.ithome.com.tw/2026/agenda" target="_blank" rel="noopener noreferrer" class="footer-link">官方議程總表</a>
        <a href="https://hwdc.ithome.com.tw/2026/speaker" target="_blank" rel="noopener noreferrer" class="footer-link">官方講者名單</a>
    </div>
    <p>© 2026 iThome 電週文化事業股份有限公司 · 簡報與專案著作權全數歸講者與原著所有</p>
    <p style="margin-top: 6px; color: var(--text-dim);">本站主按鈕 100% 直連官方原網址；精華整理供社群技術研討與快速索引之用。</p>
</footer>

<script>
    const searchInput = document.getElementById('searchInput');
    const cards = Array.from(document.querySelectorAll('.slide-card'));
    const visibleCountEl = document.getElementById('visibleCount');
    const noResult = document.getElementById('noResult');
    const filterBtns = document.querySelectorAll('.pill-btn');
    const toast = document.getElementById('toastMsg');
    const toastText = document.getElementById('toastText');
    const themeToggle = document.getElementById('themeToggle');
    const scrollProgress = document.getElementById('scrollProgress');
    const backToTop = document.getElementById('backToTop');

    let curDateFilter = 'all';
    let curTypeFilter = 'all';

    // 捲動進度與返回頂部
    window.addEventListener('scroll', () => {{
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const progress = (scrollHeight > 0) ? (scrollTop / scrollHeight) * 100 : 0;
        scrollProgress.style.width = progress + '%';

        if (scrollTop > 400) {{
            backToTop.classList.add('visible');
        }} else {{
            backToTop.classList.remove('visible');
        }}
    }});

    function scrollToTop() {{
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    // 深色 / 淺色主題切換
    function initTheme() {{
        const saved = localStorage.getItem('hwdc_theme') || 'dark';
        document.documentElement.setAttribute('data-theme', saved);
        themeToggle.innerText = (saved === 'dark') ? '🌓' : '☀️';
    }}

    themeToggle.addEventListener('click', () => {{
        const cur = document.documentElement.getAttribute('data-theme') || 'dark';
        const next = (cur === 'dark') ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('hwdc_theme', next);
        themeToggle.innerText = (next === 'dark') ? '🌓' : '☀️';
        showToast(next === 'dark' ? '已切換為深邃科技暗黑模式' : '已切換為簡約高雅亮色模式');
    }});

    initTheme();

    function runFilter() {{
        const query = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        cards.forEach(card => {{
            const cardDate = card.getAttribute('data-date');
            const cardType = card.getAttribute('data-type');
            const cardText = card.innerText.toLowerCase();

            const matchDate = (curDateFilter === 'all' || cardDate === curDateFilter);
            const matchType = (curTypeFilter === 'all' || cardType === curTypeFilter);
            const matchQuery = (!query || cardText.includes(query));

            if (matchDate && matchType && matchQuery) {{
                card.style.display = 'flex';
                visibleCount++;
            }} else {{
                card.style.display = 'none';
            }}
        }});

        visibleCountEl.innerText = visibleCount;
        noResult.style.display = (visibleCount === 0) ? 'block' : 'none';
    }}

    filterBtns.forEach(btn => {{
        btn.addEventListener('click', () => {{
            const filterType = btn.getAttribute('data-filter');
            const val = btn.getAttribute('data-val');

            document.querySelectorAll(`.pill-btn[data-filter="${{filterType}}"]`).forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            if (filterType === 'date') curDateFilter = val;
            if (filterType === 'type') curTypeFilter = val;

            runFilter();
        }});
    }});

    searchInput.addEventListener('input', runFilter);

    // 快捷鍵支援
    window.addEventListener('keydown', (e) => {{
        if (e.key === '/' && document.activeElement !== searchInput) {{
            e.preventDefault();
            searchInput.focus();
            searchInput.select();
        }} else if (e.key === 'Escape') {{
            if (searchInput.value) {{
                searchInput.value = '';
                runFilter();
            }}
        }}
    }});

    // 複製分享功能
    function copyInfo(title, speaker, url) {{
        const text = `【HWDC 2026 演講簡報精華】\\n題目：${{title}}\\n講者：${{speaker}}\\n官方原網址：${{url}}`;
        navigator.clipboard.writeText(text).then(() => {{
            showToast('已複製議程與官方原網址！');
        }}).catch(() => {{
            showToast('複製失敗，請手動選取');
        }});
    }}

    function showToast(msg) {{
        toastText.innerText = msg;
        toast.classList.add('show');
        setTimeout(() => {{
            toast.classList.remove('show');
        }}, 2500);
    }}
</script>

</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Successfully generated V4 Awwwards-grade {OUTPUT_HTML} (Total {total_count} sessions with full executive digests)")

if __name__ == "__main__":
    generate_awwwards_html_v4()
