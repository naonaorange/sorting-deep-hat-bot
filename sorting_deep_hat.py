#!/usr/bin/env python3

from tensorflow.keras import models
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class sorting_deep_hat:
    def __init__(self, model_path):
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.model = models.load_model(model_path)
        #self.model_path = model_path
        self.font_size = 19
        self.rectangle_width = 5
        self.font = ImageFont.truetype('SourceHanSansJP-Bold.otf', self.font_size)

    def release_internal_data(self):
        if self.image is not None:
            self.image = None
            self.result_data = []

    def estimate(self, input_image_path):
        self.image = cv2.imread(input_image_path)

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray,\
                                                    scaleFactor= 1.11,\
                                                    minNeighbors= 3,\
                                                    #minSize=(70, 70)\
                                                    )

        self.result_data = []
        for (x, y, w, h) in faces:
            #既に検出された顔領域内に顔が検出された場合は除外
            for (xx, yy, ww, hh) in self.result_data:
                if xx < x and x < xx + ww:
                    if yy < y and y < yy + hh:
                        continue
                if xx < x + w and x + w < xx + ww:
                    if yy < y + h and y + h < yy + hh:
                        continue

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
        #pil_image=Image.fromarray(self.image[:, :, ::-1].copy())
        #pil_draw = ImageDraw.Draw(pil_image)

        for (x, y, w, h, hn) in self.result_data:
            color = ()
            if hn == 'Glyffindor':
                color = 'red'
                house_name = 'グリフィンドール'
            elif hn == 'Hufflpuff':
                color = 'orange'
                house_name = 'ハッフルパフ'
            elif hn == 'Ravenclaw':
                color = 'blue'
                house_name = 'レイブンクロー'
            elif hn == 'Slytherin':
                color = 'green'
                house_name = 'スリザリン'

            #pil_draw.rectangle([(x, y), (x+w, y+h)], outline=color,  width=self.rectangle_width)
            
            #文字が矩形と重なってしまうため、矩形の幅と文字の大きさを考慮して位置を決定
            #text_draw_y = y - self.font_size - self.rectangle_width - 1 
            #if text_draw_y < 0:
            #    text_draw_y = 0
            #pil_draw.text((x, text_draw_y), house_name, fill=color, font=self.font)

            #cv2.rectangle(self.image, (x, y), (x + w, y + h), (0,0,255), 2)
            #cv2.putText(self.image, hn, (x, y), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 4)
        
        #pil_image.save(output_image_path)
        #pil_image.close()

        #cv2.rectangle(self.image, (x, y), (x + w, y + h), color, 2)
        #cv2.putText(self.image, house_name, (x, y), cv2.FONT_HERSHEY_PLAIN, 2, color, 4)
        cv2.imwrite(output_image_path, self.image)
        
if __name__ == '__main__':
    model_path = 'models/sorting_deep_hat.h5'
    input_image_path = 'data/sample/harrypotter.jpg'
    output_image_path = 'output.jpg'

    sdt = sorting_deep_hat(model_path)
    sdt.estimate(input_image_path)
    print(sdt.result_data)
    sdt.draw(output_image_path)
    sdt.release_internal_data()
