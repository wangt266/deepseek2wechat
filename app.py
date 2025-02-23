from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import time
from openai import OpenAI
import os
import requests

app = Flask(__name__)

APP_ID = "wx8e06c94e001b2479"  # 替换
APP_SECRET = "vercel2deepseek"  # 替换
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    response = requests.get(url).json()
    return response.get("access_token")

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
        ai_reply = f"错误: {str(e)}"

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
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
