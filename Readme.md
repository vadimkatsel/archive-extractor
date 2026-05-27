# Archive Extractor

A simple desktop application for extracting archives and automatically organizing files.

Archive Extractor helps you unpack multiple archives at once, filter specific file types, avoid duplicates, and keep your output folder clean.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

* Extract multiple archives in one click

* Supports:

    - ZIP
    - RAR
    - 7Z

* Filter extracted files by extension

    Example:

    ```text
    .package,.ts4script
    ```

    Only matching files will be kept.

* Duplicate detection

* Files are checked using SHA-256 hashes:

    - identical files are skipped
    - no duplicate content is copied

* Automatic file conflict handling

    If a file with the same name already exists:

    ```text
    mod.package
    mod_1.package
    mod_2.package
    ```

* Optional archive cleanup

    Delete archives automatically after extraction.

* Automatic 7-Zip detection

    The application:

    - searches common installation paths
    - allows manual selection if needed

* Multilingual interface

    Supported languages:

    - English
    - Русский
    - Українська

---

## Installation

### Option 1: Download executable

Download the latest release and run:

```text
ArchiveExtractor.exe
```

No Python installation required.

---

### Option 2: Run from source

Install dependencies:

```bash
pip install -r requirements.txt
```
Run:

```bash
python main.py
```

---

## Build executable

Generate a standalone `.exe`:

```bash
py -m PyInstaller --onefile --windowed main.py
```

The executable will be created in:

```text
dist/main.exe
```

---

## How to use

1. Select the folder containing archives
2. Select an output folder
3. (Optional) Enter file extensions to keep

Example:

```text
.package,.ts4script
```

4. Choose whether archives should be deleted after extraction
5. Click **Unpack**

Done.

---

## Notes

RAR extraction requires **7-Zip**.

The application will try to find it automatically in:

```text
C:\Program Files\7-Zip\
C:\Program Files (x86)\7-Zip\
```

If it is not found, select `7z.exe` manually.

---

## Technologies

- Python
- CustomTkinter
- py7zr
- hashlib
- threading
- subprocess

---

## License

MIT License