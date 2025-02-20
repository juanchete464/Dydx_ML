# -*- coding: utf-8 -*-
import os
from dydx3 import Client
from xgboost import XGBClassifier
import pandas as pd
import vectorbt as vbt
from dotenv import load_dotenv

load_dotenv()

# Configuración de dYdX
client = Client(
    host="https://api.dydx.exchange",
    api_key_credentials={
        "key": os.getenv("DYDX_API_KEY"),
        "secret": os.getenv("DYDX_API_SECRET"),
        "passphrase": os.getenv("DYDX_PASSPHRASE")
    }
)

# Descarga de datos en bloques de 100 velas
print("📊 Descargando datos de dYdX...")
all_candles = []
for i in range(0, 1000, 100):  # Descarga 1000 velas en bloques de 100
    candles = client.public.get_candles(
        market="BTC-USD",
        resolution="1HOUR",
        limit=100
    ).data["candles"]
    all_candles.extend(candles)

df = pd.DataFrame(all_candles)
df["close"] = df["close"].astype(float)

# Preprocesamiento
df["sma_50"] = df["close"].rolling(50).mean()
df["sma_200"] = df["close"].rolling(200).mean()
df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)
df.dropna(inplace=True)

# Entrenamiento con GPU
print("🎮 Entrenando modelo (usando GPU RTX 4080)...")
model = XGBClassifier(
    tree_method="gpu_hist",  # Usa GPU
    predictor="gpu_predictor",
    n_estimators=1000
)

X = df[["sma_50", "sma_200"]]
y = df["target"]

model.fit(X, y)

# Backtest
print("🔍 Realizando backtest...")
portfolio = vbt.Portfolio.from_signals(
    close=df["close"],
    entries=model.predict(X) == 1,
    exits=model.predict(X) == 0,
    fees=0.0015  # Comisiones de dYdX
)

print(f"📈 Resultados:\n{portfolio.stats()}")

# Guarda el modelo
model.save_model("/app/models/dydx_model.ubj")
print("✅ Modelo guardado en /app/models/")