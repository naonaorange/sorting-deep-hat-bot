#!/usr/bin/env python3

import math
from tensorflow.keras import models
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class sorting_deep_hat:
    def __init__(self, model_path):
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.model = models.load_model(model_path)
        #self.model_path = model_path

    def release_internal_data(self):
        if self.image is not None:
            self.image = None
            self.result_data = []

    def estimate(self, input_image_path):
        self.image = cv2.imread(input_image_path)
        self.image_height, self.image_width = self.image.shape[:2]

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray,\
                                                    scaleFactor= 1.11,\
                                                    minNeighbors= 4,\
                                                    minSize=(self.image_width // 8, self.image_height // 8)\
                                                    )

        self.result_data = []
        for (x, y, w, h) in faces:
            is_detected = True
            #既に検出された顔領域内に顔が検出された場合は除外
            for (xx, yy, ww, hh, hhnn) in self.result_data:
                if xx < x and x < xx + ww:
                    if yy < y and y < yy + hh:
                        is_detected = False
                        break
                if xx < x + w and x + w < xx + ww:
                    if yy < y + h and y + h < yy + hh:
                        is_detected = False
                        break

            if is_detected == True:
                face_image = self.image[y:y+h, x:x+w]
                face_image = cv2.resize(face_image, (100, 100))
        
                b,g,r = cv2.split(face_image)
                in_data = cv2.merge([r,g,b])
                in_data = np.array([in_data / 255.])

                #self.model = models.load_model(self.model_path)
                index = np.argmax(self.model.predict(in_data))

                if index == 0:
                    house_name = 'Glyffindor'
                elif index == 1:
                    house_name = 'Hufflpuff'
                elif index == 2:
                    house_name = 'Ravenclaw'
                elif index == 3:
                    house_name = 'Slytherin'

                self.result_data.append([x, y, w, h, house_name])
    
    def draw(self, output_image_path):
        #MatはRGB, PIL ImageはBGRのため要素の順番を変更
        pil_image=Image.fromarray(self.image[:, :, ::-1].copy())
        pil_draw = ImageDraw.Draw(pil_image)

        for (x, y, w, h, house_name) in self.result_data:
            if house_name == 'Glyffindor':
                color = 'red'
            elif house_name == 'Hufflpuff':
                color = 'orange'
            elif house_name == 'Ravenclaw':
                color = 'blue'
            elif house_name == 'Slytherin':
                color = 'green'

            rectangle_width = 5
            pil_draw.rectangle([(x, y), (x+w, y+h)], outline=color,  width=rectangle_width)

            #矩形の横幅の長さに文字が収まるようにフォントサイズを調整
            font_size = w // 8 #グリフィンドールが8文字
            if font_size < 10:
                font_size = 10
            font = ImageFont.truetype('SourceHanSansJP-Bold-Wo-Kanji.otf', font_size)

            #矩形の下に文字を描画、文字の背景を描画
            #font sizeの高さとのずれがあるため*1.3の領域を背景とする
            text_draw_y = y + h
            if text_draw_y > math.floor(self.image_height - font_size * 1.3):
                text_draw_y = math.floor(self.image_height - font_size * 1.3)
            pil_draw.rectangle([(x, y+h), \
                                (x+w, text_draw_y+font_size*1.3)],\
                                fill='white',\
                                outline='white',\
                                width=rectangle_width)
            pil_draw.text((x, text_draw_y), self.get_house_name_in_japanese(house_name), fill=color, font=font)
            #cv2.rectangle(self.image, (x, y), (x + w, y + h), color, 2)
            #cv2.putText(self.image, house_name, (x, y), cv2.FONT_HERSHEY_PLAIN, 2, color, 4)
        
        pil_image.save(output_image_path)
        #cv2.imwrite(output_image_path, self.image)
    
    def get_house_name_in_japanese(self, name):
        if name == 'Glyffindor':
            house_name = 'グリフィンドール'
        elif name == 'Hufflpuff':
            house_name = 'ハッフルパフ'
        elif name == 'Ravenclaw':
            house_name = 'レイブンクロー'
        elif name == 'Slytherin':
            house_name = 'スリザリン'
        return house_name
        
if __name__ == '__main__':
    model_path = 'models/sorting_deep_hat.h5'
    input_image_path = 'data/sample/harrypotter.jpg'
    output_image_path = 'output.jpg'

    sdt = sorting_deep_hat(model_path)
    sdt.estimate(input_image_path)
    print(sdt.result_data)
    sdt.draw(output_image_path)
    sdt.release_internal_data()
