import boto3
from botocore.exceptions import ClientError
from logging_setup import log_csv, logging
import time

#ec2 = boto3.resource('ec2')

#List all instances
def list_instances(args, config):
    print("\n=== All Instances ===")
    instance_list = []
    for instance in ec2.instances.all():
        try:
            instance_list.append(instance)
            logging.info(f"ID: {instance.id} | State: {instance.state['Name']} | Tags: {instance.tags}")
            log_csv("EC2", instance.id, "Listing Instance", "Success")
        except ClientError as e:
            logging.error(f"An AWS error occured while trying to list instances: ({e.response['Error']['Code']}): {e}")
            log_csv("EC2", instance.id, "Listing Instance", "Failed")
        except Exception as e:
            logging.error(f"An unexpected error occured: {e}")
            log_csv("EC2", instance.id, "Listing Instance", "Failed")

            
    return instance_list
         


# Filter running instances and select those to stop and add them a selected list
def filter_instances(args, config):
    instances_to_stop = []
    tag_key = args.tag_key or config.get("tag_to_check")
    tag_value = args.tag_value or config.get("stop_tag_value")

    if not tag_key or not tag_value:
        print("[ERROR] Both --tag-key and --tag-value must be provided, or set in config.")
        return []
    
    for instance in ec2.instances.filter(Filters=[ {"Name": f"tag:{tag_key}", "Values": [tag_value]},
                                                  {'Name': 'instance-state-name', 'Values': ['running']}]):
        try:
                instances_to_stop.append(instance.id)
                logging.info(f"[MATCH] {instance.id} -> Will be stopped (Tags: {tag_key}, {tag_value})")
                log_csv("EC2", instance.id, "filtering for instances", "Success")
        except ClientError as e:
                logging.error(f"AWS error occurred while filtering instances ({e.response['Error']['Code']}): {e}")
                log_csv("EC2", instance.id, "filtering for instances", "Failed")
        except Exception as e:
                logging.error(f"An Error occured while stopping instances {e}")
                log_csv("EC2", instance.id, "filtering for instances", "Failed")
    matches = len(instances_to_stop)
    if matches == 1:
         print(f"There is {matches} match for the search")
    else:
        print(f"There are {matches} matches for the search")
    log_csv("EC2", None, f"[MATHCES] {matches}", "Success")


    return instances_to_stop
             

# Stop all instances in the list
def stop_instances(args, config, instances_to_stop=None):
    if args.instance_ids:
        instances_to_stop = args.instance_ids
    elif config.get("instance_ids"):
        instances_to_stop = config.get("instance_ids")
    elif instances_to_stop is None:
        instances_to_stop = filter_instances(args, config)
    

    if not instances_to_stop:
        logging.info("No matching instances to stop")
        log_csv("EC2", None, "stopped instance", "No-match")
        return
    
    stopped_instances_list = []

    try:
            ec2.meta.client.stop_instances(InstanceIds=instances_to_stop)
            logging.info(f"\nStopping instances: {instances_to_stop}")
            for instance_id in instances_to_stop:
                instance = ec2.Instance(instance_id)
                logging.info(f"[WAITING].. Stopping {instance.id} -> State: {instance.state['Name']}")
                log_csv("EC2", instance_id, "Waiting to stop", "Success")
                #time.sleep(2)
                ec2.meta.client.get_waiter('instance_stopped').wait(InstanceIds=instances_to_stop)
                instance.reload()
                logging.info(f"[DONE] {instance.id} is now stopped")
                log_csv("EC2", instance_id, "stopped instance", "Success")
                stopped_instances_list.append(instance_id)
    except ClientError as e:
                logging.error(f"AWS error occured while trying to Stop instance {instance_id}: ({e.response['Error']['Code']}): {e}")
                log_csv("EC2", instance_id, "stopped instance", "Failed")
    except Exception as e:
                logging.error(f"An error occured while trying to Stop instance {instance_id}: {e}")
                log_csv("EC2", instance_id, "stopped instance", "Failed")


    return stopped_instances_list



EC2_ACTIONS = {
     "list-instances": list_instances,
     "filter-instances": filter_instances,
     "stop-instances": stop_instances,
}
