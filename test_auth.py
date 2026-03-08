#!/usr/bin/env python
"""Test login and signup pages"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import app
    
    with app.test_client() as client:
        # Test login page
        print("Testing GET /login...")
        resp = client.get('/login')
        print(f'Status: {resp.status_code}')
        
        if resp.status_code == 200:
            print("✓ Login page loads successfully")
        else:
            print(f"✗ Error: {resp.data.decode()[:300]}")
        
        # Test signup page
        print("\nTesting GET /signup...")
        resp = client.get('/signup')
        print(f'Status: {resp.status_code}')
        
        if resp.status_code == 200:
            print("✓ Signup page loads successfully")
        else:
            print(f"✗ Error: {resp.data.decode()[:300]}")
            
        # Test signup POST
        print("\nTesting POST /signup...")
        resp = client.post('/signup', data={'username': 'testuser', 'password': 'testpass123'})
        print(f'Status: {resp.status_code}')
        
        # Test login POST
        print("\nTesting POST /login...")
        resp = client.post('/login', data={'username': 'testuser', 'password': 'testpass123'})
        print(f'Status: {resp.status_code}')

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
