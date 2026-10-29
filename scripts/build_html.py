import json
import html
import os

META_FILE = "data/slides_meta.json"
OUTPUT_HTML = "index.html"

# 精緻極簡 SVG 幾何圖示（零 Emoji，符合 Awwwards / Editorial 設計規範）
SVG_CLOCK = '<svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6.5"/><path d="M8 4.5v3.8l2.5 1.5"/></svg>'
SVG_LOCATION = '<svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 1.5c-2.8 0-5 2.2-5 5 0 3.8 5 8 5 8s5-4.2 5-8c0-2.8-2.2-5-5-5z"/><circle cx="8" cy="6.5" r="1.8"/></svg>'
SVG_DOWNLOAD = '<svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2.5v8m0 0l-3-3m3 3l3-3M2.5 13.5h11"/></svg>'
SVG_EXTERNAL = '<svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8.5v4.5H3.5V4.5H8M10 2.5h4v4M7 9.5l7-7"/></svg>'
SVG_SHARE = '<svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="5.5" y="5.5" width="7" height="7" rx="1.5"/><path d="M3.5 10.5V3.5h7"/></svg>'
SVG_CHEVRON = '<svg class="icon chevron" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6l4 4 4-4"/></svg>'
SVG_SEARCH = '<svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="7" cy="7" r="5"/><path d="M11 11l3.5 3.5"/></svg>'
SVG_THEME = '<svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="3.5"/><path d="M8 1.5v1.5M8 13v1.5M1.5 8h1.5M13 8h1.5M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M3.4 12.6l1.1-1.1M11.5 4.5l1.1-1.1"/></svg>'

def generate_warm_editorial_html():
    with open(META_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    sessions = meta.get("sessions", [])
    total_count = len(sessions)
    pdf_sessions = [s for s in sessions if s.get("is_pdf")]
    ext_sessions = [s for s in sessions if not s.get("is_pdf")]
    total_size_mb = sum(s.get("filesize_bytes", 0) for s in pdf_sessions) / (1024 * 1024)

    day1_sessions = [s for s in sessions if "10-14" in s.get("date", "")]
    day2_sessions = [s for s in sessions if "10-15" in s.get("date", "")]

    items_html = []
    for s in sessions:
        idx = s.get("index")
        date = s.get("date", "")
        is_day1 = "10-14" in date
        day_tag = "day1" if is_day1 else "day2"
        date_label = "10/14 (三)" if is_day1 else "10/15 (四)"
        
        start_time = s.get("start_time", "")
        end_time = s.get("end_time", "")
        time_display = f"{start_time}–{end_time}" if start_time and end_time else date_label
        classroom = s.get("classroom", "主會場")
        
        title_raw = s.get("title", "")
        title = html.escape(title_raw)
        
        speaker_display = html.escape(s.get("speaker_display", ""))
        company_display = html.escape(s.get("company_display", ""))
        cover_url = s.get("cover_url") or "https://hwdc.ithome.com.tw/2026/img/slides.jpg"
        orig_url = s.get("orig_slide_url", "")
        is_pdf = s.get("is_pdf", False)
        filesize_str = s.get("filesize_str", "")

        summary = html.escape(s.get("summary", ""))
        pain_point = html.escape(s.get("pain_point", ""))
        solution = html.escape(s.get("solution", ""))
        takeaways = s.get("takeaways", [])
        takeaways_li = "".join([f"<li>{html.escape(t)}</li>" for t in takeaways])

        # 主題分類（單色線條標記，無刺眼糖果色）
        t_lower = title_raw.lower()
        if any(k in t_lower for k in ["agent", "agentic", "skill", "mcp"]):
            category = "agent"
            category_name = "Agentic AI"
        elif any(k in t_lower for k in ["coding", "架構", "架構師", "架構設計", "structurizr"]):
            category = "arch"
            category_name = "架構工程"
        elif any(k in t_lower for k in ["治理", "security", "secret", "防護", "認證", "harness"]):
            category = "sec"
            category_name = "治理與安全"
        elif any(k in t_lower for k in ["測試", "o11y", "aiops", "團隊", "工作流", "敏捷", "計費"]):
            category = "ops"
            category_name = "團隊與工作流"
        else:
            category = "general"
            category_name = "前瞻技術"

        # 下載主要按鈕文字與圖示
        if is_pdf:
            dl_text = f"官方原網址下載 PDF"
            if filesize_str:
                dl_text += f" ({filesize_str})"
            dl_icon = SVG_DOWNLOAD
        else:
            dl_text = "前往講者原教材"
            dl_icon = SVG_EXTERNAL

        item = f"""
        <article class="session-entry" data-day="{day_tag}" data-type="{'pdf' if is_pdf else 'ext'}" data-cat="{category}" data-idx="{idx}">
            <div class="entry-index">{idx:02d}</div>
            
            <div class="entry-main">
                <header class="entry-header">
                    <div class="entry-meta-line">
                        <span class="meta-badge day-badge">{date_label}</span>
                        <span class="meta-item">{SVG_CLOCK} {time_display}</span>
                        <span class="meta-item">{SVG_LOCATION} {classroom}</span>
                        <span class="meta-badge cat-badge">{category_name}</span>
                    </div>
                    <h3 class="entry-title">{title}</h3>
                    <div class="entry-speaker">
                        <span class="speaker-name">{speaker_display}</span>
                        {f'<span class="speaker-title">{company_display}</span>' if company_display else ''}
                    </div>
                </header>

                <div class="entry-preview">
                    <p class="summary-lead">{summary}</p>
                </div>

                <details class="editorial-drawer" id="details-{idx}">
                    <summary class="drawer-trigger" aria-label="展開詳細痛點與解法">
                        <span class="drawer-trigger-text">閱讀深度剖析（痛點 / 解法 / 帶走）</span>
                        {SVG_CHEVRON}
                    </summary>
                    <div class="drawer-content">
                        <div class="drawer-grid">
                            <div class="drawer-block block-pain">
                                <div class="drawer-label">核心痛點</div>
                                <div class="drawer-text">{pain_point}</div>
                            </div>
                            <div class="drawer-block block-sol">
                                <div class="drawer-label">架構解法</div>
                                <div class="drawer-text">{solution}</div>
                            </div>
                            <div class="drawer-block block-takeaway">
                                <div class="drawer-label">關鍵帶走</div>
                                <ul class="takeaway-list">{takeaways_li}</ul>
                            </div>
                        </div>
                    </div>
                </details>

                <footer class="entry-footer">
                    <div class="action-cluster">
                        <a href="{orig_url}" target="_blank" rel="noopener noreferrer" class="action-btn btn-primary" title="直連大會官方原始檔案來源">
                            {dl_icon}
                            <span>{dl_text}</span>
                        </a>
                        <button type="button" class="action-btn btn-secondary" onclick="copySessionInfo('{html.escape(title_raw)}', '{speaker_display}', '{orig_url}')" title="複製標題與官方原網址">
                            {SVG_SHARE}
                            <span>複製分享</span>
                        </button>
                    </div>
                </footer>
            </div>
        </article>
        """
        items_html.append(item)

    all_items_markup = "\n".join(items_html)

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW" data-theme="warm">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>HWDC 2026 演講簡報編年紀要 | 官方原網址直連下載</title>
    <meta name="description" content="55 場 Hello World Dev Conference 2026 簡報深度精要（痛點、解法與帶走清單），直連 iThome 官方原網址下載。">
    <meta name="theme-color" content="#FBF9F5">
    
    <!-- Open Graph Metadata -->
    <meta property="og:title" content="HWDC 2026 演講簡報編年紀要 | 官方原網址直連下載">
    <meta property="og:description" content="55 場演講，每場整理成三件事：卡在哪、怎麼解、帶走什麼。簡報 PDF 一律連回 iThome 官方來源。">
    <meta property="og:type" content="website">

    <!-- Fonts: Newsreader (Editorial Serif) + Plus Jakarta Sans + JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        :root {{
            --font-serif: 'Newsreader', 'Songti TC', 'Noto Serif TC', serif;
            --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "PingFang TC", "Microsoft JhengHei", sans-serif;
            --font-mono: 'JetBrains Mono', monospace;

            /* Warm Paper Editorial Palette (Default) */
            --bg-page: #FBF9F5;
            --bg-surface: #FFFFFF;
            --bg-subtle: #F4EFEA;
            --bg-hover: #ECE6DE;
            --text-primary: #18181B;
            --text-secondary: #52525B;
            --text-muted: #71717A;
            --border-subtle: rgba(24, 24, 27, 0.08);
            --border-strong: rgba(24, 24, 27, 0.2);
            --accent: #C2410C; /* Terracotta Rust */
            --accent-hover: #9A3412;
            --accent-subtle: rgba(194, 65, 12, 0.08);
            --shadow-paper: 0 1px 3px rgba(24, 24, 27, 0.04), 0 6px 16px rgba(24, 24, 27, 0.03);
            --radius-editorial: 4px;
            --line-height-body: 1.7;
        }}

        [data-theme="dark"] {{
            /* Deep Charcoal Editorial Palette */
            --bg-page: #101216;
            --bg-surface: #181A20;
            --bg-subtle: #20232B;
            --bg-hover: #282C37;
            --text-primary: #F4F4F5;
            --text-secondary: #A1A1AA;
            --text-muted: #71717A;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-strong: rgba(255, 255, 255, 0.2);
            --accent: #FB923C;
            --accent-hover: #F97316;
            --accent-subtle: rgba(251, 146, 60, 0.12);
            --shadow-paper: 0 1px 3px rgba(0, 0, 0, 0.3), 0 8px 24px rgba(0, 0, 0, 0.2);
        }}

        *, *::before, *::after {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-page);
            color: var(--text-primary);
            font-family: var(--font-sans);
            font-size: 15px;
            line-height: var(--line-height-body);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            transition: background-color 0.25s ease, color 0.25s ease;
        }}

        a {{
            color: inherit;
            text-decoration: none;
        }}

        .icon {{
            width: 14px;
            height: 14px;
            display: inline-block;
            vertical-align: middle;
            flex-shrink: 0;
        }}

        /* Page Layout */
        .page-container {{
            max-width: 1040px;
            margin: 0 auto;
            padding: 0 24px 80px;
        }}

        /* Editorial Header / Masthead */
        .masthead {{
            padding: 60px 0 32px;
            border-bottom: 2px solid var(--text-primary);
            margin-bottom: 32px;
        }}

        .masthead-meta {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: var(--text-muted);
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 16px;
        }}

        .theme-toggle-btn {{
            background: none;
            border: 1px solid var(--border-subtle);
            padding: 5px 10px;
            border-radius: var(--radius-editorial);
            font-family: var(--font-sans);
            font-size: 0.75rem;
            color: var(--text-secondary);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
        }}
        .theme-toggle-btn:hover {{
            background-color: var(--bg-subtle);
            color: var(--text-primary);
        }}

        .masthead-grid {{
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 32px;
            align-items: end;
        }}

        .masthead-number {{
            font-family: var(--font-serif);
            font-size: clamp(4.5rem, 12vw, 8.5rem);
            line-height: 0.85;
            font-weight: 400;
            letter-spacing: -0.04em;
            color: var(--accent);
        }}

        .masthead-content {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .masthead-title {{
            font-family: var(--font-serif);
            font-size: clamp(1.8rem, 4vw, 2.8rem);
            font-weight: 600;
            line-height: 1.15;
            letter-spacing: -0.02em;
        }}

        .masthead-desc {{
            font-size: 1.05rem;
            color: var(--text-secondary);
            max-width: 680px;
            line-height: 1.6;
        }}

        /* Origin Notice Banner */
        .origin-notice {{
            margin-top: 24px;
            padding: 12px 16px;
            background-color: var(--bg-subtle);
            border-left: 3px solid var(--accent);
            font-size: 0.85rem;
            color: var(--text-secondary);
            line-height: 1.5;
            border-radius: 0 var(--radius-editorial) var(--radius-editorial) 0;
        }}
        .origin-notice strong {{
            color: var(--text-primary);
        }}

        /* Navigation & Filtering Strip */
        .control-strip {{
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: var(--bg-page);
            padding: 14px 0;
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            backdrop-filter: blur(12px);
        }}

        .filter-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .filter-pill {{
            background: none;
            border: 1px solid var(--border-subtle);
            padding: 6px 12px;
            border-radius: var(--radius-editorial);
            font-size: 0.82rem;
            font-weight: 500;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .filter-pill:hover {{
            background-color: var(--bg-subtle);
            color: var(--text-primary);
        }}

        .filter-pill.active {{
            background-color: var(--text-primary);
            border-color: var(--text-primary);
            color: var(--bg-page);
            font-weight: 600;
        }}

        .search-box {{
            position: relative;
            display: flex;
            align-items: center;
            min-width: 220px;
        }}

        .search-box input {{
            width: 100%;
            background-color: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-editorial);
            padding: 6px 10px 6px 30px;
            font-size: 0.82rem;
            color: var(--text-primary);
            outline: none;
            transition: border-color 0.15s ease;
        }}
        .search-box input:focus {{
            border-color: var(--accent);
        }}
        .search-box .icon {{
            position: absolute;
            left: 10px;
            color: var(--text-muted);
            pointer-events: none;
        }}

        .results-summary {{
            font-family: var(--font-mono);
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-bottom: 20px;
        }}

        /* Timeline Editorial List */
        .timeline-list {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .session-entry {{
            display: grid;
            grid-template-columns: 48px 1fr;
            gap: 20px;
            padding: 24px 20px;
            background-color: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-editorial);
            box-shadow: var(--shadow-paper);
            transition: border-color 0.2s ease, transform 0.15s ease;
        }}

        .session-entry:hover {{
            border-color: var(--border-strong);
        }}

        .entry-index {{
            font-family: var(--font-mono);
            font-size: 1rem;
            font-weight: 700;
            color: var(--accent);
            opacity: 0.85;
            padding-top: 2px;
        }}

        .entry-main {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .entry-header {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .entry-meta-line {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
            font-size: 0.78rem;
            color: var(--text-muted);
        }}

        .meta-badge {{
            padding: 2px 7px;
            border-radius: 2px;
            font-family: var(--font-mono);
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}

        .day-badge {{
            background-color: var(--bg-subtle);
            color: var(--text-secondary);
        }}

        .cat-badge {{
            border: 1px solid var(--border-subtle);
            color: var(--text-secondary);
        }}

        .meta-item {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .entry-title {{
            font-family: var(--font-serif);
            font-size: clamp(1.25rem, 2.2vw, 1.55rem);
            font-weight: 600;
            line-height: 1.35;
            color: var(--text-primary);
            letter-spacing: -0.01em;
        }}

        .entry-speaker {{
            display: flex;
            flex-wrap: wrap;
            align-items: baseline;
            gap: 8px;
            font-size: 0.88rem;
        }}

        .speaker-name {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .speaker-title {{
            color: var(--text-muted);
            font-size: 0.82rem;
        }}

        .entry-preview {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.65;
        }}

        /* Progressive Disclosure Drawer */
        .editorial-drawer {{
            margin-top: 4px;
            border-top: 1px dashed var(--border-subtle);
            padding-top: 10px;
        }}

        .drawer-trigger {{
            list-style: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--accent);
            padding: 4px 0;
            user-select: none;
            transition: color 0.15s ease;
        }}
        .drawer-trigger::-webkit-details-marker {{
            display: none;
        }}
        .drawer-trigger:hover {{
            color: var(--accent-hover);
        }}

        .drawer-trigger .chevron {{
            transition: transform 0.2s ease;
        }}
        details[open] .drawer-trigger .chevron {{
            transform: rotate(180deg);
        }}

        :focus-visible {{
            outline: 2px solid var(--accent);
            outline-offset: 2px;
        }}

        .drawer-content {{
            padding-top: 14px;
        }}

        details[open] .drawer-content {{
            animation: drawerSlideDown 0.22s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        @keyframes drawerSlideDown {{
            from {{
                opacity: 0;
                transform: translateY(-4px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .drawer-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
            background-color: var(--bg-subtle);
            padding: 16px;
            border-radius: var(--radius-editorial);
            border-left: 3px solid var(--accent);
        }}

        .drawer-block {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .drawer-label {{
            font-family: var(--font-mono);
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-primary);
        }}

        .drawer-text {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }}

        .takeaway-list {{
            margin-left: 18px;
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }}

        .takeaway-list li {{
            margin-bottom: 4px;
        }}

        /* Action Cluster */
        .entry-footer {{
            padding-top: 12px;
            margin-top: 4px;
        }}

        .action-cluster {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .action-btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 8px 16px;
            min-height: 40px;
            font-size: 0.82rem;
            font-weight: 600;
            border-radius: var(--radius-editorial);
            cursor: pointer;
            transition: all 0.15s ease;
            text-decoration: none;
        }}

        .btn-primary {{
            background-color: var(--accent);
            color: #FFFFFF;
            border: 1px solid var(--accent);
        }}
        .btn-primary:hover {{
            background-color: var(--accent-hover);
            border-color: var(--accent-hover);
            color: #FFFFFF;
        }}

        .btn-secondary {{
            background: none;
            color: var(--text-secondary);
            border: 1px solid var(--border-subtle);
        }}
        .btn-secondary:hover {{
            background-color: var(--bg-subtle);
            color: var(--text-primary);
            border-color: var(--border-strong);
        }}

        /* Colophon / Footer */
        .colophon {{
            margin-top: 60px;
            padding-top: 32px;
            border-top: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            gap: 12px;
            font-size: 0.85rem;
            color: var(--text-muted);
            line-height: 1.6;
        }}

        .colophon a {{
            color: var(--text-primary);
            text-decoration: underline;
            text-underline-offset: 3px;
        }}

        /* Mobile Adjustments (375px~600px) */
        @media (max-width: 640px) {{
            .page-container {{
                padding: 0 16px 60px;
            }}
            .masthead {{
                padding: 40px 0 24px;
            }}
            .masthead-grid {{
                grid-template-columns: 1fr;
                gap: 12px;
            }}
            .masthead-number {{
                font-size: 3.5rem;
            }}
            .session-entry {{
                grid-template-columns: 1fr;
                gap: 10px;
                padding: 18px 14px;
            }}
            .entry-index {{
                font-size: 0.85rem;
                border-bottom: 1px solid var(--border-subtle);
                padding-bottom: 4px;
            }}
            .control-strip {{
                flex-direction: column;
                align-items: stretch;
            }}
            .search-box {{
                width: 100%;
            }}
            .action-cluster {{
                flex-direction: column;
            }}
            .action-btn {{
                width: 100%;
                min-height: 44px;
            }}
        }}

        /* Reduced Motion */
        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="page-container">
        <!-- Masthead -->
        <header class="masthead">
            <div class="masthead-meta">
                <span>HWDC 2026 · ARCHIVE & DIGEST</span>
                <button type="button" class="theme-toggle-btn" onclick="toggleTheme()" aria-label="切換深淺模式">
                    {SVG_THEME}
                    <span id="theme-btn-label">切換深色</span>
                </button>
            </div>
            
            <div class="masthead-grid">
                <div class="masthead-number">55</div>
                <div class="masthead-content">
                    <h1 class="masthead-title">Hello World 演講簡報編年紀要</h1>
                    <p class="masthead-desc">
                        收錄 55 場前瞻架構、Agentic 治理與工程實戰投影片。每場梳理核心痛點、技術解法與關鍵帶走，提供大會原網址直連下載。
                    </p>
                </div>
            </div>

            <div class="origin-notice">
                <strong>原網址直連聲明：</strong>
                本站所有簡報下載均直接指向 iThome 官方伺服器（<code>ccms.ithome.com.tw</code>）與講者原教材，無第三方轉存。內文深度精要為人機協作整理。
            </div>
        </header>

        <!-- Control Strip -->
        <div class="control-strip">
            <div class="filter-group">
                <button class="filter-pill active" data-filter="all" onclick="setFilter('all', this)">全部 55 場</button>
                <button class="filter-pill" data-filter="day1" onclick="setFilter('day1', this)">10/14 Day 1 (27)</button>
                <button class="filter-pill" data-filter="day2" onclick="setFilter('day2', this)">10/15 Day 2 (28)</button>
                <button class="filter-pill" data-filter="pdf" onclick="setFilter('pdf', this)">PDF 簡報 (43)</button>
                <button class="filter-pill" data-filter="ext" onclick="setFilter('ext', this)">線上教材 (12)</button>
            </div>

            <div class="search-box">
                {SVG_SEARCH}
                <input type="search" id="search-input" placeholder="搜尋主題、講者、痛點關鍵字..." oninput="handleSearch(this.value)">
            </div>
        </div>

        <div class="results-summary" id="results-count">
            顯示 55 場演講中的 55 場
        </div>

        <!-- Timeline Entries -->
        <main class="timeline-list" id="sessions-container">
            {all_items_markup}
        </main>

        <!-- Colophon -->
        <footer class="colophon">
            <div>
                <strong>HWDC 2026 Archive</strong> · 台灣 IT 專案架構師與工程團隊的前瞻技術縮影。
            </div>
            <div>
                原始活動網站：<a href="https://hwdc.ithome.com.tw/2026/slide" target="_blank" rel="noopener noreferrer">HWDC 2026 官方大會簡報頁</a> · 
                開放專案庫：<a href="https://github.com/lushinshang/hwdc-2026-slides" target="_blank" rel="noopener noreferrer">GitHub Repository</a>
            </div>
        </footer>
    </div>

    <!-- Minimal Script for Filtering, Search, Drawer and Toast -->
    <script>
        let currentFilter = 'all';
        let searchQuery = '';

        function setFilter(type, btn) {{
            currentFilter = type;
            document.querySelectorAll('.filter-pill').forEach(el => el.classList.remove('active'));
            btn.classList.add('active');
            applyFilters();
        }}

        function handleSearch(val) {{
            searchQuery = val.trim().toLowerCase();
            applyFilters();
        }}

        function applyFilters() {{
            const entries = document.querySelectorAll('.session-entry');
            let visibleCount = 0;

            entries.forEach(entry => {{
                const day = entry.getAttribute('data-day');
                const type = entry.getAttribute('data-type');
                const text = entry.innerText.toLowerCase();

                let matchesFilter = false;
                if (currentFilter === 'all') matchesFilter = true;
                else if (currentFilter === 'day1' && day === 'day1') matchesFilter = true;
                else if (currentFilter === 'day2' && day === 'day2') matchesFilter = true;
                else if (currentFilter === 'pdf' && type === 'pdf') matchesFilter = true;
                else if (currentFilter === 'ext' && type === 'ext') matchesFilter = true;

                let matchesSearch = !searchQuery || text.includes(searchQuery);

                if (matchesFilter && matchesSearch) {{
                    entry.style.display = 'grid';
                    visibleCount++;
                }} else {{
                    entry.style.display = 'none';
                }}
            }});

            const countEl = document.getElementById('results-count');
            if (countEl) {{
                countEl.textContent = `顯示 55 場演講中的 ${{visibleCount}} 場`;
            }}
        }}

        function copySessionInfo(title, speaker, url) {{
            const textToCopy = `${{title}} | ${{speaker}}\\n官方原始連結：${{url}}`;
            navigator.clipboard.writeText(textToCopy).then(() => {{
                showToast('已複製演講資訊與官方原網址！');
            }}).catch(() => {{
                showToast('複製失敗，請手動複製');
            }});
        }}

        function showToast(msg) {{
            let toast = document.getElementById('editorial-toast');
            if (!toast) {{
                toast = document.createElement('div');
                toast.id = 'editorial-toast';
                toast.style.position = 'fixed';
                toast.style.bottom = '24px';
                toast.style.right = '24px';
                toast.style.backgroundColor = 'var(--text-primary)';
                toast.style.color = 'var(--bg-page)';
                toast.style.padding = '10px 18px';
                toast.style.borderRadius = 'var(--radius-editorial)';
                toast.style.fontSize = '0.85rem';
                toast.style.fontWeight = '600';
                toast.style.boxShadow = 'var(--shadow-paper)';
                toast.style.zIndex = '9999';
                toast.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
                document.body.appendChild(toast);
            }}
            toast.textContent = msg;
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
            setTimeout(() => {{
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(8px)';
            }}, 2200);
        }}

        function toggleTheme() {{
            const html = document.documentElement;
            const current = html.getAttribute('data-theme') || 'warm';
            const next = current === 'warm' ? 'dark' : 'warm';
            html.setAttribute('data-theme', next);
            localStorage.setItem('hwdc_theme', next);
            updateThemeLabel(next);
        }}

        function updateThemeLabel(theme) {{
            const label = document.getElementById('theme-btn-label');
            if (label) {{
                label.textContent = theme === 'warm' ? '切換深色' : '切換暖紙';
            }}
        }}

        // Initialize Theme from localStorage or system preference
        (function() {{
            const saved = localStorage.getItem('hwdc_theme');
            if (saved) {{
                document.documentElement.setAttribute('data-theme', saved);
                updateThemeLabel(saved);
            }}
        }})();
    </script>
</body>
</html>
"""
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Successfully generated Warm Paper Editorial index.html (Total {total_count} sessions)")

if __name__ == "__main__":
    generate_warm_editorial_html()
