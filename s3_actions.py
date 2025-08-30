import boto3
from botocore.exceptions import ClientError
from logging_setup import logging, log_csv
from datetime import datetime, timedelta, timezone
import os
import json

#Creating the boto 3 object
s3 = boto3.resource('s3')


#Get the Bucket name (config/CLI)
def get_bucket(args, config):
    #Creating the boto 3 object
    s3 = boto3.resource('s3')

    if args.bucket_name:
        bucket_name = args.bucket_name
    elif config.get("bucket_name"):
        bucket_name = config.get("bucket_name")
    else:
        raise ValueError("Bucket name not provided (use --bucket-name or config file)")
    
    return s3.Bucket(bucket_name)




#List s3 buckets
def list_all_buckets(args, config):
    bucket_names = [bucket.name for bucket in s3.buckets.all()]
    try: 
        for name in bucket_names:
            print(name)
            logging.info(f"All s3 buckets have been listed successfully")
            log_csv("s3", name, "Listing s3 buckets", "Success")
    except Exception as e:
            logging.error(f"An Error occurred when listing s3 buckets: {e}")
            log_csv("s3", name, "Listing s3 Buckets", "Failure")

    return bucket_names


#Upload files to S3 bucket
def upload_files_s3(args, config=None):
    bucket = get_bucket(args, config)

    if hasattr(args, "prefix") and args.prefix:
        prefix = args.prefix
    elif config and config.get("prefix"):
        prefix = config.get("prefix")
    else:
        prefix = "default"


    today = datetime.now().date().strftime("%Y-%m-%d")

    local_file_path = args.local_file_path or config.get("local_file_path")
    for file in os.listdir(local_file_path):
        s3_file_path = os.path.join(local_file_path, file)
        s3_key = f"{prefix}/{str(today)}/{os.path.basename(s3_file_path)}"
    #Ensure we upload only files
        if os.path.isfile(s3_file_path):
          try:
               bucket.upload_file(s3_file_path, s3_key)
               logging.info(f"{file} has been uploaded to {bucket.name}")
               log_csv("S3", bucket.name, "upload-file", "Success")
          except ClientError as e:
               logging.error(f"An AWS error occured when trying to uploading {file}: ({e.response['Error']['Code']}): {e}")
               log_csv("S3", bucket.name, "upload-file", "Failed")
          except Exception as e:
               logging.error(f"An error occured when trying to uploading {file}: {e}")
               log_csv("S3", bucket.name, "upload-file", "Failed")

               

#Delete old files based on the last-time-modification
#Set a cut-off day for files to be deleted

def delete_files_s3(args, config):
    bucket = get_bucket(args, config)
    if hasattr(args, "cut_off_days") and args.cut_off_days:
        days = args.cut_off_days
    elif config and config.get("cut_off_days"):
        days = config.get("cut_off_days")
    else:
        days = 30
    cut_off_day = datetime.now(timezone.utc) - timedelta(days=days)
    files_to_delete = []
    for obj in bucket.objects.all():
        try:
            if obj.last_modified < cut_off_day:
              files_to_delete.append(obj.key)
              logging.info(f"{obj.key} has been added to the files to be deleted")
              log_csv("S3", bucket.name, "file-added-to-deletelist", "Success")
        except ClientError as e:
              logging.error(f"An AWS error occured when adding {obj.key} to the files to be deleted ({e.response['Error']['Code']}): {e}")
              log_csv("S3", bucket.name, "file-added-to-deletelist", "Failed")
        except Exception as e:
              logging.error(f"An error occured when adding {obj.key} to the files to be deleted {e}")
              log_csv("S3", bucket.name, "file-added-to-deletelist", "Failed") 
        

    if files_to_delete:
        delete_dict = {'Objects': [{'Key': key} for key in files_to_delete]}
        try:
            bucket.delete_objects(Delete=delete_dict)
            logging.info(f" Objects have been deleted from {bucket.name} successfully")
            log_csv("S3", bucket.name, "file-deletion", "Success")    
        except ClientError as e:
            logging.error(f"An AWS error occured while deleting the objects: {e.response['Error']['Code']}): {e} ")
            log_csv("S3", bucket.name, "file-deletion", "Failed")      
        except Exception as e:
            logging.error(f"An error occurred while deleting the objects: {e}")
            log_csv("S3", bucket.name, "file-deletion", "Failed")




S3_ACTIONS = {
    "list-buckets": list_all_buckets,
    "upload-file": upload_files_s3,
    "delete-file": delete_files_s3
}    
                                       
