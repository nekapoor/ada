import os
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from PIL import Image
import rawpy
import imageio
from werkzeug.datastructures import FileStorage
from helpers import *

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = 'server/static/'

app = Flask(__name__, static_folder='../build')
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/static/<path:path>")
def get_public_file(path):
    full_path = os.path.join('./static/', path)
    head, tail = os.path.split(full_path)
    return send_from_directory(head, tail)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/", methods=["POST"])
@cross_origin()
def upload_file():
  print("a;sdfkjadfs;j")
  print(request.files)
  if "user_file" not in request.files:
      print('adf;adfjnoooooo')
      return "No user_file key in request.files"

  file = request.files["user_file"]
  print('gothererererer')
  print(file)
  if file.filename == "":
      return "Please select a file"

  if file and allowed_file(file.filename):
      raw_basename = os.path.basename(file.filename)
      raw_basename_no_ext = os.path.splitext(raw_basename)[0]
      raw_path = UPLOAD_FOLDER + raw_basename
      jpg_path =  UPLOAD_FOLDER + raw_basename_no_ext + '.jpg'
      
      # save raw file locally
      file.save(raw_path)
      
      # upload raw dng to s3
      #upload_file_to_s3_bucket(raw_path, raw_basename, os.environ.get("BUCKET"))

      # read raw image and convert to .jpg and save
      raw_img = rawpy.imread(raw_path)
      rgb = raw_img.postprocess()
      imageio.imsave(jpg_path, rgb)

      # upload .jpg file to s3
      img = Image.open(jpg_path)
      jpg_basename = os.path.basename(img.filename) 
      #upload_file_to_s3_bucket(jpg_path, jpg_basename, os.environ.get("BUCKET"))

      return jpg_basename
  else:
      print("bad")
      return redirect("/")

@app.route("/images/roi", methods=["POST"])
@cross_origin()
def process_image_rois():
  return "true"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
