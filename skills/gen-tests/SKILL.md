---
name: gen-tests
description: Gera testes unitários para módulos de firmware ESP32 (baseado em Memfault best practices)
---

Generate unit tests for the current ESP32 firmware project.
Reference: https://interrupt.memfault.com/blog/unit-testing-basics

# STEP 1: Identify testable code

Scan `src/` for pure logic functions (app_logic.cpp, app_<module>.cpp).
Testable functions:
- Do NOT depend on hardware (no Arduino.h, no SPI, no GPIO)
- Do NOT call FreeRTOS (no xQueueSend, no xSemaphoreTake)
- Receive data and return results

Also scan tasks for business logic that SHOULD be extracted.
If found, warn:
"WARN: Function X in task_Y.cpp contains business logic. Extract to app_logic.cpp for testability."

# STEP 2: Classify dependencies

For each testable function, classify ALL dependencies:

**ONE real implementation** — the module under test. Everything else must be a test double.

Test doubles (simplest wins):
1. **Stub** (first choice): irrelevant dependency. Returns canned value, no logic.
   - Use for: logging, analytics, Serial.print, time functions
2. **Fake** (when stub is not enough): simplified working implementation.
   - Use for: mutex, filesystem, NVS, queues
   - MUST track state (lock_count, write history, call count)
   - MUST have `fake_<module>_reset()` to clear state between tests
   - MUST have verification helpers (e.g. `fake_mutex_all_unlocked()`)
3. **Mock** (last resort): test-controlled, verifies calls and arguments.
   - Use for: HTTP send, webhook dispatch, external API calls
   - MUST track: call_count, last arguments, configurable return value

Rule: Do NOT mock what can be faked. Do NOT fake what can be stubbed.

# STEP 3: Generate directory structure

```
test/
├── header_overrides/           # Simplified versions of complex headers
│   └── <header>.h              # Override auto-generated or hardware headers
├── stubs/
│   └── stub_<module>.h         # One per stubbed dependency
├── fakes/
│   ├── fake_<module>.h
│   └── fake_<module>.c         # With reset() and verification helpers
├── mocks/
│   ├── mock_<module>.h
│   └── mock_<module>.c         # With configurable returns and call tracking
└── test_<module>/
    └── test_main.cpp           # One file per tested module
```

# STEP 4: Generate test files

## Test file pattern
```cpp
#include <unity.h>

// Stubs/fakes/mocks BEFORE module under test
#include "../stubs/stub_log.h"
#include "../fakes/fake_mutex.h"

// Module under test
extern "C" {
    #include "app_logic.h"
}

void setUp(void) {
    // Reset ALL fakes before each test — clean state isolation
    fake_mutex_reset();
}

void tearDown(void) {
    // Verify clean state — catches deadlocks, leaks, dangling locks
    TEST_ASSERT_TRUE_MESSAGE(
        fake_mutex_all_unlocked(),
        "DEADLOCK: mutex still locked after test"
    );
}

// One function, one scenario, one assertion focus
void test_<function>_<scenario>(void) {
    // Arrange — setup inputs and preconditions
    // Act — call function under test
    // Assert — verify output
    TEST_ASSERT_EQUAL(expected, actual);
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_<function>_<scenario>);
    UNITY_END();
    return 0;
}
```

## Stub pattern
```cpp
// stub_<module>.h
#pragma once

// Does nothing. Returns safe default. No state.
void log_write(const char* msg) { (void)msg; return; }
int analytics_inc(int key) { (void)key; return 0; }
```

## Fake pattern (with state tracking and verification)
```cpp
// fake_mutex.h
#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FAKE_MAX_MUTEXES 64

typedef struct {
    uint8_t lock_count;
} FakeMutex;

static FakeMutex s_mutexes[FAKE_MAX_MUTEXES];
static uint32_t s_mutex_index = 0;

// Reset — MUST be called in setUp()
void fake_mutex_reset(void) {
    memset(s_mutexes, 0, sizeof(s_mutexes));
    s_mutex_index = 0;
}

// Verification helper — call in tearDown()
bool fake_mutex_all_unlocked(void) {
    for (int i = 0; i < FAKE_MAX_MUTEXES; i++) {
        if (s_mutexes[i].lock_count > 0) return false;
    }
    return true;
}

// Fake implementation
void* mutex_create(void) {
    return &s_mutexes[s_mutex_index++];
}
void mutex_lock(void* m) { ((FakeMutex*)m)->lock_count++; }
void mutex_unlock(void* m) { ((FakeMutex*)m)->lock_count--; }
```

## Mock pattern (with call tracking and configurable return)
```cpp
// mock_http.h
#pragma once
#include <string.h>

typedef struct {
    int return_code;            // Pre-program this in test
    int call_count;             // Verify after test
    char last_url[256];         // Inspect arguments
    char last_body[512];
} MockHTTP;

static MockHTTP mock_http = {0};

void mock_http_reset(void) {
    memset(&mock_http, 0, sizeof(mock_http));
}

int http_post(const char* url, const char* body) {
    mock_http.call_count++;
    strncpy(mock_http.last_url, url, sizeof(mock_http.last_url) - 1);
    strncpy(mock_http.last_body, body, sizeof(mock_http.last_body) - 1);
    return mock_http.return_code;
}
```

## Header override pattern
```cpp
// header_overrides/<header>.h
// Simplified version of complex/auto-generated header
// Only include types and defines needed for compilation
```

# STEP 5: Verify platformio.ini

Check if `[env:native]` exists in platformio.ini. If not, add:
```ini
[env:native]
platform = native
test_framework = unity
build_flags =
    -std=c++17
    -fsanitize=address
    -fno-omit-frame-pointer
    -Itest/header_overrides
test_build_src_filter =
    +<../test/stubs/>
    +<../test/fakes/>
    +<../test/mocks/>
```

The `-fsanitize=address` flag detects:
- Use-after-free
- Buffer overflow
- Heap memory errors

# STEP 6: Generate coverage script (optional)

If lcov is available, create `test/run_coverage.sh`:
```bash
#!/bin/bash
pio test -e native --verbose
lcov --capture --directory .pio/build/native/ --output-file coverage.info
lcov --remove coverage.info '*/test/*' --output-file coverage.info
genhtml coverage.info --output-directory test/coverage_report
echo "Open test/coverage_report/index.html"
```

# RULES

- Include ONE real implementation per test file — stub/fake/mock everything else
- Each test = one scenario, one function focus
- Test names: `test_<function>_<scenario>` (descriptive, English)
- Test comments in Portuguese
- Every fake MUST have `reset()` called in setUp()
- Every fake MUST have verification helper called in tearDown()
- Tests must compile with `pio test -e native`
- Tests must run in < 1 second
- If undefined symbol error → create stub for that function
- If duplicate symbol error → remove duplicate (only one implementation per dependency)
- Generate tests ONLY for existing pure logic — do not invent functions
- If no pure logic exists, warn and list what to extract from tasks
