#!/usr/bin/env python

from keras.models import load_model
import cv2
import numpy as np

class sorting_deep_hat:

    def read_model(self, model_path):
        self.model = load_model(model_path)
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    def estimate(self, input_image_path, output_image_path, face_rects, house_names):
        image = cv2.imread(input_image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 3)

        i = 0
        for (x, y, w, h) in faces:
            face_image = image[y:y+h, x:x+w]
            face_image = cv2.resize(face_image, (100, 100))
    
            b,g,r = cv2.split(face_image)
            in_data = cv2.merge([r,g,b])
            in_data = np.array([in_data / 255.])
    
            house = np.argmax(self.model.predict(in_data))
            if house == 0:
                house_names.append('Glyffindor')
                color = (0, 0, 255)
            elif house == 1:
                house_names.append('Hufflpuff')
                color = (0, 255, 255)
            elif house == 2:
                house_names.append('Ravenclaw')
                color = (255, 0, 0)
            elif house == 3:
                house_names.append('Slytherin')
                color = (0, 255, 0)
    
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(image, house_names[i], (x, y), cv2.FONT_HERSHEY_PLAIN, 2, color, 4)
            cv2.imwrite(output_image_path, image)
            i += 1
        
if __name__ == '__main__':
    model_path = 'models/sorting_deep_hat.h5'
    input_image_path = 'data/sample/harrypotter.jpg'
    output_image_path = 'output.jpg'
    face_rects = ()
    houses = []

    sdt = sorting_deep_hat()
    sdt.read_model(model_path)
    sdt.estimate(input_image_path, output_image_path, face_rects, houses)
