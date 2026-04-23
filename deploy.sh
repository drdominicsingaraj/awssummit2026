#!/bin/bash

echo "Deploying CloudFormation stack for S3 static website..."

# Deploy the CloudFormation stack
aws cloudformation create-stack --stack-name nfspdominicdemo-website --template-body file://s3-static-website.yaml --parameters ParameterKey=BucketName,ParameterValue=nfspdominicdemo2827 reon us-east-1

echo ""
echo "Checking deployment status..."

# Check the deployment status
aws cloudformation describe-stacks --stack-name nfspdominicdemo-website --query 'Stacks[0].StackStatus' --region us-east-1

echo ""
echo "Deployment script completed."
echo "You can monitor progress with:"
echo "aws cloudformation describe-stacks --stack-name nfspdominicdemo-website --region us-east-1"