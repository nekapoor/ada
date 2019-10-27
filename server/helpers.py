import boto3, botocore, os

ALLOWED_EXTENSIONS = set(['dng', 'png'])

s3 = boto3.client(
   "s3",
   aws_access_key_id=os.environ.get('ACCESS_KEY_ID'),
   aws_secret_access_key=os.environ.get('SECRET_ACCESS_KEY')
)

def upload_file_to_s3_bucket(file_path, file_name, bucket):
  response = s3.upload_file(file_path, bucket, file_name)
  return response

def allowed_file(filename):
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
