import json
import re

META_FILE = "data/slides_meta.json"

# 總編針對特定場次的精修對照表 (index -> {summary, pain_point, solution})
POLISHED_EDITS = {
    29: {
        "summary": "AI 兩週寫了 5.3 萬行，人審不完。用 OpenSpec 定規格，用唯讀權限和 Harness 把違規交付擋在門外。",
        "pain_point": "AI Coding 產出暴增，但程式碼隱含規格漂移與架構污染，人類 Reviewer 根本無法逐行審查 5 萬行代碼。",
        "solution": "導入 OpenSpec RFC 2119 驗收邊界，配合 team-pipeline 角色權限隔離與 Hook 硬防線，違規代碼直接在 CI 阻斷。"
    },
    30: {
        "summary": "AI 讓 PR 多了 72%，QA 負擔漲 300%，瓶頸從寫程式換成驗證。作法是先用實例化需求對齊，再加多道工程門檻。",
        "pain_point": "團隊以為寫程式變快就是敏捷，結果下游 QA 被暴增 300% 的測試淹沒，綠燈很多但系統品質卻沒有變好。",
        "solution": "避開 Speed Trap 速度陷阱，在寫代碼前以實例化需求（Example Mapping）對齊邊界，並建立多層防線。"
    },
    33: {
        "summary": "MCP 工具描述本身就能下毒。SBOM 和代碼掃描管不到，防線得放在架構層：憑證隔離加 Harness 硬防護。",
        "pain_point": "第三方 MCP Server 具備執行與網路權限，工具提示詞注入（Tool Poisoning）可在載入瞬間發起攻擊並橫向移動。",
        "solution": "憑證與金鑰永不進入 LLM Context，在 Gateway 層做 Audience / Scope 隔離，以確定性 Harness 攔截異常指令。"
    },
    35: {
        "summary": "別把『連線成功』當成『已授權』。PKCE、PRM、JWT 驗簽，加上三道檢查與離線撤銷補強。",
        "pain_point": "許多團隊直接把靜態 API Key 寫進 Agent 設定檔，只要連線成功就放行所有權限，缺乏動態授權與撤銷機制。",
        "solution": "實作 HTTP MCP OAuth 2.0 PKCE 流程，配合 PRM 動態探索與 JWKS 驗簽，嚴格切分 Scope 與有效期限。"
    },
    38: {
        "summary": "Coding Agent 開局就吃掉 2 萬 Token，只因載了 50 個無用工具。用 AI Gateway 加 Langfuse 量出基準線，再用日常 Tracing 做選型。",
        "pain_point": "跟風導入工具卻缺乏成本與延遲數據，Agent 預設掛載過多工具導致 Token 成本爆炸且回應延遲嚴重。",
        "solution": "透過 Langfuse 建立 Token / Latency 基準線，關閉未用工具直接省下 95% 浪費，以真實 Tracing 數據指導技術選型。"
    },
    40: {
        "summary": "企業需要確定性而非機率猜測。用 OWL / RDF 語意圖譜加 SHACL 規則，給 Agent 一個不能胡說的商業名詞標準。",
        "pain_point": "LLM 缺乏企業領域知識，遇到同名異義或專業商業邏輯時容易產生幻覺，直接生成錯誤決策。",
        "solution": "以 OWL / RDF 知識圖譜建立形式本體論，透過 SHACL 宣告商業約束規則，讓 Agent 生成前必須通過語意驗證。"
    },
    41: {
        "summary": "貝爾塔週一寫好的 Prompt，阿爾法週二無法重現。把工作流沉澱進 Git 與 Markdown，用契約化閉環取代隨意對話。",
        "pain_point": "團隊每個人各自摸索 Prompt，解法留在個人對話紀錄裡；換個人或換個模型就失效，缺乏團隊工程積累。",
        "solution": "建立『執行-驗證-反思-提案-審核』五大行為契約，將流程資產以最小 manifest 路由納入 Git 版本控管。"
    },
    43: {
        "summary": "每個人都有 AI，團隊反而更慢？問題在 Context 孤島。建立共享的團隊第三大腦，讓經驗不再重複踩坑。",
        "pain_point": "個別成員用 AI 產出變快，但決策脈絡各自鎖在個人對話框中，團隊整合同步成本反而不減反增。",
        "solution": "打破個人對話框邊界，將除錯軌跡、決策條件與業務限制結構化沉澱為團隊共用知識庫。"
    },
    44: {
        "summary": "長期記憶不能什麼都記。模仿人類海馬迴，用來源衰退、遺忘機制與模式分離，避免舊雜訊污染新決策。",
        "pain_point": "對話紀錄無差別全部存進向量庫，時間一久雜訊暴增，檢索命中率直線下滑且檢索費用高昂。",
        "solution": "模仿大腦記憶生理學，設計時間衰減係數與 Pattern Separation，高頻且被驗證有效的決策才強化留存。"
    },
    45: {
        "summary": "Terminal 跑指令太容易越界。用 ACP 協定簽約，搭 OpenAB Broker 限制執行權限與 Session 連線池。",
        "pain_point": "直接把本機 Bash 授權給 Coding Agent 風險極高，缺乏審查邊界與多 Agent 並行連線池隔離。",
        "solution": "透過 ACP 協定建立機器人間的通訊契約，以 OpenAB Broker 控管指令白名單並管理 Session 生命週期。"
    },
    48: {
        "summary": "AI 治理從網關開始。集中管理 SSO、Token 預算與 Rate Limit，外加模型自動故障轉移（Failover）。",
        "pain_point": "各專案各自串接不同大模型，帳單四散無法對帳，遇到單一供應商當機時整套服務停擺。",
        "solution": "架設統一 AI Gateway，集中身份驗證與用量限額，並設定多模型智慧路由與斷線即時備援。"
    },
    49: {
        "summary": "寫代碼變便宜了，工程師還剩下什麼？題目來自現場的洞察力、出錯後果分級放手，以及最後的架構交接。",
        "pain_point": "以為會下 Prompt 就能取代工程師，忽略了最核心的架構權衡、業務現場摩擦與非功能性需求。",
        "solution": "工程師轉型為具備 T 型審查半徑的架構把關者，依出錯衝擊光譜分級委託 Agent，專注高價值邊界決策。"
    },
    50: {
        "summary": "同一個 Prompt 為何差這麼多？別怪模型，問題在缺乏外圍工程腳手架（Harness）。",
        "pain_point": "反覆修改 Prompt 形容詞無法提升穩定度，遇到長 Context 時模型容易患上『迷失在中間（Lost-in-the-middle）』。",
        "solution": "從 Prompt 提升到 Harness 工程，建立輸入過濾、狀態邊界、自動化驗收與錯誤恢復四大外圍防護。"
    },
    51: {
        "summary": "用 AI 寫程式只是基本功。工程師往前走一步當 Product Builder，自己定義價值、痛點與驗收條件。",
        "pain_point": "工程師只等著接 Spec 做執行，當 AI 讓產出變便宜時，缺乏產品定位與商業判斷者最先被邊緣化。",
        "solution": "結合 Opportunity Solution Tree 與 User Story Mapping，工程師自己下場做價值切分與驗收標準設計。"
    },
    52: {
        "summary": "Prompt 守不住架構界線。把架構規則寫成 Lint 與 Architecture Test，代碼違規直接編譯報錯。",
        "pain_point": "在 Prompt 裡千叮嚀萬囑咐『不要跨層依賴』，Agent 下一輪還是會寫出循環引用與髒依賴。",
        "solution": "改用 forbidigo 與 depguard 撰寫架構單元測試，將分層邊界固化為靜態分析檢查，逼 Agent 自動修正。"
    },
    55: {
        "summary": "Agent Skill 也有生命週期。透過六大決策點與負案例測試，避免能力互相污染與記憶爆炸。",
        "pain_point": "團隊把所有功能一股腦寫成 Skill 塞給 Agent，導致工具描述打架、觸發混亂且執行成功率驟降。",
        "solution": "導入 Skill 生命週期治理，區分高頻核心與按需掛載能力，並以負案例測試驗證邊界乾淨。"
    }
}

# 全域清洗字典：把 PPT 行銷腔動詞換掉
REPLACE_PAIRS = [
    ("全面賦能", "輔助"),
    ("賦能", "支援"),
    ("深度重構", "重構"),
    ("建構全新價值範式", "改變工作模式"),
    ("杜絕", "避免"),
    ("斬斷", "阻斷"),
    ("落實", "執行"),
    ("打造", "建立"),
    ("核心痛點", "痛點"),
    ("關鍵解法", "解法"),
    ("關鍵帶走", "帶走"),
]

def polish():
    with open(META_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    for s in meta["sessions"]:
        idx = s["index"]
        
        # 標註重複演講的時段差異
        if idx == 1:
            s["title"] = s["title"] + " (10/14 上午場)"
        elif idx == 46:
            s["title"] = s["title"] + " (10/15 下午場)"
        elif idx == 8:
            s["title"] = s["title"] + " (10/14 工作坊)"
        elif idx == 35:
            s["title"] = s["title"] + " (10/15 工作坊)"
        elif idx == 13:
            s["title"] = s["title"] + " (10/14 演講)"
        elif idx == 29:
            s["title"] = s["title"] + " (10/15 演講)"

        # 應用總編具體精修
        if idx in POLISHED_EDITS:
            ed = POLISHED_EDITS[idx]
            s["summary"] = ed["summary"]
            s["pain_point"] = ed["pain_point"]
            s["solution"] = ed["solution"]

        # 一般欄位文字清洗
        for field in ["summary", "pain_point", "solution"]:
            txt = s.get(field, "")
            for old_w, new_w in REPLACE_PAIRS:
                txt = txt.replace(old_w, new_w)
            # 清除句式 "不是...而是..."
            txt = re.sub(r"不是([^，。；]+)而是([^，。；]+)", r"以\2取代\1", txt)
            s[field] = txt.strip()

        # takeaways 清洗
        cleaned_takeaways = []
        for t in s.get("takeaways", []):
            for old_w, new_w in REPLACE_PAIRS:
                t = t.replace(old_w, new_w)
            t = t.replace("必須", "").replace("嚴格", "").replace("全面", "").replace("精準", "").strip()
            cleaned_takeaways.append(t)
        s["takeaways"] = cleaned_takeaways

    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("Polishing data/slides_meta.json completed!")

if __name__ == "__main__":
    polish()
