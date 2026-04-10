# CLAUDE SYSTEM RULES — ESP32 Firmware (Professional Mode)

You are generating production-grade firmware for ESP32.

Platform:
- ESP32 (S2 / S3 / C3)
- PlatformIO
- Arduino framework (ESP-IDF + FreeRTOS)
- C++17

---

# ARCHITECTURE (MANDATORY)

FreeRTOS is mandatory.

Rules:
- Each peripheral/protocol runs in its own Task.
- Tasks communicate only via Queue.
- Synchronization only via Queue, EventGroup or Mutex.
- No blind polling.
- No delay().
- Use vTaskDelay(pdMS_TO_TICKS(ms)).
- Every blocking call must define a timeout macro in config.h.

Task Priorities:
- Low (1-2): logging, filesystem, display
- Medium (3): protocols (MQTT, Modbus, API, network)
- High (4-5): real-time acquisition (sensors, RFID)
- Never use configMAX_PRIORITIES without documented justification.

ISR:
- ISR must be minimal.
- ISR may only send to Queue or set EventGroup bits.
- No logic inside ISR.

---

# ABSOLUTE PROHIBITIONS

NEVER:
- Use malloc/free after initialization
- Use Arduino String
- Use sprintf (use snprintf with fixed buffer)
- Use float/double in time-critical path
- Block without timeout
- Ignore FreeRTOS return values
- Access shared peripheral without mutex
- Build JSON manually (must use ArduinoJson v7+)
- Use Doxygen-style comments (`/** */`, `@param`, `@return`, `@brief`, `@file`). Use plain C/C++ comments only (`//` or `/* */`)

If any rule is broken, warn explicitly.

---

# SEPARATION OF CONCERNS (CRITICAL)

## Pure Logic Functions

Must:
- Be hardware-independent
- Not call FreeRTOS
- Not access hardware globals
- Be testable in env:native

Contain:
- State machines
- Parsing
- Validation
- Calculations
- Payload assembly
- Business logic

## Tasks

Must contain only:
- Hardware initialization
- Peripheral I/O
- Network I/O
- Queue/Event handling
- Calls to pure logic

Tasks must NOT contain:
- Business rules
- State machine logic
- Heavy parsing logic

---

# CODE STRUCTURE

```
project/
├── include/
│   └── config.h
├── src/
│   ├── tasks/
│   ├── drivers/ (only if truly necessary)
│   ├── app_logic.cpp
│   ├── app_<module>.cpp
│   └── main.cpp
├── test/
│   ├── stubs/
│   ├── fakes/
│   ├── mocks/
│   └── test_<module>/
├── data/
└── platformio.ini
```

Naming:
- Functions: module_action()
- Globals: g_variable
- Defines: ALL_CAPS
- No magic numbers (stack, timeouts, buffer sizes)

---

# TASK RULES

- Stack defined by macro in config.h
- Priority justified according to table
- Measure stack high watermark in debug
- Long processing must be cooperative
- Tasks performing long operations must periodically yield

---

# MEMORY RULES

- Prefer static allocation
- Large buffers must be global static
- No dynamic JSON allocation
- No heap fragmentation risk

## Shared Globals

- Global written by ONE task, read by others: allowed if atomic type (uint8_t, int32_t, bool)
- Global written by MULTIPLE tasks: mandatory mutex or queue
- Prefer encapsulating with getter function (module_get_value()) to prevent external writes
- Naming: always g_ prefix

---

# PERSISTENCE RULES

- NVS (Preferences.h): user settings (SSID, IP, tokens, credentials)
- LittleFS: logs, offline cache, web portal files
- Never use SPIFFS
- Never hardcode mutable configuration

---

# COMMUNICATION

- JSON: mandatory ArduinoJson v7+
- Build payloads via JsonDocument only
- HTTP: use Arduino ecosystem libraries
- Each protocol runs in its own Task
- Always consider offline fallback with LittleFS cache

---

# TESTING (MANDATORY DESIGN)

Code must allow:
- Unit tests in env:native
- On-target tests on ESP32
- Unity framework
- 1 scenario per test
- < 1 second runtime

Use:
- Stub for fixed return
- Fake for simplified implementation
- Mock when behavior must be verified

Every fake must implement:
`fake_<module>_reset()`

Include in platformio.ini:
```ini
[env:native]
platform = native
test_framework = unity
```

---

# LOGGING

- Use Serial.printf() for all log output
- Purpose: diagnostic output for debugging via serial monitor
- Every task must log on start: `Serial.printf("[TASK_NAME] started\n")`
- Log state transitions, errors, and key events
- Log format: `[MODULE] message` (e.g. `[MQTT] connected to broker`)
- Never use Serial.println() with String concatenation
- Keep log messages short — serial bandwidth is limited
- In release builds, reduce verbosity (log only errors and state changes)

---

# RELIABILITY

- loop() must remain alive (TWDT)
- Critical init failure → log + ESP.restart()
- Arduino/ESP-IDF is the HAL (no unnecessary abstraction)
- No overengineering
- No speculative abstraction
- No unnecessary wrapper layers

---

# RESPONSE FORMAT

When generating firmware:
1. Brief architecture explanation (max 10 lines)
2. Show:
   - Pure logic file
   - Task file
   - Relevant config.h additions
3. No unused abstractions
4. No invented frameworks
5. Keep code deterministic and testable

---

# LANGUAGE

- Code: English
- Comments: Portuguese
- Communication: Brazilian Portuguese

If architecture violates these rules, consider the solution invalid.

---

# VALIDATION AFTER CODE CHANGES (MANDATORY)

After ANY code change, always:
1. Run `pio run` to compile — this ALWAYS runs, even without hardware
2. If compilation succeeds AND hardware is connected:
   - Run `pio run --target upload` to flash
   - Run `pio device monitor` to check serial output
   - Confirm the change worked correctly
3. If upload fails with connection/port error, assume no hardware — compilation success is sufficient

Never leave a code change without at least compiling successfully.
