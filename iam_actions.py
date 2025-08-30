import boto3
from botocore.exceptions import ClientError
from logging_setup import logging, log_csv
from datetime import datetime, timedelta, timezone


#Creating the boto3 object
iam = boto3.client('iam')


def list_users(args, config):
    try:
        users = iam.list_users()
        usernames = [user['UserName'] for user in users['Users']]
        for username in usernames:
            print(f'\nUser: {username}')
        logging.info(f"Usernames listed successfully: {usernames} ")
        for username in usernames:
            log_csv("IAM", username, "Username listed", "Success")
        return usernames
    except Exception as e:
        logging.error(f"Error listing Username: {e}")
        log_csv("IAM", "N/A" , "Username listed", "Failure")

def list_keys(args, config):
    if hasattr(args, "username") and args.username:
        username = args.username
    elif config:
        username = config.get("username")
    else:
        username = "user-adeoye"


    try: 
        keys = iam.list_access_keys(UserName=username)["AccessKeyMetadata"]

        if not keys:
            print(f"{username} does not have any keys at the moment")
            logging.error(f"{username} does not have any keys at the moment")
            log_csv("IAM", username, "List User Access Keys", "Empty")
            return


        for key in keys:
            print(f"Key ID: {key['AccessKeyId']} | Status: {key['Status']} | Created: {key['CreateDate']}")
            logging.info(f"Access keys for {username} has been listed successfully.")
            log_csv("IAM", username, "List User Access keys", "Success")
    except Exception as e: 
        logging.error(f"Error occured while listing keys for {username}: {e}")
        log_csv("IAM", username, "Listing User Access Keys", "Failure")



def create_new_key(args, config, username=None):
    if hasattr(args, "username") and args.username:
        username = args.username
    elif config:
        username = config.get("username")
    else:
        username = "user-adeoye"

    try:
        new_key = iam.create_access_key(UserName=username)
        logging.info(f"New Access Key has been created for {username} successfully")
        log_csv("IAM", username, "Creating a new Access-Key", "Success")
        print("New Access keyId:", new_key['AccessKey']['AccessKeyId'])
        print("New Secret AccessKey:", new_key['AccessKey']['SecretAccessKey'])
        print("Status:", new_key['AccessKey']['Status'])
        print("Date Created:", new_key['AccessKey']['CreateDate'])
    except Exception as e:
        logging.error(f"Error creating Access key: {e}")
        log_csv("IAM", username, "Creating a new Access-Key", "Failure")






def delete_key(args, config):
    username = args.username or config.get("username")
    key_id = args.access_key_id

    if not username or not key_id:
        logging.error("Username and AccessKeyId are required for delete-key.")
        return

    try:
        iam.delete_access_key(UserName=username, AccessKeyId=key_id)
        logging.info(f"Deleted access key {key_id} for user {username}.")
        log_csv("IAM", username, "Delete-Specific-Key", "Success")
    except Exception as e:
        logging.error(f"Error deleting access key {key_id} for {username}: {e}")
        log_csv("IAM", username, "Delete-Specific-Key", "Failed")





#helper function to filter for old iam keys
def find_old_keys(username, cutoff_days):
    keys = iam.list_access_keys(UserName=username)["AccessKeyMetadata"]
    cutoff = datetime.now(timezone.utc) - timedelta(days=cutoff_days)

    old_keys = [
        key["AccessKeyId"]
        for key in keys
        if key["CreateDate"] < cutoff
    ]
    return old_keys



def delete_old_keys(args, config):
    username = args.username or config.get("username")
    cut_off_days = args.key_max_age or config.get("key_max_age", 30)

    if not username:
        logging.error("No username provided (CLI or Config)")
        return

    old_keys = find_old_keys(username, cut_off_days)


    if not old_keys:
        logging.info(f"No old keys to delete for {username}")
        return
    

    for key in old_keys:  
        iam.delete_access_key(UserName=username, AccessKeyId=key)
        logging.info(f"Old key for {username} has been deleted successfully")
        log_csv("IAM", username, "Deleting-old-Access-Key", "Success")



IAM_ACTIONS = {
    "list-users": list_users,
    "create-key": create_new_key,
    "delete-key": delete_key,
    "delete-old-keys": delete_old_keys,
    "list-keys": list_keys
}