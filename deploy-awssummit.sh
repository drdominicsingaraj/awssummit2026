#!/bin/bash

echo "=== S3 Static Website CloudFormation Deployment ==="
echo "AWS Summit Hamburg Project"
echo "Using Git Bash terminal"
echo "Region: eu-central-1"
echo "Bucket: nfspdominicawssummit-website"
echo "Stack: nfspdominicawssummit-website-stack"
echo ""

echo "Step 1: Validating CloudFormation template..."
aws cloudformation validate-template --template-body file://s3-static-website.yaml --region eu-central-1

echo ""
echo "Step 2: Deploying CloudFormation stack..."
aws cloudformation create-stack \
    --stack-name nfspdominicawssummit-website-stack \
    --template-body file://s3-static-website.yaml \
    --parameters ParameterKey=BucketName,ParameterValue=nfspdominicawssummit-website \
    --region eu-central-1

echo ""
echo "Step 3: Checking initial deployment status..."
sleep 5
aws cloudformation describe-stacks \
    --stack-name nfspdominicawssummit-website-stack \
    --query 'Stacks[0].StackStatus' \
    --output text \
    --region eu-central-1

echo ""
echo "Deployment initiated! Monitor progress with:"
echo "aws cloudformation describe-stacks --stack-name nfspdominicawssummit-website-stack --region eu-central-1"
echo ""
echo "Get website URL after deployment completes:"
echo "aws cloudformation describe-stacks --stack-name nfspdominicawssummit-website-stack --query 'Stacks[0].Outputs[?OutputKey==\`WebsiteURL\`].OutputValue' --output text --region eu-central-1"