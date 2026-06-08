import os
import logging
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
from mem0 import Memory

# 設定日誌紀錄，方便在老 Mac 的終端機看清楚記憶狀況
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# =========================================================
# 🔑 總裁專屬金鑰保險箱（100% 乾淨、不綁死特定路徑）
# =========================================================
GEMINI_API_KEY = "AIzaSyB0QgeJVwGNsixs1e642m3Vil_9Gc636Dg"
LINE_CHANNEL_ACCESS_TOKEN = "6EEqMSPHzX9LhD9PvO3EfanthaRpmdiew/XDzfUgtykdU7rhcEh4UMY7GtEqbNHNmtrywUxAaXVH/et1ej2ZCvmUvYa2GtPmPLpX0eK1BHt3sQYGCjCnOSkdmsiiwVRYEn+Koucnf2v4FFZBTeQJNQdB04t89/1O/w1cDnyilFnU="
LINE_CHANNEL_SECRET = "7b66df76e27be8e709e9eef270bd11e7"

# 初始化 LINE
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 🧠 修正後的完全體 mem0 設定：全面對齊 Google 原生，絕不與 OpenAI 衝突
mem0_config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        }
    },
    "llm": {
        "provider": "google_genai",    # 👈 徹底根除衝突：改用原生 Google 驅動
        "config": {
            "model": "gemini-1.5-flash",
            "api_key": GEMINI_API_KEY
        }
    },
    "embedder": {
        "provider": "google_genai",   # 👈 徹底根除衝突：嵌入模型也同步改為原生 Google
        "config": {
            "model": "text-embedding-004",
            "api_key": GEMINI_API_KEY
        }
    }
}

try:
    logger.info("🧠 正在啟動 mem0 長期記憶通道...")
    memory = Memory.from_config(mem0_config)
    logger.info("✅ 記憶通道與 Docker Qdrant 連線成功！")
except Exception as e:
    logger.error(f"❌ 記憶通道初始化失敗: {e}")
    memory = None

# =========================================================
# 🌐 Webhook 接收端點
# =========================================================
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# =========================================================
# 🤖 核心處理：治好失憶症的 Hermes 邏輯
# =========================================================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    user_id = event.source.user_id 
    
    reply_text = "報告總裁，Hermes 正在調閱記憶中..."

    try:
        # 1. 撈取長期記憶（Facts）
        memory_context = ""
        if memory:
            try:
                previous_memories = memory.get_all(user_id=user_id)
                if previous_memories and isinstance(previous_memories, list):
                    memory_context = "【關於總裁的歷史記憶】:\n" + "\n".join([m['text'] for m in previous_memories if 'text' in m])
                elif previous_memories and hasattr(previous_memories, 'memories'):
                    memory_context = "【關於總裁的歷史記憶】:\n" + "\n".join([m.text for m in previous_memories.memories])
            except Exception as mem_err:
                logger.warning(f"⚠️ 調閱記憶受阻: {mem_err}")
        
        # 2. 呼叫大腦思考
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = (
            f"你是一位貼心、聰明的私人秘書，名叫 Hermes（黑密斯）。\n"
            f"請用繁體中文、帶點尊稱（稱呼對方為總裁、老闆或您）來回答。\n\n"
            f"{memory_context}\n\n"
            f"請根據上述記憶背景，回答總裁現在對你說的話：{user_message}"
        )
        
        response = model.generate_content(prompt)
        reply_text = response.text.strip()
        
        # 3. 雙向寫入記憶：對話成功後，立刻把新Facts打入 Docker Qdrant
        if memory:
            try:
                memory.add(user_message, user_id=user_id)
                logger.info("✅ 【實體真相】成功將總裁新指令寫入 mem0 記憶庫！")
            except Exception as mem_add_err:
                logger.error(f"❌ 寫入新記憶失敗: {mem_add_err}")
                
    except Exception as e:
        logger.error(f"❌ 核心運行出錯: {e}")
        reply_text = f"報告總裁，大腦運作有些不順，錯誤回報：{str(e)}"

    # 4. 回傳 LINE
    try:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    except Exception as line_err:
        logger.error(f"❌ 發送 LINE 訊息失敗: {line_err}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)