#!/usr/bin/env python3
"""
CloudFormation template validation script
"""

import yaml
import json
import re

def validate_yaml_syntax():
    """Validate YAML syntax by parsing with CloudFormation function support"""
    try:
        with open('s3-static-website.yaml', 'r') as f:
            content = f.read()
        
        # Replace CloudFormation intrinsic functions for YAML parsing
        content = re.sub(r'!Ref\s+(\w+)', r'"!Ref \1"', content)
        content = re.sub(r'!Sub\s+(.+)', r'"!Sub \1"', content)
        content = re.sub(r'!GetAtt\s+([\w.]+)', r'"!GetAtt \1"', content)
        
        template = yaml.safe_load(content)
        print("✅ YAML syntax is valid")
        return template
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return None

def validate_cloudformation_structure(template):
    """Validate CloudFormation template structure"""
    if not template:
        return False
    
    # Check required sections
    required_sections = ['AWSTemplateFormatVersion', 'Description', 'Parameters', 'Resources', 'Outputs']
    for section in required_sections:
        if section not in template:
            print(f"❌ Missing required section: {section}")
            return False
    
    print("✅ All required sections present")
    
    # Validate AWSTemplateFormatVersion
    if template['AWSTemplateFormatVersion'] != '2010-09-09':
        print(f"❌ Invalid AWSTemplateFormatVersion: {template['AWSTemplateFormatVersion']}")
        return False
    
    print("✅ Valid AWSTemplateFormatVersion")
    
    # Validate Parameters
    parameters = template.get('Parameters', {})
    required_params = ['BucketName', 'IndexDocument', 'ErrorDocument']
    for param in required_params:
        if param not in parameters:
            print(f"❌ Missing required parameter: {param}")
            return False
        
        param_def = parameters[param]
        if 'Type' not in param_def:
            print(f"❌ Parameter {param} missing Type")
            return False
        
        if 'Description' not in param_def:
            print(f"❌ Parameter {param} missing Description")
            return False
    
    print("✅ All required parameters present and valid")
    
    # Validate Resources
    resources = template.get('Resources', {})
    required_resources = ['S3Bucket', 'S3BucketPolicy']
    for resource in required_resources:
        if resource not in resources:
            print(f"❌ Missing required resource: {resource}")
            return False
        
        resource_def = resources[resource]
        if 'Type' not in resource_def:
            print(f"❌ Resource {resource} missing Type")
            return False
        
        if 'Properties' not in resource_def:
            print(f"❌ Resource {resource} missing Properties")
            return False
    
    print("✅ All required resources present and valid")
    
    # Validate S3 Bucket resource
    s3_bucket = resources['S3Bucket']
    if s3_bucket['Type'] != 'AWS::S3::Bucket':
        print(f"❌ S3Bucket has incorrect type: {s3_bucket['Type']}")
        return False
    
    bucket_props = s3_bucket['Properties']
    required_bucket_props = ['BucketName', 'WebsiteConfiguration', 'PublicAccessBlockConfiguration']
    for prop in required_bucket_props:
        if prop not in bucket_props:
            print(f"❌ S3Bucket missing property: {prop}")
            return False
    
    print("✅ S3Bucket resource properly configured")
    
    # Validate S3 Bucket Policy resource
    bucket_policy = resources['S3BucketPolicy']
    if bucket_policy['Type'] != 'AWS::S3::BucketPolicy':
        print(f"❌ S3BucketPolicy has incorrect type: {bucket_policy['Type']}")
        return False
    
    policy_props = bucket_policy['Properties']
    if 'Bucket' not in policy_props or 'PolicyDocument' not in policy_props:
        print("❌ S3BucketPolicy missing required properties")
        return False
    
    print("✅ S3BucketPolicy resource properly configured")
    
    # Validate Outputs
    outputs = template.get('Outputs', {})
    required_outputs = ['WebsiteURL', 'BucketWebsiteConfiguration', 'BucketName']
    for output in required_outputs:
        if output not in outputs:
            print(f"❌ Missing required output: {output}")
            return False
        
        output_def = outputs[output]
        if 'Description' not in output_def or 'Value' not in output_def:
            print(f"❌ Output {output} missing Description or Value")
            return False
    
    print("✅ All required outputs present and valid")
    
    return True

def validate_parameter_constraints():
    """Validate parameter constraints and patterns"""
    with open('s3-static-website.yaml', 'r') as f:
        content = f.read()
    
    # Check bucket name pattern
    if 'AllowedPattern:' not in content:
        print("❌ Missing AllowedPattern constraints")
        return False
    
    # Check for proper regex patterns
    bucket_pattern = r'\^[a-z0-9][a-z0-9-]*[a-z0-9]\$\|\^[a-z0-9]\$'
    html_pattern = r'\^[a-zA-Z0-9._-]+\.\(html\|htm\)\$'
    
    # Remove spaces and check patterns
    content_clean = content.replace(' ', '').replace('\n', '')
    
    if '^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$' not in content:
        print("❌ Invalid bucket name pattern")
        return False
    
    if '^[a-zA-Z0-9._-]+\.(html|htm)$' not in content:
        print("❌ Invalid HTML file pattern")
        return False
    
    print("✅ Parameter constraints properly defined")
    return True

def main():
    print("🔍 Validating CloudFormation template: s3-static-website.yaml")
    print("=" * 60)
    
    # Step 1: Validate YAML syntax
    template = validate_yaml_syntax()
    if not template:
        return False
    
    # Step 2: Validate CloudFormation structure
    if not validate_cloudformation_structure(template):
        return False
    
    # Step 3: Validate parameter constraints
    if not validate_parameter_constraints():
        return False
    
    print("=" * 60)
    print("🎉 Template validation completed successfully!")
    print("✅ YAML syntax is valid")
    print("✅ CloudFormation template structure is correct")
    print("✅ All resources are properly defined")
    print("✅ Parameters and outputs are correctly formatted")
    print("✅ Parameter constraints are properly configured")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)