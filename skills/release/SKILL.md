---
name: release
description: Gera binario OTA, commita, pusha e cria release no GitHub
---

Build, generate OTA binary, generate fullbin (complete flash image), commit, push and create a GitHub release for the current PlatformIO ESP32 project.

# STEP 1: Identify the project

Find the PlatformIO project root (directory containing `platformio.ini`).
Read `platformio.ini` to determine:
- The target environment (e.g. `esp32-s3-devkitm-1`)
- The partition table CSV file (`board_build.partitions`)
- The filesystem type (`board_build.filesystem`, expect `littlefs`)

If the user passes an environment name as argument, use that. Otherwise use the first `[env:*]` found (skip `[env:native]`).

# STEP 2: Read FIRMWARE_VERSION

Read `include/config.h` and extract the current `FIRMWARE_VERSION` define.
Expected format: `#define FIRMWARE_VERSION "PREFIX_X.Y.Z"` or `#define FIRMWARE_VERSION "X.Y.Z"`

Extract the version number (e.g. `1.0.0` from `DPOB_1.0.0`).
This version will be used for:
- Tag name: `v<VERSION>` (e.g. `v1.0.0`)
- OTA binary: `DigitalPOB_v<VERSION>_OTA.bin`
- Fullbin: `DigitalPOB_v<VERSION>.bin`

# STEP 3: Check for uncommitted changes

Run `git status` to check for uncommitted changes.
If there are changes:
- Stage the relevant files (never stage .bin files, .env, credentials)
- Commit with a descriptive message
- Push to the current branch

# STEP 4: Build firmware and filesystem

Run both builds sequentially using `~/.platformio/penv/bin/pio`:
```bash
pio run -e <ENV>
pio run -e <ENV> --target buildfs
```

Both must succeed before proceeding.

# STEP 5: Generate OTA binary

Copy `.pio/build/<ENV>/firmware.bin` to `<PROJECT_ROOT>/DigitalPOB_v<VERSION>_OTA.bin`.

This is the firmware-only binary (~1.6MB) used for OTA updates via SIRB.

# STEP 6: Read partition table and locate binaries

Read the partition table CSV (from `board_build.partitions` in platformio.ini) to find:
- `app0` (or `ota_0`) partition offset — where `firmware.bin` goes
- `spiffs` (or `littlefs`) partition offset — where the filesystem image goes

Also determine:
- Bootloader offset: `0x0` for ESP32-S3/S2/C3, `0x1000` for ESP32 classic
- Partition table offset: `0x8000` (standard)

Locate these files in `.pio/build/<ENV>/`:
- `bootloader.bin`
- `partitions.bin`
- `firmware.bin`
- `littlefs.bin` (or `spiffs.bin`)

All four must exist.

# STEP 7: Generate fullbin with esptool

Run esptool merge_bin to create the complete flash image:
```bash
~/.platformio/penv/bin/python3 -m esptool --chip <CHIP> merge_bin \
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

# STEP 8: Update CHANGELOG.md

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

# STEP 9: Check for existing release

Check if a release with the same tag already exists:
```bash
gh release view v<VERSION>
```

If it exists, delete the existing release and tag before creating a new one:
```bash
gh release delete v<VERSION> --yes
git tag -d v<VERSION>
git push origin :refs/tags/v<VERSION>
```

# STEP 10: Create GitHub release

Push any pending commits, then create the release with both binaries:
```bash
git push origin <BRANCH>

gh release create v<VERSION> \
    <PROJECT_ROOT>/DigitalPOB_v<VERSION>_OTA.bin \
    <PROJECT_ROOT>/DigitalPOB_v<VERSION>.bin \
    --target <BRANCH> \
    --title "v<VERSION>" \
    --notes "$(cat <<'EOF'
## Changelog

<content from CHANGELOG.md for this version>

### Binarios
- `DigitalPOB_v<VERSION>_OTA.bin` — firmware para OTA via SIRB (~1.6MB)
- `DigitalPOB_v<VERSION>.bin` — binario completo para gravacao via USB (~16MB)

### Gravacao via USB (fullbin)
```
esptool.py --chip <CHIP> write_flash 0x0 DigitalPOB_v<VERSION>.bin
```
EOF
)"
```

Do NOT add `--prerelease` unless the user explicitly asks for it.

# STEP 11: Report result

Print:
- Release URL
- Version
- OTA binary file name and size
- Fullbin file name and size

# RULES

- Use `~/.platformio/penv/bin/pio` if `pio` is not in PATH
- Use `~/.platformio/penv/bin/python3 -m esptool` for esptool commands
- Do NOT modify config.h FIRMWARE_VERSION — only read it
- Do NOT flash/upload to the device — only generate binaries and release
- Do NOT add `--prerelease` unless asked
- Do NOT stage .bin files, .env, or credential files in git
- If any step fails, stop and report the error clearly
- Output files go in the project root
- FIRMWARE_VERSION in config.h is the single source of truth for versioning
- Commit message must end with `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
