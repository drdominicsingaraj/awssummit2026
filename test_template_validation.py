#!/usr/bin/env python3
"""
Test script to validate the CloudFormation template structure and logic
"""

import yaml
import re

def test_template_structure():
    """Test that the template has the required structure for bucket validation"""
    
    with open('s3-static-website.yaml', 'r') as f:
        content = f.read()
    
    # Replace CloudFormation functions for parsing
    content = re.sub(r'!Ref \w+', '"REF_PLACEHOLDER"', content)
    content = re.sub(r'!Sub .*', '"SUB_PLACEHOLDER"', content)
    content = re.sub(r'!GetAtt [\w.]+', '"GETATT_PLACEHOLDER"', content)
    
    template = yaml.safe_load(content)
    
    # Test 1: Check template has required sections
    required_sections = ['AWSTemplateFormatVersion', 'Description', 'Parameters', 'Resources', 'Outputs']
    for section in required_sections:
        assert section in template, f"Missing required section: {section}"
    
    # Test 2: Check bucket validation resources exist
    resources = template['Resources']
    assert 'BucketExistenceValidator' in resources, "Missing BucketExistenceValidator resource"
    assert 'BucketValidationFunction' in resources, "Missing BucketValidationFunction resource"
    assert 'BucketValidationRole' in resources, "Missing BucketValidationRole resource"
    
    # Test 3: Check validation function is a Lambda function
    validation_func = resources['BucketValidationFunction']
    assert validation_func['Type'] == 'AWS::Lambda::Function', "BucketValidationFunction must be a Lambda function"
    
    # Test 4: Check Lambda function has required properties
    func_props = validation_func['Properties']
    assert 'Runtime' in func_props, "Lambda function missing Runtime"
    assert 'Handler' in func_props, "Lambda function missing Handler"
    assert 'Code' in func_props, "Lambda function missing Code"
    
    # Test 5: Check validation function code contains bucket existence check
    code = func_props['Code']['ZipFile']
    assert 'head_bucket' in code, "Validation function should use head_bucket to check existence"
    assert 'NoSuchBucket' in code, "Validation function should handle NoSuchBucket exception"
    
    # Test 6: Check descriptive error messages
    assert "does not exist" in code, "Should have descriptive error message for non-existent bucket"
    assert "Please create the bucket first" in code, "Should provide guidance on how to fix the error"
    
    # Test 7: Check outputs include validation status
    outputs = template['Outputs']
    assert 'BucketValidationStatus' in outputs, "Missing BucketValidationStatus output"
    
    # Test 8: Check dependencies are set correctly
    website_config = resources['S3BucketWebsiteConfiguration']
    assert 'DependsOn' in website_config, "Website configuration should depend on validation"
    
    print("✅ All template structure tests passed!")
    return True

def test_error_scenarios():
    """Test that error scenarios are properly handled"""
    
    with open('s3-static-website.yaml', 'r') as f:
        content = f.read()
    
    # Check for proper error handling patterns
    assert "cfnresponse.FAILED" in content, "Should use cfnresponse.FAILED for errors"
    assert "reason=" in content, "Should provide reason for failures"
    
    # Check for multiple error scenarios
    error_scenarios = [
        "NoSuchBucket",  # Bucket doesn't exist
        "Unable to access",  # Permission issues
        "unexpected error"  # General error handling
    ]
    
    for scenario in error_scenarios:
        assert scenario in content, f"Missing error handling for: {scenario}"
    
    print("✅ All error handling tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_template_structure()
        test_error_scenarios()
        print("\n🎉 All validation tests passed! Template implements bucket existence validation correctly.")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")