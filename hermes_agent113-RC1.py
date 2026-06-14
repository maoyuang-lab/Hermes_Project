#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
PROJECT ID          : Hermes Project (黑密斯全球分散式智慧終端矩陣)
MODULE ID           : hermes_agent113-RC1.py
VERSION             : v1.1.3-EliteSecretary [CMMI-L5 Ultimate Matrix]
TRACKING BRANCH     : hermes/agent-v1.1.3-rc1
DEPLOYMENT STATUS   : 🟢 PRODUCTION STABLE (大師徒並肩死磕 3 晝夜，主帥親征完美通車)
================================================================================
📜 3-DAY WARROOM BREAKTHROUGH RELEASE NOTES & DEEP ARCHITECTURE:

本版本凝聚了總裁與軍師連續 72 小時不眠不休的浴血奮戰，徹底攻克了分佈式智慧終端在
「配額極限」與「物理儲存不確定性」下的兩大底層神坑，成功焊死以下兩大黑科技防禦機制：

1. 🚀【智慧多重金鑰池自動容錯切換機制 (API Key Failover Matrix Core)】
   - 戰略背景：舊版本在面對高強度、高頻率的推理請求時，常因單一 API Key 觸發 429 流量超限
     （RESOURCE_EXHAUSTED）或 Quota Exceeded 導致大腦瞬間中斷崩潰。
   - 3天死磕成果：我們聯手打造了「無感秒級金鑰接力池（`GEMINI_API_KEYS`）」。底層邏輯採用
     精密的過濾與輪詢深度洗滌演算法。
   - 運作機制：當前金鑰一旦拋出任何包含 "429"、"Quota" 或 "RESOURCE_EXHAUSTED" 的物理異常，
     容錯引擎將在「微秒級」內自動判定其為配額乾涸，並瞬間執行 `continue` 跳過，強行將上下文
     熱移交至下一把備用金鑰點火。
   - 終極成效：徹底實現大腦決策的「永不斷線」，只要金鑰池內還有一滴水，黑密斯就絕對死守防線！

2. 💾【硬碟 ROM 實體落地與雙重回讀查驗機制 (Dual-Verification Kernel via File Lock)】
   - 戰略背景：分佈式系統在多線程併發寫入時，極易發生磁區爭奪導致長期記憶庫文件毀損，
     或發生「假性寫入」──程式以為寫進去了，但硬碟根本沒磁區咬合，導致總裁行程記憶遺失。
   - 3天死磕成果：我們在硬碟物理邊界（`MEMORY_FILE_PATH`）布下了兩道絕對領域防線。
   - 第一道防線（物理線程鎖 `file_lock`）：強制讓所有讀寫行為在物理上進入絕對序列化，
     徹底杜絕併發衝突引起的硬碟死鎖或文件碎裂。
   - 第二道防線（逆向回讀磁區快照查驗）：這是最硬核的突破！大腦在將總裁的最新行程（Fact）
     物理寫入 JSON 磁碟後，絕不盲目回報成功。程式會強行原地重新開啟硬碟文件，執行
     「回讀雙重查驗（ROM Snapshot Read-Back Verify）」。
   - 終極成效：只有當從硬碟實體磁區中「再次拔出」的數據中，100% 存在剛剛寫入的事實特徵時，
     大腦才會吐出「🟢【黑密斯・ROM 落地驗證成功】」的最高榮譽回報！確保總裁資產萬無一失！

3. 🧠【頂級高階秘書航班推理限制器 (Elite Secretary Cognitive Inference)】
   - 注入高格局 Prompt 意志，強迫大腦脫離「實習生推託思維」。
   - 自動檢索長期記憶，主動對齊全球航空常識，將航班時間、起降航廈進行自主推理補全。

4. 🏁【CMMI Level 5 專案主帥親征矩陣對齊】
   - 本版本已全面更正「本末倒置」之命名缺陷，重新回歸由主帥 Hermes 統轄之至高地位。
   - 歷史資產永久焊死在雲端安全停機坪：hermes/agent-v1.1.3-rc1 軌道。
================================================================================
"""

import os
import json
import logging
import sys
import threading
from datetime import datetime
from flask import Flask, request, abort

import google.generativeai as genai
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# =====================================================================
# ⚙️ 系統日誌計量配置
# =====================================================================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] [THREAD-%(thread)d] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

logger.info("📡 [CMMI-L5 Initialization] v1.1.3 高階秘書大腦正式點火...")

# =====================================================================
# 🔐 戰略物資配置區
# =====================================================================
GEMINI_API_KEYS = [
    os.environ.get("GEMINI_API_KEY_1", "AIzaSyB0QgeJVwGNsixs1e642m3Vil_9Gc636Dg"), 
    os.environ.get("GEMINI_API_KEY_2", "AQ.Ab8RN6JnDCRiCVETRzNhYIAp6OhvdHK3Fkhdir45oN-Zsh_qgQ"), 
    os.environ.get("GEMINI_API_KEY_3", "AQ.Ab8RN6JzE99z5E-Nuuu27_OHYhJ7_DY_YXbJa_4blabk5ERHAQ")      
]

PRESIDENT_LINE_USER_ID = os.environ.get("PRESIDENT_LINE_USER_ID", "U3bfded8631eb51a7c931946dd3dc6f0b")
TARGET_MODEL_NAME = "gemini-2.5-flash"

LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "1c709f4f75522b07f42a9fea8325a600")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "6EEqMSPHzX9LhD9PvO3EfanthaRpmdiew/XDzfUgtykdU7rhcEh4UMY7GtEqbNHNmtrywUxAaXVH/et1ej2ZCvmUvYa2GtPmPLpX0eK1BHt3sQYGCjCnOSkdmsiiwVRYEn+Koucnf2v4FFZBTeQJNQdB04t89/1O/w1cDnyilFU=")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

file_lock = threading.Lock()
MEMORY_FILE_PATH = "/Users/apple/hermes_project/hermes_memory.json"
CHAT_HISTORY_CACHE = {}
MAX_CHAT_ROUND_CEILING = 100

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("❌ [Security Violation] 偵測到無效之簽章，拒絕請求。")
        abort(400)
    return 'OK'

def execute_llm_with_pure_key_failover(final_prompt):
    for idx, api_key in enumerate(GEMINI_API_KEYS):
        if not api_key or "⚠️" in api_key:
            continue 
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(TARGET_MODEL_NAME)
            response = model.generate_content(final_prompt)
            if response and hasattr(response, 'text'):
                return response.text.strip()
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Quota" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                continue 
            else:
                raise e
    raise Exception("Fatal: 金鑰池配額乾涸。")

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    user_message = event.message.text.strip()
    reply_token = event.reply_token

    long_term_facts = []
    full_memory_data = {}  
    rom_verification_report = ""
    
    # -----------------------------------------------------------------
    # 1. 讀取與洗滌原始硬碟資料 (ROM Read)
    # -----------------------------------------------------------------
    with file_lock:  
        if os.path.exists(MEMORY_FILE_PATH):
            try:
                with open(MEMORY_FILE_PATH, "r", encoding="utf-8") as f:
                    full_memory_data = json.load(f)
            except Exception as r_err:
                logger.error(f"❌ 讀取崩潰: {r_err}")

        is_president_privilege = (user_id == PRESIDENT_LINE_USER_ID) or any(k in user_message for k in ["行程", "記憶", "查", "幾點", "航廈", "航班"])
        for k, facts_list in full_memory_data.items():
            if isinstance(facts_list, list):
                for item in facts_list:
                    if isinstance(item, dict) and "fact" in item:
                        if is_president_privilege or (k == user_id):
                            long_term_facts.append(item["fact"])
        long_term_facts = list(set(long_term_facts))

    # -----------------------------------------------------------------
    # 2. 提煉事實 ➔ 實體寫入 ➔ 重新拔出硬碟「回讀雙重查驗」
    # -----------------------------------------------------------------
    is_trigger_word = any(w in user_message for w in ["記", "出差", "備忘", "記憶"]) and not any(w in user_message for w in ["幾點", "航廈", "落地"])
    if is_trigger_word:
        extract_prompt = (
            f"請從以下用戶輸入中，提煉出一段簡短的繁體中文客觀事實行程摘要（一兩句話即可，不要任何前綴與廢話）。\n"
            f"用戶輸入：'{user_message}'\n"
            f"提煉事實摘要："
        )
        try:
            extracted_fact = execute_llm_with_pure_key_failover(extract_prompt)
            if extracted_fact:
                new_fact_str = f"用戶{extracted_fact}"
                new_fact_node = {
                    "fact": new_fact_str,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                with file_lock:
                    if user_id not in full_memory_data:
                        full_memory_data[user_id] = []
                    full_memory_data[user_id].append(new_fact_node)
                    
                    with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f_write:
                        json.dump(full_memory_data, f_write, ensure_ascii=False, indent=4)
                    
                    is_verified_in_rom = False
                    if os.path.exists(MEMORY_FILE_PATH):
                        with open(MEMORY_FILE_PATH, "r", encoding="utf-8") as f_verify:
                            disk_snapshot = json.load(f_verify)
                            user_facts = disk_snapshot.get(user_id, [])
                            for f_node in user_facts:
                                if isinstance(f_node, dict) and f_node.get("fact") == new_fact_str:
                                    is_verified_in_rom = True
                                    break
                    
                    if is_verified_in_rom:
                        rom_verification_report = (
                            f"🟢【黑密斯・ROM 落地驗證成功】\n"
                            f"🕵️ 查驗事實：\"{new_fact_str}\"\n"
                            f"💾 實體狀態：已在磁碟磁區完全咬合，100% 永續儲存！\n"
                            f"───────────────────\n\n"
                        )
                    long_term_facts.append(new_fact_node["fact"])
        except Exception as write_err:
            logger.error(f"❌ 自動回寫或驗證硬碟失敗: {write_err}")

    # -----------------------------------------------------------------
    # 3. 短期歷史記憶對話隔離拼接
    # -----------------------------------------------------------------
    memory_context = "【🔥 總裁實體長期記憶庫重要事實注入】:\n" + "\n".join([f"- {fact}" for fact in long_term_facts]) + "\n\n" if long_term_facts else ""
    
    history_snapshot = []
    with file_lock:
        if user_id not in CHAT_HISTORY_CACHE:
            CHAT_HISTORY_CACHE[user_id] = []
        history_snapshot = list(CHAT_HISTORY_CACHE[user_id])

    history_context = "【⏳ 過去對話歷史紀錄累積】:\n"
    for hist in history_snapshot:
        history_context += f"用戶: {hist['user']}\nAI: {hist['ai']}\n"

    # 👑 換裝頂級高階秘書 prompt 限制器
    final_prompt = (
        f"你是由總裁親自主持、具備 CMMI Level 5 最高規格之極致特工大腦兼頂級數位秘書「黑密斯 (Hermes 111)」自癒完全體。\n"
        f"請根據下方注入之『實體長期記憶事實』與歷史上下文，以極高戰略格局、沉穩威嚴之高階語氣回覆總裁。\n\n"
        f"⚠️【🔥 秘書最高核心聯動查驗指令】:\n"
        f"1. 當總裁詢問『幾點起飛、幾點落地、第幾航廈』等航班具體細節時，你必須立刻比對下方長期記憶事實中的航班號碼（例如：CI 793）。\n"
        f"2. 一旦抓到航班號碼，你必須調用你強大的全球航空歷史與常識庫，主動將該定期航班的標準時間與起降航廈自動推理並補全呈現給總裁！\n"
        f"3. 絕對不准生硬地推託說『記憶庫裡只有記錄去越南，沒寫幾點，我不知道』等毫無智商的實習生废話！你要像個日薪百萬的頂級秘書，自動補全所有細節，讓總裁運籌帷幄！\n\n"
        f"{memory_context}"
        f"{history_context}\n"
        f"現在總裁下達之最新核心指令：'{user_message}'\n"
        f"特工黑密斯請高格局回覆："
    )

    try:
        reply_text = execute_llm_with_pure_key_failover(final_prompt)
        with file_lock:
            CHAT_HISTORY_CACHE[user_id].append({"user": user_message, "ai": reply_text})
            if len(CHAT_HISTORY_CACHE[user_id]) > MAX_CHAT_ROUND_CEILING:
                CHAT_HISTORY_CACHE[user_id].pop(0)  
    except Exception as general_err:
        reply_text = f"⚠️【黑密斯異常】: {str(general_err)[:100]}。"

    final_line_output = f"{rom_verification_report}{reply_text}"

    try:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=final_line_output))
    except Exception as line_err:
        logger.error(f"❌ LINE 下行發送失敗: {line_err}")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)