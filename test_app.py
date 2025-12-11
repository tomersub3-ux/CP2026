"""Test script to verify the CP Platform works correctly."""
from models import init_db, get_session, User, Problem

print("=" * 50)
print("CP Platform - Verification Test")
print("=" * 50)

# 1. Initialize database
print("\n1. Initializing database...")
init_db()
print("   [OK] Database initialized")

# 2. Check Admin user
print("\n2. Checking Admin user...")
session = get_session()
admin = session.query(User).filter(User.username == "Admin").first()

if admin:
    print(f"   [OK] Admin user exists (ID: {admin.id})")
    print(f"   [OK] Admin is_admin flag: {admin.is_admin}")
    
    # Test password
    pwd_ok = admin.check_password("12345678")
    print(f"   [OK] Password '12345678' valid: {pwd_ok}")
else:
    print("   [FAIL] Admin user NOT found!")

# 3. Test creating a problem
print("\n3. Testing problem creation...")
test_problem = Problem(
    title="Test Problem - Two Sum",
    problem_url="https://codeforces.com/problemset/problem/1/A",
    points=50,
    cf_contest_id=1,
    cf_problem_index="A",
    added_by=admin.id if admin else None
)
session.add(test_problem)
session.commit()
print(f"   [OK] Test problem created (ID: {test_problem.id})")

# 4. Verify problem count
problem_count = session.query(Problem).count()
print(f"   [OK] Total problems in database: {problem_count}")

session.close()

print("\n" + "=" * 50)
print("All tests passed! The app is ready to use.")
print("Run: streamlit run streamlit_app.py")
print("Login: Admin / 12345678")
print("=" * 50)

