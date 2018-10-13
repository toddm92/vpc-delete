### Remove AWS Default VPCs

This Python script attempts to delete the AWS default VPC.

**Requirements:**

* Tested with:
   * Python Version: 3.7.0
   * Boto3 Version: 1.7.50
* Valid AWS API keys/profile

**Setup:**

Update with your AWS profile and the region in which you want to remove the default VPC.

```
main(profile = 'My_AWS_Profile', region = 'us-west-2')
```

More detials can be found here:
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

**Usage:**

```
python remove-vpc.py
```

**Output:**

```
VPC vpc-b5c02adc has been deleted from the us-west-2 region.
```

**To Do:**

