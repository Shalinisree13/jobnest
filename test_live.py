import requests
import re

BASE_URL = 'http://127.0.0.1:5000'

def test_login(email, password, expected_dash):
    s = requests.Session()
    # 1. Fetch login form to obtain CSRF token
    r1 = s.get(f'{BASE_URL}/login')
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', r1.text)
    assert match, "CSRF token not found on login form!"
    csrf_token = match.group(1)

    # 2. Authenticate
    r2 = s.post(f'{BASE_URL}/login', data={
        'email': email,
        'password': password,
        'csrf_token': csrf_token
    }, allow_redirects=True)
    
    print(f"Login [{email}] -> Final URL: {r2.url}")
    assert expected_dash in r2.url, f"Expected redirect to {expected_dash}, got {r2.url}"

    # 3. Direct GET on dashboard
    r3 = s.get(f'{BASE_URL}{expected_dash}')
    assert r3.status_code == 200, f"Accessing {expected_dash} returned {r3.status_code}"
    print(f"Successfully verified dashboard access: {expected_dash}")

    return s

if __name__ == '__main__':
    print("--- Testing Live End-to-End Roles ---")
    
    # Test Admin
    admin_sess = test_login('admin@jobnest.com', 'Admin@12345', '/admin')
    r_users = admin_sess.get(f'{BASE_URL}/admin/users')
    assert r_users.status_code == 200 and 'User Directory' in r_users.text
    print("Admin users management page verified.")
    
    # Test Employer
    emp_sess = test_login('employer1@techinnovations.com', 'Employer@12345', '/employer/dashboard')
    r_apps = emp_sess.get(f'{BASE_URL}/employer/jobs/1/applicants')
    assert r_apps.status_code == 200 and 'Applicants for' in r_apps.text
    print("Employer applicants management verified.")

    # Test Job Seeker
    seeker_sess = test_login('alex.morgan@email.com', 'Seeker@12345', '/seeker/dashboard')
    r_prof = seeker_sess.get(f'{BASE_URL}/seeker/profile')
    assert r_prof.status_code == 200 and 'Candidate Profile' in r_prof.text
    print("Candidate profile page verified.")

    # Test Secure PDF Resume Access
    r_res = seeker_sess.get(f'{BASE_URL}/resumes/user_6_alex_morgan_resume.pdf')
    assert r_res.status_code == 200 and r_res.content.startswith(b'%PDF'), "PDF content check failed!"
    print(f"Secure PDF resume delivery verified ({len(r_res.content)} bytes).")

    print("\nALL LIVE TESTS PASSED SUCCESSFULLY! The JobNest portal is fully operational.")
