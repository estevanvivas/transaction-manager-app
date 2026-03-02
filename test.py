import sys

try:
    from app import create_app

    app = create_app()
    print("App created successfully")

    with app.test_client() as client:
        # Test register
        resp = client.post('/auth/register', json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "Test@1234"
        })
        print(f"Register: {resp.status_code} - {resp.get_json()}")

        # Test login
        resp = client.post('/auth/login', json={
            "email": "test@test.com",
            "password": "Test@1234"
        })
        data = resp.get_json()
        print(f"Login: {resp.status_code} - {data}")

        if resp.status_code == 200:
            token = data['data']['access_token']
            headers = {"Authorization": f"Bearer {token}"}

            # Test deposit
            resp = client.post('/transactions/deposit', json={"amount": "1000.00"}, headers=headers)
            print(f"Deposit: {resp.status_code} - {resp.get_json()}")

            # Test get user
            resp = client.get('/users/me', headers=headers)
            print(f"User: {resp.status_code} - {resp.get_json()}")

            # Test withdrawal
            resp = client.post('/transactions/withdrawal', json={"amount": "100.00"}, headers=headers)
            print(f"Withdrawal: {resp.status_code} - {resp.get_json()}")

            # Test get user after withdrawal
            resp = client.get('/users/me', headers=headers)
            print(f"User after withdrawal: {resp.status_code} - {resp.get_json()}")

            # Test get transactions
            resp = client.get('/transactions/', headers=headers)
            print(f"Transactions: {resp.status_code} - {resp.get_json()}")

            # Test audit logs
            resp = client.get('/audit/my-logs', headers=headers)
            print(f"Audit logs: {resp.status_code} - {resp.get_json()}")

    print("\n=== ALL TESTS PASSED ===")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    import traceback

    traceback.print_exc()
    sys.exit(1)
