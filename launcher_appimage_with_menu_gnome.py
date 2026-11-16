#!/usr/bin/env python3
import os
import sys
import json
import re
import subprocess
import tempfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

# -------------------------------------------------
# Ścieżki
# -------------------------------------------------
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = os.path.join(SCRIPT_DIR, "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "appimage_manager_config.json")
APPS_DIR = os.path.join(SCRIPT_DIR, "AppImages")
DOWNLOADS_DIR = os.path.join(SCRIPT_DIR, "Downloads")
SCRIPTS_DIR = os.path.join(SCRIPT_DIR, "scripts")

# Katalog na ikony
ICONS_DIR = os.path.join(SCRIPT_DIR, "icons")
os.makedirs(ICONS_DIR, exist_ok=True)


# -------------------------------------------------
# Generator ikon wektorowych (styl SVG)
# -------------------------------------------------
def create_vector_icon(icon_type, size=(16, 16)):
    """Generuje ostre ikony wektorowe (w stylu SVG) bez zewnętrznych zależności."""
    # Rysujemy w 4x większej rozdzielczości dla idealnego wygładzania (antyaliasingu)
    scale = 4
    w, h = size[0] * scale, size[1] * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if icon_type == "add":
        # Zielony plus (SVG: M12 5v14M5 12h14)
        color = (46, 160, 67, 255)
        lw = 2 * scale
        pad = 3 * scale
        draw.line([(w // 2, pad), (w // 2, h - pad)], fill=color, width=lw)
        draw.line([(pad, h // 2), (w - pad, h // 2)], fill=color, width=lw)

    elif icon_type == "run":
        # Niebieski trójkąt Play (SVG: polygon points="5 3 19 12 5 21")
        color = (31, 111, 235, 255)
        pad_x = 4 * scale
        pad_y = 3 * scale
        draw.polygon([(pad_x, pad_y), (w - pad_x + scale, h // 2), (pad_x, h - pad_y)], fill=color)

    elif icon_type == "gnome":
        # Siatka aplikacji GNOME (9 kropek / kwadratów)
        color = (110, 84, 148, 255)
        dot_size = 2.5 * scale
        positions = [3 * scale, 7 * scale, 11 * scale]
        for x in positions:
            for y in positions:
                draw.rounded_rectangle([x, y, x + dot_size, y + dot_size], radius=scale, fill=color)

    elif icon_type == "delete":
        # Czerwony kosz na śmieci
        color = (218, 54, 51, 255)
        lw = int(1.5 * scale)
        # Wieczko
        draw.line([(3 * scale, 4 * scale), (13 * scale, 4 * scale)], fill=color, width=lw)
        draw.rectangle([6 * scale, 2 * scale, 10 * scale, 4 * scale], outline=color, width=lw)
        # Pojemnik
        draw.rectangle([4 * scale, 4 * scale, 12 * scale, 14 * scale], outline=color, width=lw)
        # Linie wewnątrz
        draw.line([(7 * scale, 7 * scale), (7 * scale, 11 * scale)], fill=color, width=lw)
        draw.line([(9 * scale, 7 * scale), (9 * scale, 11 * scale)], fill=color, width=lw)

    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


# -------------------------------------------------
class IconSelectionDialog(tk.Toplevel):
    """Okienko wyboru sposobu pozyskania ikony."""
    def __init__(self, parent, app_name):
        super().__init__(parent)
        self.title("Wybór ikony")
        self.geometry("380x160")
        self.resizable(False, False)
        self.result = None

        self.transient(parent)
        self.grab_set()

        tk.Label(
            self,
            text=f"Wybierz źródło ikony dla:\n{app_name}",
            font=("Arial", 10, "bold"),
            justify="center"
        ).pack(pady=15)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame,
            text="Oryginalna ikona\n(z AppImage)",
            width=16,
            height=2,
            command=self.use_original
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Moja ikona\n(wybierz plik)",
            width=16,
            height=2,
            command=self.use_custom
        ).pack(side=tk.LEFT, padx=10)

    def use_original(self):
        self.result = "original"
        self.destroy()

    def use_custom(self):
        self.result = "custom"
        self.destroy()


# -------------------------------------------------
class AppImageManager:
    ICON_SIZE = (24, 24)

    def __init__(self, root):
        self.root = root
        self.root.title("AppImage Manager")
        self.root.geometry("460x380")

        # ---- UI -------------------------------------------------
        tk.Label(root, text="Zarządzaj swoimi aplikacjami AppImage:", font=("Arial", 10)).pack(pady=(8, 4))

        self.tree = ttk.Treeview(root, show='tree')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        self.icons = {}
        self.load_apps()

        # ---- Kompaktowy pasek przycisków z ikonami SVG ----
        self.btn_icons = {
            "add": create_vector_icon("add", (15, 15)),
            "run": create_vector_icon("run", (15, 15)),
            "gnome": create_vector_icon("gnome", (15, 15)),
            "delete": create_vector_icon("delete", (15, 15))
        }

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=10, pady=8)

        btn_style = {
            "compound": tk.LEFT,
            "padx": 6,
            "pady": 3,
            "font": ("Arial", 9)
        }

        tk.Button(
            btn_frame,
            text=" Dodaj",
            image=self.btn_icons["add"],
            command=self.select_file,
            **btn_style
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        tk.Button(
            btn_frame,
            text=" Uruchom",
            image=self.btn_icons["run"],
            command=self.run_app,
            **btn_style
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        tk.Button(
            btn_frame,
            text=" Menu GNOME",
            image=self.btn_icons["gnome"],
            command=self.add_to_gnome_menu,
            **btn_style
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        tk.Button(
            btn_frame,
            text=" Usuń",
            image=self.btn_icons["delete"],
            command=self.delete_app,
            **btn_style
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.tree.bind('<Double-Button-1>', self.run_app)

        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(APPS_DIR, exist_ok=True)
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        os.makedirs(SCRIPTS_DIR, exist_ok=True)

    # -------------------------------------------------
    def _load_icon(self, icon_path):
        if icon_path and os.path.isfile(icon_path):
            try:
                im = Image.open(icon_path).convert("RGBA")
                im.thumbnail(self.ICON_SIZE, Image.LANCZOS)
                return ImageTk.PhotoImage(im)
            except Exception:
                pass

        im = Image.new("RGBA", self.ICON_SIZE, (200, 200, 200, 255))
        return ImageTk.PhotoImage(im)

    # -------------------------------------------------
    def load_apps(self):
        self.tree.delete(*self.tree.get_children())
        if not os.path.exists(CONFIG_FILE):
            return

        with open(CONFIG_FILE, "r") as f:
            apps = json.load(f)

        for app_name, app_info in apps.items():
            icon = self._load_icon(app_info.get('icon'))
            self.icons[app_name] = icon
            self.tree.insert("", "end", text=f" {app_name}", image=icon, values=(app_name,))

    # -------------------------------------------------
    def _get_selected_app_name(self):
        selected_id = self.tree.focus()
        if not selected_id:
            return None
        # Pobieramy czystą nazwę z values (bez spacji dodanej dla estetyki)
        vals = self.tree.item(selected_id, "values")
        if vals:
            return vals[0]
        return self.tree.item(selected_id, "text").strip()

    # -------------------------------------------------
    def select_custom_icon(self):
        icon_types = [('Image files', '*.png *.jpg *.jpeg *.svg'), ('All files', '*.*')]
        icon_path = filedialog.askopenfilename(
            initialdir=ICONS_DIR,
            filetypes=icon_types
        )
        return icon_path if icon_path else None

    # -------------------------------------------------
    def extract_icon_from_appimage(self, appimage_path, app_name):
        temp_dir = tempfile.mkdtemp()
        try:
            subprocess.run(
                [appimage_path, '--appimage-extract'],
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=90
            )

            squashfs_root = os.path.join(temp_dir, 'squashfs-root')
            if not os.path.isdir(squashfs_root):
                return None

            icon_name = None
            desktop_files = []

            for root_dir, dirs, files in os.walk(squashfs_root):
                for file in files:
                    if file.endswith('.desktop'):
                        desktop_files.append(os.path.join(root_dir, file))

            for df_path in desktop_files:
                try:
                    with open(df_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if line.startswith('Icon='):
                                icon_name = line.strip().split('=', 1)[1]
                                break
                except Exception:
                    pass
                if icon_name:
                    break

            icon_path_found = None
            extensions = ['.png', '.svg', '.xpm']

            if icon_name:
                for root_dir, dirs, files in os.walk(squashfs_root):
                    for file in files:
                        for ext in extensions:
                            if file == icon_name + ext or file.lower() == icon_name.lower() + ext:
                                icon_path_found = os.path.join(root_dir, file)
                                break
                    if icon_path_found:
                        break

            if not icon_path_found:
                max_size = 0
                for root_dir, dirs, files in os.walk(squashfs_root):
                    for file in files:
                        if file.endswith('.png'):
                            p = os.path.join(root_dir, file)
                            try:
                                size = os.path.getsize(p)
                                if size > max_size:
                                    max_size = size
                                    icon_path_found = p
                            except Exception:
                                pass

            if icon_path_found and os.path.exists(icon_path_found):
                ext = os.path.splitext(icon_path_found)[1]
                safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', app_name)
                dest_icon_path = os.path.join(ICONS_DIR, f"{safe_name}{ext}")

                shutil.copy(icon_path_found, dest_icon_path)
                return dest_icon_path

        except Exception as e:
            print(f"Błąd podczas wyciągania ikony: {e}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return None

    # -------------------------------------------------
    def _get_desktop_file_path(self, app_name):
        desktop_dir = os.path.expanduser("~/.local/share/applications")
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', app_name).lower()
        return os.path.join(desktop_dir, f"appimage_mgr_{safe_name}.desktop")

    # -------------------------------------------------
    def create_desktop_shortcut(self, app_name, app_path, icon_path):
        desktop_filename = self._get_desktop_file_path(app_name)
        os.makedirs(os.path.dirname(desktop_filename), exist_ok=True)

        try:
            os.chmod(app_path, 0o755)
        except Exception as e:
            print(f"Nie udało się nadać uprawnień wykonywalności: {e}")

        desktop_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec="{app_path}"
Icon={icon_path}
Categories=Utility;Application;
Terminal=false
"""
        try:
            with open(desktop_filename, "w") as df:
                df.write(desktop_content)
            return True
        except Exception as e:
            print(f"Błąd zapisu pliku .desktop: {e}")
            return False

    # -------------------------------------------------
    def select_file(self):
        filetypes = [
            ("AppImage / Skrypty", "*.AppImage *.appimage *.sh"),
            ("Wszystkie pliki", "*.*")
        ]
        appimage_path = filedialog.askopenfilename(
            initialdir=DOWNLOADS_DIR, filetypes=filetypes
        )
        if not appimage_path:
            return

        base_name = os.path.basename(appimage_path)
        is_appimage = base_name.lower().endswith('.appimage')

        if is_appimage:
            new_app_path = os.path.join(APPS_DIR, base_name)
            app_name = re.sub(r'(?i)\.appimage$', '', base_name)
            app_name = re.sub(r'-x86_64$', '', app_name)
        else:
            new_app_path = os.path.join(SCRIPTS_DIR, base_name)
            app_name = os.path.splitext(base_name)[0]

        try:
            if os.path.abspath(appimage_path) != os.path.abspath(new_app_path):
                if os.path.exists(new_app_path):
                    os.remove(new_app_path)
                os.rename(appimage_path, new_app_path)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się przenieść pliku: {e}")
            return

        try:
            os.chmod(new_app_path, 0o755)
        except Exception as e:
            print(f"Nie udało się nadać uprawnień: {e}")

        icon_path = None
        if is_appimage:
            dialog = IconSelectionDialog(self.root, app_name)
            self.root.wait_window(dialog)

            if dialog.result == "original":
                self.root.config(cursor="watch")
                self.root.update()
                icon_path = self.extract_icon_from_appimage(new_app_path, app_name)
                self.root.config(cursor="")

                if not icon_path:
                    messagebox.showwarning("Uwaga", "Nie udało się automatycznie wyciągnąć ikony. Wybierz plik ręcznie.")
                    icon_path = self.select_custom_icon()
            elif dialog.result == "custom":
                icon_path = self.select_custom_icon()
            else:
                return
        else:
            icon_path = self.select_custom_icon()

        if not icon_path:
            messagebox.showwarning("Brak ikony", "Proszę wybrać lub wyciągnąć ikonę dla aplikacji.")
            return

        apps = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                apps = json.load(f)

        apps[app_name] = {
            "path": new_app_path,
            "icon": icon_path
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(apps, f, indent=4)

        self.create_desktop_shortcut(app_name, new_app_path, icon_path)

        messagebox.showinfo("Sukces", f"Zaktualizowano / dodano aplikację: {app_name}")
        self.load_apps()

    # -------------------------------------------------
    def add_to_gnome_menu(self):
        app_name = self._get_selected_app_name()
        if not app_name:
            messagebox.showwarning("Brak wyboru", "Proszę wybrać aplikację z listy.")
            return

        if not os.path.exists(CONFIG_FILE):
            messagebox.showerror("Błąd", "Brak pliku konfiguracyjnego.")
            return

        with open(CONFIG_FILE, "r") as f:
            apps = json.load(f)

        app_info = apps.get(app_name)
        if not app_info:
            messagebox.showerror("Błąd", f"Nie znaleziono wpisu dla {app_name}.")
            return

        success = self.create_desktop_shortcut(app_name, app_info["path"], app_info["icon"])
        if success:
            messagebox.showinfo("Sukces", f"Aplikacja '{app_name}' została pomyślnie dodana do menu GNOME!")
        else:
            messagebox.showerror("Błąd", "Nie udało się dodać aplikacji do menu GNOME.")

    # -------------------------------------------------
    def delete_app(self):
        """Usuwa aplikację z listy, z menu GNOME oraz opcjonalnie z dysku."""
        app_name = self._get_selected_app_name()
        if not app_name:
            messagebox.showwarning("Brak wyboru", "Proszę wybrać aplikację do usunięcia.")
            return

        confirm = messagebox.askyesno(
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć '{app_name}' z menedżera oraz z menu GNOME?"
        )
        if not confirm:
            return

        if not os.path.exists(CONFIG_FILE):
            return

        with open(CONFIG_FILE, "r") as f:
            apps = json.load(f)

        app_info = apps.pop(app_name, None)

        # Zapis zaktualizowanej listy
        with open(CONFIG_FILE, "w") as f:
            json.dump(apps, f, indent=4)

        # Usunięcie pliku .desktop z menu GNOME
        desktop_file = self._get_desktop_file_path(app_name)
        if os.path.exists(desktop_file):
            try:
                os.remove(desktop_file)
            except Exception as e:
                print(f"Nie udało się usunąć skrótu GNOME: {e}")

        # Pytanie o usunięcie pliku fizycznego (.AppImage / .sh)
        if app_info and os.path.exists(app_info.get("path", "")):
            delete_file = messagebox.askyesno(
                "Usunąć plik z dysku?",
                f"Czy chcesz również trwale usunąć plik programu z dysku?\n\n{app_info['path']}"
            )
            if delete_file:
                try:
                    os.remove(app_info["path"])
                except Exception as e:
                    messagebox.showerror("Błąd", f"Nie udało się usunąć pliku z dysku: {e}")

        self.load_apps()
        messagebox.showinfo("Usunięto", f"Aplikacja '{app_name}' została usunięta.")

    # -------------------------------------------------
    def run_app(self, event=None):
        app_name = self._get_selected_app_name()
        if not app_name:
            messagebox.showwarning("Brak wyboru", "Proszę wybrać aplikację z listy.")
            return

        with open(CONFIG_FILE, "r") as f:
            apps = json.load(f)
        app_path = apps.get(app_name, {}).get("path")

        if not app_path:
            messagebox.showerror("Błąd", f"Ścieżka do {app_name} nie znaleziona.")
            return

        if app_path.endswith('.sh'):
            subprocess.Popen(['bash', app_path])
        else:
            subprocess.Popen([app_path])


# -------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    AppImageManager(root)
    root.mainloop()
