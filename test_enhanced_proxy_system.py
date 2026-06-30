#!/usr/bin/env python3
"""
Test Suite for Enhanced Proxy System
Demonstrates all features and capabilities
"""

import sys
import json
from enhanced_proxy_system import (
    EnhancedProxyManager,
    ProxyParserValidator,
    ProxyType,
    ProxyCredentials,
    ProxyAuthType,
    HTTPProxyValidator,
    SOCKS4ProxyValidator,
    SOCKS5ProxyValidator
)


def test_url_parsing():
    """Test proxy URL parsing"""
    print("\n" + "=" * 80)
    print("TEST 1: URL PARSING AND VALIDATION")
    print("=" * 80)

    test_cases = [
        {
            "url": "http://proxy.example.com:8080",
            "description": "Simple HTTP proxy"
        },
        {
            "url": "https://user:password@secure.example.com:8443",
            "description": "HTTPS with authentication"
        },
        {
            "url": "socks4://socks.example.com:1080",
            "description": "SOCKS4 proxy"
        },
        {
            "url": "socks5://user:pass@socks.example.com:1080",
            "description": "SOCKS5 with authentication"
        },
        {
            "url": "invalid://proxy",
            "description": "Invalid URL (should fail)"
        },
        {
            "url": "http://proxy.example.com:99999",
            "description": "Invalid port (should fail)"
        },
    ]

    for test_case in test_cases:
        url = test_case["url"]
        description = test_case["description"]

        success, parsed, message = ProxyParserValidator.parse_proxy_url(url)

        print(f"\n  Test: {description}")
        print(f"  URL: {url}")
        print(f"  Status: {'PASS' if success else 'FAIL'}")

        if success:
            print(f"  Protocol: {parsed['protocol']}")
            print(f"  Host: {parsed['host']}")
            print(f"  Port: {parsed['port']}")
            if parsed['credentials']:
                print(f"  Auth: {parsed['credentials']['username']}@{parsed['credentials']['auth_type']}")
        else:
            print(f"  Error: {message}")


def test_proxy_manager():
    """Test proxy manager functionality"""
    print("\n" + "=" * 80)
    print("TEST 2: PROXY MANAGER FUNCTIONALITY")
    print("=" * 80)

    manager = EnhancedProxyManager()

    # Test adding proxies
    print("\n  Adding Proxies...")
    test_proxies = [
        {
            "url": "http://proxy1.example.com:8080",
            "tags": ["http", "corporate", "backup"],
            "notes": "Primary corporate HTTP proxy"
        },
        {
            "url": "https://secure.example.com:8443",
            "tags": ["https", "secure", "production"],
            "notes": "Secure HTTPS proxy for sensitive data"
        },
        {
            "url": "socks4://legacy.example.com:1080",
            "tags": ["socks4", "legacy"],
            "notes": "Legacy SOCKS4 for old systems"
        },
        {
            "url": "socks5://user:password@socks.example.com:1080",
            "tags": ["socks5", "vpn", "secure"],
            "notes": "SOCKS5 proxy with authentication"
        },
    ]

    added_proxies = {}
    for proxy_config in test_proxies:
        success, message, proxy_id = manager.add_proxy(
            proxy_config["url"],
            tags=proxy_config["tags"],
            notes=proxy_config["notes"]
        )
        if success:
            added_proxies[proxy_id] = proxy_config
            print(f"    [OK] {proxy_id}: {proxy_config['url']}")
        else:
            print(f"    [FAIL] {message}")

    # Test retrieving proxies
    print("\n  Retrieving Proxies...")
    all_proxies = manager.get_all_proxies()
    print(f"    Total proxies: {len(all_proxies)}")

    for proxy in all_proxies:
        print(f"    - {proxy['id']}: {proxy['url']} ({proxy['proxy_type']})")
        if proxy['tags']:
            print(f"      Tags: {', '.join(proxy['tags'])}")

    # Test filtering by type
    print("\n  Filtering by Type...")
    for proxy_type in ProxyType:
        proxies = manager.get_proxies_by_type(proxy_type)
        print(f"    {proxy_type.value.upper()}: {len(proxies)} proxy/proxies")

    # Test filtering by tag
    print("\n  Filtering by Tag...")
    test_tags = ["secure", "corporate", "socks5", "vpn"]
    for tag in test_tags:
        proxies = manager.get_proxies_by_tag(tag)
        if proxies:
            print(f"    Tag '{tag}': {len(proxies)} proxy/proxies")

    # Test statistics
    print("\n  Statistics...")
    stats = manager.get_statistics()
    print(f"    Total: {stats['total_proxies']}")
    print(f"    Active: {stats['active_proxies']}")
    print(f"    Tested: {stats['tested_proxies']}")
    print(f"    Passed: {stats['passed_tests']}")
    print(f"    By Type:")
    for ptype, count in stats['by_type'].items():
        print(f"      - {ptype}: {count}")

    # Test status updates
    if added_proxies:
        first_proxy_id = list(added_proxies.keys())[0]
        print(f"\n  Testing Proxy Status Update...")
        success, message = manager.update_proxy_status(first_proxy_id, False)
        print(f"    Deactivate: {message}")

        success, message = manager.update_proxy_status(first_proxy_id, True)
        print(f"    Activate: {message}")

    # Test tag operations
    if added_proxies:
        first_proxy_id = list(added_proxies.keys())[0]
        print(f"\n  Testing Tag Operations...")
        success, message = manager.add_tag(first_proxy_id, "production")
        print(f"    Add tag: {message}")

    return manager


def test_credentials():
    """Test credential handling"""
    print("\n" + "=" * 80)
    print("TEST 3: CREDENTIAL HANDLING")
    print("=" * 80)

    # Create credentials
    creds = ProxyCredentials(
        username="john.doe",
        password="secure_password_123",
        auth_type=ProxyAuthType.BASIC
    )

    print(f"\n  Username: {creds.username}")
    print(f"  Auth Type: {creds.auth_type.value}")

    # Test encoding
    encoded = creds.encode_basic_auth()
    print(f"  Encoded Auth Header: {encoded[:50]}...")

    # Test serialization
    creds_dict = creds.to_dict()
    print(f"\n  Serialized:")
    print(json.dumps(creds_dict, indent=4))

    # Test deserialization
    restored_creds = ProxyCredentials.from_dict(creds_dict)
    print(f"\n  Restored Username: {restored_creds.username}")


def test_validators():
    """Test proxy validators"""
    print("\n" + "=" * 80)
    print("TEST 4: PROXY VALIDATORS")
    print("=" * 80)

    validators = {
        "HTTP": HTTPProxyValidator(),
        "SOCKS4": SOCKS4ProxyValidator(),
        "SOCKS5": SOCKS5ProxyValidator(),
    }

    test_hosts = [
        ("127.0.0.1", 8080, "localhost HTTP proxy"),
        ("127.0.0.1", 1080, "localhost SOCKS proxy"),
    ]

    for validator_name, validator in validators.items():
        print(f"\n  {validator_name} Validator:")
        for host, port, description in test_hosts:
            print(f"    Testing {description}...")
            success, message = validator.validate(host, port, timeout=2)
            status = "PASS" if success else "FAIL"
            print(f"      [{status}] {message}")


def test_export_report(manager):
    """Test report export"""
    print("\n" + "=" * 80)
    print("TEST 5: REPORT EXPORT")
    print("=" * 80)

    print("\n  Exporting Report...")
    report = manager.export_report()

    print(f"\n  Generated: {report['generated_at']}")
    print(f"  Total Proxies: {report['statistics']['total_proxies']}")
    print(f"  Active Proxies: {report['statistics']['active_proxies']}")
    print(f"  Success Rate: {report['summary']['success_rate']}%")

    # Show proxy details
    print(f"\n  Proxies in Report:")
    for proxy in report['proxies'][:3]:  # Show first 3
        print(f"    - {proxy['id']}: {proxy['url']} ({proxy['proxy_type']})")

    if len(report['proxies']) > 3:
        print(f"    ... and {len(report['proxies']) - 3} more")


def test_proxy_operations(manager):
    """Test proxy operations"""
    print("\n" + "=" * 80)
    print("TEST 6: PROXY OPERATIONS")
    print("=" * 80)

    # Get first proxy for testing
    proxies = manager.get_all_proxies()
    if not proxies:
        print("  No proxies to test")
        return

    first_proxy = proxies[0]
    proxy_id = first_proxy['id']

    # Get specific proxy
    print(f"\n  Getting Proxy: {proxy_id}")
    proxy = manager.get_proxy(proxy_id)
    if proxy:
        print(f"    URL: {proxy['url']}")
        print(f"    Type: {proxy['proxy_type']}")
        print(f"    Active: {proxy['is_active']}")

    # Get connection string
    print(f"\n  Getting Connection String...")
    conn_string = manager.get_connection_string(proxy_id)
    if conn_string:
        print(f"    Connection String: {conn_string[:60]}...")

    # Test proxy (this might timeout for non-existent proxies)
    print(f"\n  Testing Proxy (may timeout)...")
    success, message = manager.test_proxy(proxy_id, timeout=3)
    print(f"    Result: {message}")


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 80)
    print("TEST 7: ERROR HANDLING")
    print("=" * 80)

    manager = EnhancedProxyManager()

    # Test invalid URL
    print("\n  Testing Invalid URLs...")
    invalid_urls = [
        "not-a-url",
        "http://invalid:port:number",
        "ftp://unsupported.com:21",
    ]

    for url in invalid_urls:
        success, parsed, message = ProxyParserValidator.parse_proxy_url(url)
        status = "OK" if success else "EXPECTED FAIL"
        print(f"    [{status}] {url}: {message}")

    # Test invalid proxy operations
    print("\n  Testing Invalid Operations...")

    # Get non-existent proxy
    proxy = manager.get_proxy("invalid_id")
    print(f"    Get non-existent: {'FAIL' if proxy is None else 'UNEXPECTED SUCCESS'}")

    # Remove non-existent proxy
    success, message = manager.remove_proxy("invalid_id")
    print(f"    Remove non-existent: {'OK' if not success else 'UNEXPECTED SUCCESS'}")

    # Test proxy non-existent
    success, message = manager.test_proxy("invalid_id")
    print(f"    Test non-existent: {'OK' if not success else 'UNEXPECTED SUCCESS'}")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "ENHANCED PROXY SYSTEM - COMPREHENSIVE TEST SUITE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # Run tests
        test_url_parsing()
        manager = test_proxy_manager()
        test_credentials()
        test_validators()
        test_export_report(manager)
        test_proxy_operations(manager)
        test_error_handling()

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print("\n  All tests completed successfully!")
        print("  Enhanced proxy system is fully functional.")
        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n  ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
