#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
PROJECT ID          : Hermes Project (黑密斯全球分散式智慧終端矩陣)
MODULE ID           : task1_collector-12-1.py
VERSION             : v5.7.1-SectorIsolation (成分股隔離暨去重死命令完全體)
================================================================================
"""
import sys
import os
import json
import logging
import smtplib
import re
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime

sys.path.insert(0, '/Users/apple/Library/Python/3.9/lib/python/site-packages')
from google import genai
from google.genai import types
import yfinance as yf

# =====================================================================
# ⚙️ 系統日誌計量配置
# =====================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

# =====================================================================
# 🔐 戰略物資配置區
# =====================================================================
GEMINI_API_KEYS = [
    os.environ.get("GEMINI_API_KEY_1", "AQ.Ab8RN6JQOHO7MeqTHJqaiEyVwJQyPvdqvzx53ZydjCawokJ1-w"),
    os.environ.get("GEMINI_API_KEY_2", "AQ.Ab8RN6JnDCRiCVETRzNhYIAp6OhvdHK3Fkhdir45oN-Zsh_qgQ"),
    os.environ.get("GEMINI_API_KEY_3", "AQ.Ab8RN6JzE99z5E-Nuuu27_OHYhJ7_DY_YXbJa_4blabk5ERHAQ"),
    os.environ.get("GEMINI_API_KEY_4", "AQ.Ab8RN6Ia5tVvGYw7nb7R8_2YU50lrgtyCdl1f9Os0uLS10yw6A"),
]
TARGET_MODEL_NAME = "gemini-2.5-flash"
TASK1_MEMORY_PATH = "/Users/apple/hermes_project/task1_memory.json"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "Chen.tok1979@gmail.com"
SENDER_PASSWORD = "zaopqbdaqlxomedw"
RECEIVER_EMAIL = "mao.yuang@gmail.com"

# =====================================================================
#  總裁欽定之絕對真理白名單 (用於 Stage 1 決定分析範圍與隔離約束)
# =====================================================================
HARDCODE_CANDIDATE_POOL = {
    "DJI": ["UNH", "GS", "MSFT", "HD", "AMGN", "CAT", "CRM", "V", "JPM", "BA", "TRV", "AXP", "WMT", "JNJ", "PG"],
    "SPX": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "TSLA", "UNH", "JPM", "V", "XOM", "LLY", "MA", "AVGO"],
    "IXIC": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "COST", "NFLX", "AMD", "PEP", "ADBE", "LIN", "TMUS"],
    "SOX": ["NVDA", "AVGO", "TSM", "AMD", "QCOM", "INTC", "MU", "MRVL", "AMAT", "LRCX", "KLAC", "SNPS", "CDNS", "ARM", "MCHP"]
}

# =====================================================================
# 🧠 v5.6.0 核心升級：物件導向金融實體識別與注入引擎 (OOP NER)
# =====================================================================
class TickerMarkerInjector:
    """
    【強制標記暨極簡注入引擎】
    依賴 AI 在文章中輸出的 [TICKER] 標記，Python 直接正則抓取並替換為鐵三角數據。
    """
    def __init__(self):
        self.ticker_cache = {}

    def fetch_yfinance_data(self, ticker):
        if ticker in self.ticker_cache:
            return self.ticker_cache[ticker]
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info or info.get('quoteType') != 'EQUITY' or info.get('currency') != 'USD':
                self.ticker_cache[ticker] = None
                return None
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
            mc = info.get('marketCap', 0)
            if not price or price <= 0:
                self.ticker_cache[ticker] = None
                return None
            if not mc or mc < 1_000_000_000:
                shares = info.get('sharesOutstanding', 0)
                mc = (price * shares) if (price and shares) else 0
                if mc < 1_000_000_000:
                    self.ticker_cache[ticker] = None
                    return None
            change_percent = info.get('regularMarketChangePercent', 0)
            if not change_percent:
                prev_p = info.get('regularMarketPreviousClose') or info.get('previousClose')
                if price and prev_p:
                    change_percent = ((price - prev_p) / prev_p) * 100
            data = {
                "change_percent": float(change_percent) if change_percent else 0.0,
                "current_price": float(price),
                "market_cap_b": float(mc) / 1e9
            }
            self.ticker_cache[ticker] = data
            return data
        except Exception as e:
            logger.debug(f"⚠️ yfinance 獲取 {ticker} 失敗: {e}")
            self.ticker_cache[ticker] = None
            return None

    def inject(self, report_text):
        logger.info("🔬 [極簡注入引擎啟動] 正在掃描 [TICKER] 標記並注入數據...")
        pattern = r'\[([A-Z]{1,5})\]'
        matches = re.findall(pattern, report_text)
        if not matches:
            logger.warning("️ 未在文章中發現 [TICKER] 標記，注入跳過。")
            return report_text
        
        unique_tickers = set(matches)
        for ticker in unique_tickers:
            data = self.fetch_yfinance_data(ticker)
            if data and data.get('current_price') > 0:
                sign = "+" if data['change_percent'] >= 0 else ""
                injection_str = f" ({sign}{data['change_percent']:.2f}%, 收盤: ${data['current_price']:.2f}, 市值: ${data['market_cap_b']:.1f}B)"
                report_text = report_text.replace(f"[{ticker}]", injection_str)
                logger.info(f"✅ 注入成功: [{ticker}] -> {injection_str}")
            else:
                report_text = report_text.replace(f"[{ticker}]", "")
                logger.info(f"⚠️ 無效 Ticker 或無數據，已清除標記: [{ticker}]")
        return report_text

# =====================================================================
# 🛡️ Python 真理驗證與強制排序引擎 (白名單直出)
# =====================================================================
def enforce_true_market_cap_ranking():
    logger.info("⚖️ [真理驗證引擎] 正在從白名單中抓取真實數據，執行加權排序...")
    true_ranking = {}
    for idx, tickers in HARDCODE_CANDIDATE_POOL.items():
        ranked_stocks = []
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                if not info or info.get('quoteType') != 'EQUITY' or info.get('currency') != 'USD': continue
                mc = info.get('marketCap', 0)
                price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
                if not mc or mc < 10_000_000_000:
                    shares = info.get('sharesOutstanding', 0)
                    mc = (price * shares) if (price and shares) else 0
                    if mc < 10_000_000_000: continue
                change_percent = info.get('regularMarketChangePercent', 0)
                if not change_percent:
                    prev_p = info.get('regularMarketPreviousClose') or info.get('previousClose')
                    if price and prev_p: change_percent = ((price - prev_p) / prev_p) * 100
                ranked_stocks.append({"ticker": ticker, "market_cap": float(mc), "current_price": float(price), "change_percent": float(change_percent) if change_percent else 0.0})
            except Exception as e: pass
        if idx == "DJI": ranked_stocks.sort(key=lambda x: x["current_price"], reverse=True)
        else: ranked_stocks.sort(key=lambda x: x["market_cap"], reverse=True)
        true_ranking[idx] = ranked_stocks[:5]
    return true_ranking

def stitch_top5_into_report(report_text, true_ranking):
    top5_texts = {}
    for idx, stocks in true_ranking.items():
        lines = []
        for s in stocks:
            sign = "+" if s['change_percent'] >= 0 else ""
            lines.append(f"        - {s['ticker']} ({sign}{s['change_percent']:.2f}%, 收盤: ${s['current_price']:.2f}, 市值: ${s['market_cap']/1e9:.1f}B)")
        top5_texts[idx] = "\n".join(lines)
    title_mapping = {"📊 藍籌權重巨頭表現：": "DJI", " 大盤權重巨頭表現：": "SPX", "📊 科技權重巨頭表現：": "IXIC", "📊 半導體權重龍頭表現：": "SOX"}
    report_text = re.sub(r'[（(]?\s*權重股具體數據.*?看板\s*[）)]?', '', report_text)
    for title, idx in title_mapping.items():
        if idx not in top5_texts: continue
        insert_text = f"\n{top5_texts[idx]}\n"
        pattern = re.escape(title) + r'[^\n]*\n*'
        if re.search(pattern, report_text):
            report_text = re.sub(pattern, title + insert_text, report_text, count=1)
    return report_text

# =====================================================================
#  郵件與 LLM 呼叫模組
# =====================================================================
def send_email_to_president(report_content):
    today_str = datetime.now().strftime("%Y-%m-%d")
    msg = MIMEText(report_content, 'plain', 'utf-8')
    msg['Subject'] = Header(f"【黑密斯矩陣・Task1 每日美股戰略情報】-{today_str}", 'utf-8')
    msg['From'] = Header(f"Hermes Agent Task1 <{SENDER_EMAIL}>", 'utf-8')
    msg['To'] = Header(RECEIVER_EMAIL, 'utf-8')
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
        server.close()
        logger.info("🟢 [Email Pushed] 戰報已 100% 成功遞送至總裁親啟信箱！")
    except Exception as e: logger.error(f"❌ Email 發射失敗: {e}")

def call_gemini_with_double_shield(prompt, tools_config=None, required_keywords=None, forbidden_keywords=None):
    key_index = 0
    while key_index < len(GEMINI_API_KEYS):
        current_key = GEMINI_API_KEYS[key_index]
        for attempt in range(2):
            try:
                client = genai.Client(api_key=current_key)
                if tools_config:
                    response = client.models.generate_content(model=TARGET_MODEL_NAME, contents=prompt, config=types.GenerateContentConfig(tools=tools_config))
                else:
                    response = client.models.generate_content(model=TARGET_MODEL_NAME, contents=prompt)
                result_text = response.text.strip()
                if not result_text or "error" in result_text.lower(): raise ValueError("AI 回傳無效雜訊。")
                if forbidden_keywords and any(fk in result_text for fk in forbidden_keywords): raise ValueError("觸犯防偷懶條款！")
                if required_keywords and not all(kw in result_text for kw in required_keywords): raise ValueError("缺失必要變數！")
                return result_text
            except Exception as e:
                if attempt == 0: logger.info("🔄 [軟故障原地自愈] 再次逼問 AI...")
                else: key_index += 1
    raise RuntimeError("💥 [核心崩潰] 4 個金鑰軌道已全數耗盡！")

# =====================================================================
# 🚀 主執行管線
# =====================================================================
def main():
    logger.info("🚀 [Task1 v5.7.1 成分股隔離完全體點火]...")
    try:
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Python 白名單直出 Top 5
        true_ranking = enforce_true_market_cap_ranking()
        
        # 2. Stage 1.5: AI 抓取收盤與催化劑事件
        data_gathering_prompt = (
            f"重要時空指引：現在時間是 {current_time_str}。\n"
            f"請利用 Google Search 精準查詢截止至今日（美東時間最新交易日收盤）以下核心數據：\n"
            f"1. 美股四大指數最新精確收盤價、漲跌點數、漲跌幅。請務必使用中文簡稱：『道瓊』、『標普500』、『那斯達克』、『費城半導體』。\n"
            f"2. 找出當天實際主導或嚴重衝擊這四大指數盤面、影響前三大的核心股票是哪三隻？它們具體發生了什麼催化劑事件？\n"
            f"   ⚠️【絕對數字封殺令】：描述催化劑事件時，**絕對禁止**寫出任何個股的『漲跌幅%』、『收盤價』或『市值』！只需寫出公司名稱/Ticker 和純文字事件邏輯。\n"
        )
        raw_facts = call_gemini_with_double_shield(data_gathering_prompt, tools_config=[{"google_search": {}}], required_keywords=["道瓊", "標普", "那斯達克", "費城"])
        
        # 3. Stage 2: AI 撰寫黑皮書 (強制成分股隔離)
        final_synthesis_prompt = (
            f"你現在是華爾街頂級投行的資深宏觀策略合夥人。\n"
            f"️【合夥人最高禁令 - 成分股隔離與去重死命令】：\n"
            f"1. 絕對禁止將同一組異動股（如 SpaceX, Intel, Micron）重複套用在四大指數中！每個指數必須根據其自身的成分股特性，挑選真正屬於該指數且當天有異動的股票！\n"
            f"2. 【道瓊指數】的異動股，必須嚴格從道瓊30只成分股（如 UNH, GS, MSFT, HD, CAT, AMGN 等）中挑選！絕對不允許寫 Intel 或 Micron！\n"
            f"3. 【費城半導體指數】的異動股，必須嚴格從半導體供應鏈（如 NVDA, TSM, AVGO, AMD, INTC, MU 等）中挑選！絕對不允許寫 SpaceX！\n"
            f"4. 如果當天某個指數沒有特別突出的專屬異動股，請從該指數的權重股中挑選漲跌幅最大的進行分析，絕不允許跨指數抄襲異動股！\n\n"
            f"5. 在分析「核心異動股」時，提到股票名稱時，**必須**在名稱後方加上中括號標註其 Ticker（例如：Arm Holdings [ARM]、Intel [INTC]）。\n"
            f"   **絕對禁止**寫出任何『漲跌幅%』、『收盤價』或『市值』數字！Python 引擎會自動將 [TICKER] 替換為完整的鐵三角數據。\n\n"
            f"📋 【今日美股核心量化與動態事件事實庫】：\n{raw_facts}\n\n"
            f"❌【排版禁令】：嚴禁使用 Markdown 表格語法。\n"
            f"👑【第一部分：最新收盤數據】\n請嚴格遵循奢華條列式輸出。\n"
            f"👑【第二部分：機構級核心戰略分析】\n"
            f"### **【細部分析與成分股解構】**\n"
            f"1. **【道瓊指數細部分析】**\n   * 📊 藍籌權重巨頭表現：\n   * 🎯 核心異動股與事件：(請從道瓊成分股中挑選，如 UNH, GS, CAT 等)\n   * 🔮 Overall 宏觀收斂：\n"
            f"2. **【標準普爾 500 指數細部分析】**\n   * 📊 大盤權重巨頭表現：\n   * 🎯 核心異動股與事件：(請從標普權重股中挑選)\n   * 🔮 Overall 宏觀收斂：\n"
            f"3. **【那斯達克綜合指數細部分析】**\n   * 📊 科技權重巨頭表現：\n   *  影響板塊前三大股票與變化：(請從科技/成長股中挑選)\n   * 🔮 Overall 宏觀收斂：\n"
            f"4. **【費城半導體指數細部分析】**\n   * 📊 半導體權重龍頭表現：\n   * 🎯 影響板塊前三大股票與變化：(請從半導體供應鏈中挑選，如 INTC, MU, AMD 等)\n   * 🔮 Overall 宏觀收斂：\n"
            f"請確保段落之間適度留白，保持華爾街高階黑皮書的純文字極致美感。"
        )
        report_text = call_gemini_with_double_shield(final_synthesis_prompt, required_keywords=["藍籌權重巨頭表現", "大盤權重巨頭表現", "科技權重巨頭表現", "半導體權重龍頭表現"])
        
        # 4. Python 強制插入 Top 5 數據
        report_text = stitch_top5_into_report(report_text, true_ranking)
        
        # 5. v5.6.0 核心升級：呼叫極簡注入引擎，替換 [TICKER] 為數據！
        injector = TickerMarkerInjector()
        report_text = injector.inject(report_text)
        
        print("\n👑 ==================== 📄 總裁御覽・2026 美股戰略大局情報 ====================")
        print(report_text)
        print("========================================================================\n")
        
        # 6. 落地與發信
        task1_node = {"task_id": "task1_us_market", "timestamp": current_time_str, "raw_report": report_text}
        os.makedirs(os.path.dirname(TASK1_MEMORY_PATH), exist_ok=True)
        with open(TASK1_MEMORY_PATH, "w", encoding="utf-8") as f: json.dump(task1_node, f, ensure_ascii=False, indent=4)
        send_email_to_president(report_text)
        logger.info("🏁 [Ultimate System Secured] 2026 鋼鐵防線全量暢通！")
        
    except Exception as e: logger.error(f"💥 Task1 發生終端異常: {e}")

if __name__ == "__main__":
    main()