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

sdh = sorting_deep_hat.sorting_deep_hat()


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
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=event.message.text+'\nv1.0'))

# Other Message Type
@handler.add(MessageEvent, message=ImageMessage)
def handle_content_message(event):
    if not isinstance(event.message, ImageMessage):
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    ext = 'jpg'
	
    #Create the temp file to save the input file.
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)

        tempfile_path = tf.name
        dist_path = tf.name + '.' + ext
        dist_name = os.path.basename(dist_path)

        os.rename(tempfile_path, dist_path)

        result = sdh.estimate(\
            os.path.join('static', 'tmp', dist_name),\
            os.path.join('static', 'tmp', dist_name))


        if len(result) == 0:
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='顔が大きく写る写真を使って、\n帽子をかぶりなおすのじゃ')
                ])
        else:
            img_path = request.host_url + os.path.join('static', 'tmp', dist_name)
            img_path = 'https' + img_path[4:] # http -> https
    
            t = ''
            i = 0
            for r in result:
                if r[4] == 'Glyffindor':
                    t += 'グリフィンドール !!'
                elif r[4] == 'Hufflpuff':
                    t += 'ハッフルパフ !!'
                elif r[4] == 'Ravenclaw':
                    t += 'レイブンクロー !!'
                elif r[4] == 'Slytherin':
                    t += 'スリザリン !!'
            
                if i < len(result) - 1:
                    t += '\n'
                i += 1

            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='tempfile_path\n' + tempfile_path),
                    TextSendMessage(text='dist_path\n' + dist_path),
                    TextSendMessage(text='dist_name\n' + dist_name),
                    TextSendMessage(text=t),
                    ImageSendMessage(original_content_url=img_path, preview_image_url=img_path)
                ])

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


if __name__ == "__main__":
    sdh.read_model('models/sorting_deep_hat.h5')
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
#    app.run(host="127.0.0.1", port=port)
