library(dplyr)
fee_oryg <- read.csv("E:/STUDIA/II STOPNIA/PRACA_MAGISTERSKA/opaty_w_btc.csv")

fee_m <- fee_oryg %>%
  group_by(block_height) %>%
  summarise(
    fee = mean(fee),
    price_BTC = mean(price_BTC),
    datetime = first(datetime),
    .groups = "drop"
  )

fee_m210plus <- fee_m[fee_m$block_height>(210)*10^3,]

fee <- fee_m210plus %>%
  mutate(BHby1000 = floor(block_height / 1000) * 1000) %>%
  group_by(BHby1000) %>%
  summarise(
    fee = mean(fee),
    price_BTC = mean(price_BTC),
    datetime = first(datetime),
    .groups = "drop"
  )

plot(x=fee$BHby1000, y=fee$fee, type = 'l')
abline(v=1:4*(210*10^3), col = "red")

ts_fee <- ts(fee$fee, frequency = 210)
plot(ts_fee)
abline(v=1:4, col = "red")

ggseasonplot(ts_fee)

monthplot(ts_fee)


library(forecast)
seasonplot(ts_fee, 
           col = rainbow(12), 
           year.labels = TRUE, 
           pch = 19)

lag.plot(ts_fee,lags = 21, do.lines = FALSE)

ts_fee_diff <- diff(ts_fee)
plot(ts_fee_diff)
lag.plot(ts_fee_diff,lags = 25, do.lines = FALSE)


feePD <- decompose(ts_fee, type = "additive")
plot(feePD)

feePD <- decompose(ts_fee, type = "multiplicative")
plot(feePD)


model <- auto.arima(ts_fee, seasonal = TRUE)
summary(model)

model <- auto.arima(
  ts_fee,
  seasonal = TRUE,
  stepwise = FALSE,
  approximation = FALSE
)
summary(model)
fitted_values <- fitted(model)
plot(ts_fee, main = "Dane oryginalne i dopasowanie ARIMA", col = "black")
lines(fitted_values, col = "blue", lty = 2)
legend("topleft", legend = c("Oryginał", "ARIMA fitted"), col = c("black", "blue"), lty = c(1, 2))

forecasted <- forecast(model, h = 3*21)
plot(forecasted, main = "Prognoza ARIMA")

aa_model <- auto.arima(ts_fee)
summary(aa_model)

# Fitted values (dopasowanie modelu do danych historycznych)
fitted_values <- fitted(aa_model)

# Wykres oryginalnych danych + wartości dopasowanych
plot(ts_fee, main = "Dane oryginalne i dopasowanie ARIMA", col = "black")
lines(fitted_values, col = "blue", lty = 2)
legend("topleft", legend = c("Oryginał", "ARIMA fitted"), col = c("black", "blue"), lty = c(1, 2))

forecasted <- forecast(aa_model, h = 210)

# Wykres prognozy
plot(forecasted, main = "Prognoza ARIMA")

wygl = 20
ts_feef <- stats::filter(x=ts_fee,filter = rep(1/wygl,wygl), sides = 2)
plot (ts_feef)
model <- auto.arima(
  ts_feef,
  seasonal = TRUE,
  stepwise = FALSE,
  approximation = FALSE
)
summary(model)
