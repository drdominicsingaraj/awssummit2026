# S3 Static Website CloudFormation Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying a static website using Amazon S3 and CloudFormation. The solution configures an S3 bucket for static website hosting with public read access, making your HTML files accessible via a public web endpoint.

## Prerequisites

### AWS Account and Permissions

Before deploying, ensure you have:

1. **AWS Account**: Active AWS account with billing configured
2. **AWS CLI**: Installed and configured with appropriate credentials
3. **IAM Permissions**: Your AWS user/role must have the following permissions:
   - `cloudformation:CreateStack`
   - `cloudformation:UpdateStack`
   - `cloudformation:DeleteStack`
   - `cloudformation:DescribeStacks`
   - `cloudformation:ValidateTemplate`
   - `s3:CreateBucket`
   - `s3:PutBucketWebsite`
   - `s3:PutBucketPolicy`
   - `s3:GetBucketLocation`
   - `s3:ListBucket`

### Required Files

Ensure you have the following files in your deployment directory:
- `s3-static-website.yaml` - The CloudFormation template
- Your website content files (HTML, CSS, JavaScript, images)

### AWS CLI Configuration

Verify your AWS CLI is properly configured:

```bash
aws configure list
aws sts get-caller-identity
```

## Template Parameters

The CloudFormation template accepts the following parameters:

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `BucketName` | String | Name of the S3 bucket to create | `my-static-website-bucket` |

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `IndexDocument` | String | `index.html` | Default document served for directory requests | `home.html` |
| `ErrorDocument` | String | `error.html` | Custom error page for 404 errors | `404.html` |

### Parameter Constraints

- **BucketName**: 
  - Must be 3-63 characters long
  - Must start and end with lowercase letter or number
  - Can contain only lowercase letters, numbers, and hyphens
  - Must be globally unique across all AWS accounts
  - Cannot contain periods or uppercase letters

- **IndexDocument** and **ErrorDocument**:
  - Must be valid HTML file names
  - Must end with `.html` or `.htm` extension
  - Can contain letters, numbers, periods, underscores, and hyphens

## Step-by-Step Deployment Instructions

### Step 1: Validate the CloudFormation Template

Before deployment, validate the template syntax:

```bash
aws cloudformation validate-template \
    --template-body file://s3-static-website.yaml
```

Expected output should show template parameters and capabilities without errors.

### Step 2: Deploy the CloudFormation Stack

Deploy the stack using AWS CLI:

```bash
aws cloudformation create-stack \
    --stack-name my-static-website \
    --template-body file://s3-static-website.yaml \
    --parameters ParameterKey=BucketName,ParameterValue=my-unique-bucket-name-2024 \
    --capabilities CAPABILITY_IAM
```

#### Alternative: Deploy with Custom Parameters

```bash
aws cloudformation create-stack \
    --stack-name my-static-website \
    --template-body file://s3-static-website.yaml \
    --parameters \
        ParameterKey=BucketName,ParameterValue=my-unique-bucket-name-2024 \
        ParameterKey=IndexDocument,ParameterValue=home.html \
        ParameterKey=ErrorDocument,ParameterValue=404.html \
    --capabilities CAPABILITY_IAM
```

### Step 3: Monitor Deployment Progress

Check the deployment status:

```bash
aws cloudformation describe-stacks \
    --stack-name my-static-website \
    --query 'Stacks[0].StackStatus'
```

Wait for the status to change to `CREATE_COMPLETE`. This typically takes 2-5 minutes.

### Step 4: Retrieve Website URL

Once deployment is complete, get the website URL:

```bash
aws cloudformation describe-stacks \
    --stack-name my-static-website \
    --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
    --output text
```

### Step 5: Upload Website Content

Upload your HTML files to the newly created S3 bucket:

```bash
# Upload a single file
aws s3 cp index.html s3://my-unique-bucket-name-2024/

# Upload entire directory
aws s3 sync ./website-content/ s3://my-unique-bucket-name-2024/ --delete

# Upload with public-read ACL (if needed)
aws s3 cp index.html s3://my-unique-bucket-name-2024/ --acl public-read
```

### Step 6: Verify Website Accessibility

Test your website by accessing the URL from Step 4 in a web browser or using curl:

```bash
curl -I http://my-unique-bucket-name-2024.s3-website-us-east-1.amazonaws.com
```

Expected response should show `HTTP/1.1 200 OK` status.

## Parameter Usage Examples

### Basic Deployment

Minimal deployment with default settings:

```bash
aws cloudformation create-stack \
    --stack-name basic-website \
    --template-body file://s3-static-website.yaml \
    --parameters ParameterKey=BucketName,ParameterValue=basic-site-2024
```

### Custom Document Names

Deployment with custom index and error documents:

```bash
aws cloudformation create-stack \
    --stack-name custom-website \
    --template-body file://s3-static-website.yaml \
    --parameters \
        ParameterKey=BucketName,ParameterValue=custom-site-2024 \
        ParameterKey=IndexDocument,ParameterValue=main.html \
        ParameterKey=ErrorDocument,ParameterValue=not-found.html
```

### Development Environment

Deployment for development environment:

```bash
aws cloudformation create-stack \
    --stack-name dev-website \
    --template-body file://s3-static-website.yaml \
    --parameters \
        ParameterKey=BucketName,ParameterValue=dev-myapp-website-2024 \
        ParameterKey=IndexDocument,ParameterValue=index.html \
        ParameterKey=ErrorDocument,ParameterValue=error.html \
    --tags Key=Environment,Value=Development Key=Project,Value=MyApp
```

## Post-Deployment Verification

### 1. Verify Stack Creation

Check that all resources were created successfully:

```bash
aws cloudformation describe-stack-resources \
    --stack-name my-static-website
```

### 2. Test Website Functionality

Perform these verification steps:

**Test Index Document:**
```bash
curl http://your-bucket-name.s3-website-region.amazonaws.com/
```

**Test Error Document:**
```bash
curl http://your-bucket-name.s3-website-region.amazonaws.com/nonexistent-page
```

**Test Direct File Access:**
```bash
curl http://your-bucket-name.s3-website-region.amazonaws.com/index.html
```

### 3. Verify Security Configuration

Check that the bucket policy allows public read access:

```bash
aws s3api get-bucket-policy \
    --bucket your-bucket-name \
    --query Policy \
    --output text | jq .
```

### 4. Test MIME Types

Verify that different file types are served with correct Content-Type headers:

```bash
# Test HTML file
curl -I http://your-bucket-name.s3-website-region.amazonaws.com/index.html

# Test CSS file
curl -I http://your-bucket-name.s3-website-region.amazonaws.com/styles.css

# Test JavaScript file
curl -I http://your-bucket-name.s3-website-region.amazonaws.com/script.js
```

## Stack Management

### Update Stack

To update the stack with new parameters:

```bash
aws cloudformation update-stack \
    --stack-name my-static-website \
    --template-body file://s3-static-website.yaml \
    --parameters \
        ParameterKey=BucketName,ParameterValue=my-unique-bucket-name-2024 \
        ParameterKey=IndexDocument,ParameterValue=new-index.html
```

### Delete Stack

To delete the stack and all resources:

```bash
# First, empty the S3 bucket
aws s3 rm s3://my-unique-bucket-name-2024 --recursive

# Then delete the stack
aws cloudformation delete-stack \
    --stack-name my-static-website
```

**Warning**: Deleting the stack will permanently remove the S3 bucket and all its contents.

## Troubleshooting Common Issues

### Issue 1: Bucket Name Already Exists

**Error Message:**
```
The requested bucket name is not available. The bucket namespace is shared by all users of the system.
```

**Solution:**
- Choose a more unique bucket name
- Add random numbers or your organization name to the bucket name
- Try different combinations until you find an available name

**Example Fix:**
```bash
# Instead of: my-website
# Try: my-website-company-2024-abc123
```

### Issue 2: Access Denied During Deployment

**Error Message:**
```
User: arn:aws:iam::123456789012:user/username is not authorized to perform: s3:CreateBucket
```

**Solution:**
- Verify your AWS credentials have the required IAM permissions
- Contact your AWS administrator to grant necessary permissions
- Ensure you're deploying to the correct AWS region

**Check Permissions:**
```bash
aws iam get-user-policy \
    --user-name your-username \
    --policy-name your-policy-name
```

### Issue 3: Website Returns 403 Forbidden

**Symptoms:**
- Stack deploys successfully
- Website URL returns 403 Forbidden error
- Files exist in the S3 bucket

**Possible Causes and Solutions:**

1. **Missing Index Document:**
   ```bash
   # Upload index.html to bucket root
   aws s3 cp index.html s3://your-bucket-name/
   ```

2. **Incorrect File Permissions:**
   ```bash
   # Set public-read ACL on files
   aws s3 cp index.html s3://your-bucket-name/ --acl public-read
   ```

3. **Bucket Policy Not Applied:**
   ```bash
   # Verify bucket policy exists
   aws s3api get-bucket-policy --bucket your-bucket-name
   ```

### Issue 4: Website Returns 404 Not Found

**Symptoms:**
- Website URL is accessible
- Specific pages return 404 errors
- Error document is not displayed

**Solutions:**

1. **Check File Names:**
   ```bash
   # List all objects in bucket
   aws s3 ls s3://your-bucket-name/ --recursive
   ```

2. **Verify Error Document:**
   ```bash
   # Upload error document
   aws s3 cp error.html s3://your-bucket-name/
   ```

3. **Check URL Structure:**
   - Ensure file paths match exactly (case-sensitive)
   - Use forward slashes for directory separators
   - Remove any trailing spaces in file names

### Issue 5: Stack Creation Fails

**Error Message:**
```
Template format error: Unresolved resource dependencies
```

**Solution:**
- Validate template syntax before deployment
- Check for circular dependencies in template
- Ensure all referenced resources exist

**Validation Command:**
```bash
aws cloudformation validate-template \
    --template-body file://s3-static-website.yaml
```

### Issue 6: Slow Website Loading

**Symptoms:**
- Website loads but very slowly
- Large files take excessive time to download

**Solutions:**

1. **Enable CloudFront (Optional Enhancement):**
   - Consider adding CloudFront distribution for better performance
   - This requires template modification

2. **Optimize Content:**
   ```bash
   # Compress files before upload
   gzip -k *.html *.css *.js
   
   # Upload with appropriate encoding
   aws s3 cp index.html.gz s3://your-bucket-name/index.html \
       --content-encoding gzip \
       --content-type text/html
   ```

### Issue 7: Template Validation Errors

**Common Validation Issues:**

1. **Invalid Parameter Values:**
   ```yaml
   # Ensure parameter values match constraints
   BucketName: my-valid-bucket-name-123  # Valid
   BucketName: My-Invalid-Bucket-Name    # Invalid (uppercase)
   ```

2. **Missing Required Parameters:**
   ```bash
   # Always provide BucketName parameter
   --parameters ParameterKey=BucketName,ParameterValue=your-bucket-name
   ```

## Security Considerations

### Public Access Configuration

The template configures the S3 bucket for public read access. This means:

- **Allowed**: Anyone can read/download files from your website
- **Denied**: Public users cannot upload, modify, or delete files
- **Recommendation**: Only upload content you want to be publicly accessible

### Best Practices

1. **Content Review**: Always review content before uploading to ensure no sensitive information is included

2. **Access Logging**: Consider enabling S3 access logging for monitoring:
   ```bash
   aws s3api put-bucket-logging \
       --bucket your-bucket-name \
       --bucket-logging-status file://logging-config.json
   ```

3. **Versioning**: Enable versioning for content backup:
   ```bash
   aws s3api put-bucket-versioning \
       --bucket your-bucket-name \
       --versioning-configuration Status=Enabled
   ```

## Cost Optimization

### Understanding Costs

S3 static website hosting costs include:
- **Storage**: $0.023 per GB per month (US East 1)
- **Requests**: $0.0004 per 1,000 GET requests
- **Data Transfer**: $0.09 per GB for data transfer out

### Cost Optimization Tips

1. **Compress Files**: Use gzip compression to reduce storage and transfer costs
2. **Optimize Images**: Use appropriate image formats and sizes
3. **Monitor Usage**: Set up CloudWatch billing alerts
4. **Lifecycle Policies**: Configure automatic deletion of old versions

## Advanced Configuration

### Custom Domain Setup

To use a custom domain (requires additional DNS configuration):

1. **Purchase Domain**: Register domain through Route 53 or external registrar
2. **Create CNAME Record**: Point your domain to the S3 website endpoint
3. **SSL Certificate**: Use CloudFront for HTTPS support

### Content Delivery Network (CDN)

For better performance, consider adding CloudFront:

1. **Create Distribution**: Point CloudFront to your S3 website endpoint
2. **Configure Caching**: Set appropriate cache behaviors
3. **SSL Certificate**: Enable HTTPS through CloudFront

## Support and Resources

### AWS Documentation
- [S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [CloudFormation User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/)

### Useful Commands Reference

```bash
# Quick deployment
aws cloudformation create-stack --stack-name site --template-body file://s3-static-website.yaml --parameters ParameterKey=BucketName,ParameterValue=my-site-2024

# Check status
aws cloudformation describe-stacks --stack-name site --query 'Stacks[0].StackStatus'

# Get website URL
aws cloudformation describe-stacks --stack-name site --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' --output text

# Upload content
aws s3 sync ./content/ s3://my-site-2024/

# Test website
curl -I $(aws cloudformation describe-stacks --stack-name site --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' --output text)
```

This deployment guide provides comprehensive instructions for successfully deploying and managing your S3 static website using CloudFormation.