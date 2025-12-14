import av
from pyzbar import pyzbar
from PIL import Image
import cv2
import numpy as np

class BarcodeScanner:
    last_result = None

    def recv(self, frame):
        
        img = frame.to_ndarray(format="bgr24")

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)

        decoded_objects = pyzbar.decode(pil_img)

        if decoded_objects:
            barcode_data = decoded_objects[0].data.decode("utf-8")
            BarcodeScanner.last_result = barcode_data

            for obj in decoded_objects:
                x, y, w, h = obj.rect

                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 4)

                text = obj.data.decode("utf-8")
                cv2.putText(
                    img, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 3
                )

                cv2.putText(
                    img, obj.type, (x, y + h + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2
                )

        return av.VideoFrame.from_ndarray(img, format="bgr24")