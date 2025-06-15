from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ここにLINE Developersから取得したトークンとシークレットを入れる
LINE_CHANNEL_ACCESS_TOKEN = 'QtG9TCjTpAboZBjusWynCf12Z6w39BaP0a5QLDF61kAY8ZjB5fWXNAGTest9jw0QIOyMDMy6bCpkcV6gTnvSZFRg2qA4ls06aagzpseqG92DlbVXKyz4FMZs4IaiYp62kkibxczJRtBDPpbPTo9HgwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '502df43ea292825f76fda66774deaf3a'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初期状態の部屋管理（1〜9番の部屋）
rooms = {str(i): "　" for i in range(1, 10)}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()

    # 状況一覧の文字列を生成する関数
    def get_status_text():
        return "\n".join([f"{i}：{rooms[str(i)]}" for i in range(1, 10)])

    # 1. 状況確認
    if user_text == "状況":
        status = get_status_text()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=status))
        return

    # 2. 入室（例：3田中）
    if len(user_text) >= 2 and user_text[0].isdigit():
        room_number = user_text[0]
        if room_number in rooms:
            name = user_text[1:]
            if rooms[room_number] == "　":
                rooms[room_number] = name
                status = get_status_text()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=status))
            else:
                current_user = rooms[room_number]
                message = f"{room_number}番の部屋は「{current_user}」が使用しています"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
            return

    # 3. 退室（例：田中退室）
    if user_text.endswith("退室"):
        name = user_text[:-2]
        for k, v in rooms.items():
            if v == name:
                rooms[k] = "　"
                status = get_status_text()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=status))
                return
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{name}はどの部屋にもいません"))
        return

    # 4. 施錠（リセット）
    if user_text == "施錠":
        for k in rooms:
            rooms[k] = "　"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="お疲れさまでした"))
        return

    # 不明な入力
    line_bot_api.reply_message(event.reply_token, TextSendMessage(
        text="正しく入力して下さい"))

if __name__ == "__main__":
    app.run(port=5000)