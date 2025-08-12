# English version below

[Go to English version](#analysis-and-forecasting-of-bitcoin-network-transaction-fees)

# Analiza i prognozowanie opłat transakcyjnych sieci Bitcoina

## Opis projektu

Celem projektu było lepsze zrozumienie, jak kształtują się opłaty transakcyjne w sieci Bitcoin oraz ocena możliwości ich skutecznego prognozowania na podstawie danych samodzielnie pozyskanych z blockchaina.

Porównano dwa podejścia prognostyczne:

- **Wielowymiarowe** – oparte na wielu cechach opisujących dany blok i transakcje,
- **Jednowymiarowe** – możliwe do zastosowania w praktycznych przypadkach, gdy dostępne są tylko podstawowe informacje (np. numer bloku, czas).

Pozwoliło to na ocenę skuteczności modeli w różnych warunkach oraz lepsze zrozumienie mechanizmów działania sieci Bitcoin.

## Automatyczne pozyskiwanie i przetwarzanie danych z blockchaina Bitcoina

W celu pozyskania danych nawiązano połączenie VPN z serwerem koła naukowego, gdzie zainstalowano i skonfigurowano pełny węzeł Bitcoin Core.

<p align="center">
  <img src="screenshots/screeny/blockchain-info.JPG" alt="BlockchainInfo" />
</p>

Dane o blokach były automatycznie pobierane w ustalonych zakresach za pomocą skryptu [`Pobierz_Bloki_V4.py`](data_download/Pobierz_Bloki_V4.py), napisanego w Pythonie. Początkowo dane zapisywano w formacie CSV, jednak ze względu na duży rozmiar plików, zdecydowano się na format **Parquet**, znacznie wydajniejszy przy pracy z dużymi zbiorami.

Następnie użyto skryptu [`Pobierz_Probke.py`](data_download/Pobierz_Probke.py), który losowo wybiera 1% rekordów z każdego pliku. Dzięki temu wygenerowano próbkę, która:

- zachowuje chronologię oryginalnych danych,
- a jednocześnie jest wystarczająco mała, by umożliwić efektywną analizę i modelowanie.

## Eksploracyjna analiza danych (EDA)

W ramach eksploracyjnej analizy danych (EDA) przeprowadzono szereg wizualizacji i analiz statystycznych, mających na celu lepsze zrozumienie zależności pomiędzy cechami zbioru danych. Przeanalizowano m.in. zmienność liczby transakcji w bloku, wartość przesyłanych środków, rozmiar bloków, nagrody dla górników oraz wysokość opłat transakcyjnych.

Dodatkowo, korzystając z platformy [https://www.blockchain.com](https://www.blockchain.com/explorer/charts/market-price), w dniu 18 lutego 2025 roku pobrano plik JSON zawierający historyczne dane cenowe Bitcoina. Dane te stanowią cenne uzupełnienie zbioru danych, umożliwiając porównanie zmian cenowych z innymi parametrami blockchaina. Uwzględnienie danych cenowych przyczyniło się do lepszego zrozumienia dynamiki ekosystemu Bitcoina.

### Rysunek 3.6: Średnia opłata transakcyjna w USD (tygodniowo) vs. Cena Bitcoina

<p align="center">
  <img src="screenshots/VSC/oplataUSD_cenaBTC.png" alt="OplataCena" />
</p>

Wykres ukazuje zależność pomiędzy średnią opłatą transakcyjną wyrażoną w USD a ceną Bitcoina. Zauważalna jest ogólna zgodność trendów – w okresach wzrostu ceny Bitcoina obserwuje się również wzrost opłat, co może świadczyć o zwiększonym obciążeniu sieci i rosnącym zainteresowaniu użytkowników.

### Rysunek 3.7: Macierz korelacji (Pearsona)

<p align="center">
  <img src="screenshots/VSC/macierz_korealacji.png" alt="MacierzKorelacji" />
</p>

Analiza macierzy korelacji pozwala wskazać kilka istotnych zależności:

- **Silna dodatnia korelacja** pomiędzy `block_height` a `timestamp` (~1) – wynika z rosnącej struktury blockchaina.
- **Silna dodatnia korelacja** między `input_value` a `output_value` (~1) – różnica między nimi to opłata transakcyjna, zazwyczaj niewielka.
- **Silna korelacja** między `size` a `weight` (~0.91) – obie zmienne opisują rozmiar danych w bloku.
- **Silna ujemna korelacja** `block_height` a `miner_reward` (~-0.88) – odzwierciedla wpływ halvingu na zmniejszającą się nagrodę blokową.
- Pozostałe zmienne wykazują słabe korelacje z innymi cechami, w tym opłatami.

## Przetwarzanie danych

W celu przygotowania danych do trenowania modeli predykcyjnych wykonano następujące kroki:

- **Imputacja braków danych** – nie stwierdzono brakujących wartości.
- **Inżynieria cech** – na podstawie daty utworzono nowe zmienne: rok, miesiąc, dzień, dzień tygodnia.
- **Podział danych**:
  - `train`: 2009-01-09 — 2022-01-01  
  - `validation`: 2022-01-01 — 2024-01-01  
  - `test`: 2024-01-01 — 2024-12-16
- **Selekcja zmiennych** – wykorzystano tylko kolumny numeryczne oraz `DayOfWeek` jako cechę kategoryczną.
- **Skalowanie danych** – zastosowano `MinMaxScaler` do przeskalowania danych numerycznych.
- **Kodowanie kategorii** – użyto one-hot encoding dla zmiennej `DayOfWeek`.

## Trenowanie i ocena modeli wielowymiarowych

Na podstawie danych wyodrębniono szereg cech opisujących bloki i transakcje w sieci Bitcoin, które posłużyły jako wejście do klasycznych modeli regresyjnych.

Przetestowano różne algorytmy, m.in.:
- Regresję liniową i jej warianty (Ridge, ElasticNet),
- Drzewa decyzyjne,
- Random Forest,
- Gradient Boosting,
- XGBoost.

Modele oparte na drzewach (szczególnie XGBoost) osiągały lepsze wyniki niż klasyczne regresje, co uzasadniło ich dalsze wykorzystanie.

## Dostrajanie hiperparametrów

W kolejnym kroku skupiono się na dostrojeniu modelu **XGBoost**, wykorzystując zarówno ręczne modyfikacje, jak i automatyczne przeszukiwanie siatki parametrów z użyciem `GridSearchCV`. Zastosowano 3-krotną walidację krzyżową dla 18 konfiguracji, by znaleźć optymalne ustawienia.

**Najlepsze parametry uzyskane w GridSearchCV:**
```python
{'learning_rate': 0.06, 'max_depth': 6, 'n_estimators': 330}
```

Dzięki temu udało się poprawić RMSE oraz współczynnik $R^2$, co wskazuje na lepsze dopasowanie i większą ogólność modelu.

## Predykcja na zbiorze testowym

Wytrenowany model XGBoost po dostrojeniu przetestowano na niezależnym zbiorze testowym. Wyniki wskazują na średni błąd RMSE wynoszący ~0.00065 BTC oraz umiarkowane $R^2$ (~0.23), co oznacza, że model tylko częściowo oddaje zmienność danych.

<p align="center">
  <img src="screenshots/VSC/PrognozowanieGridSearchCV.png" alt="PrognozowanieGridSearchCV" width="90%" />
</p>

Model miał trudności z przewidywaniem nagłych skoków opłat – szczególnie w okolicach halvingu Bitcoina – co może sugerować konieczność użycia bardziej zaawansowanych lub nieliniowych podejść w przyszłości.

## Modele jednowymiarowe

W tej części pracy skupiono się na prognozowaniu opłat transakcyjnych na podstawie **pojedynczej zmiennej czasowej** – wysokości bloku (`block_height`). Podejście to symuluje scenariusz, w którym nie mamy dostępu do szczegółowych danych o transakcjach, lecz chcemy przewidywać opłaty na podstawie samego przebiegu czasu.

Zrealizowano dwa podejścia:

- **Regresja liniowa**, wykorzystująca sam numer bloku jako predyktor.
- **Model SARIMA**, uwzględniający sezonowość i autokorelację w szeregu czasowym.

Zbiór treningowy obejmował dane od pierwszego do trzeciego halvingu, a testowy – od trzeciego halvingu wzwyż.

**Wyniki:**

- Regresja liniowa sprawdziła się jako punkt odniesienia, lecz nie radziła sobie z sezonowością ani gwałtownymi zmianami opłat.
- Model **SARIMA(1,1,1)(2,1,1)[144]** znacznie lepiej uchwycił dynamikę zmian, w tym niektóre skoki cenowe.

<p align="center">
  <img src="screenshots/VSC/SARIMA_USD.PNG" alt="SARIMA" width="90%" />
</p>

SARIMA wykazała wyraźnie lepsze dopasowanie do danych testowych niż regresja liniowa, choć nadal miała problemy z przewidywaniem ekstremalnych skoków opłat. Pokazuje to potencjał modeli szeregów czasowych przy ograniczonym zakresie danych wejściowych.

## Podsumowanie

Projekt miał na celu analizę i prognozowanie opłat transakcyjnych w sieci Bitcoin przy użyciu danych on-chain oraz rynkowych. Opracowano kompletny pipeline obejmujący pobieranie danych z węzła Bitcoin Core (RPC), ich przetwarzanie oraz eksplorację.

W części modelowej zastosowano zarówno:

- **modele wielowymiarowe** (regresja liniowa, Ridge, ElasticNet, Random Forest, XGBoost), jak i  
- **modele jednowymiarowe** (regresja liniowa, SARIMA) bazujące wyłącznie na numerze bloku (`block_height`).

Najlepsze wyniki osiągnął model **XGBoost**, zoptymalizowany przy użyciu `GridSearchCV` (`learning_rate=0.06`, `max_depth=6`, `n_estimators=330`), uzyskując **R² ≈ 23%** na zbiorze testowym. Choć wartości te nie są wysokie, odzwierciedlają złożoność zjawiska – opłaty transakcyjne są silnie zależne od nieregularnych i trudnych do przewidzenia czynników rynkowych.

Modele jednowymiarowe, mimo prostoty, nie były w stanie uchwycić zmienności danych – **R² regresji liniowej ≈ 2%**, **SARIMA < 0%** – co wskazuje na ich ograniczoną praktyczność w dokładnym prognozowaniu.

Warto przypomnieć, że analiza oparta była na 1% próbie danych. Użycie pełnych danych mogłoby znacząco poprawić trafność modeli. Dalsze kierunki rozwoju to m.in. użycie sieci neuronowych, podejść hybrydowych oraz uwzględnienie danych sentymentu rynkowego (np. z mediów społecznościowych).

# Analysis and Forecasting of Bitcoin Network Transaction Fees

## Project Description

The aim of this project was to gain a better understanding of how transaction fees in the Bitcoin network evolve and to assess the feasibility of effectively forecasting them based on data independently obtained from the blockchain.

Two forecasting approaches were compared:

- **Multivariate** – based on multiple features describing each block and its transactions,  
- **Univariate** – applicable in practical cases when only basic information is available (e.g., block number, timestamp).

This comparison made it possible to evaluate model performance under different conditions and gain deeper insight into the mechanisms of the Bitcoin network.

## Automated Data Acquisition and Processing from the Bitcoin Blockchain

To acquire the data, a VPN connection was established with a research group’s server, where a full Bitcoin Core node was installed and configured.

<p align="center">
  <img src="screenshots/screeny/blockchain-info.JPG" alt="BlockchainInfo" />
</p>

Block data was automatically retrieved in predefined ranges using the Python script [`Pobierz_Bloki_V4.py`](data_download/Pobierz_Bloki_V4.py). Initially, the data was saved in CSV format, but due to large file sizes, the **Parquet** format was adopted, offering much better performance for large datasets.

Next, the script [`Pobierz_Probke.py`](data_download/Pobierz_Probke.py) was used to randomly sample 1% of the records from each file. This produced a sample that:

- preserved the chronological order of the original dataset,
- was small enough for efficient analysis and modeling.

## Exploratory Data Analysis (EDA)

A variety of visualizations and statistical analyses were carried out to better understand relationships between dataset features. This included examining variability in the number of transactions per block, transferred value, block size, miner rewards, and transaction fees.

Additionally, on February 18, 2025, a JSON file containing historical Bitcoin price data was downloaded from [https://www.blockchain.com](https://www.blockchain.com/explorer/charts/market-price). These data complemented the on-chain dataset, allowing comparisons between price changes and other blockchain parameters. Incorporating price data helped to better understand Bitcoin’s ecosystem dynamics.

### Figure 3.6: Average Transaction Fee in USD (Weekly) vs. Bitcoin Price

<p align="center">
  <img src="screenshots/VSC/oplataUSD_cenaBTC.png" alt="OplataCena" />
</p>

The chart shows the relationship between the average transaction fee in USD and the Bitcoin price. There is a general alignment of trends – during periods of rising Bitcoin prices, transaction fees tend to increase as well, potentially indicating higher network demand and increased user activity.

### Figure 3.7: Pearson Correlation Matrix

<p align="center">
  <img src="screenshots/VSC/macierz_korealacji.png" alt="MacierzKorelacji" />
</p>

Key insights from the correlation matrix analysis:

- **Strong positive correlation** between `block_height` and `timestamp` (~1) – due to the blockchain’s sequential structure.
- **Strong positive correlation** between `input_value` and `output_value` (~1) – their difference is the transaction fee, which is usually small.
- **Strong correlation** between `size` and `weight` (~0.91) – both describe the block’s data size.
- **Strong negative correlation** between `block_height` and `miner_reward` (~-0.88) – reflects the halving effect reducing block rewards.
- Other variables showed weak correlations with transaction fees.

## Data Processing

To prepare the data for predictive modeling, the following steps were taken:

- **Missing values imputation** – no missing values were found.  
- **Feature engineering** – extracted year, month, day, and day of the week from the timestamp.  
- **Data splitting**:
  - `train`: 2009-01-09 — 2022-01-01  
  - `validation`: 2022-01-01 — 2024-01-01  
  - `test`: 2024-01-01 — 2024-12-16
- **Feature selection** – used only numeric columns and `DayOfWeek` as a categorical feature.  
- **Scaling** – applied `MinMaxScaler` to numeric features.  
- **Encoding** – applied one-hot encoding to the `DayOfWeek` variable.

## Training and Evaluation of Multivariate Models

From the dataset, multiple features describing Bitcoin blocks and transactions were extracted and used as inputs to classical regression models.

The tested algorithms included:

- Linear Regression and its variants (Ridge, ElasticNet),  
- Decision Trees,  
- Random Forest,  
- Gradient Boosting,  
- XGBoost.

Tree-based models (especially XGBoost) achieved better results than linear regressions, which justified their further use.

## Hyperparameter Tuning

The next step was to fine-tune the **XGBoost** model, using both manual adjustments and automated grid search with `GridSearchCV`. A 3-fold cross-validation was applied across 18 configurations to find the optimal setup.

**Best parameters from GridSearchCV:**
```python
{'learning_rate': 0.06, 'max_depth': 6, 'n_estimators': 330}
```
This resulted in improved RMSE and $R^2$ scores, indicating a better model fit and stronger generalization capabilities.

## Test Set Prediction

The tuned XGBoost model was evaluated on an independent test dataset.  
The results showed:

- **RMSE**: ~0.00065 BTC  
- **R²**: ~0.23  

This means the model was able to capture part of the variability in transaction fees but not all of it.

<p align="center">
  <img src="screenshots/VSC/PrognozowanieGridSearchCV.png" alt="PrognozowanieGridSearchCV" width="90%" />
</p>

The model struggled to predict sudden spikes in fees – especially around Bitcoin halving events – suggesting that more advanced or non-linear approaches may be necessary in the future.

## Univariate Models

This part of the study focused on forecasting transaction fees based on a **single time-based variable** – the block height (`block_height`).  
This approach simulates a scenario where no detailed transaction-level data is available, and predictions must rely solely on the passage of time.

Two approaches were implemented:

- **Linear Regression** – using only the block number as a predictor.  
- **SARIMA model** – incorporating seasonality and autocorrelation in the time series.

The training dataset covered data from the first to the third halving, while the test dataset included data from the third halving onward.

**Results:**

- Linear Regression served as a baseline but failed to capture seasonality or sudden changes in transaction fees.  
- The **SARIMA(1,1,1)(2,1,1)[144]** model better captured the dynamics of changes, including some fee spikes.

<p align="center">
  <img src="screenshots/VSC/SARIMA_USD.PNG" alt="SARIMA" width="90%" />
</p>

SARIMA achieved a noticeably better fit to the test data than Linear Regression, although it still struggled with predicting extreme fee spikes.  
This demonstrates the potential of time series models when only a limited set of input variables is available.

## Summary

The project aimed to analyze and forecast Bitcoin transaction fees using both on-chain and market data.  
A complete pipeline was developed, covering data acquisition from a Bitcoin Core node (via RPC), processing, and exploratory analysis.

In the modeling stage, both approaches were applied:

- **Multivariate models** (Linear Regression, Ridge, ElasticNet, Random Forest, XGBoost)  
- **Univariate models** (Linear Regression, SARIMA) based solely on block height (`block_height`)

The best results were achieved by the **XGBoost** model, optimized with `GridSearchCV`  
(`learning_rate=0.06`, `max_depth=6`, `n_estimators=330`), achieving **R² ≈ 23%** on the test set.  
Although this is not a high value, it reflects the complexity of the phenomenon – transaction fees are heavily influenced by irregular and hard-to-predict market factors.

Univariate models, despite their simplicity, were unable to capture the variability in the data – **R² for Linear Regression ≈ 2%**, **SARIMA < 0%** – highlighting their limited practical usefulness for accurate forecasting.

It should be noted that the analysis was based on a 1% sample of the data.  
Using the full dataset could significantly improve model accuracy.  
Future development directions include neural networks, hybrid approaches, and incorporating market sentiment data (e.g., from social media).
