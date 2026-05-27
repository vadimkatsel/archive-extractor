from pathlib import Path
import shutil
import subprocess
import zipfile
import threading
import hashlib
import py7zr
from tkinter import filedialog, messagebox
import tempfile


# ================== 7-Zip Auto-Detection ==================

SEVEN_ZIP_CANDIDATES = [
    r"C:\Program Files\7-Zip\7z.exe",
    r"C:\Program Files (x86)\7-Zip\7z.exe",
]


def find_7zip():
    """Return the path to 7z.exe if found in common locations, else None."""
    for path in SEVEN_ZIP_CANDIDATES:
        if Path(path).exists():
            return path
    return None


# ================== Translations ==================

LANGUAGES = {
    "English": {
        "title": "Archive Extractor",
        "subtitle": "Extract archives and filter files",
        "btn_input": "Archives",
        "btn_output": "Output",
        "not_selected": "Not selected",
        "extensions_label": "Which extensions to keep? (leave blank for all)",
        "extensions_placeholder": ".package,.ts4script",
        "delete_checkbox": "Delete archive after extraction",
        "status_waiting": "Waiting",
        "btn_unpack": "Unpack",
        "lang_label": "Language",
        "err_title": "Error",
        "err_no_input": "Select the folder with archives",
        "err_no_output": "Select the output folder",
        "indexing": "Indexing existing files...",
        "index_error": "Indexing error: ",
        "extracting": "Extracting",
        "skip_duplicate": "⚠ Skipped duplicate: ",
        "renamed": "⚠ Name conflict, saved as: ",
        "deleted_archive": "Deleted archive ",
        "error": "Error: ",
        "no_archives": "No archives found",
        "done": "Done",
        "status_extracting": "Extracting {index}/{total}: {name}",
        "btn_7zip": "7-Zip",
        "7zip_auto": "Auto-detected",
        "7zip_not_found": "Not found — please select manually",
        "err_no_7zip": "7-Zip not found. Please select 7z.exe manually.",
    },
    "Русский": {
        "title": "Archive Extractor",
        "subtitle": "Распаковка архивов и фильтрация файлов",
        "btn_input": "Архивы",
        "btn_output": "Вывод",
        "not_selected": "Не выбрано",
        "extensions_label": "Какие расширения оставить? (пусто = все)",
        "extensions_placeholder": ".package,.ts4script",
        "delete_checkbox": "Удалять архив после распаковки",
        "status_waiting": "Ожидание",
        "btn_unpack": "Распаковать",
        "lang_label": "Язык",
        "err_title": "Ошибка",
        "err_no_input": "Выберите папку с архивами",
        "err_no_output": "Выберите папку вывода",
        "indexing": "Индексирую существующие файлы...",
        "index_error": "Ошибка индексации: ",
        "extracting": "Распаковываю",
        "skip_duplicate": "⚠ Пропущен дубликат: ",
        "renamed": "⚠ Конфликт имени, сохранено как: ",
        "deleted_archive": "Удалён архив ",
        "error": "Ошибка: ",
        "no_archives": "Архивы не найдены",
        "done": "Готово",
        "status_extracting": "Распаковываю {index}/{total}: {name}",
        "btn_7zip": "7-Zip",
        "7zip_auto": "Найдено автоматически",
        "7zip_not_found": "Не найдено — выберите вручную",
        "err_no_7zip": "7-Zip не найден. Укажите путь к 7z.exe вручную.",
    },
    "Українська": {
        "title": "Archive Extractor",
        "subtitle": "Розпакування архівів та фільтрація файлів",
        "btn_input": "Архіви",
        "btn_output": "Вивід",
        "not_selected": "Не вибрано",
        "extensions_label": "Які розширення залишити? (порожньо = всі)",
        "extensions_placeholder": ".package,.ts4script",
        "delete_checkbox": "Видаляти архів після розпакування",
        "status_waiting": "Очікування",
        "btn_unpack": "Розпакувати",
        "lang_label": "Мова",
        "err_title": "Помилка",
        "err_no_input": "Виберіть папку з архівами",
        "err_no_output": "Виберіть папку виводу",
        "indexing": "Індексую наявні файли...",
        "index_error": "Помилка індексації: ",
        "extracting": "Розпаковую",
        "skip_duplicate": "⚠ Пропущено дублікат: ",
        "renamed": "⚠ Конфлікт імені, збережено як: ",
        "deleted_archive": "Видалено архів ",
        "error": "Помилка: ",
        "no_archives": "Архіви не знайдено",
        "done": "Готово",
        "status_extracting": "Розпаковую {index}/{total}: {name}",
        "btn_7zip": "7-Zip",
        "7zip_auto": "Знайдено автоматично",
        "7zip_not_found": "Не знайдено — виберіть вручну",
        "err_no_7zip": "7-Zip не знайдено. Вкажіть шлях до 7z.exe вручну.",
    },
}


class App:

    def __init__(self, root, ctk):

        self.root = root
        self.ctk = ctk
        self.existing_hashes = {}
        self.current_lang = "English"
        self._is_running = False

        root.title("Archive Extractor")
        root.geometry("900x800")

        self.input_folder = None
        self.output_folder = None
        self.seven_zip_path = find_7zip()  # None if not found in standard locations

        main = ctk.CTkFrame(root)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # ================== Language Selector ==================
        lang_frame = ctk.CTkFrame(main, fg_color="transparent")
        lang_frame.pack(fill="x", padx=40, pady=(10, 0))

        self.lang_label_widget = ctk.CTkLabel(
            lang_frame,
            text=self._t("lang_label") + ":",
            font=("Segoe UI", 13)
        )
        self.lang_label_widget.pack(side="left", padx=(0, 8))

        self.lang_var = ctk.StringVar(value=self.current_lang)
        self.lang_dropdown = ctk.CTkOptionMenu(
            lang_frame,
            values=list(LANGUAGES.keys()),
            variable=self.lang_var,
            command=self.set_language,
            width=160
        )
        self.lang_dropdown.pack(side="left")

        # ================== Title ==================
        self.title_label = ctk.CTkLabel(
            main,
            text=self._t("title"),
            font=("Segoe UI", 28, "bold")
        )
        self.title_label.pack(pady=(15, 5))

        # ================== Subtitle ==================
        self.subtitle_label = ctk.CTkLabel(
            main,
            text=self._t("subtitle"),
            font=("Segoe UI", 14)
        )
        self.subtitle_label.pack(pady=(0, 20))

        # ================== Paths Section ==================
        paths_frame = ctk.CTkFrame(main, fg_color="transparent")
        paths_frame.pack(fill="x", padx=40, pady=15)
        paths_frame.grid_columnconfigure((0, 1), weight=1)

        # ================== Archive Path ==================
        input_wrapper = ctk.CTkFrame(
            paths_frame, fg_color="gray", corner_radius=20, height=50
        )
        input_wrapper.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        input_wrapper.grid_columnconfigure(1, weight=1)

        self.btn_input = ctk.CTkButton(
            input_wrapper,
            text=self._t("btn_input"),
            width=120,
            height=40,
            corner_radius=15,
            command=self.select_input
        )
        self.btn_input.grid(row=0, column=0, padx=5, pady=5)

        self.input_label = ctk.CTkLabel(
            input_wrapper,
            text=self._t("not_selected"),
            fg_color="transparent",
            anchor="w"
        )
        self.input_label.grid(row=0, column=1, sticky="ew", padx=(10, 15))

        # ================== Output Path ==================
        output_wrapper = ctk.CTkFrame(
            paths_frame, fg_color="gray", corner_radius=20, height=50
        )
        output_wrapper.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        output_wrapper.grid_columnconfigure(1, weight=1)

        self.btn_output = ctk.CTkButton(
            output_wrapper,
            text=self._t("btn_output"),
            width=120,
            height=40,
            corner_radius=15,
            command=self.select_output
        )
        self.btn_output.grid(row=0, column=0, padx=5, pady=5)

        self.output_label = ctk.CTkLabel(
            output_wrapper,
            text=self._t("not_selected"),
            fg_color="transparent",
            anchor="w"
        )
        self.output_label.grid(row=0, column=1, sticky="ew", padx=(10, 15))

        # ================== 7-Zip Path ==================
        # Spans both columns; hidden when 7-Zip is auto-detected successfully
        sevenzip_wrapper = ctk.CTkFrame(
            paths_frame, fg_color="gray", corner_radius=20, height=50
        )
        sevenzip_wrapper.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10)
        )
        sevenzip_wrapper.grid_columnconfigure(1, weight=1)

        self.btn_7zip = ctk.CTkButton(
            sevenzip_wrapper,
            text=self._t("btn_7zip"),
            width=120,
            height=40,
            corner_radius=15,
            command=self.select_7zip
        )
        self.btn_7zip.grid(row=0, column=0, padx=5, pady=5)

        _7zip_default = (
            self._t("7zip_auto") + f"  ({self.seven_zip_path})"
            if self.seven_zip_path
            else self._t("7zip_not_found")
        )
        self.sevenzip_label = ctk.CTkLabel(
            sevenzip_wrapper,
            text=_7zip_default,
            fg_color="transparent",
            anchor="w"
        )
        self.sevenzip_label.grid(row=0, column=1, sticky="ew", padx=(10, 15))

        # Hide the row when 7-Zip was found automatically
        if self.seven_zip_path:
            sevenzip_wrapper.grid_remove()
        self._sevenzip_wrapper = sevenzip_wrapper

        # ================== Settings Section ==================
        settings_frame = ctk.CTkFrame(main, fg_color="transparent")
        settings_frame.pack(fill="x", padx=40, pady=15)

        self.extensions_label_widget = ctk.CTkLabel(
            settings_frame,
            text=self._t("extensions_label")
        )
        self.extensions_label_widget.pack(pady=(0, 5))

        self.extensions = ctk.CTkEntry(
            settings_frame,
            placeholder_text=self._t("extensions_placeholder")
        )
        self.extensions.pack(fill="x")

        # ================== Checkbox to Delete Unpacked Archives ==================
        self.delete_archives = ctk.BooleanVar(value=False)
        self.delete_checkbox_widget = ctk.CTkCheckBox(
            settings_frame,
            text=self._t("delete_checkbox"),
            variable=self.delete_archives
        )
        self.delete_checkbox_widget.pack(pady=(10, 0))

        # ================== Status ==================
        self.status = ctk.CTkLabel(main, text=self._t("status_waiting"))
        self.status.pack()

        self.progress = ctk.CTkProgressBar(main)
        self.progress.pack(fill="x", pady=10)
        self.progress.set(0)

        # ================== Unpack Button ==================
        self.btn_unpack = ctk.CTkButton(
            main,
            text=self._t("btn_unpack"),
            height=45,
            command=self._start_unpack
        )
        self.btn_unpack.pack(fill="x", pady=15)

        # ================== Logs ==================
        self.log = ctk.CTkTextbox(main, height=300)
        self.log.pack(fill="both", expand=True)

    # ================= helpers =================

    def _t(self, key):
        """Return translated string for the current language."""
        return LANGUAGES[self.current_lang].get(key, key)

    def _gui(self, fn, *args, **kwargs):
        """Schedule a GUI call safely from any thread via root.after()."""
        self.root.after(0, lambda: fn(*args, **kwargs))

    def write(self, text):
        """Append a line to the log box (thread-safe)."""
        def _do():
            self.log.insert("end", text + "\n")
            self.log.see("end")
        self._gui(_do)

    def _set_status(self, text):
        """Update the status label (thread-safe)."""
        self._gui(self.status.configure, text=text)

    def _set_progress(self, value):
        """Update the progress bar (thread-safe)."""
        self._gui(self.progress.set, value)

    def _set_running(self, running: bool):
        """Enable/disable the unpack button (thread-safe)."""
        state = "disabled" if running else "normal"
        self._gui(self.btn_unpack.configure, state=state)
        self._is_running = running

    # ================= language =================

    def set_language(self, lang):
        """Switch all UI text to the chosen language."""
        self.current_lang = lang

        self.lang_label_widget.configure(text=self._t("lang_label") + ":")
        self.title_label.configure(text=self._t("title"))
        self.subtitle_label.configure(text=self._t("subtitle"))
        self.btn_input.configure(text=self._t("btn_input"))
        self.btn_output.configure(text=self._t("btn_output"))
        self.extensions_label_widget.configure(text=self._t("extensions_label"))
        self.delete_checkbox_widget.configure(text=self._t("delete_checkbox"))
        self.btn_unpack.configure(text=self._t("btn_unpack"))
        self.btn_7zip.configure(text=self._t("btn_7zip"))

        # Only reset path labels when no folder has been chosen yet
        if not self.input_folder:
            self.input_label.configure(text=self._t("not_selected"))
        if not self.output_folder:
            self.output_label.configure(text=self._t("not_selected"))

        # Retranslate 7-zip label only if it still shows the auto-detected path
        if self.seven_zip_path and self.seven_zip_path in SEVEN_ZIP_CANDIDATES:
            self.sevenzip_label.configure(
                text=self._t("7zip_auto") + f"  ({self.seven_zip_path})"
            )
        elif not self.seven_zip_path:
            self.sevenzip_label.configure(text=self._t("7zip_not_found"))

        # Reset status only when it is still showing a "waiting" string
        current_status = self.status.cget("text")
        if any(
            current_status == ld.get("status_waiting")
            for ld in LANGUAGES.values()
        ):
            self.status.configure(text=self._t("status_waiting"))

    # ================= folder pickers =================

    def select_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder = folder
            self.input_label.configure(text=folder)

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_label.configure(text=folder)

    def select_7zip(self):
        path = filedialog.askopenfilename(
            title="Select 7z.exe",
            filetypes=[("7z.exe", "7z.exe"), ("Executable", "*.exe")]
        )
        if path:
            self.seven_zip_path = path
            self.sevenzip_label.configure(text=path)

    # ================= core logic =================

    def get_file_hash(self, path):
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def build_existing_hashes(self, output_dir, wanted_extensions):
        """Hash every matching file already in the output folder."""
        self.write(self._t("indexing"))
        files = [
            f for f in output_dir.rglob("*")
            if f.is_file() and (
                not wanted_extensions or f.suffix.lower() in wanted_extensions
            )
        ]
        total = len(files)
        self._set_progress(0)
        self.existing_hashes.clear()
        for index, file in enumerate(files, start=1):
            try:
                self.existing_hashes[self.get_file_hash(file)] = file.name
            except Exception as e:
                self.write(self._t("index_error") + str(e))
            self._set_progress(index / total if total else 1)

    def _unique_destination(self, output_dir: Path, filename: str) -> Path:
        """
        Return a destination path that does not collide with an existing file.
        If output_dir/filename already exists, appends _1, _2, ... before the suffix.
        """
        dest = output_dir / filename
        if not dest.exists():
            return dest
        stem = dest.stem
        suffix = dest.suffix
        counter = 1
        while True:
            candidate = output_dir / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def _start_unpack(self):
        """Validate inputs, then launch the worker thread."""
        if self._is_running:
            return
        if not self.input_folder:
            messagebox.showerror(self._t("err_title"), self._t("err_no_input"))
            return
        if not self.output_folder:
            messagebox.showerror(self._t("err_title"), self._t("err_no_output"))
            return
        self._set_running(True)
        threading.Thread(target=self._unpack_worker, daemon=True).start()

    def _unpack_worker(self):
        """Background worker — all GUI calls go through write()/_set_*()."""
        try:
            self._do_unpack()
        finally:
            self._set_running(False)

    def _do_unpack(self):
        wanted_extensions = {
            ext.strip().lower()
            for ext in self.extensions.get().split(",")
            if ext.strip()
        }
        # Empty set means "keep everything"
        filter_extensions = bool(wanted_extensions)

        input_dir = Path(self.input_folder)
        output_dir = Path(self.output_folder)
        output_dir.mkdir(exist_ok=True)

        self.build_existing_hashes(output_dir, wanted_extensions)

        archives = [
            f for f in input_dir.iterdir()
            if f.is_file() and f.suffix.lower() in {".zip", ".rar", ".7z"}
        ]

        total = len(archives)
        if total == 0:
            self.write(self._t("no_archives"))
            return

        self._set_progress(0)

        for index, archive_file in enumerate(archives, start=1):
            temp_extract = Path(tempfile.mkdtemp())
            try:
                self._set_status(
                    self._t("status_extracting").format(
                        index=index, total=total, name=archive_file.name
                    )
                )
                self.write(self._t("extracting") + " " + archive_file.name)

                suffix = archive_file.suffix.lower()
                if suffix == ".zip":
                    with zipfile.ZipFile(archive_file, "r") as arc:
                        arc.extractall(temp_extract)

                elif suffix == ".7z":
                    with py7zr.SevenZipFile(archive_file, "r") as arc:
                        arc.extractall(temp_extract)

                elif suffix == ".rar":
                    # Requires 7-Zip — auto-detected or manually selected
                    if not self.seven_zip_path:
                        self.write(self._t("err_no_7zip"))
                        continue
                    subprocess.run(
                        [
                            self.seven_zip_path,
                            "x", str(archive_file),
                            f"-o{temp_extract}", "-y"
                        ],
                        check=True
                    )

                for extracted_file in temp_extract.rglob("*"):
                    if not extracted_file.is_file():
                        continue
                    if filter_extensions and (
                        extracted_file.suffix.lower() not in wanted_extensions
                    ):
                        continue

                    file_hash = self.get_file_hash(extracted_file)
                    if file_hash in self.existing_hashes:
                        self.write(
                            self._t("skip_duplicate") + extracted_file.name
                        )
                        continue

                    self.existing_hashes[file_hash] = extracted_file.name

                    destination = self._unique_destination(
                        output_dir, extracted_file.name
                    )
                    if destination.name != extracted_file.name:
                        self.write(self._t("renamed") + destination.name)

                    shutil.move(str(extracted_file), str(destination))

                if self.delete_archives.get():
                    archive_file.unlink()
                    self.write(self._t("deleted_archive") + archive_file.name)

            except Exception as e:
                self.write(self._t("error") + str(e))

            finally:
                shutil.rmtree(temp_extract, ignore_errors=True)

            self._set_progress(index / total)

        # Clean up any empty subdirectories left in output
        for folder in sorted(output_dir.rglob("*"), reverse=True):
            try:
                folder.rmdir()
            except Exception:
                pass

        self._set_progress(1)
        self._set_status(self._t("status_waiting"))
        self.write(self._t("done"))