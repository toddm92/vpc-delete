### Remove AWS Default VPCs

This Python script attempts to delete the AWS default VPC in each region in parallel.

**Requirements:**

* Tested with:
   * Python version: 3.7.0
   * Boto3 version: 1.9.143
   * Botocore version: 1.12.154
* Valid AWS API keys/profile

**Usage:**

```
./remove_vpc.py [profile] [dryrun_bool]
```

**Output:**

```
VPC vpc-0b43a362 has been deleted from the ap-south-1 region.
VPC vpc-b22dd5db has been deleted from the eu-west-3 region.
VPC vpc-74b7551d has been deleted from the eu-west-2 region.
VPC vpc-3f71855a has been deleted from the eu-west-1 region.
VPC vpc-d58e6cbc has been deleted from the ap-northeast-2 region.
VPC (default) was not found in the ap-northeast-1 region.
VPC vpc-4053e625 has been deleted from the sa-east-1 region.
VPC vpc-4c06ea25 has been deleted from the ca-central-1 region.
VPC vpc-7b80631e has been deleted from the ap-southeast-1 region.
VPC vpc-41db3924 has been deleted from the ap-southeast-2 region.
VPC vpc-47ea0b2e has been deleted from the eu-central-1 region.
VPC vpc-1c558e79 has existing resources in the us-east-1 region.
VPC (default) was not found in the us-east-2 region.
VPC (default) was not found in the us-west-1 region.
VPC vpc-1839c57d has existing resources in the us-west-2 region.
```

**References:**

* https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

