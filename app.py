import os

from flask import Flask, request, render_template, send_from_directory
from selectorlib import Extractor
import requests
import json
from time import sleep



app = Flask(__name__)
# app = Flask(__name__, static_folder="images")



APP_ROOT = os.path.dirname(os.path.abspath(__file__))

classes = ['Black Jeans','Blue Jeans','Horizontal Striped Shirt','Solid Shirt','Vertical Striped Shirt']

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    target = os.path.join(APP_ROOT, 'images/')
    # target = os.path.join(APP_ROOT, 'static/')
    print(target)
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("Accept incoming file:", filename)
        print ("Save it to:", destination)
        upload.save(destination)
        #import tensorflow as tf
        import numpy as np
        from tensorflow.keras.preprocessing import image

        from tensorflow.keras.models import load_model

        new_model = load_model('model.h5')
        new_model.summary()
        test_image = image.load_img('/home/r3b007/find_your_fashion/images/'+filename,target_size=(64,64))
        test_image = image.img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis = 0)
        result = new_model.predict(test_image)
        result1 = result[0]
        for i in range(5):
    
            if result1[i] == 1.:
                break;
        prediction = classes[i]
    with open('search_results_output.jsonl', 'w') as outfile:
        data = scrape(prediction)
        if data:
            for product in data['products']:
                product['search_url'] = 'https://www.amazon.com/s?k='+prediction
                print("Saving Product: %s" % product['title'])
                json.dump(product, outfile)
                outfile.write("\n")

    # return send_from_directory("images", filename, as_attachment=True)

    return render_template("template.html",image_name=filename, text=prediction)


e = Extractor.from_yaml_file('search_results.yml')


def scrape(prediction):
    url = 'https://www.amazon.com/s?k='+prediction
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    print("Downloading %s" % url)
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n" % url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d" % (url, r.status_code))
        return None
    # Pass the HTML of the page and create
    return e.extract(r.text)


# product_data = []
                # sleep(5)


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

if __name__ == "__main__":
    app.run(debug=False)

