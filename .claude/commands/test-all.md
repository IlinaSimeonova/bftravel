---
name: test-all
description: Run complete test suite after feature implementation
---

Test the feature we just implemented:

@api-tester test all API endpoints involved in this feature. Create pytest files in correct app/tests structure.

@curl-tester test all HTML pages involved in this feature. Create test files in correct structure.

@e2e-tester create Playwright tests for the complete user flow. Take screenshots at each step.

@test-master audit the tests that were just created:
- Verify proper file structure and organization
- Identify any gaps in test coverage
- Refactor duplicate or inefficient tests
- Ensure all tests follow conventions