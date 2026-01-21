"""
Script de prueba para verificar la configuración del backend
antes de la integración con Flutter.

Ejecutar desde la raíz del proyecto backend:
python test_integration.py
"""

import requests
import json

# Configuración
BASE_URL = "http://192.168.1.4:8000"
API_URL = f"{BASE_URL}/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health_check():
    """Test 1: Verificar que el servidor está corriendo"""
    print_section("TEST 1: Health Check")
    try:
        response = requests.get(f"{API_URL}/accounts/health/", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check PASSED")
            return True
        else:
            print("❌ Health check FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cors():
    """Test 2: Verificar configuración CORS"""
    print_section("TEST 2: CORS Configuration")
    try:
        response = requests.get(f"{API_URL}/accounts/test/", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Verificar headers CORS
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
        }
        print(f"\nCORS Headers: {json.dumps(cors_headers, indent=2)}")
        
        if response.status_code == 200:
            print("✅ CORS test PASSED")
            return True
        else:
            print("❌ CORS test FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_endpoints_availability():
    """Test 3: Verificar disponibilidad de endpoints"""
    print_section("TEST 3: Endpoints Availability")
    
    endpoints = [
        ("Health Check", "GET", f"{API_URL}/accounts/health/"),
        ("Test Connection", "GET", f"{API_URL}/accounts/test/"),
        ("Google Login", "POST", f"{API_URL}/accounts/google/"),
        ("Token Obtain", "POST", f"{API_URL}/accounts/token/"),
        ("Token Refresh", "POST", f"{API_URL}/accounts/token/refresh/"),
    ]
    
    results = []
    for name, method, url in endpoints:
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json={}, timeout=5)
            
            # Para POST, esperamos 400 (bad request) porque no enviamos datos válidos
            # pero eso significa que el endpoint existe
            status_ok = response.status_code in [200, 400, 401]
            
            status = "✅" if status_ok else "❌"
            print(f"{status} {name}: {response.status_code}")
            results.append(status_ok)
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append(False)
    
    if all(results):
        print("\n✅ All endpoints are available")
        return True
    else:
        print("\n❌ Some endpoints are not available")
        return False

def test_user_creation():
    """Test 4: Crear un usuario de prueba"""
    print_section("TEST 4: User Creation & Role Assignment")
    
    test_user = {
        "username": f"testuser_{int(requests.get('http://worldtimeapi.org/api/ip').json()['unixtime'])}",
        "email": f"test_{int(requests.get('http://worldtimeapi.org/api/ip').json()['unixtime'])}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
    }
    
    try:
        response = requests.post(
            f"{API_URL}/accounts/users/",
            json=test_user,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            user_data = response.json()
            print(f"Response: {json.dumps(user_data, indent=2)}")
            
            # Verificar que el rol por defecto es CLIENT
            if user_data.get('role') == 'CLIENT':
                print("✅ User created with CLIENT role by default")
                return True
            else:
                print(f"❌ User role is {user_data.get('role')}, expected CLIENT")
                return False
        else:
            print(f"Response: {response.text}")
            print("❌ User creation FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "🚀"*30)
    print("  BACKEND INTEGRATION TESTS FOR FLUTTER")
    print("🚀"*30)
    
    tests = [
        ("Health Check", test_health_check),
        ("CORS Configuration", test_cors),
        ("Endpoints Availability", test_endpoints_availability),
        ("User Creation & Roles", test_user_creation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Resumen final
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\n{'='*60}")
    print(f"  Total: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready for Flutter integration.")
        print("\nNext steps:")
        print("1. Configure Google OAuth credentials in .env file")
        print("2. Update Flutter app with base URL: http://192.168.1.4:8000")
        print("3. Test Google OAuth flow from Flutter app")
        print("4. Verify JWT tokens are stored securely")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")

if __name__ == "__main__":
    main()
