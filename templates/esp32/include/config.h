#pragma once

// ============================================================================
// {{PROJECT_NAME}} — Configurações globais
// {{PROJECT_DESCRIPTION}}
// ============================================================================

// ---- Serial ----
#define SERIAL_BAUD_RATE 115200

// ---- FreeRTOS task stacks ----
#define TASK_STACK_LOG       2048
#define TASK_STACK_PROTOCOL  4096
#define TASK_STACK_SENSOR    3072

// ---- Task priorities ----
#define TASK_PRIO_LOG       1
#define TASK_PRIO_DISPLAY   2
#define TASK_PRIO_PROTOCOL  3
#define TASK_PRIO_SENSOR    4

// ---- Timeouts (ms) ----
#define QUEUE_TIMEOUT_MS      100
#define MUTEX_TIMEOUT_MS      100
#define HTTP_REQUEST_TIMEOUT  10000
#define MQTT_CONNECT_TIMEOUT  5000

// ---- Queue sizes ----
#define QUEUE_SIZE_EVENTS   16
#define QUEUE_SIZE_SENSOR   8

// ---- Buffers ----
#define JSON_BUFFER_SIZE    512
#define HTTP_BUFFER_SIZE    1024
