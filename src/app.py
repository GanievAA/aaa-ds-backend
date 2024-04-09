from flask import Flask, request
from requests import ConnectTimeout, HTTPError
from PIL import UnidentifiedImageError
from models.plate_reader import PlateReader
import logging
import io
import requests

app = Flask(__name__)
plate_reader = PlateReader.load_from_file("/app/model_weights/plate_reader_model.pth")


@app.route('/')
def read_plate():
    images_id = request.args.getlist('image_id', None)
    print("images_id", images_id)
    if images_id == []:
        return "Пожалуйста, укажите image_id. Это можно сделать в браузере, пример http://158.160.66.165:8080/?image_id=10022", 200

    car_numbers = []
    for image_id in images_id:
        try:
            response = requests.get(f"http://178.154.220.122:7777/images/{image_id}", timeout=0.5)
        except ConnectTimeout as con_error:
            return {
                "error": "Connection time out",
                "image_id": image_id
            }, 500

        try:
            im = io.BytesIO(response.content)
        except UnicodeDecodeError as decode_error:
            return {
                "error": "Invalid image",
                "image_id": image_id
            }, 400
        except TypeError as type_error:
            return {
                "error": "Can not decode bytes",
                "image_id": image_id
            }, 400

        try:
            car_numbers.append(plate_reader.read_text(im))
        except UnidentifiedImageError as error:
            return {
                "error": "Invalid image format",
                "image_id": image_id
            }, 400

    return {
        "images_id": images_id,
        "car numbers": car_numbers
    }, 200


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )
    app.json.ensure_ascii = False
    app.run(host='0.0.0.0', port=8080, debug=False)

