#!/usr/bin/env python
"""
Simple test to verify the app is working
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# Test the basic functionality
with app.test_client() as client:
    # Test homepage
    print("Testing GET /...")
    response = client.get('/')
    print(f"Status: {response.status_code}")
    
    # Test /learn endpoint with sample data
    print("\nTesting POST /learn...")
    data = {
        "topic": "Python Programming",
        "user_id": "test_user",
        "profile": {
            "learning_style": "Visual",
            "level": "Beginner",
            "accuracy": 80
        }
    }
    import json
    response = client.post('/learn', 
                          data=json.dumps(data),
                          content_type='application/json')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = json.loads(response.data)
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            content = result.get('content', '')
            print(f"Content length: {len(content)}")
            print(f"First 200 chars:\n{content[:200]}")
        else:
            print(f"Error: {result.get('error')}")
    else:
        print(f"Response: {response.data.decode()}")

print("\nTest completed!")
