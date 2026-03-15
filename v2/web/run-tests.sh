#!/bin/bash

# ACQUISITOR Test Runner
# Runs all E2E tests for the 46 user stories

echo "=========================================="
echo "🧪 ACQUISITOR Test Runner"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if API is running
echo "🔍 Checking API server..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ API server is running${NC}"
else
    echo -e "${RED}❌ API server not running. Start it first:${NC}"
    echo "   cd v2/api && python3 main.py"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules/@playwright" ]; then
    echo "📦 Installing Playwright..."
    npm install
    npx playwright install
fi

echo ""
echo "=========================================="
echo "🚀 Running Test Suite"
echo "=========================================="
echo ""

# Run tests based on argument
case "${1:-all}" in
    "auth")
        echo -e "${BLUE}📝 Running Authentication Tests (US-001)${NC}"
        npx playwright test auth/
        ;;
    "onboarding")
        echo -e "${BLUE}📝 Running Onboarding Tests (US-002-009)${NC}"
        npx playwright test onboarding/
        ;;
    "dashboard")
        echo -e "${BLUE}📝 Running Dashboard Tests (US-010-012)${NC}"
        npx playwright test dashboard/
        ;;
    "leads")
        echo -e "${BLUE}📝 Running Lead Tests (US-013-018)${NC}"
        npx playwright test leads/
        ;;
    "pipeline")
        echo -e "${BLUE}📝 Running Pipeline Tests (US-019-022)${NC}"
        npx playwright test pipeline/
        ;;
    "crm")
        echo -e "${BLUE}📝 Running CRM Tests (US-023-028)${NC}"
        npx playwright test crm/
        ;;
    "email")
        echo -e "${BLUE}📝 Running Email Tests (US-029-032)${NC}"
        npx playwright test email/
        ;;
    "settings")
        echo -e "${BLUE}📝 Running Settings Tests (US-033-036)${NC}"
        npx playwright test settings/
        ;;
    "import")
        echo -e "${BLUE}📝 Running Import Tests (US-037-040)${NC}"
        npx playwright test import/
        ;;
    "p0")
        echo -e "${YELLOW}📝 Running P0 Critical Tests${NC}"
        npx playwright test --grep "P0"
        ;;
    "p1")
        echo -e "${YELLOW}📝 Running P1 Important Tests${NC}"
        npx playwright test --grep "P1"
        ;;
    "ui")
        echo -e "${GREEN}🖥️  Opening Playwright UI Mode${NC}"
        npx playwright test --ui
        ;;
    "debug")
        echo -e "${GREEN}🐛 Running in Debug Mode${NC}"
        npx playwright test --debug
        ;;
    "report")
        echo -e "${BLUE}📊 Showing Test Report${NC}"
        npx playwright show-report
        ;;
    "all"|*)
        echo -e "${GREEN}🧪 Running All 46 User Story Tests${NC}"
        echo ""
        npx playwright test
        ;;
esac

echo ""
echo "=========================================="
echo "✅ Test Run Complete"
echo "=========================================="
echo ""
echo "View report: npm run test:report"
echo ""
