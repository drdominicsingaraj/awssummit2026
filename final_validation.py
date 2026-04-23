#!/usr/bin/env python3
import yaml
import re

# Read and validate the template
with open('s3-static-website.yaml', 'r') as f:
    content = f.read()

# Replace CloudFormation functions for parsing
content_parsed = re.sub(r'!Ref\s+(\w+)', r'"REF_\1"', content)
content_parsed = re.sub(r'!Sub\s+(.+)', r'"SUB_PLACEHOLDER"', content_parsed)
content_parsed = re.sub(r'!GetAtt\s+([\w.]+)', r'"GETATT_PLACEHOLDER"', content_parsed)

try:
    template = yaml.safe_load(content_parsed)
    print("✅ YAML parsing successful")
    
    # Check key sections
    assert 'AWSTemplateFormatVersion' in template
    assert 'Parameters' in template
    assert 'Resources' in template
    assert 'Outputs' in template
    
    # Check resources
    assert 'S3Bucket' in template['Resources']
    assert 'S3BucketPolicy' in template['Resources']
    
    print("✅ All required sections and resources present")
    print("✅ CloudFormation template validation completed successfully!")
    
except Exception as e:
    print(f"❌ Validation failed: {e}")