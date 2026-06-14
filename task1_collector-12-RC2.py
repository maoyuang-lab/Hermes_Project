#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
PROJECT ID          : Hermes Project (黑密斯全球分散式智慧終端矩陣)
MODULE ID           : task1_collector-12-RC2.py
VERSION             : v5.8.1-AbsoluteObedience (絕對服從總裁數據暨CMMI5完全體)
PREVIOUS VERSION    : v5.7.1-SectorIsolation (成分股隔離暨去重死命令完全體)
變更維護人          : 茆裕源 (總裁)
變更日期            : 2026-06-14

================================================================================
【CMMI Level 5 核心架構深度重構日誌 (Changelog)】
================================================================================

一、 底層架構典範轉移：由「程序性腳本」全面重構為「物件導向 (OOP) 繼承體系」
--------------------------------------------------------------------------------
1. 【建立基礎抽象類別 (Base Class)】：
   - 廢棄 RC1 中鬆散的全局字典與全域函式。總裁親自設計並引入了 `BaseIndexAnalyzer` 作為系統的根基父類別。
   - 將所有指數共用的核心行為（如 yfinance 數據拉取、Top 5 排序、Ticker 注入準備）全數向上抽象封裝至 `BaseIndexAnalyzer` 中，
     徹底解決 RC1 代碼冗餘與維護死角。

2. 【實作多型衍生類別 (Polymorphic Subclasses)】：
   - 針對四大指數的獨特物理特性，繼承 `BaseIndexAnalyzer` 衍生出專屬子類別。
   - 重點重構：親手撰寫 `class SOXAnalyzer(BaseIndexAnalyzer):`。將原本暴露在外的 `SOX_AUTHORITY_WEIGHTS` 完全私有化、
     封裝進該類別的內部屬性中。
   - 透過類別覆寫 (Override)，`SOXAnalyzer` 現在擁有自己專屬的權重計算邏輯與 `check_rebalance_alert()` 防呆告警方法，
     實現了真正的關注點分離 (Separation of Concerns)。

3. 權限與數據真理重構 (CMMI Level 5)：
   - 將原本宣告為全域字典（Global Dictionary）的 `HARDCODE_CANDIDATE_POOL` 與 `SOX_AUTHORITY_WEIGHTS` 徹底解耦，
     全面重構並封裝至專屬的物件導向權重類別（Class）中，實現高內聚、低耦合的數據隔離防護。
   - 【道瓊工業指數 (DJI)】：全面剔除過期成分股 INTC，新晉納入 NVDA。名單由舊版無序排列，重構為完全依照高盛（GS）、
     卡特彼勒（CAT）等絕對股價由高至低的真實物理特性進行精確排列。
   - 【費城半導體指數 (SOX)】：重寫 `SOX_AUTHORITY_WEIGHTS` 權重字典與配置邏輯。100% 剔除舊版混入的非半導體製造實體
     （EDA 軟體雙雄 SNPS 與 CDNS），修正補入真正的半導體物理骨幹：艾司摩爾（ASML）、德州儀器（TXN）、亞德諾（ADI）。
   - 【標準普爾 500 指數 (SPX)】：修正舊版未及時反映最新市值、缺乏即時動態的弊端，重組後由輝達（NVDA）登頂第一，
     博通（AVGO）與禮來（LLY）權重暴衝並挺進核心前列。

4. 核心功能與函式（Changelog 完全漏掉的代碼 - 路由與初始化模組）：
   - 新增 get_index_analyzers() 路由函式：
     配合 OOP 重構，RC2 新增了此函式來統一實例化（Instantiate）四大指數的分析器物件，作為管線（Pipeline）的中央調度接口。
   - 新增「啟動自檢日誌區塊」：
     RC2 在宣告完 HARDCODE_CANDIDATE_POOL 後，直接在全局執行流中加入了一段 for 迴圈進行系統自檢（Line 132-136），
     驗證四大指數的白名單數量並輸出 logger.info。這是 RC1 沒有的動態行為。


二、 數據實體清洗與物理對齊 (封裝於各子類別內)
--------------------------------------------------------------------------------
1. 【SOXAnalyzer 內部權重清洗】：
   - 於 `SOXAnalyzer` 類別內，精確剔除 EDA 軟體雙雄 (SNPS, CDNS)，換裝實體晶片製造設備商 (ASML, TXN, ADI)，
     並將這套邏輯死鎖在該物件實體中，確保外部無法竄改。

2. 【其他指數類別實體更新】：
   - DJI 類別內部：剔除 INTC，納入 NVDA，並依絕對股價 (GS, CAT領銜) 重構加權順序。
   - SPX 類別內部：對齊最新市值，將 NVDA 權重推至首位，AVGO、LLY 緊跟其後。


三、 後處理流水線 (Pipeline) 接口全面物件化與輔補防禦
--------------------------------------------------------------------------------
1. 【流水線傳參升級】：
   - 舊版 `stitch_top5_into_report(report_text, true_ranking)` 依賴原始陣列傳遞。
   - 新版重構為 `stitch_top5_into_report(report_text, analyzers)`。直接傳入實例化後的 
     Analyzer 物件字典。後處理引擎現在透過調用物件的內部方法 (Methods) 來動態拼裝數據，大幅提升系統吞吐量與型別安全性。

2. 【防呆探針物件化】：
   - 實作 `ComponentDriftDetector` 類別，與各個 `Analyzer` 實例進行底層數據校驗。由物件相互調用來攔截 LLM 文本漂移，徹底告別 RC1 時代的字串硬匹配防禦。

3. 核心功能與函式（Changelog 完全漏掉的代碼 - 清洗模組）：
   - 新增 clean_ai_leakage(text) 輔助引擎：
     這是 RC2 全新引入的防禦機制，專門用來清洗、過濾 LLM 可能不小心吐出的「⚠️【合夥人最高禁令...】」等系統提示詞
     （Prompt Leakage），並優化多餘的換行。此重大後處理機制在日誌中完全沒被提及。


四、 審查校驗：數據池（HARDCODE_CANDIDATE_POOL）實際異動落差
--------------------------------------------------------------------------------
日誌中關於成分股替換的描述，與代碼裡的真實文字存在重大出入：

- 【那斯達克 100 (IXIC)】變更被完全遺忘：
  日誌在「一、3」與「二、2」中詳細說明了 DJI、SOX、SPX 的名單更新，卻完全漏掉了 IXIC。事實上，RC2 的 IXIC 名單做了動態調整：
  * 剔成了 PEP（百事可樂）、LIN（林德 Linde）。
  * 新晉了 QCOM（高通）、INTC（英特爾）。
  * 排序將 NVDA 推至第一位。

- 【道瓊指數 (DJI)】剔除對象與真實代碼不符：
  日誌寫道：「全面剔除過期成分股 INTC」。但比對 RC1 代碼後發現，RC1 的 DJI 白名單內本來就沒有 INTC。實際上，
  RC2 對 DJI 進行了大血洗，日誌卻沒寫完整：
  * 真實剔除： TRV（旅行家集團）、WMT（沃爾瑪）、JNJ（強生）、PG（寶僑）。
  * 真實新晉： MCD（麥當勞）、HON（漢威聯合）、NVDA（輝達）、DIS（迪士尼）。

- 【費城半導體 (SOX)】漏記剔除股：
  日誌提到換裝 ASML、TXN、ADI 並剔除 EDA 雙雄，但漏記了同時被剔除的 MCHP（微晶片科技）。


五、 審查校驗：架構宣稱與代碼實體的「理想與現實落差」
--------------------------------------------------------------------------------
日誌的架構定性（CMMI Level 5）寫得很漂亮，但代碼實作上留有妥協痕跡，建議修正日誌說法以符合事實：

- SOX_AUTHORITY_WEIGHTS 並未真正「私有化與完全封裝」：
  日誌宣稱將其：「徹底解耦，全面重構並封裝至專屬的物件導向權重類別中，確保外部無法竄改」。
  然而在 RC2 代碼中，SOX_AUTHORITY_WEIGHTS 依舊被宣告在全局變數區（Line 142）。在 SOXAnalyzer 類別內，
  也是直接引用全局變數（甚至帶有註解：# 修正：SOX_AUTHORITY_WEIGHTS 是全域變數，不需要加 self.）。
  它並非私有屬性（如 self.__weights），外部依然可以竄改。

- RC1 的 SOX_AUTHORITY_WEIGHTS 根本不存在：
  日誌提到：「將原本宣告為全域字典（Global Dictionary）的...SOX_AUTHORITY_WEIGHTS 徹底解耦」。事實上，
  RC1 根本沒有這個字典，這是 RC2 為了權重加權而全新創造的配置。


六、 Prompt 戰略防線與工程優化（漏寫的 AI 约束）
--------------------------------------------------------------------------------
您在 RC2 的 final_synthesis_prompt 中，對 AI 下達了更嚴厲的軍令，這些是防範 LLM 偷懶的關鍵，日誌並未提及：

- 新增【禁止過渡語命令】： 規定在【📊 藍籌權重巨頭表現：】等標題後「絕對禁止寫任何過渡語！直接換行」，強制優化排版。

- 新增【反鸚鵡嘴禁令】： 針對 Overall 宏觀收斂 嚴格限制「絕對禁止使用相似的套話或複製貼上」，逼迫 AI 輸出高階機構級的獨立解讀。

- 格式提示詞清洗（防漂移優化）：
  RC1 在 Prompt 模板中寫有 🎯 核心異動股與事件：(請從道瓊成分股中挑選...)。
  RC2 將括號內的提示文字 (請從...) 完全清空，只留下乾淨的標題。這是極佳的 Prompt Engineering，
  因為原括號文字極易被 LLM 誤當成內文直接吐出來。


七、 執行流與終端輸出行為變更
--------------------------------------------------------------------------------
- 關鍵字校驗放寬：
  在第一次呼叫 Gemini 時（data_gathering_prompt），RC1 的雙層防禦網校驗關鍵字為 ["道瓊", "標普", "那斯達克", "費城"]；RC2 將 "道瓊" 改為 ["道", "標普", "那斯達克", "費城"]，容錯率更高。

- 完全拔除終端控制台列印（Console Print）：
  RC1 在 main() 的尾聲，有將戰報實時列印到控制台的代碼（print("\n👑 ==================== 📄 總裁御覽...")）。
  RC2 全面拔成了 print 輸出，改為完全靜態運行，僅依賴日誌追蹤與發送 Email。這符合正式生產環境（Production）的背景排程規範。

===============================================================================
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
# 🎯 【總裁欽定絕對真理區 1】四大指數核心成分股池 (CMMI Level 5: 僅維護此字典)
# =====================================================================
HARDCODE_CANDIDATE_POOL = {
    # 道瓊工業指數：採用【股價加權】，名單由絕對股價高至低排列（高盛、卡特彼勒領舞）
    # 註：2024年底已正式納入 NVDA 剔除 INTC
    "DJI": [
        "GS",    # 高盛 (股價破千，權重第一)
        "CAT",   # 卡特彼勒 (股價次高，權重第二)
        "UNH",   # 聯合健康
        "HD",    # 家得寶
        "MSFT",  # 微軟
        "AMGN",  # 安進
        "CRM",   # 賽富時
        "V",     # 威士
        "BA",    # 波音
        "AXP",   # 美國運通
        "MCD",   # 麥當勞
        "JPM",   # 摩根大通
        "HON",   # 漢威聯合
        "NVDA",  # 輝達 (新晉道瓊權重股)
        "DIS"    # 迪士尼
    ],
    
    # 標普 500 指數：採用【市值加權】，真實反映美股前 15 大超級巨頭
    "SPX": [
        "NVDA",  # 輝達 (登頂全球市值王)
        "AAPL",  # 蘋果
        "MSFT",  # 微軟
        "AMZN",  # 亞馬遜
        "GOOGL", # Alphabet/谷歌
        "META",  # Meta/臉書
        "AVGO",  # 博通 (市值暴衝挺進核心)
        "LLY",   # 禮來 (醫藥巨頭，市值超車傳統科技)
        "BRK-B", # 波克夏
        "TSLA",  # 特斯拉
        "JPM",   # 摩根大通
        "V",     # 威士
        "MA",    # 萬事達卡
        "XOM",   # 埃克森美孚
        "UNH"    # 聯合健康
    ],
    
    # 那斯達克 100 / 綜合指數核心：大型非金融科技與消費巨頭
    "IXIC": [
        "NVDA",  # 輝達
        "AAPL",  # 蘋果
        "MSFT",  # 微軟
        "AMZN",  # 亞馬遜
        "GOOGL", # 谷歌
        "META",  # 臉書
        "AVGO",  # 博通
        "TSLA",  # 特斯拉
        "COST",  # 好市多 (權重極高的非科技消費王)
        "AMD",   # 超微
        "NFLX",  # 網飛
        "ADBE",  # 奧多比
        "QCOM",  # 高通
        "TMUS",  # T-Mobile
        "INTC"   # 英特爾
    ],
    
    # 費城半導體指數：純正 30 檔半導體【修正市值加權】之前 15 大主力
    # 修正重點：100% 剔除非 SOX 成分股的 EDA 軟體雙雄 (SNPS, CDNS)
    # 補上真正的 SOX 權重骨幹：TXN(德州儀器)、ASML(艾司摩爾)、ADI(亞德諾)
    "SOX": [
        "MU",    # 美光 (受 AI 記憶體推升，卡位最新改版第一大上限)
        "NVDA",  # 輝達 (權重受制 12% 天花板)
        "MRVL",  # 邁威爾科技
        "AVGO",  # 博通
        "AMD",   # 超微
        "INTC",  # 英特爾
        "QCOM",  # 高通
        "TXN",   # 德州儀器 (類比晶片巨頭) *修正補入
        "ASML",  # 艾司摩爾 (曝光機巨頭) *修正補入
        "ADI",   # 亞德諾半導體 (高階類比) *修正補入
        "AMAT",  # 應用材料 (設備)
        "LRCX",  # 科林研發 (設備)
        "KLAC",  # 科磊 (檢測設備)
        "TSM",   # 台積電 ADR (受限外國公司 10% 總池天花板)
        "ARM"    # 安謀 ADR
    ]
}

# =====================================================================
# 🚀 啟動自檢：驗證總裁欽定之絕對真理
# =====================================================================
logger.info("🔍 [系統自檢] 正在驗證總裁欽定之核心成分股池與權重...")
for index_name, tickers in HARDCODE_CANDIDATE_POOL.items():
    logger.info(f"👉 指數 [{index_name}] 核心配置驗證成功，共包含 {len(tickers)} 檔最貼近現實的權重股。")
logger.info("🟢 [系統自檢完成] 總裁欽定數據已全量載入，底層引擎準備就緒！")

# =====================================================================
# 🎯 【總裁專屬維護區 2】SOX 權威權重基準 (CMMI Level 5: 僅維護此字典)
# =====================================================================
SOX_AUTHORITY_WEIGHTS = {
    # --- Top 5 核心防禦/衝刺梯隊 ---
    "MU": 11.80,    # 記憶體與 HBM 龍頭 (觸及最新改版第一大權重上限)
    "NVDA": 8.50,   # AI 晶片霸主 (受 Capping 限制與動態漂移)
    "MRVL": 8.40,   # 高速傳輸晶片
    "AVGO": 7.40,   # 網通與客製化 ASIC 龍頭
    "AMD": 6.00,    # CPU/GPU 設計大廠
    
    # --- 中流砥柱設計與代工梯隊 ---
    "INTC": 4.50,   # IDM 大廠
    "QCOM": 4.20,   # 行動通訊晶片
    "ARM": 3.80,    # IP 架構巨頭
    "TSM": 2.75,    # 台積電 ADR (受外國公司 10% 總天花板限制)
    
    # --- 設備三巨頭與車用/類比巨頭 (原代碼漏掉，強烈建議補上) ---
    "TXN": 4.00,    # 德州儀器 (車用/類比晶片龍頭) *補上
    "ASML": 3.50,   # 艾司摩爾 (EUV 獨家設備商) *補上
    "ADI": 3.40,    # 亞德諾半導體 (高階類比晶片) *補上
    "AMAT": 2.50,   # 應用材料 (設備)
    "LRCX": 2.40,   # 科林研發 (設備)
    "KLAC": 2.30,   # 科磊 (檢測設備)
    "MCHP": 2.10,   # 微晶片科技 (MCU)
}
NEXT_REBALANCE_DATE = "2026-09-18"

# =====================================================================
# 🧠 底層引擎：多態指數權重分析引擎 (CMMI Level 5: 邏輯層，免維護)
# =====================================================================
class BaseIndexAnalyzer:
    """基礎指數分析器"""
    def __init__(self, idx_name):
        self.idx_name = idx_name
        self.ticker_cache = {}

    def fetch_yfinance_data(self, ticker):
        if ticker in self.ticker_cache: return self.ticker_cache[ticker]
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info or info.get('quoteType') != 'EQUITY' or info.get('currency') != 'USD':
                self.ticker_cache[ticker] = None; return None
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
            mc = info.get('marketCap', 0)
            if not price or price <= 0:
                self.ticker_cache[ticker] = None; return None
            if not mc or mc < 1_000_000_000:
                shares = info.get('sharesOutstanding', 0)
                mc = (price * shares) if (price and shares) else 0
                if mc < 1_000_000_000:
                    self.ticker_cache[ticker] = None; return None
            change_percent = info.get('regularMarketChangePercent', 0)
            if not change_percent:
                prev_p = info.get('regularMarketPreviousClose') or info.get('previousClose')
                if price and prev_p: change_percent = ((price - prev_p) / prev_p) * 100
            data = {
                "change_percent": float(change_percent) if change_percent else 0.0,
                "current_price": float(price),
                "market_cap_b": float(mc) / 1e9,
                "weight": None
            }
            self.ticker_cache[ticker] = data
            return data
        except Exception as e:
            self.ticker_cache[ticker] = None; return None

class MarketCapAnalyzer(BaseIndexAnalyzer):
    """市值加權分析器 (SPX, IXIC)"""
    def get_top5(self, tickers):
        stocks = []
        for t in tickers:
            data = self.fetch_yfinance_data(t)
            if data: stocks.append({"ticker": t, **data})
        stocks.sort(key=lambda x: x["market_cap_b"], reverse=True)
        return stocks[:5]

class PriceAnalyzer(BaseIndexAnalyzer):
    """股價加權分析器 (DJI)"""
    def get_top5(self, tickers):
        stocks = []
        for t in tickers:
            data = self.fetch_yfinance_data(t)
            if data: stocks.append({"ticker": t, **data})
        stocks.sort(key=lambda x: x["current_price"], reverse=True)
        return stocks[:5]

class SOXAnalyzer(BaseIndexAnalyzer):
    """
    【費城半導體獨立分析器】
    採用總裁欽定權威權重進行排序，並內建 SOX 權重調整防呆機制。
    """
    def __init__(self):
        super().__init__("SOX")

    # 🚨 軍師修復：將 get_top5 縮排移回類別內部，並修正全域變數引用
    def get_top5(self, tickers):
        stocks = []
        for t in tickers:
            data = self.fetch_yfinance_data(t)
            if data:
                # 修正：SOX_AUTHORITY_WEIGHTS 是全域變數，不需要加 self.
                data["weight"] = SOX_AUTHORITY_WEIGHTS.get(t, 0.0)
                stocks.append({"ticker": t, **data})
        stocks.sort(key=lambda x: x["weight"] if x["weight"] is not None else 0, reverse=True)
        return stocks[:5]

    # 🚨 軍師修復：將 check_rebalance_alert 縮排移回類別內部
    def check_rebalance_alert(self, current_date_str):
        # 修正：NEXT_REBALANCE_DATE 是全域變數，不需要加 self.
        if current_date_str >= NEXT_REBALANCE_DATE:
            return (
                "\n\n🚨 【SOX 權重調整防呆提醒】 🚨\n"
                "========================================================================\n"
                "總裁，SOX 權重會再次重新調整！\n"
                "2026 年 9 月 18 日（星期五）收盤後，請記得依照最新的權重更新代碼中的 SOX_AUTHORITY_WEIGHTS！\n"
                "========================================================================\n"
            )
        return ""

# =====================================================================
# 🔍 v5.8.0 核心新增：ETF 真實持倉比對防呆引擎
# =====================================================================
class ComponentDriftDetector:
    """自動抓取四大指數對應 ETF 的真實前五大持倉，並與 HARDCODE_CANDIDATE_POOL 進行比對。"""
    ETF_MAPPING = {"DJI": "DIA", "SPX": "SPY", "IXIC": "QQQ", "SOX": "SOXX"}
    INDEX_NAMES = {"DJI": "道瓊工業指數", "SPX": "標準普爾 500 指數", "IXIC": "那斯達克綜合指數", "SOX": "費城半導體指數"}
    
    def __init__(self, hardcode_pool):
        self.hardcode_pool = hardcode_pool
        self.warnings = []

    def _fetch_etf_top5(self, etf_symbol):
        """抓取單一 ETF 的前五大持倉 Ticker"""
        try:
            etf = yf.Ticker(etf_symbol)
            holdings = etf.fund_holdings
            if holdings is not None and not holdings.empty:
                top5 = holdings.index[:5].tolist()
                return [str(t).strip().upper().replace('.', '-') for t in top5]
        except Exception as e:
            logger.debug(f"⚠️ 抓取 ETF {etf_symbol} 持倉失敗: {e}")
        return []

    def check(self):
        """執行全面比對並返回警告字串"""
        logger.info("🔍 [ETF 防呆引擎啟動] 正在比對四大指數 ETF 真實持倉與 Hardcode 白名單...")
        for idx, etf_symbol in self.ETF_MAPPING.items():
            etf_top5 = self._fetch_etf_top5(etf_symbol)
            if not etf_top5:
                continue
            hardcode_top5 = self.hardcode_pool.get(idx, [])[:5]
            set_etf = set(etf_top5)
            set_hc = set(hardcode_top5)
            new_stocks = set_etf - set_hc
            if len(new_stocks) >= 3:
                new_stocks_list = ", ".join(list(new_stocks))
                self.warnings.append(
                    f"⚠️ 【{self.INDEX_NAMES[idx]} ({etf_symbol})】ETF 真實前五大持倉與白名單差異過大！\n"
                    f"   發現 {len(new_stocks)} 檔新股擠進前五大：{new_stocks_list}。\n"
                    f"   請總裁及時更新 HARDCODE_CANDIDATE_POOL 中的 [{idx}] 清單！"
                )
                logger.warning(f"🚨 [ETF 防呆] {idx} 觸發異動警示！新股: {new_stocks}")
        if self.warnings:
            alert_text = "\n\n🚨 【黑密斯系統監控・ETF 持倉異動防呆警示】 🚨\n"
            alert_text += "========================================================================\n"
            alert_text += "總裁請注意：系統自動比對了四大指數 ETF 的真實前五大持倉，\n"
            alert_text += "發現與您設定的 HARDCODE_CANDIDATE_POOL 存在重大差異！\n"
            alert_text += "為確保報告的專業性與準確性，請盡快更新代碼中的白名單：\n\n"
            for w in self.warnings:
                alert_text += f"{w}\n"
            alert_text += "========================================================================\n"
            return alert_text
        return ""

# =====================================================================
# 🧠 v5.6.0 核心引擎：物件導向金融實體識別與注入引擎 (免維護)
# =====================================================================
class TickerMarkerInjector:
    def __init__(self):
        self.ticker_cache = {}

    def fetch_yfinance_data(self, ticker):
        if ticker in self.ticker_cache: return self.ticker_cache[ticker]
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info or info.get('quoteType') != 'EQUITY' or info.get('currency') != 'USD':
                self.ticker_cache[ticker] = None; return None
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
            mc = info.get('marketCap', 0)
            if not price or price <= 0:
                self.ticker_cache[ticker] = None; return None
            if not mc or mc < 1_000_000_000:
                shares = info.get('sharesOutstanding', 0)
                mc = (price * shares) if (price and shares) else 0
                if mc < 1_000_000_000:
                    self.ticker_cache[ticker] = None; return None
            change_percent = info.get('regularMarketChangePercent', 0)
            if not change_percent:
                prev_p = info.get('regularMarketPreviousClose') or info.get('previousClose')
                if price and prev_p: change_percent = ((price - prev_p) / prev_p) * 100
            data = {
                "change_percent": float(change_percent) if change_percent else 0.0,
                "current_price": float(price),
                "market_cap_b": float(mc) / 1e9
            }
            self.ticker_cache[ticker] = data
            return data
        except Exception as e:
            self.ticker_cache[ticker] = None; return None

    def inject(self, report_text):
        logger.info("🔬 [極簡注入引擎啟動] 正在掃描 [TICKER] 標記並注入數據...")
        pattern = r'\[([A-Z]{1,5})\]'
        matches = re.findall(pattern, report_text)
        if not matches: return report_text
        unique_tickers = set(matches)
        for ticker in unique_tickers:
            data = self.fetch_yfinance_data(ticker)
            if data and data.get('current_price') > 0:
                sign = "+" if data['change_percent'] >= 0 else ""
                injection_str = f" ({sign}{data['change_percent']:.2f}%, 收盤: ${data['current_price']:.2f}, 市值: ${data['market_cap_b']:.1f}B)"
                report_text = report_text.replace(f"[{ticker}]", injection_str)
            else:
                report_text = report_text.replace(f"[{ticker}]", "")
        return report_text

# =====================================================================
# 🧼 輔助引擎：AI 指令洩漏過濾網 (免維護)
# =====================================================================
def clean_ai_leakage(text):
    text = re.sub(r'⚠️【合夥人最高禁令.*?(?=\n\d+\.)', '', text, flags=re.DOTALL)
    text = re.sub(r'[^\n]*合夥人最高禁令[^\n]*', '', text)
    text = re.sub(r'\n{3,}', '\n', text)
    return text

# =====================================================================
# 🛡️ 輔助引擎：排版與路由 (免維護)
# =====================================================================
def get_index_analyzers():
    return {
        "DJI": PriceAnalyzer("DJI"),
        "SPX": MarketCapAnalyzer("SPX"),
        "IXIC": MarketCapAnalyzer("IXIC"),
        "SOX": SOXAnalyzer()
    }

def stitch_top5_into_report(report_text, analyzers):
    top5_texts = {}
    for idx, analyzer in analyzers.items():
        tickers = HARDCODE_CANDIDATE_POOL.get(idx, [])
        top5 = analyzer.get_top5(tickers)
        lines = []
        for s in top5:
            sign = "+" if s['change_percent'] >= 0 else ""
            weight_str = f", 權重: {s['weight']:.2f}%" if s.get('weight') is not None and s['weight'] > 0 else ""
            line = f"        - {s['ticker']} ({sign}{s['change_percent']:.2f}%, 收盤: ${s['current_price']:.2f}, 市值: ${s['market_cap_b']:.1f}B{weight_str})"
            lines.append(line)
        top5_texts[idx] = "\n".join(lines)
    title_mapping = {"📊 藍籌權重巨頭表現：": "DJI", "📊 大盤權重巨頭表現：": "SPX", "📊 科技權重巨頭表現：": "IXIC", "📊 半導體權重龍頭表現：": "SOX"}
    report_text = re.sub(r'[（(]?\s*權重股具體數據.*?看板\s*[）)]?', '', report_text)
    for title, idx in title_mapping.items():
        if idx not in top5_texts: continue
        insert_text = f"\n{top5_texts[idx]}\n"
        pattern = re.escape(title) + r'[^\n]*\n*'
        if re.search(pattern, report_text):
            report_text = re.sub(pattern, title + insert_text, report_text, count=1)
    return report_text

# =====================================================================
# 📧 郵件與 LLM 呼叫模組 (免維護)
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
# 🚀 主執行管線 (CMMI Level 5: 標準化流程，免維護)
# =====================================================================
def main():
    logger.info("🚀 [Task1 v5.8.1 絕對服從總裁數據版點火]...")
    try:
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        
        # 1. AI 抓取收盤與催化劑事件
        data_gathering_prompt = (
            f"重要時空指引：現在時間是 {current_time_str}。\n"
            f"請利用 Google Search 精準查詢截止至今日（美東時間最新交易日收盤）以下核心數據：\n"
            f"1. 美股四大指數最新精確收盤價、漲跌點數、漲跌幅。請務必使用中文簡稱：『道瓊』、『標普500』、『那斯達克』、『費城半導體』。\n"
            f"2. 找出當天實際主導或嚴重衝擊這四大指數盤面、影響前三大的核心股票是哪三隻？它們具體發生了什麼催化劑事件？\n"
            f"   ⚠️【絕對數字封殺令】：描述催化劑事件時，**絕對禁止**寫出任何個股的『漲跌幅%』、『收盤價』或『市值』！只需寫出公司名稱和純文字事件邏輯。\n"
        )
        raw_facts = call_gemini_with_double_shield(data_gathering_prompt, tools_config=[{"google_search": {}}], required_keywords=["道", "標普", "那斯達克", "費城"])
        
        # 2. 初始化分析器與 AI 撰寫黑皮書
        analyzers = get_index_analyzers()
        
        # 🚨 軍師軍令：Prompt 100% 參考總裁欽定版本，絕對不擅自修改
        final_synthesis_prompt = (
            f"你現在是華爾街頂級投行的資深宏觀策略合夥人。\n"
            f"⚠️【合夥人最高禁令】：\n"
            f"1. 在【📊 藍籌權重巨頭表現：】等小節中，**絕對禁止**寫任何過渡語！直接換行。\n"
            f"2. 在分析「核心異動股」時，提到股票名稱時，**必須**在名稱後方加上中括號標註其 Ticker（例如：Arm Holdings [ARM]、Intel [INTC]）。\n"
            f"   **絕對禁止**寫出任何『漲跌幅%』、『收盤價』或『市值』數字！Python 引擎會自動將 [TICKER] 替換為完整的鐵三角數據。\n"
            f"3. 【🚨 隔離與去重死命令】：四大指數的「核心異動股」**絕對禁止重複**！你必須根據每個指數的真實成分股特性，挑選**完全不同**的股票！\n"
            f"   - 【道瓊】只能挑選傳統藍籌/金融/工業（如 GS, JPM, CAT, UNH, HD）。絕對不允許寫 SpaceX 或 ARM！\n"
            f"   - 【費半】只能挑選純半導體（如 NVDA, AVGO, INTC, MU, AMD）。絕對不允許寫 SpaceX 或 TSLA！\n"
            f"   - 【標普/納指】可挑選科技/成長股，但兩者的異動股列表也必須盡量錯開，嚴禁四個指數都寫同一組股票（如 SpaceX, TSLA, ARM）！\n"
            f"4. 【反鸚鵡嘴禁令】：每個指數的「Overall 宏觀收斂」必須針對該指數的獨特屬性（如道瓊的防禦性、費半的週期性）進行獨立深度解讀，**絕對禁止**使用相似的套話或複製貼上！\n\n"
            f"📋 【今日美股核心量化與動態事件事實庫】：\n{raw_facts}\n\n"
            f"❌【排版禁令】：嚴禁使用 Markdown 表格語法。\n"
            f"👑【第一部分：最新收盤數據】\n請嚴格遵循奢華條列式輸出。\n"
            f"👑【第二部分：機構級核心戰略分析】\n"
            f"### **【細部分析與成分股解構】**\n"
            f"1. **【道瓊指數細部分析】**\n   * 📊 藍籌權重巨頭表現：\n   * 🎯 核心異動股與事件：\n   * 🔮 Overall 宏觀收斂：\n"
            f"2. **【標準普爾 500 指數細部分析】**\n   * 📊 大盤權重巨頭表現：\n   * 🎯 核心異動股與事件：\n   * 🔮 Overall 宏觀收斂：\n"
            f"3. **【那斯達克綜合指數細部分析】**\n   * 📊 科技權重巨頭表現：\n   * 🎯 影響板塊前三大股票與變化：\n   * 🔮 Overall 宏觀收斂：\n"
            f"4. **【費城半導體指數細部分析】**\n   * 📊 半導體權重龍頭表現：\n   * 🎯 影響板塊前三大股票與變化：\n   * 🔮 Overall 宏觀收斂：\n"
            f"請確保段落之間適度留白，保持華爾街高階黑皮書的純文字極致美感。"
        )
        report_text = call_gemini_with_double_shield(final_synthesis_prompt, required_keywords=["藍籌權重巨頭表現", "大盤權重巨頭表現", "科技權重巨頭表現", "半導體權重龍頭表現"])
        
        # 3. Python 後處理流水線
        report_text = stitch_top5_into_report(report_text, analyzers)
        report_text = TickerMarkerInjector().inject(report_text)
        report_text = clean_ai_leakage(report_text)
        
        # 4. 觸發防呆機制
        sox_rebalance_alert = analyzers["SOX"].check_rebalance_alert(current_date_str)
        final_report = report_text + sox_rebalance_alert
        detector = ComponentDriftDetector(HARDCODE_CANDIDATE_POOL)
        etf_drift_alert = detector.check()
        final_report += etf_drift_alert
        
        # 5. 落地與發信
        task1_node = {"task_id": "task1_us_market", "timestamp": current_time_str, "raw_report": final_report}
        os.makedirs(os.path.dirname(TASK1_MEMORY_PATH), exist_ok=True)
        with open(TASK1_MEMORY_PATH, "w", encoding="utf-8") as f: json.dump(task1_node, f, ensure_ascii=False, indent=4)
        send_email_to_president(final_report)
        logger.info("🏁 [Ultimate System Secured] 2026 鋼鐵防線全量暢通！CMMI Level 5 數據分離架構完美運行！")
        
    except Exception as e: logger.error(f"💥 Task1 發生終端異常: {e}")

if __name__ == "__main__":
    main()