"""
Proxy Authentication Handler - Usage Examples

Demonstrates all authentication methods:
1. Basic authentication
2. Digest authentication
3. NTLM authentication
4. Certificate-based authentication
5. Authentication with challenges
6. Custom headers and configuration
"""

from proxy_auth_handler import (
    ProxyAuthHandler,
    ProxyConfig,
    AuthType,
    create_auth_handler,
)


def example_1_basic_auth():
    """Example 1: Basic authentication (username/password)."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Authentication")
    print("=" * 70)

    config = ProxyConfig(
        proxy_url="http://proxy.example.com:8080",
        auth_type=AuthType.BASIC,
        username="john_doe",
        password="secure_password_123"
    )

    handler = ProxyAuthHandler(config)
    headers = handler.get_auth_headers()

    print(f"\nProxy URL: {handler.get_proxy_url()}")
    print(f"Auth Type: {config.auth_type.value}")
    print(f"\nAuthentication Headers:")
    for key, value in headers.items():
        if "Authorization" in key:
            # Show masked password
            print(f"  {key}: Basic [credentials]")
        else:
            print(f"  {key}: {value}")

    print(f"\nConnection Config:")
    conn_config = handler.get_connection_config()
    for key, value in conn_config.items():
        print(f"  {key}: {value}")

    print()


def example_2_digest_auth():
    """Example 2: Digest authentication."""
    print("=" * 70)
    print("EXAMPLE 2: Digest Authentication")
    print("=" * 70)

    config = ProxyConfig(
        proxy_url="http://proxy.example.com:8080",
        auth_type=AuthType.DIGEST,
        username="user@company.com",
        password="digest_password_456",
        domain="COMPANY"
    )

    handler = ProxyAuthHandler(config)

    print(f"\nProxy URL: {handler.get_proxy_url()}")
    print(f"Auth Type: {config.auth_type.value}")
    print(f"Domain: {config.domain}")

    # Simulate server challenge
    challenge = (
        'Digest realm="Proxy Realm", '
        'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093", '
        'qop="auth", '
        'opaque="5ccc069c403ebaf9f0171986f2c632e5", '
        'algorithm=MD5'
    )

    print(f"\nServer Challenge: {challenge}")

    response_headers = handler.handle_challenge(challenge)

    print(f"\nResponse Headers:")
    for key, value in response_headers.items():
        # Show abbreviated Digest response
        if "Authorization" in key:
            print(f"  {key}: {value[:80]}...")
        else:
            print(f"  {key}: {value}")

    print()


def example_3_ntlm_auth():
    """Example 3: NTLM authentication."""
    print("=" * 70)
    print("EXAMPLE 3: NTLM Authentication")
    print("=" * 70)

    config = ProxyConfig(
        proxy_url="http://proxy.example.com:8080",
        auth_type=AuthType.NTLM,
        username="domain\\username",
        password="ntlm_password_789",
        domain="CORP",
        workstation="WORKSTATION01"
    )

    handler = ProxyAuthHandler(config)

    print(f"\nProxy URL: {handler.get_proxy_url()}")
    print(f"Auth Type: {config.auth_type.value}")
    print(f"Domain: {config.domain}")
    print(f"Workstation: {config.workstation}")

    # Type 1 message (negotiate)
    type1_headers = handler.get_auth_headers()
    print(f"\nType 1 Message (Negotiate):")
    for key, value in type1_headers.items():
        if "Authorization" in key:
            print(f"  {key}: {value[:60]}...")
        else:
            print(f"  {key}: {value}")

    # Simulate Type 2 challenge from server
    type2_challenge = (
        "NTLM TlRMTVNTUAACAAAABgAGADgAAAAFgokCHIACAAYAHgAAAAYABgBEAAAABAAEAFoAAAADgAwBDgAAAA9DAE9SUAIAAAR"
        "EAEMATwBSAFAABgAcAEUAQQBTAFQARQBSATAAEABFAEEAUwBUAEUAUgABAAYARQBBAFMAVABFAFIAAwAcAEUAQQBTAFQARQBSAA4AAAQ"
        "ARQBBAFMAVABFAFIABAAAAA="
    )

    print(f"\nType 2 Message (Challenge) from server")

    # Type 3 response
    type3_headers = handler.handle_challenge(type2_challenge)
    print(f"\nType 3 Message (Authenticate):")
    for key, value in type3_headers.items():
        if "Authorization" in key:
            print(f"  {key}: {value[:60]}...")
        else:
            print(f"  {key}: {value}")

    print()


def example_4_certificate_auth():
    """Example 4: Certificate-based authentication."""
    print("=" * 70)
    print("EXAMPLE 4: Certificate-Based Authentication (mTLS)")
    print("=" * 70)

    config = ProxyConfig(
        proxy_url="https://secure-proxy.example.com:8443",
        auth_type=AuthType.CERTIFICATE,
        cert_path="/path/to/client-cert.pem",
        key_path="/path/to/client-key.pem",
        ca_bundle="/path/to/ca-bundle.pem",
        verify_ssl=True
    )

    handler = ProxyAuthHandler(config)

    print(f"\nProxy URL: {handler.get_proxy_url()}")
    print(f"Auth Type: {config.auth_type.value}")
    print(f"Verify SSL: {config.verify_ssl}")

    conn_config = handler.get_connection_config()

    print(f"\nConnection Configuration:")
    for key, value in conn_config.items():
        print(f"  {key}: {value}")

    print()


def example_5_custom_headers():
    """Example 5: Custom headers and advanced configuration."""
    print("=" * 70)
    print("EXAMPLE 5: Custom Headers & Advanced Configuration")
    print("=" * 70)

    custom_headers = {
        "User-Agent": "Custom-HTTP-Client/1.0",
        "X-Correlation-ID": "req-12345-67890",
        "X-API-Key": "api-key-xyz",
    }

    config = ProxyConfig(
        proxy_url="http://corporate-proxy.example.com:3128",
        auth_type=AuthType.BASIC,
        username="employee@corp.com",
        password="corporate_password",
        custom_headers=custom_headers,
        timeout=60,
        verify_ssl=True
    )

    handler = ProxyAuthHandler(config)

    print(f"\nProxy URL: {handler.get_proxy_url()}")
    print(f"Auth Type: {config.auth_type.value}")
    print(f"Timeout: {config.timeout}s")

    all_headers = handler.get_auth_headers()

    print(f"\nAll Headers (Auth + Custom):")
    for key, value in all_headers.items():
        if "Authorization" in key or "password" in key:
            print(f"  {key}: [REDACTED]")
        else:
            print(f"  {key}: {value}")

    print()


def example_6_convenience_function():
    """Example 6: Using convenience function."""
    print("=" * 70)
    print("EXAMPLE 6: Convenience Function - create_auth_handler()")
    print("=" * 70)

    # Basic auth with convenience function
    handler = create_auth_handler(
        proxy_url="http://proxy.example.com:8080",
        auth_type="basic",
        username="quick_user",
        password="quick_pass",
        timeout=30
    )

    print(f"\nCreated handler using convenience function:")
    print(f"  Proxy: {handler.get_proxy_url()}")
    print(f"  Auth Type: {handler.config.auth_type.value}")
    print(f"  Timeout: {handler.config.timeout}s")

    headers = handler.get_auth_headers()
    print(f"  Auth Headers: {list(headers.keys())}")

    print()


def example_7_multiple_schemes():
    """Example 7: Comparing all authentication schemes."""
    print("=" * 70)
    print("EXAMPLE 7: Comparison of All Authentication Schemes")
    print("=" * 70)

    schemes = [
        ("basic", {"username": "user", "password": "pass"}),
        ("digest", {"username": "user", "password": "pass"}),
        ("ntlm", {"username": "user", "password": "pass", "domain": "CORP"}),
    ]

    for auth_type, auth_params in schemes:
        print(f"\n{auth_type.upper()} Authentication:")
        print("-" * 50)

        try:
            handler = create_auth_handler(
                proxy_url="http://proxy.example.com:8080",
                auth_type=auth_type,
                **auth_params
            )

            config = handler.get_connection_config()
            print(f"  URL: {config['proxy_url']}")
            print(f"  Type: {config['auth_type']}")
            print(f"  Timeout: {config['timeout']}s")

            # Show initial headers
            headers = handler.get_auth_headers()
            if headers:
                print(f"  Initial Headers: {list(headers.keys())}")

        except Exception as e:
            print(f"  Error: {e}")

    print()


def example_8_configuration_export():
    """Example 8: Export configuration."""
    print("=" * 70)
    print("EXAMPLE 8: Configuration Export to JSON")
    print("=" * 70)

    config = ProxyConfig(
        proxy_url="http://proxy.example.com:8080",
        auth_type=AuthType.BASIC,
        username="export_user",
        password="export_pass",
        timeout=45,
        verify_ssl=True
    )

    handler = ProxyAuthHandler(config)

    print("\nConfiguration as JSON (safe - no credentials):")
    json_config = handler.to_json()
    print(json_config)

    print()


def example_9_error_handling():
    """Example 9: Error handling and validation."""
    print("=" * 70)
    print("EXAMPLE 9: Error Handling & Validation")
    print("=" * 70)

    print("\nTest 1: Missing credentials for Basic auth")
    print("-" * 50)
    try:
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.BASIC,
            username="user"
            # Missing password
        )
    except ValueError as e:
        print(f"  Caught expected error: {e}")

    print("\nTest 2: Missing certificate for certificate auth")
    print("-" * 50)
    try:
        config = ProxyConfig(
            proxy_url="https://secure-proxy.example.com:8443",
            auth_type=AuthType.CERTIFICATE,
            cert_path="/nonexistent/cert.pem",
            key_path="/nonexistent/key.pem"
        )
    except FileNotFoundError as e:
        print(f"  Caught expected error: {e}")

    print("\nTest 3: Invalid proxy URL")
    print("-" * 50)
    try:
        config = ProxyConfig(
            proxy_url="invalid-url",
            auth_type=AuthType.BASIC,
            username="user",
            password="pass"
        )
        handler = ProxyAuthHandler(config)
        print(f"  Created handler with URL: {handler.get_proxy_url()}")
    except Exception as e:
        print(f"  Error: {e}")

    print()


def example_10_production_usage():
    """Example 10: Production usage pattern."""
    print("=" * 70)
    print("EXAMPLE 10: Production Usage Pattern")
    print("=" * 70)

    print("\nProduction Example: HTTP Client with Proxy Auth")
    print("-" * 50)

    # Create handler
    handler = create_auth_handler(
        proxy_url="http://proxy.corp.com:8080",
        auth_type="basic",
        username="service_account",
        password="rotating_password_123",
        timeout=30
    )

    # Get configuration for HTTP client
    proxy_config = handler.get_connection_config()
    auth_headers = handler.get_auth_headers()

    print(f"\nStep 1: Get proxy configuration")
    print(f"  Proxy URL: {proxy_config['proxy_url']}")
    print(f"  Auth Type: {proxy_config['auth_type']}")

    print(f"\nStep 2: Prepare HTTP request headers")
    print(f"  Headers to include:")
    for key in auth_headers.keys():
        print(f"    - {key}")

    print(f"\nStep 3: Make HTTP request through proxy")
    print(f"  Example Python requests:")
    print(f"    import requests")
    print(f"    session = requests.Session()")
    print(f"    session.proxies = {{'http': '{proxy_config['proxy_url']}'}}")
    print(f"    session.headers.update({auth_headers})")
    print(f"    response = session.get('http://api.example.com/data')")

    print(f"\nStep 4: Handle authentication challenges")
    challenge = 'Basic realm="Proxy Server"'
    print(f"  Server challenge: {challenge}")
    response = handler.handle_challenge(challenge)
    print(f"  Generated response headers: {list(response.keys())}")

    print()


def main():
    """Run all examples."""
    examples = [
        example_1_basic_auth,
        example_2_digest_auth,
        example_3_ntlm_auth,
        example_4_certificate_auth,
        example_5_custom_headers,
        example_6_convenience_function,
        example_7_multiple_schemes,
        example_8_configuration_export,
        example_9_error_handling,
        example_10_production_usage,
    ]

    print("\n")
    print("=" * 70)
    print("PROXY AUTHENTICATION HANDLER - USAGE EXAMPLES")
    print("=" * 70)
    print()

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}\n")

    print("=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
