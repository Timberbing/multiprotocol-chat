# Komunikator Tekstowy - Dokumentacja Projektu

Celem projektu było wykonanie aplikacji czatu w konsoli. 
Architektura aplikacji została podzielona na dwie części - kod klienta oraz kod serwera.
Klient komunikuje się z serwerem w celu udostępnienia podstawowych danych (np. nazwa użytkownika, port, na którym klient nasłuchuje czy jest stan online / offline), które potem przekazywane są wszystkim klientom. 
Sam czat odbywa się w trybie peer-to-peer, czyli klienci sami zestawiają ze sobą połączenie na podstawie danych otrzymanych od serwera (tj. adres IP, port, na którym uruchomiony jest listener TCP oraz nazwa użytkownika).  

## Zastosowania protokołów komunikacyjnych
- **TCP** - Komunikacja między klientami (tj. wysłanie wiadmości).
    Za każdym razem gdy klient chce wysłać do innego klienta wiadomość, zestawiane jest **między nimi** połączenie TCP (każdy klient ma uruchomiony serwer TCP - linia 68 w pliku `client_client.py`).
    *Kod klienta* - linia 68 w `client_client.py`.

- **UDP** - Komunikacja typu multicast. Po uruchomieniu klient zapisuje się do grupy multicastowej i w ten sposób serwer dowiaduje się o przyłączeniu nowego klienta (od tego momentu gdy któryś klient odpyta serwer o listę dostępnych klientów, nowo przyłączony klient będzie znajdował się na tej liście).
    *Kod serwera* - linia 131 w `daemon_file.py`.
    *Kod klienta*- linia 47 w `client_client.py`.

- **SCTP** - Sprawdzanie stanu klienta. Za pomocą protokołu SCTP serwer odświeża listę klientów, jeżeli klient się nie zgłasza, jego stan jest zmieniany na "offline".
    *Kod serwera* - linia 90 w pliku `daemon_file.py`.
    *Kod klienta* - linia 27 w pliku `client_client.py`.

## Tryb demona
Serwer działa w trybie demona (plik `daemon_file.py`). 
Można go uruchomić, zatrzymać bądź zrestartować podając kolejne argumenty: `start`, `stop`, `restart`.

## Logowanie
Serwer zapisuje logi do pliku `multiproto.log` w bieżącym folderze.

## Uruchomienie
Do uruchomienia programu wymagane jest zainstalowanie biblioteki `pysctp`. 
Można to zrobić za pomocą komendy `pip install pysctp`.
W niektórych dystrybucjach uruchomienie programu serwera może zwracać błąd i przerywać działanie programu.
Jest to spowodowane błędem w bibliotece pysctp, naprawić go można modyfikując jej kod źródłowy w odpowiednim miejscu (szczegóły w pliku `fix.md`).

Aby uruchomić serwer, należy uruchomić plik deamon serwera: `python3 daemon_file.py start`.

Do zatrzymania daemona należy użyć argumentu stop: `python daemon_file.py stop`.

Uruchomienie pliku klienta: `python3 client_client.py`. 
