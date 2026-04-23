#!/usr/bin/env python3
"""
Comprehensive CloudFormation Template Validation for S3 Static Website
Task 9: Final checkpoint - Complete deployment verification
"""

import yaml
import json
import re
import sys
from typing import Dict, List, Any

def validate_template_structure(template: Dict[str, Any]) -> List[str]:
    """Validate basic CloudFormation template structure"""
    issues = []
    
    # Required sections
    required_sections = ['AWSTemplateFormatVersion', 'Parameters', 'Resources', 'Outputs']
    for section in required_sections:
        if section not in template:
            issues.append(f"Missing required section: {section}")
    
    # Check template version
    if template.get('AWSTemplateFormatVersion') != '2010-09-09':
        issues.append("Invalid AWSTemplateFormatVersion")
    
    return issues

def validate_parameters(parameters: Dict[str, Any]) -> List[str]:
    """Validate template parameters"""
    issues = []
    
    # Required parameters
    required_params = ['BucketName']
    for param in required_params:
        if param not in parameters:
            issues.append(f"Missing required parameter: {param}")
    
    # Check BucketName parameter
    if 'BucketName' in parameters:
        bucket_param = parameters['BucketName']
        if bucket_param.get('Type') != 'String':
            issues.append("BucketName parameter must be of type String")
        if 'AllowedPattern' not in bucket_param:
            issues.append("BucketName parameter missing AllowedPattern constraint")
    
    # Check optional parameters have defaults
    optional_params = ['IndexDocument', 'ErrorDocument']
    for param in optional_params:
        if param in parameters and 'Default' not in parameters[param]:
            issues.append(f"Optional parameter {param} should have a default value")
    
    return issues

def validate_resources(resources: Dict[str, Any]) -> List[str]:
    """Validate template resources"""
    issues = []
    
    # Required resources
    required_resources = ['S3Bucket', 'S3BucketPolicy']
    for resource in required_resources:
        if resource not in resources:
            issues.append(f"Missing required resource: {resource}")
    
    # Validate S3Bucket resource
    if 'S3Bucket' in resources:
        s3_bucket = resources['S3Bucket']
        if s3_bucket.get('Type') != 'AWS::S3::Bucket':
            issues.append("S3Bucket resource must be of type AWS::S3::Bucket")
        
        properties = s3_bucket.get('Properties', {})
        if 'WebsiteConfiguration' not in properties:
            issues.append("S3Bucket missing WebsiteConfiguration")
        if 'PublicAccessBlockConfiguration' not in properties:
            issues.append("S3Bucket missing PublicAccessBlockConfiguration")
    
    # Validate S3BucketPolicy resource
    if 'S3BucketPolicy' in resources:
        bucket_policy = resources['S3BucketPolicy']
        if bucket_policy.get('Type') != 'AWS::S3::BucketPolicy':
            issues.append("S3BucketPolicy resource must be of type AWS::S3::BucketPolicy")
        
        properties = bucket_policy.get('Properties', {})
        if 'PolicyDocument' not in properties:
            issues.append("S3BucketPolicy missing PolicyDocument")
    
    return issues

def validate_outputs(outputs: Dict[str, Any]) -> List[str]:
    """Validate template outputs"""
    issues = []
    
    # Required outputs
    required_outputs = ['WebsiteURL', 'BucketWebsiteConfiguration']
    for output in required_outputs:
        if output not in outputs:
            issues.append(f"Missing required output: {output}")
    
    # Check WebsiteURL output
    if 'WebsiteURL' in outputs:
        website_url = outputs['WebsiteURL']
        if 'Value' not in website_url:
            issues.append("WebsiteURL output missing Value")
        if 'Description' not in website_url:
            issues.append("WebsiteURL output missing Description")
    
    return issues

def validate_requirements_compliance(template: Dict[str, Any]) -> List[str]:
    """Validate compliance with specific requirements"""
    issues = []
    
    # Requirement 1.1: S3 Static Website Hosting
    resources = template.get('Resources', {})
    if 'S3Bucket' in resources:
        s3_bucket = resources['S3Bucket']
        properties = s3_bucket.get('Properties', {})
        website_config = properties.get('WebsiteConfiguration', {})
        
        if 'IndexDocument' not in website_config:
            issues.append("Requirement 1.3: Missing IndexDocument configuration")
        if 'ErrorDocument' not in website_config:
            issues.append("Requirement 1.4: Missing ErrorDocument configuration")
    
    # Requirement 1.5 & 4.1: Public Access
    if 'S3BucketPolicy' in resources:
        bucket_policy = resources['S3BucketPolicy']
        policy_doc = bucket_policy.get('Properties', {}).get('PolicyDocument', {})
        statements = policy_doc.get('Statement', [])
        
        public_read_found = False
        for statement in statements:
            if (statement.get('Effect') == 'Allow' and 
                statement.get('Principal') == '*' and 
                's3:GetObject' in statement.get('Action', [])):
                public_read_found = True
                break
        
        if not public_read_found:
            issues.append("Requirement 1.5/4.1: Missing public read access policy")
    
    # Requirement 2.3: Website URL Output
    outputs = template.get('Outputs', {})
    if 'WebsiteURL' not in outputs:
        issues.append("Requirement 2.3: Missing WebsiteURL output")
    
    return issues

def validate_security_best_practices(template: Dict[str, Any]) -> List[str]:
    """Validate security best practices"""
    issues = []
    
    resources = template.get('Resources', {})
    
    # Check bucket policy is least-privilege
    if 'S3BucketPolicy' in resources:
        bucket_policy = resources['S3BucketPolicy']
        policy_doc = bucket_policy.get('Properties', {}).get('PolicyDocument', {})
        statements = policy_doc.get('Statement', [])
        
        for statement in statements:
            if statement.get('Effect') == 'Allow' and statement.get('Principal') == '*':
                actions = statement.get('Action', [])
                if isinstance(actions, str):
                    actions = [actions]
                
                # Check for overly permissive actions
                dangerous_actions = ['s3:*', 's3:Put*', 's3:Delete*']
                for action in actions:
                    if action in dangerous_actions:
                        issues.append(f"Security: Overly permissive action '{action}' in bucket policy")
    
    return issues

def main():
    """Main validation function"""
    print("🔍 CloudFormation Template Final Validation")
    print("=" * 50)
    
    try:
        # Read the template file
        with open('s3-static-website.yaml', 'r') as f:
            content = f.read()
        
        # Parse YAML (handle CloudFormation functions)
        # Replace CloudFormation intrinsic functions for parsing
        content_for_parsing = content
        content_for_parsing = re.sub(r'!Ref\s+([A-Za-z0-9:_-]+)', r'"REF_\1"', content_for_parsing)
        content_for_parsing = re.sub(r'!Sub\s+([\'"]?)([^\'"\n]+)\1', r'"SUB_PLACEHOLDER"', content_for_parsing)
        content_for_parsing = re.sub(r'!GetAtt\s+([A-Za-z0-9._-]+)', r'"GETATT_PLACEHOLDER"', content_for_parsing)
        content_for_parsing = re.sub(r'!If\s*\[([^\]]+)\]', r'"IF_PLACEHOLDER"', content_for_parsing)
        content_for_parsing = re.sub(r'!Not\s*\[([^\]]+)\]', r'"NOT_PLACEHOLDER"', content_for_parsing)
        content_for_parsing = re.sub(r'!Equals\s*\[([^\]]+)\]', r'"EQUALS_PLACEHOLDER"', content_for_parsing)
        
        template = yaml.safe_load(content_for_parsing)
        
        print("✅ YAML parsing successful")
        
        # Run all validations
        all_issues = []
        
        print("\n📋 Validating template structure...")
        structure_issues = validate_template_structure(template)
        all_issues.extend(structure_issues)
        
        print("📋 Validating parameters...")
        parameter_issues = validate_parameters(template.get('Parameters', {}))
        all_issues.extend(parameter_issues)
        
        print("📋 Validating resources...")
        resource_issues = validate_resources(template.get('Resources', {}))
        all_issues.extend(resource_issues)
        
        print("📋 Validating outputs...")
        output_issues = validate_outputs(template.get('Outputs', {}))
        all_issues.extend(output_issues)
        
        print("📋 Validating requirements compliance...")
        requirements_issues = validate_requirements_compliance(template)
        all_issues.extend(requirements_issues)
        
        print("📋 Validating security best practices...")
        security_issues = validate_security_best_practices(template)
        all_issues.extend(security_issues)
        
        # Report results
        print("\n" + "=" * 50)
        if all_issues:
            print("❌ VALIDATION FAILED")
            print(f"Found {len(all_issues)} issues:")
            for i, issue in enumerate(all_issues, 1):
                print(f"  {i}. {issue}")
            return 1
        else:
            print("✅ VALIDATION PASSED")
            print("All checks completed successfully!")
            
            # Additional verification
            print("\n🎯 Final Verification Summary:")
            print("✅ Template structure is valid")
            print("✅ All required parameters present")
            print("✅ All required resources defined")
            print("✅ All required outputs configured")
            print("✅ Requirements compliance verified")
            print("✅ Security best practices followed")
            print("✅ Template ready for deployment")
            
            return 0
            
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())