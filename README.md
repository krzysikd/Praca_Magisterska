# Analiza i prognozowanie opłat transakcyjnych sieci Bitcoina

## Opis projektu

Celem mojej pracy było lepsze zrozumienie, jak kształtują się opłaty transakcyjne w sieci Bitcoin i czy jesteśmy w stanie je skutecznie przewidywać, na podstawie danych samodzielnie pozyskanych z blockchaina. 

Chciałem również porównać dwa podejścia prognostyczne:

- **Wielowymiarowe** – oparte na wielu cechach opisujących dany blok i transakcje,
- **Jednowymiarowe** – które można zastosować w bardziej praktycznych przypadkach, gdy mamy dostęp tylko do podstawowych informacji, takich jak numer bloku czy czas.

Dzięki temu mogłem ocenić skuteczność różnych modeli prognozowania opłat w różnych warunkach oraz lepiej zrozumieć specyfikę działania sieci Bitcoin.

## Automatyczne pozyskiwanie i przetwarzanie danych z blockchaina Bitcoina

W celu pozyskania danych połączyłem się przez VPN z serwerem koła naukowego, gdzie zainstalowałem i odpowiednio skonfigurowałem pełny węzeł Bitcoin Core.

<p align="center">
  <img src="screenshots/screeny/blockchain-info.JPG" alt="BlockchainInfo" />
</p>

Dane o blokach były automatycznie pobierane w ustalonych zakresach za pomocą skryptu [`Pobierz_Bloki_V4.py`](data_download/Pobierz_Bloki_V4.py), napisanego w Pythonie. Początkowo zapisywałem je w formacie CSV, jednak szybko okazało się, że ich rozmiar stanowi problem. Z tego względu przeszedłem na format **Parquet**, który jest znacznie bardziej wydajny przy pracy z dużymi zbiorami danych.

Następnie stworzyłem skrypt [`Pobierz_Probke.py`](data_download/Pobierz_Probke.py), który losowo wybiera 1% rekordów z każdego pliku. Dzięki temu mogłem wygenerować próbkę, która:

- zachowuje chronologię oryginalnych danych,
- a jednocześnie jest na tyle mała, że da się ją wygodnie analizować i modelować w kolejnych etapach pracy.


