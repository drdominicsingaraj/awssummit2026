#!/usr/bin/env python3
"""
CloudFormation template validation script with support for intrinsic functions
"""
import yaml
import json
import sys
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

def validate_cloudformation_template(file_path):
    """Validate CloudFormation template syntax"""
    try:
        with open(file_path, 'r') as f:
            template = yaml.load(f, Loader=CloudFormationLoader)
        
        # Basic structure validation
        required_sections = ['AWSTemplateFormatVersion']
        for section in required_sections:
            if section not in template:
                print(f"ERROR: Missing required section: {section}")
                return False
        
        # Check for common sections
        common_sections = ['Parameters', 'Resources', 'Outputs', 'Conditions']
        found_sections = []
        for section in common_sections:
            if section in template:
                found_sections.append(section)
                print(f"✓ Found {section} section")
        
        # Validate Parameters section
        if 'Parameters' in template:
            params = template['Parameters']
            print(f"  - {len(params)} parameters defined")
            for param_name, param_def in params.items():
                if 'Type' not in param_def:
                    print(f"  WARNING: Parameter {param_name} missing Type")
        
        # Validate Resources section
        if 'Resources' in template:
            resources = template['Resources']
            print(f"  - {len(resources)} resources defined")
            for resource_name, resource_def in resources.items():
                if 'Type' not in resource_def:
                    print(f"  ERROR: Resource {resource_name} missing Type")
                    return False
        
        print("✓ Template syntax is valid")
        print(f"✓ Template structure is complete with {len(found_sections)} main sections")
        return True
        
    except yaml.YAMLError as e:
        print(f"YAML Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "s3-static-website.yaml"
    success = validate_cloudformation_template(file_path)
    sys.exit(0 if success else 1)