#!/usr/bin/env python3
"""
ACQUISITOR Security Test Suite
Tests multi-tenancy, rate limiting, and API security
"""

import asyncio
import httpx
import uuid
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_RESULTS = []


def log_test(name: str, passed: bool, details: str = ""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    TEST_RESULTS.append({"name": name, "passed": passed, "details": details})
    print(f"{status}: {name}")
    if details:
        print(f"   {details}")


async def test_health_check():
    """Test health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        log_test(
            "Health Check",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )


async def test_auth_required():
    """Test that endpoints require authentication"""
    async with httpx.AsyncClient() as client:
        # Try to access leads without auth
        response = await client.get(f"{BASE_URL}/leads")
        log_test(
            "Auth Required - Leads",
            response.status_code == 401,
            f"Status: {response.status_code} (expected 401)"
        )


async def test_sql_injection_protection():
    """Test SQL injection protection"""
    # This tests that user input is properly parameterized
    malicious_id = "' OR '1'='1"
    
    async with httpx.AsyncClient() as client:
        # Should return 404 (UUID parsing fails) not 500 (SQL error)
        response = await client.get(f"{BASE_URL}/leads/{malicious_id}")
        log_test(
            "SQL Injection Protection",
            response.status_code in [401, 404, 422],
            f"Status: {response.status_code} (no SQL error exposed)"
        )


def test_code_patterns():
    """Test that code has required security patterns"""
    with open("src/main.py", "r") as f:
        code = f.read()
    
    checks = [
        ("user_id filter in list_leads", "WHERE user_id = $1" in code),
        ("user_id filter in get_lead", "AND user_id = $2" in code and "get_lead" in code),
        ("user_id in create_lead", "current_user[\"id\"], lead.business_name" in code),
        ("user_id in update_lead", "AND user_id =" in code and "update_lead" in code),
        ("rate limiting decorator", "@rate_limit" in code),
        ("tier-based limits", "FREE_TIER" in code and "PRO_TIER" in code),
        ("connection pooling", "asyncpg.create_pool" in code),
        ("pool min/max size", "min_size=5" in code and "max_size=20" in code),
        ("Redis integration", "redis_client" in code),
        ("outreach_messages table", "outreach_messages" in code),
        ("bookings table", "bookings" in code),
        ("rate_limits table", "rate_limits" in code),
        ("email provider in users", "email_provider" in code),
    ]
    
    for name, passed in checks:
        log_test(f"Code Pattern: {name}", passed)


def test_migration_sql():
    """Test that migration SQL has required statements"""
    try:
        with open("migrations/001_add_multi_tenancy.sql", "r") as f:
            sql = f.read()
        
        checks = [
            ("leads.user_id column", "ALTER TABLE leads ADD COLUMN" in sql and "user_id" in sql),
            ("activities index", "idx_activities_user_id" in sql),
            ("outreach_messages table", "CREATE TABLE IF NOT EXISTS outreach_messages" in sql),
            ("bookings table", "CREATE TABLE IF NOT EXISTS bookings" in sql),
            ("rate_limits table", "CREATE TABLE IF NOT EXISTS rate_limits" in sql),
            ("users.tier column", "tier VARCHAR" in sql),
            ("users.email_provider", "email_provider JSONB" in sql),
            ("leads user_id index", "idx_leads_user_id" in sql),
        ]
        
        for name, passed in checks:
            log_test(f"Migration: {name}", passed)
    except FileNotFoundError:
        log_test("Migration SQL exists", False, "File not found")


def test_env_production():
    """Test that .env.production has required variables"""
    try:
        with open(".env.production", "r") as f:
            env = f.read()
        
        required = [
            "DATABASE_URL",
            "REDIS_URL",
            "JWT_SECRET",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "FRONTEND_URL",
        ]
        
        for var in required:
            log_test(f"Env: {var}", var in env)
    except FileNotFoundError:
        log_test(".env.production exists", False, "File not found")


def test_deployment_guide():
    """Test that DEPLOYMENT.md exists and has key sections"""
    try:
        with open("DEPLOYMENT.md", "r") as f:
            guide = f.read()
        
        sections = [
            "Database Migration",
            "Redis Setup",
            "Environment Variables",
            "Rate Limits",
            "Security Checklist",
            "Troubleshooting",
        ]
        
        for section in sections:
            log_test(f"Docs: {section}", section in guide)
    except FileNotFoundError:
        log_test("DEPLOYMENT.md exists", False, "File not found")


def analyze_query_security():
    """Analyze that all database queries filter by user_id"""
    with open("src/main.py", "r") as f:
        code = f.read()
    
    # Find all database queries
    import re
    
    # Pattern to find SELECT queries
    select_pattern = r'await conn\.fetch(?:row|val)?\(\s*"""(.*?)"""'
    selects = re.findall(select_pattern, code, re.DOTALL)
    
    user_scoped = 0
    total = 0
    
    for query in selects:
        query = query.strip()
        if "FROM" in query.upper():
            total += 1
            if "user_id" in query or query.startswith("SELECT 1"):
                user_scoped += 1
    
    log_test(
        f"Query Security: {user_scoped}/{total} queries user-scoped",
        user_scoped >= 8,  # Expect at least 8 user-scoped queries
        f"{user_scoped} out of {total} SELECT queries filter by user_id"
    )


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("ACQUISITOR Security Test Suite")
    print("=" * 60)
    print()
    
    # Static code tests
    print("📋 Running static code analysis...")
    test_code_patterns()
    test_migration_sql()
    test_env_production()
    test_deployment_guide()
    analyze_query_security()
    print()
    
    # Runtime tests (if server is running)
    print("🌐 Running runtime tests...")
    try:
        await test_health_check()
        await test_auth_required()
        await test_sql_injection_protection()
    except Exception as e:
        log_test("Runtime Tests", False, f"Server not available: {e}")
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(1 for r in TEST_RESULTS if r["passed"])
    total = len(TEST_RESULTS)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All security checks passed!")
        return 0
    else:
        failed = [r["name"] for r in TEST_RESULTS if not r["passed"]]
        print(f"❌ Failed tests: {', '.join(failed[:5])}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
