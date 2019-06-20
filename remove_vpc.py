#!/usr/bin/env python3
"""
Remove those pesky AWS default VPCs.
Python Version: 3.7.0
Boto3 Version: 1.7.50
"""

import sys
import boto3
from botocore.exceptions import ClientError
from multiprocessing.dummy import Pool as ThreadPool
import itertools

dryrun = True

def delete_igw(ec2, vpc_id):
  """
  Detach and delete the internet gateway
  """
  args = {
    'Filters' : [
      {
        'Name' : 'attachment.vpc-id',
        'Values' : [ vpc_id ]
      }
    ]
  }
  try:
    igw = ec2.describe_internet_gateways(**args)['InternetGateways']
  except ClientError as e:
    print(e.response['Error']['Message'])
  if igw:
    igw_id = igw[0]['InternetGatewayId']
    try:
      print("  Detaching " + str(igw_id))
      if (dryrun != True): ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    except ClientError as e:
      print(e.response['Error']['Message'])
    try:
      print("  Deleting " + str(igw_id))
      if (dryrun != True): ec2.delete_internet_gateway(InternetGatewayId=igw_id)
    except ClientError as e:
      print(e.response['Error']['Message'])


def delete_subs(ec2, args):
  """
  Delete the subnets
  """
  try:
    subs = ec2.describe_subnets(**args)['Subnets']
  except ClientError as e:
    print(e.response['Error']['Message'])
  if subs:
    for sub in subs:
      sub_id = sub['SubnetId']
      try:
        print("  Deleting " + str(sub_id))
        if (dryrun != True): ec2.delete_subnet(SubnetId=sub_id)
      except ClientError as e:
        print(e.response['Error']['Message'])


def delete_rtbs(ec2, args):
  """
  Delete the route tables
  """
  try:
    rtbs = ec2.describe_route_tables(**args)['RouteTables']
  except ClientError as e:
    print(e.response['Error']['Message'])
  if rtbs:
    for rtb in rtbs:
      main = 'false'
      for assoc in rtb['Associations']:
        main = assoc['Main']
      if main == True:
        continue
      rtb_id = rtb['RouteTableId']
      try:
        print("  Deleting " + str(rtb_id))
        if (dryrun != True): = ec2.delete_route_table(RouteTableId=rtb_id)
      except ClientError as e:
        print(e.response['Error']['Message'])


def delete_acls(ec2, args):
  """
  Delete the network access lists (NACLs)
  """
  try:
    acls = ec2.describe_network_acls(**args)['NetworkAcls']
  except ClientError as e:
    print(e.response['Error']['Message'])
  if acls:
    for acl in acls:
      default = acl['IsDefault']
      if default == True:
        continue
      acl_id = acl['NetworkAclId']
      try:
        print("  Deleting " + str(acl_id))
        if (dryrun != True): ec2.delete_network_acl(NetworkAclId=acl_id)
      except ClientError as e:
        print(e.response['Error']['Message'])


def delete_sgps(ec2, args):
  """
  Delete any security groups
  """
  try:
    sgps = ec2.describe_security_groups(**args)['SecurityGroups']
  except ClientError as e:
    print(e.response['Error']['Message'])
  if sgps:
    for sgp in sgps:
      default = sgp['GroupName']
      if default == 'default':
        continue
      sg_id = sgp['GroupId']
      try:
        print("  Deleting " + str(sg_id))
        if (dryrun != True): ec2.delete_security_group(GroupId=sg_id)
      except ClientError as e:
        print(e.response['Error']['Message'])


def delete_vpc(ec2, vpc_id, region):
  """
  Delete the VPC
  """
  try:
    print("  Deleting " + str(vpc_id))
    if (dryrun != True): ec2.delete_vpc(VpcId=vpc_id)
  except ClientError as e:
    print(e.response['Error']['Message'])
  else:
    print('VPC {} has been deleted from the {} region.'.format(vpc_id, region))


def get_regions(ec2):
  """
  Return all AWS regions
  """
  regions = []
  try:
    aws_regions = ec2.describe_regions()['Regions']
  except ClientError as e:
    print(e.response['Error']['Message'])
  else:
    for region in aws_regions:
      regions.append(region['RegionName'])
  return regions


def delete_everything_in_region(ec2, session, region=None):
  """
  Do the work..
  Order of operation:
  1.) Delete the internet gateway
  2.) Delete subnets
  3.) Delete route tables
  4.) Delete network access lists
  5.) Delete security groups
  6.) Delete the VPC
  """
  print("Scanning Region: " + str(region))
  ec2 = session.client('ec2', region_name=region)
  attribs = ec2.describe_account_attributes(AttributeNames=[ 'default-vpc' ])['AccountAttributes']
  if len(attribs) > 0:
      vpc_id = attribs[0]['AttributeValues'][0]['AttributeValue']
  else:
    print('VPC (default) was not found in the {} region.'.format(region))
    return
  print(" Removing VPC: " + str(vpc_id))
  # Are there any existing resources?  Since most resources attach an ENI, let's check..
  args = {
    'Filters' : [
      {
        'Name' : 'vpc-id',
        'Values' : [ vpc_id ]
      }
    ]
  }
  eni = ec2.describe_network_interfaces(**args)['NetworkInterfaces']
  if eni:
    print(' VPC {} has existing resources in the {} region.'.format(vpc_id, region))
    return
  delete_igw(ec2, vpc_id)
  delete_subs(ec2, args)
  delete_rtbs(ec2, args)
  delete_acls(ec2, args)
  delete_sgps(ec2, args)
  delete_vpc(ec2, vpc_id, region)


def main(profile=None):
  # AWS Credentials
  # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
  session = boto3.Session(profile_name=profile)
  ec2 = session.client('ec2', region_name='us-east-1')
  regions = get_regions(ec2)
  if dryrun: print("Dryrun, not actually deleting anything")
  pool = ThreadPool(len(regions))
  pool.starmap(delete_everything_in_region, zip(itertools.repeat(ec2), itertools.repeat(session), regions))
  pool.close()
  pool.join()  # wait for parallel requests to complete


if __name__ == "__main__":
  if ( len(sys.argv) == 2):
    dryrun = True
    main(profile = sys.argv[1])
  elif ( len(sys.argv) == 3):
    dryrun = (sys.argv[2] == True)
    main(profile = sys.argv[1])
  else:
    main()
