#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專案名稱: Hermes Project
腳本名稱: hermes_agent07.py
版本編號: v0.7.0
維護人員: 茆裕源 (總裁) & AI 軍師
變更日期: 2026-06-08

【版本變更日誌 (Changelog)】
- v0.6.0: 基礎多模態架構，整合 Flask、LINE Webhook、OpenAI、Gemini 備援大腦與 Mem0 長期記憶。
- v0.7.0 (Current): 
    1. 修復 Mem0 記憶體通道初始化失敗問題：
       因 mem0 官方標準關鍵字定義，將大腦(LLM)與嵌入向量(Embedding)的 provider 
       由自訂的 "google_genai" 修正為官方標準規範的 "google"。
    2. 優化經典版環境相容性：針對老 Mac 底層 Python 3.9 (LibreSSL 環境) 的未來擴充保留接口。
    3. 全面落實軟體工程規範，提升主版本號至 07 以供 Git 追蹤管理。
"""

import os
import logging
from flask import Flask, request, abort
from dotenv import load_dotenv

# 載入通訊與大模型核心套件
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
from mem0 import Memory

# ==========================================
# 1. 系統日誌與環境配置
# ==========================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 載入環境變數 (.env)
load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 驗證必要環境變數是否存在
if not all([LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, GEMINI_API_KEY]):
    logger.error("❌ 核心環境變數缺失，請檢查 .env 檔案配置。")

# 初始化 LINE Bot API 接口
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化 Google Gemini 備援大腦
genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# 2. 核心長期記憶體 (Mem0) 初始化組態變更
# ==========================================
logger.info("🧠 正在啟動 mem0 長期記憶通道...")

# 【軟體工程重要備註】
# 修正重點：mem0 內部 Pydantic 驗證不接受 "google_genai" 作為 provider 名稱。
# 依據 mem0 v2.0.0+ 官方規範，Gemini 系列大腦與 Embedding 的合法標籤必須精確填寫為 "google"。
mem0_config = {
    "llm": {
        "provider": "google",  # 已修正：由 google_genai 改為官方標準標籤 google
        "config": {
            "model": "gemini-1.5-flash",
            "temperature": 0.2,
            "max_tokens": 1500,
            "api_key": GEMINI_API_KEY
        }
    },
    "embedder": {
        "provider": "google",  # 已修正：由 google_genai 改為官方標準標籤 google
        "config": {
            "model": "text-embedding-004",
            "api_key": GEMINI_API_KEY
        }
    }
}

try:
    # 建立具備長期記憶能力的 AI 記憶體精靈
    memory = Memory.from_config(mem0_config)
    logger.info("✅ 記憶通道初始化成功！長期記憶體已完全對接。")
except Exception as e:
    logger.error(f"❌ 記憶通道初始化失敗: {e}")
    memory = None

# ==========================================
# 3. 建立通訊通訊埠 (Flask Webhook)
# ==========================================
app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    """
    接收 LINE 伺服器傳送過來的 Webhook 事件
    """
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    logger.info(f"📥 收到 Webhook 訊號本體: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("⚠️ 簽章驗證失敗 (Invalid Signature)，請檢查 Channel Secret 配置。")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    處理使用者的文字訊息，並透過 AI 大腦與長期記憶做出回應
    """
    user_id = event.source.user_id
    user_message = event.message.text
    logger.info(f"👤 使用者 [{user_id}] 說: {user_message}")

    # 1. 檢索長期記憶 (如果記憶模組啟動成功)
    relevant_memories = ""
    if memory:
        try:
            previous_context = memory.search(query=user_message, user_id=user_id)
            if previous_context:
                relevant_memories = "\n".join([m['text'] for m in previous_context])
                logger.info(f"🔍 喚醒歷史記憶碎片: {relevant_memories}")
        except Exception as e:
            logger.error(f"讀取記憶失敗: {e}")

    # 2. 建立具備歷史上下文的提示詞 (Prompt)
    system_instruction = "你是領航智能特助 Hermes。請根據過往記憶(若有)與當前對話，給予總裁最精準、高格局的商務與技術建議。\n"
    if relevant_memories:
        system_instruction += f"【已知總裁歷史背景與偏好記憶】:\n{relevant_memories}\n"

    try:
        # 3. 呼叫 Gemini 核心進行決策思考
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
        response = model.generate_content(user_message)
        reply_text = response.text
        
        # 4. 同步將本次談話中有價值的細節沉澱進長期記憶中
        if memory:
            try:
                memory.add(user_message, user_id=user_id)
                logger.info("💾 新的談話細節已安全沉澱至長期記憶資料庫。")
            except Exception as e:
                logger.error(f"沉澱記憶失敗: {e}")

    except Exception as e:
        logger.error(f"🤖 AI 大腦思考時發生阻礙: {e}")
        reply_text = "報告總裁，Hermes 核心神經元傳輸遭遇微幅波動，我正在自我優化中，請稍後嘗試。"

    # 將思考成果回傳給 LINE 使用者
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    # 宣告在通訊埠 5000 建立全面網路監聽 (支援 0.0.0.0 跨裝置通訊)
    logger.info("🚀 Hermes Agent v0.7.0 正在啟動生產力監聽門戶...")
    app.run(host='0.0.0.0', port=5000, debug=True)