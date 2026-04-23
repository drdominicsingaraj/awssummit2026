@echo off
echo Deploying CloudFormation stack for S3 static website...
aws cloudformation create-stack ^
    --stack-name nfspdominicdemo-website ^
    --template-body file://s3-static-website.yaml ^
    --parameters ParameterKey=BucketName,ParameterValue=nfspdominicdemo ^
    --region us-east-1

echo.
echo Checking deployment status...
aws cloudformation describe-stacks ^
    --stack-name nfspdominicdemo-website ^
    --query "Stacks[0].StackStatus" ^
    --region us-east-1

echo.
echo Deployment script completed. Check the output above for results.
pause