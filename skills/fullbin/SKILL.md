---
name: fullbin
description: Gera binario completo (bootloader + partitions + app + LittleFS) para gravar com esptool
---

Generate a single merged binary containing all flash partitions for the current PlatformIO ESP32 project.

# STEP 1: Identify the project

Find the PlatformIO project root (directory containing `platformio.ini`).
Read `platformio.ini` to determine:
- The target environment (e.g. `esp32-s3-devkitm-1`)
- The partition table CSV file (`board_build.partitions`)
- The filesystem type (`board_build.filesystem`, expect `littlefs`)

If the user passes an environment name as argument, use that. Otherwise use the first `[env:*]` found (skip `[env:native]`).

# STEP 2: Read FIRMWARE_VERSION

Read `include/config.h` and extract the current `FIRMWARE_VERSION` define.
Expected format: `#define FIRMWARE_VERSION "X.Y.Z"` or `#define FIRMWARE_VERSION "X.Y.Z_SUFFIX"`

The version MUST follow [Semantic Versioning](https://semver.org/lang/pt-BR/):
- MAJOR.MINOR.PATCH (e.g. `1.0.5`, `2.1.0`)
- Optional suffix after underscore (e.g. `1.0.5_JLCPCB`)

This version will be used to name the output file as: `DigitalPOB_v<VERSION>.bin`
Example: `FIRMWARE_VERSION "1.0.5_JLCPCB"` → `DigitalPOB_v1.0.5_JLCPCB.bin`

# STEP 3: Build firmware and filesystem

Run both builds sequentially:
```bash
pio run -e <ENV>
pio run -e <ENV> --target buildfs
```

Both must succeed before proceeding.

# STEP 4: Read partition table

Read the partition table CSV to find the offsets:
- `app0` (or `ota_0`) partition offset — this is where `firmware.bin` goes
- `spiffs` (or `littlefs`) partition offset — this is where the filesystem image goes

Also determine:
- Bootloader offset: `0x0` for ESP32-S3/C3, `0x1000` for ESP32 classic
- Partition table offset: `0x8000` (standard)

# STEP 5: Locate binaries

Find these files in `.pio/build/<ENV>/`:
- `bootloader.bin`
- `partitions.bin`
- `firmware.bin`
- `littlefs.bin` (or `spiffs.bin`)

All four must exist.

# STEP 6: Merge with esptool

Run esptool merge_bin:
```bash
python3 -m esptool --chip <CHIP> merge_bin \
    -o <PROJECT_ROOT>/DigitalPOB_v<VERSION>.bin \
    --flash_mode dio \
    --flash_size <FLASH_SIZE> \
    <BOOTLOADER_OFFSET> .pio/build/<ENV>/bootloader.bin \
    0x8000 .pio/build/<ENV>/partitions.bin \
    <APP_OFFSET> .pio/build/<ENV>/firmware.bin \
    <FS_OFFSET> .pio/build/<ENV>/littlefs.bin
```

Where:
- `<CHIP>`: derive from board (esp32s3, esp32s2, esp32c3, esp32)
- `<FLASH_SIZE>`: from `board_upload.flash_size` (e.g. `16MB`)
- `<BOOTLOADER_OFFSET>`: `0x0` for S3/S2/C3, `0x1000` for classic ESP32
- `<APP_OFFSET>`: from partition table (e.g. `0x10000`)
- `<FS_OFFSET>`: from partition table (e.g. `0x610000`)
- `<VERSION>`: from `FIRMWARE_VERSION` in config.h

# STEP 7: Update CHANGELOG.md

If `CHANGELOG.md` does not exist in the project root, create it with the template below.

The format is based on [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/pt-BR/).

If `CHANGELOG.md` already exists, check if the current version already has an entry.
- If it does, do NOT modify the changelog.
- If it does NOT, ask the user what changed and add a new entry at the top of the changelog (below the header).

Changelog entry format:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing features

### Fixed
- Bug fixes

### Removed
- Removed features
```

Only include sections that have content. Use Portuguese for descriptions.

Template for new CHANGELOG.md:
```markdown
# Changelog

Todas as mudancas notaveis neste projeto serao documentadas neste arquivo.

O formato e baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [X.Y.Z] - YYYY-MM-DD

### Added
- (ask user)
```

# STEP 8: Report result

Print:
- Output file name and size
- FIRMWARE_VERSION used
- The esptool command to flash it manually:
```
esptool.py --chip <CHIP> write_flash 0x0 DigitalPOB_v<VERSION>.bin
```

# RULES

- Use `python3 -m esptool` (installed by PlatformIO at `~/.platformio/penv/bin/python3`)
- If `~/.platformio/penv/bin/pio` is not in PATH, use full path
- Do NOT modify any project files (no platformio.ini changes, no extra_scripts)
- Do NOT modify config.h FIRMWARE_VERSION — only read it
- Do NOT upload — only generate the merged binary
- If any step fails, stop and report the error clearly
- Output file goes in the project root as `DigitalPOB_v<VERSION>.bin`
- FIRMWARE_VERSION in config.h is the single source of truth for versioning
