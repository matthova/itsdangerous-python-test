from app import app
from itsdangerous import URLSafeSerializer
from flask import request
import os
import dotenv
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection

s = URLSafeSerializer('secret-key')

def upload_to_s3(aws_access_key_id, aws_secret_access_key, file, bucket, key, callback=None, md5=None, reduced_redundancy=False, content_type=None):
    """
    Uploads the given file to the AWS S3
    bucket and key specified.

    callback is a function of the form:

    def callback(complete, total)

    The callback should accept two integer parameters,
    the first representing the number of bytes that
    have been successfully transmitted to S3 and the
    second representing the size of the to be transmitted
    object.

    Returns boolean indicating success/failure of upload.
    """
    try:
        size = os.fstat(file.fileno()).st_size
    except:
        # Not all file objects implement fileno(),
        # so we fall back on this
        file.seek(0, os.SEEK_END)
        size = file.tell()

    conn = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
    bucket = conn.get_bucket(bucket, validate=True)
    k = Key(bucket)
    k.key = key
    if content_type:
        k.set_metadata('Content-Type', content_type)
    sent = k.set_contents_from_file(file, cb=callback, md5=md5, reduced_redundancy=reduced_redundancy, rewind=True)

    # Rewind for later use
    file.seek(0)

    if sent == size:
        return True
    return False


@app.route('/', methods=['GET'])
def index():
    test1 = s.sign('foo')
    print test1
    test2 = s.unsign(test1)
    print test2
    return "Hello, World!"

@app.route('/', methods=['POST'])
def parse1234():
    try:
        preval = request.form.get("key")
        print preval
        postval = s.loads(preval)
        print postval
        return 'sup?'
    except:
        return 'fail whale'

@app.route('/files', methods=['POST'])
def upload():
    file = open(os.path.abspath('blah.txt'),'rb')
    print file.name
    key = 'blah.txt'
    if upload_to_s3(dotenv.get('AWS_ACCESS_KEY'), dotenv.get('AWS_SECRET_KEY'), file, dotenv.get('S3_BUCKET'), key):
       return 'success'
    else:
       return 'fail'


@app.route('/files', methods=['GET'])
def get_files():
    conn = S3Connection(dotenv.get('AWS_ACCESS_KEY'), dotenv.get('AWS_SECRET_KEY'))
    bucket = conn.get_bucket(dotenv.get('S3_BUCKET'))
    for key in bucket.list():
        print key.name.encode('utf-8')
    return 'success'
