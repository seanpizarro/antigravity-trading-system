#!/usr/bin/env python3
"""
Debug script for risk assessment issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deepseek_analyst import RiskAssessment

def test_risk_assessment():
    # Test the RiskAssessment object with correct parameters
    risk = RiskAssessment(
        alert_level=1, 
        message="Test assessment",
        concerns=["Test concern"],
        recommendations=["Test recommendation"]
    )
    
    print("Testing RiskAssessment object:")
    print(f"Direct access - Alert Level: {risk.alert_level}")
    print(f"Direct access - Message: {risk.message}")
    print(f"Direct access - Concerns: {risk.concerns}")
    print(f"Direct access - Recommendations: {risk.recommendations}")
    
    # Test if get method exists
    if hasattr(risk, 'get'):
        print(f"\n✅ Get method exists!")
        print(f"Get method - Alert Level: {risk.get('alert_level')}")
        print(f"Get method - Message: {risk.get('message')}")
        print(f"Get method - Concerns: {risk.get('concerns')}")
        print(f"Get method with default: {risk.get('nonexistent', 'default_value')}")
    else:
        print("\n❌ No 'get' method found - this is the issue!")
        
    # Test conversion to dict
    if hasattr(risk, 'to_dict'):
        risk_dict = risk.to_dict()
        print(f"\n✅ Dict conversion works!")
        print(f"Dict: {risk_dict}")
    else:
        print("\n❌ No 'to_dict' method found!")

if __name__ == "__main__":
    test_risk_assessment()
