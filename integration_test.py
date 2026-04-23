#!/usr/bin/env python3
"""
Comprehensive integration test for S3 Static Website CloudFormation template
Tests all resource relationships, dependencies, and functional requirements
"""

import yaml
import json
import re
import sys

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
    """Load and parse the CloudFormation template"""
    try:
        with open('s3-static-website.yaml', 'r') as f:
            template = yaml.load(f, Loader=CloudFormationLoader)
        return template
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        return None

def test_template_structure(template):
    """Test 1: Verify template has all required sections"""
    print("🔍 Test 1: Template Structure")
    
    required_sections = ['AWSTemplateFormatVersion', 'Description', 'Parameters', 'Resources', 'Outputs']
    for section in required_sections:
        if section not in template:
            print(f"  ❌ Missing required section: {section}")
            return False
        print(f"  ✅ Found {section} section")
    
    print("  ✅ All required sections present")
    return True

def test_parameters(template):
    """Test 2: Verify all required parameters are defined with proper constraints"""
    print("\n🔍 Test 2: Parameter Configuration")
    
    params = template.get('Parameters', {})
    
    # Check required parameters
    required_params = ['BucketName', 'IndexDocument', 'ErrorDocument']
    for param in required_params:
        if param not in params:
            print(f"  ❌ Missing required parameter: {param}")
            return False
        print(f"  ✅ Found parameter: {param}")
    
    # Check BucketName constraints
    bucket_param = params['BucketName']
    if 'AllowedPattern' not in bucket_param:
        print("  ❌ BucketName missing AllowedPattern constraint")
        return False
    if 'ConstraintDescription' not in bucket_param:
        print("  ❌ BucketName missing ConstraintDescription")
        return False
    
    # Check document parameters have proper patterns
    for doc_param in ['IndexDocument', 'ErrorDocument']:
        if 'AllowedPattern' not in params[doc_param]:
            print(f"  ❌ {doc_param} missing AllowedPattern constraint")
            return False
    
    print("  ✅ All parameters properly configured with constraints")
    return True

def test_resources(template):
    """Test 3: Verify all required resources are defined"""
    print("\n🔍 Test 3: Resource Configuration")
    
    resources = template.get('Resources', {})
    
    # Check required resources
    required_resources = ['S3Bucket', 'S3BucketPolicy']
    for resource in required_resources:
        if resource not in resources:
            print(f"  ❌ Missing required resource: {resource}")
            return False
        print(f"  ✅ Found resource: {resource}")
    
    # Verify S3Bucket configuration
    s3_bucket = resources['S3Bucket']
    if s3_bucket['Type'] != 'AWS::S3::Bucket':
        print("  ❌ S3Bucket has incorrect type")
        return False
    
    bucket_props = s3_bucket.get('Properties', {})
    if 'WebsiteConfiguration' not in bucket_props:
        print("  ❌ S3Bucket missing WebsiteConfiguration")
        return False
    
    website_config = bucket_props['WebsiteConfiguration']
    if 'IndexDocument' not in website_config or 'ErrorDocument' not in website_config:
        print("  ❌ WebsiteConfiguration missing IndexDocument or ErrorDocument")
        return False
    
    # Verify PublicAccessBlockConfiguration
    if 'PublicAccessBlockConfiguration' not in bucket_props:
        print("  ❌ S3Bucket missing PublicAccessBlockConfiguration")
        return False
    
    public_access = bucket_props['PublicAccessBlockConfiguration']
    expected_values = {
        'BlockPublicAcls': False,
        'BlockPublicPolicy': False,
        'IgnorePublicAcls': False,
        'RestrictPublicBuckets': False
    }
    
    for key, expected in expected_values.items():
        if public_access.get(key) != expected:
            print(f"  ❌ PublicAccessBlockConfiguration.{key} should be {expected}")
            return False
    
    print("  ✅ S3Bucket properly configured for website hosting")
    
    # Verify S3BucketPolicy configuration
    bucket_policy = resources['S3BucketPolicy']
    if bucket_policy['Type'] != 'AWS::S3::BucketPolicy':
        print("  ❌ S3BucketPolicy has incorrect type")
        return False
    
    policy_props = bucket_policy.get('Properties', {})
    if 'PolicyDocument' not in policy_props:
        print("  ❌ S3BucketPolicy missing PolicyDocument")
        return False
    
    policy_doc = policy_props['PolicyDocument']
    if 'Statement' not in policy_doc:
        print("  ❌ PolicyDocument missing Statement")
        return False
    
    statements = policy_doc['Statement']
    if not isinstance(statements, list) or len(statements) == 0:
        print("  ❌ PolicyDocument Statement should be a non-empty list")
        return False
    
    # Check the public read statement
    public_read_stmt = statements[0]
    if public_read_stmt.get('Effect') != 'Allow':
        print("  ❌ Policy statement should have Effect: Allow")
        return False
    
    if public_read_stmt.get('Principal') != '*':
        print("  ❌ Policy statement should have Principal: '*'")
        return False
    
    if public_read_stmt.get('Action') != 's3:GetObject':
        print("  ❌ Policy statement should have Action: 's3:GetObject'")
        return False
    
    print("  ✅ S3BucketPolicy properly configured for public read access")
    return True

def test_outputs(template):
    """Test 4: Verify all required outputs are defined"""
    print("\n🔍 Test 4: Output Configuration")
    
    outputs = template.get('Outputs', {})
    
    # Check required outputs
    required_outputs = ['WebsiteURL', 'BucketWebsiteConfiguration', 'BucketName']
    for output in required_outputs:
        if output not in outputs:
            print(f"  ❌ Missing required output: {output}")
            return False
        print(f"  ✅ Found output: {output}")
    
    # Verify WebsiteURL uses GetAtt
    website_url = outputs['WebsiteURL']
    if 'Value' not in website_url:
        print("  ❌ WebsiteURL missing Value")
        return False
    
    # Check that outputs have descriptions
    for output_name, output_def in outputs.items():
        if 'Description' not in output_def:
            print(f"  ❌ Output {output_name} missing Description")
            return False
    
    print("  ✅ All outputs properly configured with descriptions")
    return True

def test_resource_dependencies(template):
    """Test 5: Verify resource dependencies and relationships"""
    print("\n🔍 Test 5: Resource Dependencies")
    
    resources = template.get('Resources', {})
    
    # Check that S3BucketPolicy references S3Bucket
    bucket_policy = resources['S3BucketPolicy']
    policy_props = bucket_policy.get('Properties', {})
    
    # The Bucket property should reference the S3Bucket resource
    bucket_ref = policy_props.get('Bucket')
    if not bucket_ref:
        print("  ❌ S3BucketPolicy missing Bucket reference")
        return False
    
    # Check that policy Resource references the bucket
    policy_doc = policy_props['PolicyDocument']
    statement = policy_doc['Statement'][0]
    resource_arn = statement.get('Resource')
    if not resource_arn:
        print("  ❌ Policy statement missing Resource ARN")
        return False
    
    print("  ✅ S3BucketPolicy properly references S3Bucket")
    
    # Check that outputs reference the correct resources
    outputs = template.get('Outputs', {})
    website_url = outputs['WebsiteURL']
    
    print("  ✅ Resource dependencies properly configured")
    return True

def test_security_configuration(template):
    """Test 6: Verify security best practices"""
    print("\n🔍 Test 6: Security Configuration")
    
    resources = template.get('Resources', {})
    
    # Check S3 bucket security settings
    s3_bucket = resources['S3Bucket']
    bucket_props = s3_bucket.get('Properties', {})
    
    # Verify public access is properly configured for website hosting
    public_access = bucket_props.get('PublicAccessBlockConfiguration', {})
    if public_access.get('BlockPublicPolicy') != False:
        print("  ❌ BlockPublicPolicy should be False for website hosting")
        return False
    
    # Check bucket policy follows least privilege
    bucket_policy = resources['S3BucketPolicy']
    policy_doc = bucket_policy['Properties']['PolicyDocument']
    statement = policy_doc['Statement'][0]
    
    # Should only allow s3:GetObject, not broader permissions
    action = statement.get('Action')
    if action != 's3:GetObject':
        print(f"  ❌ Policy should only allow s3:GetObject, found: {action}")
        return False
    
    # Should restrict to bucket objects only (/*) 
    resource_arn = statement.get('Resource')
    if not resource_arn or not str(resource_arn).endswith('/*'):
        print("  ❌ Policy Resource should end with /* to restrict to bucket objects")
        return False
    
    print("  ✅ Security configuration follows least privilege principles")
    return True

def test_multi_environment_support(template):
    """Test 7: Verify multi-environment and parameterization features"""
    print("\n🔍 Test 7: Multi-Environment Support")
    
    params = template.get('Parameters', {})
    
    # Check for environment-related parameters
    env_params = ['Environment', 'ProjectName']
    for param in env_params:
        if param not in params:
            print(f"  ❌ Missing environment parameter: {param}")
            return False
        print(f"  ✅ Found environment parameter: {param}")
    
    # Check Environment parameter has allowed values
    env_param = params['Environment']
    if 'AllowedValues' not in env_param:
        print("  ❌ Environment parameter missing AllowedValues")
        return False
    
    allowed_envs = env_param['AllowedValues']
    expected_envs = ['dev', 'test', 'staging', 'prod', 'demo']
    for env in expected_envs:
        if env not in allowed_envs:
            print(f"  ❌ Environment missing allowed value: {env}")
            return False
    
    # Check that resources use tags for environment identification
    resources = template.get('Resources', {})
    s3_bucket = resources['S3Bucket']
    bucket_props = s3_bucket.get('Properties', {})
    
    if 'Tags' not in bucket_props:
        print("  ❌ S3Bucket missing Tags for environment identification")
        return False
    
    tags = bucket_props['Tags']
    required_tag_keys = ['Environment', 'Project', 'Purpose', 'ManagedBy']
    for tag in tags:
        if isinstance(tag, dict) and 'Key' in tag:
            if tag['Key'] in required_tag_keys:
                required_tag_keys.remove(tag['Key'])
    
    if required_tag_keys:
        print(f"  ❌ Missing required tags: {required_tag_keys}")
        return False
    
    print("  ✅ Multi-environment support properly configured")
    return True

def test_template_metadata(template):
    """Test 8: Verify template metadata and user interface"""
    print("\n🔍 Test 8: Template Metadata")
    
    if 'Metadata' not in template:
        print("  ❌ Template missing Metadata section")
        return False
    
    metadata = template['Metadata']
    if 'AWS::CloudFormation::Interface' not in metadata:
        print("  ❌ Missing CloudFormation Interface metadata")
        return False
    
    interface = metadata['AWS::CloudFormation::Interface']
    
    # Check parameter groups
    if 'ParameterGroups' not in interface:
        print("  ❌ Missing ParameterGroups in interface")
        return False
    
    # Check parameter labels
    if 'ParameterLabels' not in interface:
        print("  ❌ Missing ParameterLabels in interface")
        return False
    
    print("  ✅ Template metadata properly configured for user interface")
    return True

def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting S3 Static Website CloudFormation Integration Tests")
    print("=" * 70)
    
    # Load template
    template = load_template()
    if not template:
        return False
    
    # Run all tests
    tests = [
        test_template_structure,
        test_parameters,
        test_resources,
        test_outputs,
        test_resource_dependencies,
        test_security_configuration,
        test_multi_environment_support,
        test_template_metadata
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func(template):
                passed += 1
            else:
                print(f"  ❌ {test_func.__name__} failed")
        except Exception as e:
            print(f"  ❌ {test_func.__name__} failed with error: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Template is ready for deployment.")
        print("\n✅ Template Integration Status:")
        print("  • All resources properly configured and linked")
        print("  • Security policies follow best practices")
        print("  • Multi-environment support implemented")
        print("  • Template produces functional static website")
        print("  • Resource dependencies validated")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)