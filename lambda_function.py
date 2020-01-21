from PIL import Image, JpegImagePlugin, ExifTags
import boto3
import os
import re

s3 = boto3.client('s3')

LARGE_RATIO = int(os.environ['LARGE_RATIO'])
MEDIUM_RATIO = int(os.environ['MEDIUM_RATIO'])
SMALL_RATIO = int(os.environ['SMALL_RATIO'])


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    tmp = u'/tmp/' + os.path.basename(key)

    try:
        s3.download_file(Bucket=bucket, Key=key, Filename=tmp)
        JpegImagePlugin._getmp = lambda x: None

        originalImage = Image.open(tmp, 'r')
        o_width, o_height = originalImage.size
        
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation' : break
        exif = dict(originalImage._getexif().items())
        
        if exif[orientation] == 3:
            originalImage = originalImage.rotate(180, expand=True)
        elif exif[orientation] == 6:
            originalImage = originalImage.rotate(270, expand=True)
        elif exif[orientation] == 8:
            originalImage = originalImage.rotate(90, expand=True)
            
        originalImage.save(tmp, 'JPEG', optimize=True)
        destOriginalImagePath = re.sub(r'^input/', 'original/', key)
        s3.upload_file(Filename=tmp, Bucket=bucket, Key=destOriginalImagePath)

        large_image = Image.open(tmp, 'r')
        large_image.thumbnail((o_width / LARGE_RATIO, o_height / LARGE_RATIO), Image.LANCZOS)
        large_image.save(tmp, 'JPEG', optimize=True)
        large_image_path = re.sub(r'^input/', 'large/', key)
        s3.upload_file(Filename=tmp, Bucket=bucket, Key=large_image_path)
        
        medium_image = Image.open(tmp, 'r')
        medium_image.thumbnail((o_width / MEDIUM_RATIO, o_height / MEDIUM_RATIO), Image.LANCZOS)
        medium_image.save(tmp, 'JPEG', optimize=True)
        medium_image_path = re.sub(r'^input/', 'medium/', key)
        s3.upload_file(Filename=tmp, Bucket=bucket, Key=medium_image_path)

        small_image = Image.open(tmp, 'r')
        small_image.thumbnail((o_width / SMALL_RATIO, o_height / SMALL_RATIO), Image.LANCZOS)
        small_image.save(tmp, 'JPEG', optimize=True)
        small_image_path = re.sub(r'^input/', 'small/', key)
        s3.upload_file(Filename=tmp, Bucket=bucket, Key=small_image_path)

        return

    except Exception as e:
        print(e)
        raise e
