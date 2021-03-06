# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import errno
import os
import sys
import tempfile
from argparse import ArgumentParser

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageMessage, FollowEvent, JoinEvent,
    ImageSendMessage
)

import sorting_deep_hat
import time
import requests
import mimetypes

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)


if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
sdh = sorting_deep_hat.sorting_deep_hat('models/sorting_deep_hat.h5')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    is_input_message_ok = False
    url = ""
    img_path = ""
    fail_msg = ""

    #Check the input message
    if not isinstance(event.message, TextMessage):
        pass
    else:
        url = event.message.text


        #Check the input message
        if len(url) > 8:
            if url[:8] == "https://" or url[:7] == "http://":
                try:
                    res = requests.get(url)
                    res.raise_for_status()
                    content_type = res.headers['content-type']
                    if 'image' in content_type:
                        ext = mimetypes.guess_extension(content_type)
                        if ext == ".bmp" or ext == ".jpe" or ext == ".jpeg" or ext ==".jpg" or ext == ".png" or ext == ".tiff" or ext == ".tif":
                            #Create the temp file to save the input file.
                            with tempfile.NamedTemporaryFile(dir=static_tmp_path, delete=False) as tf:
                                tf.write(res.content)

                            img_name = os.path.basename(tf.name) + ext
                            img_path = os.path.join('static', 'tmp', img_name)
                            os.rename(tf.name, img_path)
                            is_input_message_ok = True

                except Exception as ex:
                    fail_msg = "URLから画像を取得できません。\n画像を送信してください。"
                    #pass

    #Execute sorting
    if is_input_message_ok == True:
        execute(event, img_path)
    
    else:
        if fail_msg == "":
            fail_msg = "画像を送信してください。"
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=fail_msg)
        ]   )

# Other Message Type
@handler.add(MessageEvent, message=ImageMessage)
def handle_content_message(event):
    is_input_message_ok = False
    img_path = ''

    #Check the input message
    if not isinstance(event.message, ImageMessage):
        pass
    else:
        message_content = line_bot_api.get_message_content(event.message.id)

        #Create the temp file to save the input file.
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
        
            img_name = os.path.basename(tf.name) + '.jpg'
            img_path = os.path.join('static', 'tmp', img_name)
            os.rename(tf.name, img_path)

        is_input_message_ok = True

    #Execute sorting
    if is_input_message_ok == True:     
        execute(event, img_path)
    
    else:
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='別の画像を送ってください。')
        ]   )

@handler.add(FollowEvent)
def handle_follow(event):
    pass

def execute(event, img_path):
    sdh.estimate(img_path)

    #Can not detect the face
    if len(sdh.result_data) == 0:
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='別の画像を送ってください。\n例えば、写っている顔が小さい場合は判断できない場合があります。')
        ]   )
    else:
        sdh.draw(img_path)

        house_names = ''
        i = 0
        for (x, y, w, h, hn) in sdh.result_data:
            house_names += sdh.get_house_name_in_japanese(hn)
            house_names += ' !'
            if i < len(sdh.result_data) - 1:
                house_names += '\n'
            i += 1

        img_url = request.host_url + img_path
        img_url = 'https' + img_url[4:] # http -> https

        line_bot_api.reply_message(
            event.reply_token, [
            TextSendMessage(text=house_names),
            ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
        ])
        
    sdh.release_internal_data()



if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
#    app.run(host="127.0.0.1", port=port)
