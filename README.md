
# AppImage Manager

Prosty menedżer aplikacji dla systemu Linux, napisany w Pythonie z użyciem Tkintera. Pozwala dodawać pliki `.AppImage` i skrypty `.sh` do listy, przypisywać im ikony oraz uruchamiać je z poziomu graficznego okna.




## Funkcje

- Dodawanie plików `.AppImage` i `.sh`
- Przenoszenie dodanych plików do odpowiednich katalogów aplikacji
- Przypisywanie ikon PNG
- Wyświetlanie aplikacji na liście z ikonami
- Uruchamianie aplikacji przyciskiem lub dwukrotnym kliknięciem
- Zapisywanie informacji o aplikacjach w pliku JSON

## Wymagania

- Python 3
- Tkinter
- Pillow

Instalacja biblioteki Pillow:

```bash
python3 -m pip install Pillow
```
Dodano funkcję integracji zarządzanych aplikacji z menu systemowym środowiska GNOME. Dzięki temu aplikacje i skrypty dodane do menedżera pojawiają się bezpośrednio w menu startowym systemu, co pozwala na uruchamianie ich bez konieczności korzystania z głównego okna aplikacji.

🛠️ Główne zmiany:
Automatyczne tworzenie skrótów: Podczas dodawania nowego pliku .AppImage lub skryptu .sh program automatycznie generuje plik aktywatora .desktop w katalogu użytkownika (~/.local/share/applications/).

Tytuł (Commit / PR Title):
feat: dodano funkcję usuwania aplikacji, kompaktowy pasek narzędzi z ikonami wektorowymi SVG oraz usprawniono obsługę plików

Opis (PR Description):
🚀 Co nowego?
Funkcja usuwania aplikacji: Dodano możliwość usuwania pozycji z listy w menedżerze oraz automatycznego czyszczenia skrótów z menu systemowego GNOME (~/.local/share/applications/). Podczas usuwania program pyta również, czy trwale usunąć plik wykonywalny (.AppImage / .sh) z dysku.

Nowoczesny pasek narzędzi: Przebudowano interfejs, zmniejszając przyciski i układając je w kompaktowym panelu.

Wektorowe ikony (SVG): Zaimplementowano wbudowany generator ikon w stylu SVG (dodawanie, uruchamianie, menu GNOME, usuwanie), dzięki czemu interfejs jest czytelny i nie wymaga zewnętrznych bibliotek graficznych.

🛠️ Poprawki i ulepszenia:
Poprawka filtrowania plików: Naprawiono filtry w oknie dialogowym wyboru plików pod systemami Linux (zamiana średników na spacje), dzięki czemu pliki .AppImage i .appimage są teraz widoczne od razu bez konieczności ręcznego przełączania na „All files”.

Obsługa dużych plików: Zwiększono limit czasu (timeout do 90 sekund) oraz zadbano o wcześniejsze nadanie uprawnień wykonywalności (chmod +x), co pozwala bezbłędnie wyciągać oryginalne ikony nawet z dużych plików AppImage (~200MB+).

Nadpisywanie ikon: Usprawniono logikę ponownego dodawania aplikacji – jeśli zmienisz zdanie i zechcesz z powrotem przywrócić oryginalną ikonę zamiast własnej (lub odwrotnie), program poprawnie nadpisze konfigurację i zaktualizuje skrót w menu GNOME.

Ręczna synchronizacja z menu: Dodano nowy przycisk „Dodaj do menu GNOME” w interfejsie graficznym, który pozwala ręcznie zarejestrować wybraną aplikację z listy.

Uprawnienia wykonywalności: Skrypt dba o automatyczne nadanie uprawnień do uruchamiania (chmod +x) dla dodawanych plików.

Modyfikacja UI: Przeniesiono przyciski sterujące do dedykowanego panelu (Frame), poprawiając czytelność i układ okna aplikacji.
