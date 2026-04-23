#!/usr/bin/env python3
"""
Test script for multi-environment CloudFormation template functionality
"""
import yaml
import json
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

def test_multi_environment_features(template_path):
    """Test multi-environment features of the CloudFormation template"""
    print("Testing Multi-Environment CloudFormation Template")
    print("=" * 50)
    
    try:
        with open(template_path, 'r') as f:
            template = yaml.load(f, Loader=CloudFormationLoader)
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        return False
    
    test_results = []
    
    # Test 1: Environment parameter validation
    print("\n1. Testing Environment Parameter...")
    params = template.get('Parameters', {})
    env_param = params.get('Environment', {})
    
    if 'AllowedValues' in env_param:
        allowed_envs = env_param['AllowedValues']
        expected_envs = ['dev', 'test', 'staging', 'prod', 'demo']
        if set(allowed_envs) >= set(expected_envs):
            print("✓ Environment parameter supports multiple environments")
            test_results.append(True)
        else:
            print(f"❌ Missing environments. Found: {allowed_envs}, Expected: {expected_envs}")
            test_results.append(False)
    else:
        print("❌ Environment parameter missing AllowedValues")
        test_results.append(False)
    
    # Test 2: Project name parameter for organization
    print("\n2. Testing Project Name Parameter...")
    project_param = params.get('ProjectName', {})
    if project_param and 'Default' in project_param:
        print("✓ ProjectName parameter exists with default value")
        test_results.append(True)
    else:
        print("❌ ProjectName parameter missing or no default")
        test_results.append(False)
    
    # Test 3: Bucket name parameter validation
    print("\n3. Testing Bucket Name Parameter Validation...")
    bucket_param = params.get('BucketName', {})
    if 'AllowedPattern' in bucket_param and 'ConstraintDescription' in bucket_param:
        print("✓ BucketName has proper validation pattern and description")
        test_results.append(True)
    else:
        print("❌ BucketName missing validation pattern or description")
        test_results.append(False)
    
    # Test 4: Optional versioning parameter
    print("\n4. Testing Versioning Parameter...")
    versioning_param = params.get('EnableVersioning', {})
    if versioning_param and 'AllowedValues' in versioning_param:
        allowed_values = versioning_param['AllowedValues']
        if 'true' in allowed_values and 'false' in allowed_values:
            print("✓ EnableVersioning parameter supports true/false values")
            test_results.append(True)
        else:
            print("❌ EnableVersioning parameter missing proper allowed values")
            test_results.append(False)
    else:
        print("❌ EnableVersioning parameter missing or incomplete")
        test_results.append(False)
    
    # Test 5: Cost center parameter for billing
    print("\n5. Testing Cost Center Parameter...")
    cost_param = params.get('CostCenter', {})
    if cost_param and 'Default' in cost_param:
        print("✓ CostCenter parameter exists for billing tracking")
        test_results.append(True)
    else:
        print("❌ CostCenter parameter missing")
        test_results.append(False)
    
    # Test 6: Conditions for conditional logic
    print("\n6. Testing Conditions...")
    conditions = template.get('Conditions', {})
    expected_conditions = ['HasCostCenter', 'EnableVersioningCondition']
    found_conditions = list(conditions.keys())
    
    if all(cond in found_conditions for cond in expected_conditions):
        print("✓ Required conditions exist for multi-environment logic")
        test_results.append(True)
    else:
        print(f"❌ Missing conditions. Found: {found_conditions}, Expected: {expected_conditions}")
        test_results.append(False)
    
    # Test 7: Environment-specific tagging
    print("\n7. Testing Environment-Specific Tagging...")
    resources = template.get('Resources', {})
    s3_bucket = resources.get('S3Bucket', {})
    bucket_props = s3_bucket.get('Properties', {})
    tags = bucket_props.get('Tags', [])
    
    required_tag_keys = ['Environment', 'Project', 'Purpose', 'ManagedBy', 'StackName']
    found_tag_keys = [tag.get('Key') for tag in tags if isinstance(tag, dict) and 'Key' in tag]
    
    if all(key in found_tag_keys for key in required_tag_keys):
        print("✓ S3 bucket has comprehensive environment-specific tags")
        test_results.append(True)
    else:
        print(f"❌ Missing required tags. Found: {found_tag_keys}, Expected: {required_tag_keys}")
        test_results.append(False)
    
    # Test 8: Enhanced outputs for multi-environment use
    print("\n8. Testing Enhanced Outputs...")
    outputs = template.get('Outputs', {})
    expected_outputs = ['WebsiteURL', 'BucketName', 'Environment', 'ProjectName', 'VersioningStatus']
    found_outputs = list(outputs.keys())
    
    if all(output in found_outputs for output in expected_outputs):
        print("✓ Template has comprehensive outputs for multi-environment tracking")
        test_results.append(True)
    else:
        print(f"❌ Missing outputs. Found: {found_outputs}, Expected: {expected_outputs}")
        test_results.append(False)
    
    # Test 9: Parameter grouping in metadata
    print("\n9. Testing Parameter Grouping...")
    metadata = template.get('Metadata', {})
    cf_interface = metadata.get('AWS::CloudFormation::Interface', {})
    param_groups = cf_interface.get('ParameterGroups', [])
    
    if len(param_groups) >= 3:  # Expecting at least 3 groups
        group_labels = [group.get('Label', {}).get('default', '') for group in param_groups]
        if any('Environment' in label for label in group_labels):
            print("✓ Parameters are well-organized with environment grouping")
            test_results.append(True)
        else:
            print("❌ Missing environment-specific parameter grouping")
            test_results.append(False)
    else:
        print("❌ Insufficient parameter grouping for multi-environment use")
        test_results.append(False)
    
    # Test 10: Flexible bucket naming validation
    print("\n10. Testing Flexible Bucket Naming...")
    bucket_pattern = bucket_param.get('AllowedPattern', '')
    # Should allow various bucket naming patterns for different environments
    if bucket_pattern and len(bucket_pattern) > 20:  # Complex pattern
        print("✓ Bucket naming pattern is flexible for multi-environment use")
        test_results.append(True)
    else:
        print("❌ Bucket naming pattern may be too restrictive")
        test_results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("✅ Template is well-configured for multi-environment use")
        return True
    else:
        print("❌ Template needs improvements for multi-environment use")
        return False

if __name__ == "__main__":
    template_path = sys.argv[1] if len(sys.argv) > 1 else "s3-static-website.yaml"
    success = test_multi_environment_features(template_path)
    sys.exit(0 if success else 1)