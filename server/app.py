import os
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from PIL import Image
import rawpy
import imageio
from werkzeug.datastructures import FileStorage
import numpy
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

  req_data = request.get_json()
  outputs = []
  filepath = req_data['url']
  rois = req_data['rois']

  print(rois)
  print(filepath)
  raw_basename = os.path.basename(filepath)
  raw_basename_no_ext = os.path.splitext(raw_basename)[0]

  print(raw_basename_no_ext)
  raw_filepath = UPLOAD_FOLDER + raw_basename_no_ext + '.dng'

  with rawpy.imread(raw_filepath) as raw:
    print(raw)
    for roi in rois:
      roi_output = process_roi(raw, roi)
      outputs.append(roi_output)
  
  print(outputs)
  return jsonify({'data':outputs})

def process_roi(raw, roi):

  print(roi)
  a_srgb = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB, output_bps=8) # RAW -> sRGB
  a_xyz = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.XYZ, output_bps=8) # RAW -> XYZ

  ac_srgb = a_srgb[int(roi['x1']) : int(roi['x2']), int(roi['y1']) : int(roi['y2'])] # new array for selection of image (srgb)
  ac_xyz = a_xyz[int(roi['x1']) : int(roi['x2']), int(roi['y1']) : int(roi['y2'])] # new array for selection of image (xyz)

  # obtain median values from these arrays (these calls include sorting under the hood)
  med_srgb = numpy.median(ac_srgb, axis=(0, 1))
  med_xyz = numpy.median(ac_xyz, axis=(0, 1))

  # Return an RoiOutput
  srgb_obj = {'r': med_srgb[0], 'g': med_srgb[1], 'b': med_srgb[2]}
  xyz_obj = {'x': med_xyz[0], 'y': med_xyz[1], 'z': med_xyz[2]}
  return {'label': roi['index'], 'xyz': xyz_obj, 'srgb': srgb_obj}


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
