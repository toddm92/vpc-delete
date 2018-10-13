"""

Remove those pesky AWS default VPCs.

Python Version: 3.7.0
Boto3 Version: 1.7.50

"""

import boto3
from botocore.exceptions import ClientError


def delete_igw(ec2, vpc_id):
  """
  Detach and delete the internet gateway
  """

  try:
    igw = ec2.describe_internet_gateways(
            Filters = [
              {
                'Name' : 'attachment.vpc-id',
                'Values' : [ vpc_id ]
              }
            ]
          )['InternetGateways']
  except ClientError as e:
    print(e.response['Error']['Message'])

  if igw:
    igw_id = igw[0]['InternetGatewayId']

    try:
      ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    except ClientError as e:
      print(e.response['Error']['Message'])

    try:
      ec2.delete_internet_gateway(InternetGatewayId=igw_id)
    except ClientError as e:
      print(e.response['Error']['Message'])

  return


def delete_subs(ec2, vpc_id):
  """
  Delete the subnets
  """

  try:
    subs = ec2.describe_subnets(
             Filters = [
               {
                 'Name' : 'vpc-id',
                 'Values' : [ vpc_id ]
               }
             ]
           )['Subnets']
  except ClientError as e:
    print(e.response['Error']['Message'])

  if subs:
    for sub in subs:
      sub_id = sub['SubnetId']

      try:
        ec2.delete_subnet(SubnetId=sub_id)
      except ClientError as e:
        print(e.response['Error']['Message'])

  return


def delete_rtbs(ec2, vpc_id):
  """
  Delete the route tables
  """

  try:
    rtbs = ec2.describe_route_tables(
             Filters = [
               {
                 'Name' : 'vpc-id',
                 'Values' : [ vpc_id ]
               }
             ]
           )['RouteTables']
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
        ec2.delete_route_table(RouteTableId=rtb_id)
      except ClientError as e:
        print(e.response['Error']['Message'])

  return


def delete_acls(ec2, vpc_id):
  """
  Delete the network access lists (NACLs)
  """

  try:
    acls = ec2.describe_network_acls(
             Filters = [
               {
                 'Name' : 'vpc-id',
                 'Values' : [ vpc_id ]
               }
             ]
           )['NetworkAcls']
  except ClientError as e:
    print(e.response['Error']['Message'])

  if acls:
    for acl in acls:
      default = acl['IsDefault']
      if default == True:
        continue
      acl_id = acl['NetworkAclId']

      try:
        ec2.delete_network_acl(NetworkAclId=acl_id)
      except ClientError as e:
        print(e.response['Error']['Message'])

  return


def delete_sgps(ec2, vpc_id):
  """
  Delete any security groups
  """

  try:
    sgps = ec2.describe_security_groups(
             Filters = [
               {
                 'Name' : 'vpc-id',
                 'Values' : [ vpc_id ]
               }
             ]
           )['SecurityGroups']
  except ClientError as e:
    print(e.response['Error']['Message'])

  if sgps:
    for sgp in sgps:
      default = sgp['GroupName']
      if default == 'default':
        continue
      sg_id = sgp['GroupId']

      try:
        ec2.delete_security_group(GroupId=sg_id)
      except ClientError as e:
        print(e.response['Error']['Message'])

  return


def delete_vpc(ec2, vpc_id, region):
  """
  Delete the VPC
  """

  try:
    ec2.delete_vpc(VpcId=vpc_id)
  except ClientError as e:
    print(e.response['Error']['Message'])

  else:
    print('VPC {} has been deleted from the {} region.'.format(vpc_id, region))

  return


def main(profile, region):
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

  # AWS Credentials
  # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
  #
  session = boto3.Session(profile_name=profile)
  ec2  = session.client('ec2', region_name=region)

  try:
    attribs = ec2.describe_account_attributes(AttributeNames=[ 'default-vpc' ])['AccountAttributes']
  except ClientError as e:
    print(e.response['Error']['Message'])
    return

  else:
    vpc_id = attribs[0]['AttributeValues'][0]['AttributeValue']

  if vpc_id == 'none':
    print('A default VPC was not found in the {} region.'.format(region))
    return

  # Are there any existing resources?  Since most resources attach an ENI, let's check..
  try:
    eni = ec2.describe_network_interfaces(
            Filters = [
              {
                'Name': 'vpc-id',
                'Values': [ vpc_id ]
              }
            ]
          )['NetworkInterfaces']
  except ClientError as e:
    print(e.response['Error']['Message'])
    return

  if eni:
    print('VPC {} has existing resources.'.format(vpc_id))
    return

  result = delete_igw(ec2, vpc_id)
  result = delete_subs(ec2, vpc_id)
  result = delete_rtbs(ec2, vpc_id)
  result = delete_acls(ec2, vpc_id)
  result = delete_sgps(ec2, vpc_id)
  result = delete_vpc(ec2, vpc_id, region)

  return


if __name__ == "__main__":

  main(profile = 'My_AWS_Profile', region = 'us-west-2')

