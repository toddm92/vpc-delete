"""

Remove those pesky AWS default VPCs.

Python Version: 3.7.0
Boto3 Version: 1.7.50

"""

import concurrent.futures
import sys

import boto3
from botocore.exceptions import ClientError
import traceback


def delete_igw(ec2, vpc_id):
    """
    Detach and delete the internet gateway
    """

    args = {"Filters": [{"Name": "attachment.vpc-id", "Values": [vpc_id]}]}
    igws = ec2.describe_internet_gateways(**args)["InternetGateways"]

    for igw in igws:
        igw_id = igw["InternetGatewayId"]

        ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        ec2.delete_internet_gateway(InternetGatewayId=igw_id)


def delete_subs(ec2, args):
    """
    Delete the subnets
    """

    subs = ec2.describe_subnets(**args)["Subnets"]

    for sub in subs:
        sub_id = sub["SubnetId"]
        ec2.delete_subnet(SubnetId=sub_id)


def delete_rtbs(ec2, args):
    """
    Delete the route tables
    """

    rtbs = ec2.describe_route_tables(**args)["RouteTables"]

    if rtbs:
        for rtb in rtbs:
            main = False
            for assoc in rtb["Associations"]:
                main = assoc["Main"]
                if not main:
                    rtb_id = rtb["RouteTableId"]
                    ec2.delete_route_table(RouteTableId=rtb_id)


def delete_acls(ec2, args):
    """
    Delete the network access lists (NACLs)
    """

    acls = ec2.describe_network_acls(**args)["NetworkAcls"]

    for acl in acls:
        is_default = acl["IsDefault"]
        if not is_default:
            acl_id = acl["NetworkAclId"]
            ec2.delete_network_acl(NetworkAclId=acl_id)
            break


def delete_sgps(ec2, args):
    """
    Delete any security groups
    """

    sgps = ec2.describe_security_groups(**args)["SecurityGroups"]

    if sgps:
        for sgp in sgps:
            default = sgp["GroupName"]
            if default == "default":
                continue
            sg_id = sgp["GroupId"]
            ec2.delete_security_group(GroupId=sg_id)


def delete_vpc(ec2, vpc_id, region):
    """
    Delete the VPC
    """

    ec2.delete_vpc(VpcId=vpc_id)
    print(f"VPC {vpc_id} has been deleted from the {region} region.")


def get_regions(ec2):
    """
    Return all AWS regions
    """

    aws_regions = ec2.describe_regions()["Regions"]
    return [region["RegionName"] for region in aws_regions]


def process_region(region):
    ec2 = boto3.Session().client("ec2", region_name=region)

    try:
        attribs = ec2.describe_account_attributes(AttributeNames=["default-vpc"])
    except ClientError as e:
        # this can happen with e.g. SCPs preventing access to a particular region:
        raise RuntimeError(
            "Unable to query VPCs in {}: {}".format(
                region, e.response["Error"]["Message"]
            )
        ) from e

    assert 1 == len(attribs["AccountAttributes"])
    vpc_id = attribs["AccountAttributes"][0]["AttributeValues"][0]["AttributeValue"]

    if vpc_id == "none":
        raise RuntimeError(f"Default VPC was not found in the {region} region.")

    # Are there any existing resources?  Since most resources attach an ENI, let's check..

    args = {"Filters": [{"Name": "vpc-id", "Values": [vpc_id]}]}
    eni = ec2.describe_network_interfaces(**args)["NetworkInterfaces"]

    if eni:
        print(f"VPC {vpc_id} has existing resources in the {region} region.")
    else:
        print(f"Deleting unused VPC {vpc_id} in the {region} region.")
        delete_igw(ec2, vpc_id)
        delete_subs(ec2, args)
        delete_rtbs(ec2, args)
        delete_acls(ec2, args)
        delete_sgps(ec2, args)
        delete_vpc(ec2, vpc_id, region)


def main():
    """
    Do the work..

    Order of operation:

    1.) Confirm that the VPC has no allocated network interfaces
    2.) Delete the internet gateway
    3.) Delete subnets
    4.) Delete route tables
    5.) Delete network access lists
    6.) Delete security groups
    7.) Delete the VPC
    """

    # AWS Credentials
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

    session = boto3.Session()
    ec2 = session.client("ec2", region_name="us-east-1")

    regions = get_regions(ec2)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(process_region, region): region for region in regions
        }
        for future in concurrent.futures.as_completed(futures):
            region = futures[future]

            try:
                future.result()
            except Exception as exc:
                print(f"Error processing {region}: {exc}", file=sys.stderr)
                if not isinstance(exc, (ClientError, RuntimeError)):
                    traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    main()
