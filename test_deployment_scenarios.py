#!/usr/bin/env python3
"""
Test different deployment scenarios for the multi-environment CloudFormation template
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

def validate_parameter_constraints(template, test_params):
    """Validate parameter constraints against test values"""
    params_def = template.get('Parameters', {})
    validation_results = []
    
    for param_name, test_value in test_params.items():
        if param_name not in params_def:
            validation_results.append(f"❌ Parameter {param_name} not found in template")
            continue
            
        param_def = params_def[param_name]
        
        # Check AllowedValues constraint
        if 'AllowedValues' in param_def:
            allowed = param_def['AllowedValues']
            if test_value not in allowed:
                validation_results.append(f"❌ {param_name}='{test_value}' not in allowed values: {allowed}")
                continue
        
        # Check AllowedPattern constraint
        if 'AllowedPattern' in param_def:
            import re
            pattern = param_def['AllowedPattern']
            if not re.match(pattern, test_value):
                validation_results.append(f"❌ {param_name}='{test_value}' doesn't match pattern: {pattern}")
                continue
        
        # Check MinLength/MaxLength constraints
        if 'MinLength' in param_def:
            min_len = param_def['MinLength']
            if len(test_value) < min_len:
                validation_results.append(f"❌ {param_name}='{test_value}' shorter than minimum length {min_len}")
                continue
                
        if 'MaxLength' in param_def:
            max_len = param_def['MaxLength']
            if len(test_value) > max_len:
                validation_results.append(f"❌ {param_name}='{test_value}' longer than maximum length {max_len}")
                continue
        
        validation_results.append(f"✓ {param_name}='{test_value}' passes validation")
    
    return validation_results

def test_deployment_scenarios(template_path):
    """Test various deployment scenarios"""
    print("Testing Deployment Scenarios for Multi-Environment Template")
    print("=" * 60)
    
    try:
        with open(template_path, 'r') as f:
            template = yaml.load(f, Loader=CloudFormationLoader)
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        return False
    
    # Define test scenarios
    scenarios = [
        {
            "name": "Development Environment",
            "params": {
                "BucketName": "myproject-dev-website-2024",
                "Environment": "dev",
                "ProjectName": "myproject",
                "IndexDocument": "index.html",
                "ErrorDocument": "error.html",
                "EnableVersioning": "false",
                "CostCenter": "DEV-001"
            }
        },
        {
            "name": "Production Environment",
            "params": {
                "BucketName": "company-prod-site",
                "Environment": "prod",
                "ProjectName": "company-website",
                "IndexDocument": "home.html",
                "ErrorDocument": "404.html",
                "EnableVersioning": "true",
                "CostCenter": "PROD-MARKETING"
            }
        },
        {
            "name": "Staging Environment",
            "params": {
                "BucketName": "test-staging-bucket",
                "Environment": "staging",
                "ProjectName": "test-project",
                "IndexDocument": "index.htm",
                "ErrorDocument": "error.htm",
                "EnableVersioning": "true",
                "CostCenter": ""  # Empty cost center
            }
        },
        {
            "name": "Demo Environment",
            "params": {
                "BucketName": "demo123",
                "Environment": "demo",
                "ProjectName": "demo",
                "IndexDocument": "main.html",
                "ErrorDocument": "notfound.html",
                "EnableVersioning": "false",
                "CostCenter": "DEMO"
            }
        },
        {
            "name": "Edge Case - Minimum Length Bucket",
            "params": {
                "BucketName": "abc",  # 3 characters (minimum)
                "Environment": "test",
                "ProjectName": "min",
                "IndexDocument": "i.html",
                "ErrorDocument": "e.html",
                "EnableVersioning": "false",
                "CostCenter": ""
            }
        },
        {
            "name": "Edge Case - Maximum Length Bucket",
            "params": {
                "BucketName": "a" + "b" * 61 + "c",  # 63 characters
                "Environment": "test",
                "ProjectName": "long-project-name-test",
                "IndexDocument": "index.html",
                "ErrorDocument": "error.html",
                "EnableVersioning": "true",
                "CostCenter": "VERY-LONG-COST-CENTER-CODE-FOR-TESTING-LIMITS"
            }
        }
    ]
    
    all_scenarios_passed = True
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Testing {scenario['name']}")
        print("-" * 40)
        
        validation_results = validate_parameter_constraints(template, scenario['params'])
        
        scenario_passed = True
        for result in validation_results:
            print(f"  {result}")
            if result.startswith("❌"):
                scenario_passed = False
        
        if scenario_passed:
            print(f"  ✅ {scenario['name']} scenario PASSED")
        else:
            print(f"  ❌ {scenario['name']} scenario FAILED")
            all_scenarios_passed = False
    
    # Test invalid scenarios that should fail
    print(f"\n{len(scenarios) + 1}. Testing Invalid Scenarios (Should Fail)")
    print("-" * 40)
    
    invalid_scenarios = [
        {
            "name": "Invalid Environment",
            "params": {"Environment": "invalid-env"},
            "expected": "should fail environment validation"
        },
        {
            "name": "Invalid Bucket Name (uppercase)",
            "params": {"BucketName": "MyBucket"},
            "expected": "should fail bucket name pattern"
        },
        {
            "name": "Invalid Versioning Value",
            "params": {"EnableVersioning": "maybe"},
            "expected": "should fail versioning validation"
        },
        {
            "name": "Bucket Name Too Short",
            "params": {"BucketName": "ab"},
            "expected": "should fail minimum length"
        },
        {
            "name": "Invalid HTML Extension",
            "params": {"IndexDocument": "index.txt"},
            "expected": "should fail HTML extension pattern"
        }
    ]
    
    for invalid_scenario in invalid_scenarios:
        print(f"  Testing {invalid_scenario['name']}...")
        validation_results = validate_parameter_constraints(template, invalid_scenario['params'])
        
        failed_as_expected = any(result.startswith("❌") for result in validation_results)
        if failed_as_expected:
            print(f"    ✓ Correctly rejected invalid input ({invalid_scenario['expected']})")
        else:
            print(f"    ❌ Should have rejected invalid input ({invalid_scenario['expected']})")
            all_scenarios_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("DEPLOYMENT SCENARIOS SUMMARY")
    print("=" * 60)
    
    if all_scenarios_passed:
        print("✅ All deployment scenarios passed validation")
        print("✅ Template is ready for multi-environment deployment")
        print("\nKey Multi-Environment Features Validated:")
        print("  • Flexible bucket naming for different environments")
        print("  • Environment-specific parameter validation")
        print("  • Optional cost center tracking")
        print("  • Configurable versioning per environment")
        print("  • Comprehensive parameter constraints")
        print("  • Proper rejection of invalid inputs")
        return True
    else:
        print("❌ Some deployment scenarios failed")
        print("❌ Template needs fixes before multi-environment deployment")
        return False

if __name__ == "__main__":
    template_path = sys.argv[1] if len(sys.argv) > 1 else "s3-static-website.yaml"
    success = test_deployment_scenarios(template_path)
    sys.exit(0 if success else 1)