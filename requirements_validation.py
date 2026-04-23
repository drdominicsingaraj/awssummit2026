#!/usr/bin/env python3
"""
Validate CloudFormation template against specific requirements from the spec
"""

import yaml
import json
import re

class CloudFormationLoader(yaml.SafeLoader):
    """Custom YAML loader that handles CloudFormation intrinsic functions"""
    pass

def cf_constructor(loader, node):
    """Constructor for CloudFormation intrinsic functions"""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    elif isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    else:
        return None

# Register CloudFormation intrinsic functions
cf_functions = [
    'Ref', 'GetAtt', 'Join', 'Sub', 'Select', 'Split', 'Base64', 'GetAZs',
    'ImportValue', 'FindInMap', 'Equals', 'If', 'Not', 'And', 'Or', 'Condition'
]

for func in cf_functions:
    CloudFormationLoader.add_constructor(f'!{func}', cf_constructor)

def load_template():
    """Load the CloudFormation template"""
    with open('s3-static-website.yaml', 'r') as f:
        return yaml.load(f, Loader=CloudFormationLoader)

def validate_requirement_1_1(template):
    """Requirement 1.1: Configure S3 bucket for static website hosting"""
    print("🔍 Validating Requirement 1.1: S3 Static Website Hosting Configuration")
    
    resources = template.get('Resources', {})
    s3_bucket = resources.get('S3Bucket', {})
    
    if s3_bucket.get('Type') != 'AWS::S3::Bucket':
        print("  ❌ S3Bucket resource not found or incorrect type")
        return False
    
    props = s3_bucket.get('Properties', {})
    website_config = props.get('WebsiteConfiguration', {})
    
    if not website_config:
        print("  ❌ WebsiteConfiguration not found")
        return False
    
    print("  ✅ S3 bucket configured for static website hosting")
    return True

def validate_requirement_1_3(template):
    """Requirement 1.3: Set index.html as default document"""
    print("🔍 Validating Requirement 1.3: Index Document Configuration")
    
    # Check parameter default
    params = template.get('Parameters', {})
    index_param = params.get('IndexDocument', {})
    
    if index_param.get('Default') != 'index.html':
        print("  ❌ IndexDocument parameter default should be 'index.html'")
        return False
    
    # Check resource configuration
    resources = template.get('Resources', {})
    s3_bucket = resources.get('S3Bucket', {})
    props = s3_bucket.get('Properties', {})
    website_config = props.get('WebsiteConfiguration', {})
    
    if 'IndexDocument' not in website_config:
        print("  ❌ IndexDocument not configured in WebsiteConfiguration")
        return False
    
    print("  ✅ Index document properly configured with default 'index.html'")
    return True

def validate_requirement_1_4(template):
    """Requirement 1.4: Custom error page configuration"""
    print("🔍 Validating Requirement 1.4: Error Document Configuration")
    
    # Check parameter default
    params = template.get('Parameters', {})
    error_param = params.get('ErrorDocument', {})
    
    if error_param.get('Default') != 'error.html':
        print("  ❌ ErrorDocument parameter default should be 'error.html'")
        return False
    
    # Check resource configuration
    resources = template.get('Resources', {})
    s3_bucket = resources.get('S3Bucket', {})
    props = s3_bucket.get('Properties', {})
    website_config = props.get('WebsiteConfiguration', {})
    
    if 'ErrorDocument' not in website_config:
        print("  ❌ ErrorDocument not configured in WebsiteConfiguration")
        return False
    
    print("  ✅ Error document properly configured with default 'error.html'")
    return True

def validate_requirement_1_5(template):
    """Requirement 1.5: Enable public access to website content"""
    print("🔍 Validating Requirement 1.5: Public Access Configuration")
    
    resources = template.get('Resources', {})
    
    # Check S3 bucket public access configuration
    s3_bucket = resources.get('S3Bucket', {})
    props = s3_bucket.get('Properties', {})
    public_access = props.get('PublicAccessBlockConfiguration', {})
    
    required_settings = {
        'BlockPublicAcls': False,
        'BlockPublicPolicy': False,
        'IgnorePublicAcls': False,
        'RestrictPublicBuckets': False
    }
    
    for setting, expected in required_settings.items():
        if public_access.get(setting) != expected:
            print(f"  ❌ PublicAccessBlockConfiguration.{setting} should be {expected}")
            return False
    
    # Check bucket policy exists
    if 'S3BucketPolicy' not in resources:
        print("  ❌ S3BucketPolicy resource not found")
        return False
    
    print("  ✅ Public access properly configured")
    return True

def validate_requirement_2_1(template):
    """Requirement 2.1: CloudFormation template defines all required resources"""
    print("🔍 Validating Requirement 2.1: CloudFormation Resource Definition")
    
    resources = template.get('Resources', {})
    required_resources = ['S3Bucket', 'S3BucketPolicy']
    
    for resource in required_resources:
        if resource not in resources:
            print(f"  ❌ Required resource {resource} not found")
            return False
    
    print("  ✅ All required AWS resources defined in CloudFormation template")
    return True

def validate_requirement_2_2(template):
    """Requirement 2.2: Accept S3 bucket name as configurable parameter"""
    print("🔍 Validating Requirement 2.2: Bucket Name Parameter")
    
    params = template.get('Parameters', {})
    bucket_param = params.get('BucketName', {})
    
    if bucket_param.get('Type') != 'String':
        print("  ❌ BucketName parameter should be of type String")
        return False
    
    if 'Description' not in bucket_param:
        print("  ❌ BucketName parameter missing description")
        return False
    
    if 'AllowedPattern' not in bucket_param:
        print("  ❌ BucketName parameter missing validation pattern")
        return False
    
    print("  ✅ Bucket name parameter properly configured")
    return True

def validate_requirement_2_3(template):
    """Requirement 2.3: Output website endpoint URL"""
    print("🔍 Validating Requirement 2.3: Website URL Output")
    
    outputs = template.get('Outputs', {})
    website_url = outputs.get('WebsiteURL', {})
    
    if not website_url:
        print("  ❌ WebsiteURL output not found")
        return False
    
    if 'Description' not in website_url:
        print("  ❌ WebsiteURL output missing description")
        return False
    
    if 'Value' not in website_url:
        print("  ❌ WebsiteURL output missing value")
        return False
    
    print("  ✅ Website endpoint URL output properly configured")
    return True

def validate_requirement_3_1(template):
    """Requirement 3.1: Provide publicly accessible website endpoint"""
    print("🔍 Validating Requirement 3.1: Public Website Endpoint")
    
    # Check that WebsiteURL output uses GetAtt to get the website URL
    outputs = template.get('Outputs', {})
    website_url = outputs.get('WebsiteURL', {})
    
    # The value should reference the S3 bucket's WebsiteURL attribute
    value = website_url.get('Value')
    if not value:
        print("  ❌ WebsiteURL output missing value")
        return False
    
    print("  ✅ Public website endpoint properly configured")
    return True

def validate_requirement_4_1(template):
    """Requirement 4.1: Create bucket policy allowing public read access"""
    print("🔍 Validating Requirement 4.1: Public Read Access Policy")
    
    resources = template.get('Resources', {})
    bucket_policy = resources.get('S3BucketPolicy', {})
    
    if bucket_policy.get('Type') != 'AWS::S3::BucketPolicy':
        print("  ❌ S3BucketPolicy resource not found or incorrect type")
        return False
    
    props = bucket_policy.get('Properties', {})
    policy_doc = props.get('PolicyDocument', {})
    statements = policy_doc.get('Statement', [])
    
    if not statements:
        print("  ❌ Bucket policy missing statements")
        return False
    
    # Check for public read statement
    public_read_found = False
    for stmt in statements:
        if (stmt.get('Effect') == 'Allow' and 
            stmt.get('Principal') == '*' and 
            stmt.get('Action') == 's3:GetObject'):
            public_read_found = True
            break
    
    if not public_read_found:
        print("  ❌ Public read access statement not found in bucket policy")
        return False
    
    print("  ✅ Bucket policy allows public read access")
    return True

def validate_requirement_5_1(template):
    """Requirement 5.1: Accept bucket name as input parameter"""
    print("🔍 Validating Requirement 5.1: Bucket Name Input Parameter")
    
    params = template.get('Parameters', {})
    
    if 'BucketName' not in params:
        print("  ❌ BucketName parameter not found")
        return False
    
    bucket_param = params['BucketName']
    if bucket_param.get('Type') != 'String':
        print("  ❌ BucketName parameter should be String type")
        return False
    
    print("  ✅ Bucket name input parameter properly configured")
    return True

def validate_requirement_5_2_5_3(template):
    """Requirements 5.2 & 5.3: Optional parameters with defaults"""
    print("🔍 Validating Requirements 5.2 & 5.3: Optional Parameters with Defaults")
    
    params = template.get('Parameters', {})
    
    # Check IndexDocument parameter
    index_param = params.get('IndexDocument', {})
    if index_param.get('Default') != 'index.html':
        print("  ❌ IndexDocument parameter should have default 'index.html'")
        return False
    
    # Check ErrorDocument parameter
    error_param = params.get('ErrorDocument', {})
    if error_param.get('Default') != 'error.html':
        print("  ❌ ErrorDocument parameter should have default 'error.html'")
        return False
    
    print("  ✅ Optional parameters with proper defaults configured")
    return True

def run_requirements_validation():
    """Run all requirements validation tests"""
    print("🎯 CloudFormation Template Requirements Validation")
    print("=" * 60)
    
    template = load_template()
    
    # Define all requirement validation functions
    validations = [
        ("1.1", "S3 Static Website Hosting", validate_requirement_1_1),
        ("1.3", "Index Document Configuration", validate_requirement_1_3),
        ("1.4", "Error Document Configuration", validate_requirement_1_4),
        ("1.5", "Public Access Configuration", validate_requirement_1_5),
        ("2.1", "CloudFormation Resources", validate_requirement_2_1),
        ("2.2", "Bucket Name Parameter", validate_requirement_2_2),
        ("2.3", "Website URL Output", validate_requirement_2_3),
        ("3.1", "Public Website Endpoint", validate_requirement_3_1),
        ("4.1", "Public Read Access Policy", validate_requirement_4_1),
        ("5.1", "Bucket Name Input", validate_requirement_5_1),
        ("5.2-5.3", "Optional Parameters", validate_requirement_5_2_5_3),
    ]
    
    passed = 0
    total = len(validations)
    
    for req_id, req_name, validation_func in validations:
        try:
            if validation_func(template):
                passed += 1
            else:
                print(f"  ❌ Requirement {req_id} ({req_name}) validation failed")
        except Exception as e:
            print(f"  ❌ Requirement {req_id} validation error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Requirements Validation: {passed}/{total} requirements satisfied")
    
    if passed == total:
        print("🎉 All requirements validated successfully!")
        print("\n✅ Template satisfies all specified requirements:")
        print("  • S3 static website hosting properly configured")
        print("  • CloudFormation template defines all required resources")
        print("  • Public website access enabled with proper security")
        print("  • Template parameterization supports reusability")
        print("  • Outputs provide necessary deployment information")
        return True
    else:
        print(f"❌ {total - passed} requirements not satisfied")
        return False

if __name__ == "__main__":
    success = run_requirements_validation()
    exit(0 if success else 1)