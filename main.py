import argparse
import os
import json
from logging_setup import log_csv

from ec2_actions import EC2_ACTIONS
from s3_actions import S3_ACTIONS
from iam_actions import IAM_ACTIONS


def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path) as file:
            return json.load(file)
    return {}
    

def get_args():
    parser = argparse.ArgumentParser(description="An AWS resource cleaner & auditor")

    parser.add_argument("--config", default="config.json", help="Path to config file")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without executing")


    #Create a Subparser
    subparsers = parser.add_subparsers(dest="service", required=True)

    #EC2 Sub-command
    ec2_parser = subparsers.add_parser("ec2", help="Manage EC2 instances")
    

    #EC2 subarser
    ec2_subparsers = ec2_parser.add_subparsers(dest="action", required=True)
    
    #List instances action(parser)
    ec2_subparsers.add_parser("list-instances", help="List EC2 instances")

    #Filter instances action(parser)
    filter_instances_parser = ec2_subparsers.add_parser("filter-instances", help="Filter EC2 instances")
    filter_instances_parser.add_argument("--tag-key", help="Tag key to filter instances")
    filter_instances_parser.add_argument("--tag-value", help="Tag value to filter instances")

    #Stop instances action(parser)
    stop_instances_parser = ec2_subparsers.add_parser("stop-instances", help="Stop EC2 instances")
    stop_instances_parser.add_argument("--instance-ids", nargs="+", help="Stop one or more EC2 instances with their ID")

    #--------------------------------------------------------------------------------------------------------------------

    #S3 Sub-Command
    s3_parser = subparsers.add_parser("s3", help="Manage S3 Bucket Actions")

    #S3 subparser
    s3_subparser = s3_parser.add_subparsers(dest="action", required=True)

    #List s3 buckets
    s3_subparser.add_parser("list-buckets", help="List S3 Buckets")

    #s3 Upload file
    upload_file_parser = s3_subparser.add_parser("upload-file", help="Upload a file")
    upload_file_parser.add_argument("--bucket-name", required=True, help="The S3 bucket name")
    upload_file_parser.add_argument("--local-file-path", required=True, help="The file path")
    upload_file_parser.add_argument("--prefix", help="Build file path in S3")
    
    #S3 Delete files
    delete_file_parser = s3_subparser.add_parser("delete-file", help="Delete files")
    delete_file_parser.add_argument("--bucket-name", required=True, help="The S3 bucket name")
    delete_file_parser.add_argument("--cut-off-days", type=int, default=30, help="Number of days before now to filter objects (default:30)")

    #-------------------------------------------------------------------------------------------------------------------------------------------------------

    #IAM Sub-Command
    iam_parser = subparsers.add_parser("iam", help="Manage IAM Actions")

    #IAM Subparser
    iam_subparser = iam_parser.add_subparsers(dest="action", required=True)
    
    #IAM List Users parser
    iam_subparser.add_parser("--list-users", help="List IAM Users")

    #IAM List User Keys
    list_keys = iam_subparser.add_parser("list-keys", help="List user access keys")
    list_keys.add_argument("--username", help="Username to list keys")

    #IAM Create Key parser
    create_key = iam_subparser.add_parser("create-key", help="Create new keys")
    create_key.add_argument("--username", help="Username to create keys")

    #IAM Delete Key parser
    delete_key = iam_subparser.add_parser("delete-key", help="Delete a specific access key")
    delete_key.add_argument("--username", required =True, help="IAM Username")
    delete_key.add_argument("--access-key-id", required=True, help="Access Key ID to delete")

    #IAM Delete Old keys parser
    delete_oldkey_parser =  iam_subparser.add_parser("delete-old-keys", help="Delete old IAM Access keys")
    delete_oldkey_parser.add_argument("--username", help="IAM Username to delete Keys for")
    delete_oldkey_parser.add_argument("--key-max-age", type=int, default=30, help="Days after key are considered old")

    return parser.parse_args()

def main():
    args = get_args()
    config = load_config(args.config)


    if args.dry_run:
        print(f"[DryRun] Would execute: {args.action} on {args.service}")
        return

    try:
        #Linking EC2 Actions
        if args.service == "ec2":
            EC2_ACTIONS[args.action](args, config)
        #Linking S3 Actions
        elif args.service == "s3":
            S3_ACTIONS[args.action](args, config)
        #Linking IAM Actions
        elif args.service == "iam":
            IAM_ACTIONS[args.action](args, config)
    except Exception as e:
        print(f"Error: {e}")
        log_csv("Main()", "Actions", {e}, "Failure")
        

            


if __name__ == "__main__":
    main()
    

    







