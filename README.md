### Remove AWS Default VPCs

This Python script attempts to delete the AWS default VPC in each region.

**Requirements:**

* Tested with:
   * Python version: 3.7.0
   * Boto3 version: 1.7.50
   * Botocore version: 1.10.50
* Valid AWS API keys/profile

**Setup:**

Update with your AWS profile / credentials.

```
main(profile = '<YOUR_PROFILE>')
```

Details can be found here:
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

**Usage:**

```
python remove-vpc.py
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

**To Do:**

