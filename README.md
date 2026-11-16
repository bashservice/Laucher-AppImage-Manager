# AppImage Manager & GNOME Launcher

Lekka i intuicyjna aplikacja napisana w języku Python (z użyciem biblioteki **Tkinter**) służąca do zarządzania aplikacjami typu **AppImage** oraz skryptami powłoki (`.sh`) w systemach Linux (ze szczególnym uwzględnieniem integracji ze środowiskiem **GNOME**).

https://github.com/user-attachments/assets/7cbc0a42-d9c8-4ad2-a0e1-879265e687f7

## 🚀 Główne funkcje

* **Zarządzanie aplikacjami**: Łatwe dodawanie, uruchamianie i usuwanie plików `.AppImage` oraz skryptów `.sh`.
* **Automatyczna obsługa ikon**: 
  * Automatyczne wyciąganie oryginalnej ikony bezpośrednio z wnętrza pakietu AppImage (analiza plików `.desktop` oraz zasobów).
  * Opcja ręcznego wskazania własnej ikony (`.png`, `.jpg`, `.svg`, `.xpm`).
* **Wbudowane ikony wektorowe**: Generator wektorowy w stylu SVG dla przycisków interfejsu bez konieczności instalowania zewnętrznych pakietów ikon.
* **Integracja z menu GNOME**: Automatyczne tworzenie skrótów systemowych w `~/.local/share/applications`, dzięki czemu aplikacje pojawiają się w systemowym menu startowym.
* **Kompleksowe usuwanie**: Usuwanie aplikacji z menedżera, czyszczenie skrótów GNOME oraz opcjonalne trwałe usunięcie pliku wykonywalnego z dysku.

---

## 📋 Wymagania

* **Python 3.x**
* **Pillow** (biblioteka do obsługi obrazów w Pythonie)
* System Linux z obsługą standardu XDG Desktop (np. GNOME)

### Instalacja wymaganych bibliotek:
```bash
pip install Pillow
