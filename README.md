# S3 Static Website CloudFormation

A comprehensive AWS CloudFormation solution for deploying static websites on Amazon S3 with automated infrastructure provisioning, multi-environment support, and robust validation testing.

## 🌟 Overview

This repository provides a production-ready CloudFormation template that creates and configures an S3 bucket for static website hosting. The solution includes comprehensive deployment scripts, validation tools, and testing frameworks to ensure reliable infrastructure deployment.

**Featured Content**: Dr. Dominic Singaraj's professional portfolio - showcasing expertise in cloud architecture, AI strategy, and AWS advocacy.

## 🚀 Features
<!--  -->
- **Multi-Environment Support**: Deploy to dev, test, staging, prod, or demo environments
- **Parameterized Configuration**: Flexible bucket naming, custom index/error documents
- **Security Best Practices**: Least-privilege access policies and proper public access configuration
- **Comprehensive Validation**: Template syntax validation, security checks, and functional testing
- **Resource Tagging**: Environment-specific tagging for cost tracking and organization
- **Optional Versioning**: S3 bucket versioning support for content management

## 📁 Repository Structure

```
├── s3-static-website.yaml          # Main CloudFormation template
├── kiro-wordpress-stack.yaml       # Alternative WordPress deployment
├── index.html                      # Sample website content
├── Error.html                      # Custom error page
├── deploy.sh                       # Deployment automation script
├── DEPLOYMENT.md                   # Comprehensive deployment guide
├── validation_report.md            # Template validation results
├── INTEGRATION_SUMMARY.md          # Integration testing summary
├── .kiro/specs/                    # Project specifications
│   └── s3-static-website-cloudformation/
│       ├── requirements.md         # Project requirements
│       ├── design.md              # Technical design
│       └── tasks.md               # Implementation tasks
└── test_*.py                      # Validation and testing scripts
```

## 🛠️ Quick Start

### Prerequisites

- AWS CLI installed and configured
- AWS account with appropriate IAM permissions
- Unique S3 bucket name (globally unique across all AWS accounts)

### Basic Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd s3-static-website-cloudformation
   ```

2. **Deploy the CloudFormation stack**
   ```bash
   aws cloudformation create-stack \
     --stack-name my-static-website \
     --template-body file://s3-static-website.yaml \
     --parameters ParameterKey=BucketName,ParameterValue=my-unique-bucket-name-2024
   ```

3. **Upload your website content**
   ```bash
   aws s3 sync ./website-content/ s3://my-unique-bucket-name-2024/
   ```

4. **Get your website URL**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name my-static-website \
     --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
     --output text
   ```

## 📋 Template Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `BucketName` | String | *Required* | Globally unique S3 bucket name |
| `Environment` | String | `dev` | Environment (dev, test, staging, prod, demo) |
| `ProjectName` | String | `static-website` | Project name for tagging |
| `IndexDocument` | String | `index.html` | Default index document |
| `ErrorDocument` | String | `error.html` | Custom error page |
| `EnableVersioning` | String | `false` | Enable S3 bucket versioning |
| `CostCenter` | String | *(Optional)* | Cost center for billing tracking |

## 🔧 Advanced Configuration

### Multi-Environment Deployment

Deploy to different environments with environment-specific configurations:

```bash
# Development environment
aws cloudformation create-stack \
  --stack-name dev-website \
  --template-body file://s3-static-website.yaml \
  --parameters \
    ParameterKey=BucketName,ParameterValue=dev-myapp-website-2024 \
    ParameterKey=Environment,ParameterValue=dev \
    ParameterKey=ProjectName,ParameterValue=MyApp

# Production environment
aws cloudformation create-stack \
  --stack-name prod-website \
  --template-body file://s3-static-website.yaml \
  --parameters \
    ParameterKey=BucketName,ParameterValue=prod-myapp-website-2024 \
    ParameterKey=Environment,ParameterValue=prod \
    ParameterKey=EnableVersioning,ParameterValue=true
```

### Custom Documents

Configure custom index and error documents:

```bash
aws cloudformation create-stack \
  --stack-name custom-website \
  --template-body file://s3-static-website.yaml \
  --parameters \
    ParameterKey=BucketName,ParameterValue=custom-site-2024 \
    ParameterKey=IndexDocument,ParameterValue=main.html \
    ParameterKey=ErrorDocument,ParameterValue=404.html
```

## 🧪 Testing & Validation

The repository includes comprehensive testing tools:

### Template Validation
```bash
# Validate CloudFormation template syntax
aws cloudformation validate-template --template-body file://s3-static-website.yaml

# Run custom validation scripts
python validate_template.py
python validate_cf_template.py
```

### Functional Testing
```bash
# Test deployment scenarios
python test_deployment_scenarios.py

# Integration testing
python integration_test.py

# Multi-environment testing
python test_multi_environment.py
```

### Deployment Readiness Check
```bash
python deployment_readiness_check.py
```

## 📊 Outputs

The CloudFormation stack provides the following outputs:

- **WebsiteURL**: Complete S3 website endpoint URL
- **BucketName**: Name of the created S3 bucket
- **BucketWebsiteConfiguration**: Website configuration status
- **Environment**: Deployment environment
- **ProjectName**: Associated project name
- **BucketDomainName**: S3 bucket domain name
- **VersioningStatus**: Bucket versioning status

## 🔒 Security

The template implements security best practices:

- **Least-Privilege Access**: Bucket policy grants only `s3:GetObject` permissions
- **Public Access Configuration**: Properly configured for website hosting
- **Parameter Validation**: Input constraints prevent invalid configurations
- **Resource Tagging**: Comprehensive tagging for security and compliance

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Comprehensive deployment guide with troubleshooting
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)**: Integration testing results
- **[validation_report.md](validation_report.md)**: Template validation report
- **[.kiro/specs/](/.kiro/specs/s3-static-website-cloudformation/)**: Detailed project specifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 About the Author

**Dr. Dominic Singaraj** - Principal Cloud Development Coach | AI Strategist | AWS Advocate

- 🌐 AWS One Stop Shop Community Founder
- 🎓 MIT Executive Program: AI - Business Strategy Graduate
- 🏢 Principal Cloud Development Coach at Neuefische GmbH
- 📚 AWS re/Start Program Leader

Connect with Dr. Dominic:
- LinkedIn: [Dr. Dominic Singaraj](https://linkedin.com/in/dominicsingaraj)
- Community: [AWS One Stop Shop](https://awsonestopshop.com)

## 🆘 Support

For support and questions:

1. Check the [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
2. Review existing [Issues](../../issues)
3. Create a new issue with detailed information
4. Join the AWS One Stop Shop Community for cloud architecture discussions

## 🏷️ Tags

`aws` `cloudformation` `s3` `static-website` `infrastructure-as-code` `devops` `cloud` `website-hosting` `aws-s3` `iac`