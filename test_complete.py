#!/usr/bin/env python
"""Comprehensive test of auth pages and learning functionality"""
import sys
import os
import sqlite3
sys.path.insert(0, os.path.dirname(__file__))

# Clean up database before testing
DB_FILE = 'users.db'
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print("Cleaned up old database")

try:
    from app import app
    import json
    
    with app.test_client() as client:
        print("=" * 50)
        print("TESTING AUTHENTICATION PAGES")
        print("=" * 50)
        
        # Test 1: Signup page GET
        print("\n1. Testing GET /signup...")
        resp = client.get('/signup')
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert b'Create Account' in resp.data or b'Sign Up' in resp.data
        print("   ✓ Signup page loads with form")
        
        # Test 2: Signup POST (with confirm_password)
        print("\n2. Testing POST /signup (create account)...")
        resp = client.post('/signup', 
                          data={'username': 'testuser123', 'password': 'password123', 'confirm_password': 'password123'},
                          follow_redirects=False)
        assert resp.status_code == 302, f"Expected redirect (302), got {resp.status_code}"
        print("   ✓ Signup redirects to login page")
        
        # Test 3: Login page GET
        print("\n3. Testing GET /login...")
        resp = client.get('/login')
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert b'Login' in resp.data or b'Log In' in resp.data
        print("   ✓ Login page loads with form")
        
        # Test 4: Login POST
        print("\n4. Testing POST /login (authenticate)...")
        resp = client.post('/login',
                          data={'username': 'testuser123', 'password': 'password123'},
                          follow_redirects=False)
        assert resp.status_code == 302, f"Expected redirect (302), got {resp.status_code}"
        print("   ✓ Login successful, redirects to home")
        
        print("\n" + "=" * 50)
        print("TESTING LEARNING FUNCTIONALITY")
        print("=" * 50)
        
        # Test 5: GET / (homepage)
        print("\n5. Testing GET / (homepage)...")
        resp = client.get('/')
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert b'Personalized Learning' in resp.data or b'Topic' in resp.data
        print("   ✓ Homepage loads successfully")
        
        # Test 6: POST /learn (generate content) - requires login
        print("\n6. Testing POST /learn (generate learning material)...")
        payload = {
            'topic': 'Python Programming',
            'user_id': 'testuser123',
            'profile': {
                'learning_style': 'Visual',
                'level': 'Beginner',
                'accuracy': 85
            }
        }
        resp = client.post('/learn',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = json.loads(resp.data)
        assert data.get('success') == True, f"Expected success=True, got {data}"
        assert 'content' in data, "Expected 'content' in response"
        assert 'Python' in str(data['content']), "Expected topic in content"
        print("   ✓ Learning material generated successfully")
        print(f"   - Content length: {len(str(data['content']))} characters")
        
        # Test 7: Logout
        print("\n7. Testing /logout...")
        resp = client.get('/logout', follow_redirects=False)
        assert resp.status_code == 302, f"Expected redirect (302), got {resp.status_code}"
        print("   ✓ Logout successful")
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print("\nThe app is working correctly:")
        print("- Login page: http://127.0.0.1:5000/login")
        print("- Signup page: http://127.0.0.1:5000/signup")
        print("- Home page: http://127.0.0.1:5000/")

except AssertionError as e:
    print(f"\n❌ TEST FAILED: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

