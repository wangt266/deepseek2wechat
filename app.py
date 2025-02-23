from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import time
from openai import OpenAI
import os

app = Flask(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # 从环境变量读取
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        echostr = request.args.get('echostr')
        if echostr:
            return echostr
        return "Hello, this is a test!"

    xml_data = request.data.decode('utf-8')
    root = ET.fromstring(xml_data)
    from_user = root.find('FromUserName').text
    to_user = root.find('ToUserName').text
    content = root.find('Content').text

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": content}
            ],
            stream=False
        )
        ai_reply = response.choices[0].message.content
    except Exception as e:
        ai_reply = "抱歉，我遇到点问题，请稍后再试！"

    reply_xml = f"""
    <xml>
        <ToUserName>{from_user}</ToUserName>
        <FromUserName>{to_user}</FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType>text</MsgType>
        <Content>{ai_reply}</Content>
    </xml>
    """
    return Response(reply_xml, mimetype='application/xml')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Vercel 用 PORT，默认 5000
    app.run(host="0.0.0.0", port=port, debug=True)
