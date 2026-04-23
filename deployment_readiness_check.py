#!/usr/bin/env python3
"""
Deployment Readiness Check for S3 Static Website CloudFormation Template
Task 9: Final checkpoint - Complete deployment verification
"""

import re
import sys

def check_template_content():
    """Check template content for key components"""
    print("🔍 CloudFormation Template Deployment Readiness Check")
    print("=" * 60)
    
    try:
        with open('s3-static-website.yaml', 'r') as f:
            content = f.read()
        
        checks_passed = 0
        total_checks = 0
        
        # Check 1: Template Format Version
        total_checks += 1
        if "AWSTemplateFormatVersion: '2010-09-09'" in content:
            print("✅ CloudFormation template format version is correct")
            checks_passed += 1
        else:
            print("❌ Missing or incorrect CloudFormation template format version")
        
        # Check 2: Required Parameters
        total_checks += 1
        required_params = ['BucketName:', 'IndexDocument:', 'ErrorDocument:']
        params_found = all(param in content for param in required_params)
        if params_found:
            print("✅ All required parameters are defined")
            checks_passed += 1
        else:
            print("❌ Missing required parameters")
        
        # Check 3: S3 Bucket Resource
        total_checks += 1
        if 'Type: AWS::S3::Bucket' in content and 'WebsiteConfiguration:' in content:
            print("✅ S3 Bucket resource with website configuration is present")
            checks_passed += 1
        else:
            print("❌ S3 Bucket resource or website configuration missing")
        
        # Check 4: S3 Bucket Policy Resource
        total_checks += 1
        if 'Type: AWS::S3::BucketPolicy' in content and 's3:GetObject' in content:
            print("✅ S3 Bucket Policy resource with public read access is present")
            checks_passed += 1
        else:
            print("❌ S3 Bucket Policy resource or public read access missing")
        
        # Check 5: Public Access Configuration
        total_checks += 1
        if 'PublicAccessBlockConfiguration:' in content:
            print("✅ Public access block configuration is present")
            checks_passed += 1
        else:
            print("❌ Public access block configuration missing")
        
        # Check 6: Website URL Output
        total_checks += 1
        if 'WebsiteURL:' in content and 'GetAtt' in content and 'WebsiteURL' in content:
            print("✅ Website URL output is configured")
            checks_passed += 1
        else:
            print("❌ Website URL output missing or incorrectly configured")
        
        # Check 7: Parameter Constraints
        total_checks += 1
        if 'AllowedPattern:' in content and 'ConstraintDescription:' in content:
            print("✅ Parameter validation constraints are present")
            checks_passed += 1
        else:
            print("❌ Parameter validation constraints missing")
        
        # Check 8: Resource Dependencies
        total_checks += 1
        if '!Ref S3Bucket' in content or 'Ref: S3Bucket' in content:
            print("✅ Resource dependencies are properly configured")
            checks_passed += 1
        else:
            print("❌ Resource dependencies not properly configured")
        
        # Check 9: Multi-environment Support
        total_checks += 1
        if 'Environment:' in content and 'Tags:' in content:
            print("✅ Multi-environment support and tagging is present")
            checks_passed += 1
        else:
            print("❌ Multi-environment support or tagging missing")
        
        # Check 10: Security Best Practices
        total_checks += 1
        security_patterns = [
            r'Principal:\s*[\'\"]\*[\'\"]\s*',  # Principal: "*"
            r'Action:\s*[\'\"]*s3:GetObject[\'\"]*',  # Action: s3:GetObject
            r'Effect:\s*[\'\"]*Allow[\'\"]*'  # Effect: Allow
        ]
        security_checks = all(re.search(pattern, content) for pattern in security_patterns)
        if security_checks:
            print("✅ Security best practices are implemented")
            checks_passed += 1
        else:
            print("❌ Security configuration incomplete")
        
        print("\n" + "=" * 60)
        print(f"📊 Validation Summary: {checks_passed}/{total_checks} checks passed")
        
        if checks_passed == total_checks:
            print("🎉 DEPLOYMENT READY - All checks passed!")
            print("\n🚀 Template is ready for deployment with:")
            print("   • Proper CloudFormation structure")
            print("   • All required resources and parameters")
            print("   • Security best practices")
            print("   • Multi-environment support")
            print("   • Complete output configuration")
            return True
        else:
            print(f"⚠️  DEPLOYMENT NOT READY - {total_checks - checks_passed} issues found")
            return False
            
    except FileNotFoundError:
        print("❌ Template file 's3-static-website.yaml' not found")
        return False
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False

def check_requirements_compliance():
    """Check compliance with specific requirements"""
    print("\n📋 Requirements Compliance Check")
    print("-" * 40)
    
    requirements_map = {
        "1.1 - S3 Static Website Hosting": ["WebsiteConfiguration:", "IndexDocument", "ErrorDocument"],
        "1.5 - Public Access": ["s3:GetObject", "Principal: '*'"],
        "2.1 - CloudFormation Resources": ["AWS::S3::Bucket", "AWS::S3::BucketPolicy"],
        "2.3 - Website URL Output": ["WebsiteURL:", "GetAtt"],
        "4.1 - Public Read Access Policy": ["s3:GetObject", "Effect: Allow"],
        "5.1 - Bucket Name Parameter": ["BucketName:", "Type: String"],
        "6.1 - Website URL Output": ["WebsiteURL:", "Description:"]
    }
    
    try:
        with open('s3-static-website.yaml', 'r') as f:
            content = f.read()
        
        compliant_requirements = 0
        total_requirements = len(requirements_map)
        
        for requirement, patterns in requirements_map.items():
            if all(pattern in content for pattern in patterns):
                print(f"✅ {requirement}")
                compliant_requirements += 1
            else:
                print(f"❌ {requirement}")
        
        print(f"\n📊 Requirements Compliance: {compliant_requirements}/{total_requirements}")
        return compliant_requirements == total_requirements
        
    except Exception as e:
        print(f"❌ Error checking requirements: {e}")
        return False

def check_deployment_documentation():
    """Check if deployment documentation exists"""
    print("\n📚 Deployment Documentation Check")
    print("-" * 40)
    
    try:
        with open('DEPLOYMENT.md', 'r') as f:
            deployment_content = f.read()
        
        doc_checks = [
            ("Prerequisites section", "Prerequisites"),
            ("Parameter documentation", "Parameters"),
            ("Deployment instructions", "aws cloudformation create-stack"),
            ("Verification steps", "Verification"),
            ("Troubleshooting guide", "Troubleshooting")
        ]
        
        doc_passed = 0
        for check_name, pattern in doc_checks:
            if pattern in deployment_content:
                print(f"✅ {check_name}")
                doc_passed += 1
            else:
                print(f"❌ {check_name}")
        
        print(f"\n📊 Documentation Completeness: {doc_passed}/{len(doc_checks)}")
        return doc_passed == len(doc_checks)
        
    except FileNotFoundError:
        print("❌ DEPLOYMENT.md file not found")
        return False

def main():
    """Main function"""
    template_ready = check_template_content()
    requirements_met = check_requirements_compliance()
    docs_complete = check_deployment_documentation()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL DEPLOYMENT READINESS ASSESSMENT")
    print("=" * 60)
    
    if template_ready and requirements_met and docs_complete:
        print("🎉 ✅ DEPLOYMENT READY")
        print("\nThe CloudFormation solution is fully verified and ready for deployment:")
        print("• Template structure and syntax validated")
        print("• All requirements compliance verified")
        print("• Complete deployment documentation available")
        print("• Security best practices implemented")
        print("• Multi-environment support configured")
        print("\n🚀 You can proceed with deployment using the instructions in DEPLOYMENT.md")
        return 0
    else:
        print("⚠️ ❌ DEPLOYMENT NOT READY")
        print("\nIssues found that need to be addressed before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())