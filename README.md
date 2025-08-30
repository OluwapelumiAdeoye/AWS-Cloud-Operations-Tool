# AWS-Cloud-Operations-Tool
A lightweight Python CLI tool built with Boto3 to manage and audit AWS resources (IAM, S3, and EC2).
The tool provides easy command-line access to common cloud engineering tasks, with support for a DryRun mode for safe testing.
Features

IAM
list-users → List all IAM users in the account.
list-keys → List access keys for a specific IAM user.
create-key → Create a new access key for a user.
delete-key → Delete an existing access key.
delete-old-keys → Delete IAM access keys older than a set threshold.

S3
list-buckets → View all available S3 buckets.
list-objects → View all objects inside a given bucket.

EC2
list → List running EC2 instances with their IDs and IPs.
stop → Stop one or multiple EC2 instances.
terminate → Terminate one or multiple EC2 instances.

Logging
Every action performed is logged with details about:
The service (IAM, S3, EC2)
The action taken (e.g., list, create, delete)
The timestamp of the action
The result (success or error message)

Logs are stored in a dedicated log file (e.g., aws_resource_tool.log) so you can trace what happened during execution.

How It Works
The tool uses argparse for command-line parsing. Each AWS service has its own subcommands for managing resources.

Example:
# List all IAM users
python main.py iam list-users

# Stop an EC2 instance
python main.py ec2 stop --instance-ids i-0123456789abcdef0

# List objects in an S3 bucket
python main.py s3 list-objects --bucket my-bucket-name

 A --dryrun flag is also available but excluded from demo runs so outputs remain practical.


 Why This Project Matters
Automates repetitive AWS tasks
Reinforces best practices for handling IAM credentials
Demonstrates Python + Boto3 usage for cloud resource management
Improves reliability with logs and dry-run support

 
