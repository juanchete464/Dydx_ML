import requests
import datetime

# ================= CONFIGURACIÓN =================

# Parámetros para la evaluación del riesgo:
LIQUIDITY_THRESHOLD = 10000        # Liquidez mínima aceptable en USD
MIN_TOKEN_AGE_HOURS = 24           # Mínimo 24 horas de antigüedad
SUSPICIOUS_KEYWORDS = ['scam', 'fake', 'new', 'pump']  # Palabras que elevan el riesgo
RISK_THRESHOLD = 10                # Umbral para aprobar la señal (si el score es <= 10, se aprueba)

# ================= FUNCIONES =================

def obtener_datos_token(api_url):
    """
    Función para obtener datos del token desde una API.
    Se espera que devuelva una lista de diccionarios con la siguiente información:
      - token_name: nombre del token
      - liquidity: liquidez actual en USD
      - creation_time: fecha de creación (ISO8601)
      - distribution: lista de porcentajes de tokens en las principales billeteras
      - audit: estado de auditoría ('positive', 'negative' o 'none')
      - on_chain_alerts: booleano, True si hay alertas on-chain
      - community: puntuación de la comunidad (0 = buena, 1 = mediocre, 2 = mala)
    
    Si no se puede acceder a la API, se retornan datos simulados.
    """
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error en la API. Código de estado:", response.status_code)
    except Exception as e:
        print("Excepción al obtener datos de la API:", e)
    
    # Datos simulados en caso de fallo en la API
    print("Utilizando datos simulados.")
    return [
        {
            "token_name": "LegitToken",
            "liquidity": 25000,
            "creation_time": (datetime.datetime.utcnow() - datetime.timedelta(hours=72)).isoformat(),
            "distribution": [0.05, 0.10, 0.12],
            "audit": "positive",
            "on_chain_alerts": False,
            "community": 0
        },
        {
            "token_name": "MediocreToken",
            "liquidity": 15000,
            "creation_time": (datetime.datetime.utcnow() - datetime.timedelta(hours=30)).isoformat(),
            "distribution": [0.16, 0.10],
            "audit": "negative",
            "on_chain_alerts": False,
            "community": 1
        },
        {
            "token_name": "NewScamToken",
            "liquidity": 5000,
            "creation_time": (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).isoformat(),
            "distribution": [0.40, 0.20],
            "audit": "none",
            "on_chain_alerts": True,
            "community": 2
        }
    ]

def calcular_antiguedad(creation_time):
    """
    Calcula la antigüedad del token en horas.
    """
    try:
        token_time = datetime.datetime.fromisoformat(creation_time)
        ahora = datetime.datetime.utcnow()
        diferencia = ahora - token_time
        return diferencia.total_seconds() / 3600.0
    except Exception as e:
        print("Error al calcular la antigüedad:", e)
        return 0

def evaluar_rugpull(token):
    """
    Calcula una puntuación de riesgo basada en múltiples factores.
    """
    score = 0
    nombre = token.get('token_name', '').lower()
    liquidez = token.get('liquidity', 0)
    creation_time = token.get('creation_time', None)
    distribution = token.get('distribution', [])
    audit = token.get('audit', 'none')
    on_chain_alerts = token.get('on_chain_alerts', False)
    community = token.get('community', 0)

    # Evaluación de la antigüedad
    if creation_time:
        edad = calcular_antiguedad(creation_time)
        if edad < MIN_TOKEN_AGE_HOURS:
            score += 5
        elif edad < MIN_TOKEN_AGE_HOURS * 2:
            score += 3
    else:
        score += 5  # Sin información de creación

    # Evaluación de la liquidez
    if liquidez < LIQUIDITY_THRESHOLD:
        score += 5
    elif liquidez < LIQUIDITY_THRESHOLD * 2:
        score += 2

    # Evaluación de la distribución (tokenomics)
    if distribution:
        mayor_concentracion = max(distribution)
        if mayor_concentracion > 0.3:
            score += 5
        elif mayor_concentracion > 0.15:
            score += 3

    # Indicadores en el nombre
    if any(palabra in nombre for palabra in SUSPICIOUS_KEYWORDS):
        score += 3

    # Evaluación de auditoría
    if audit == 'negative' or audit == 'none':
        score += 5

    # Evaluación de comportamiento on-chain
    if on_chain_alerts:
        score += 5

    # Evaluación de la comunidad (2 puntos por cada nivel negativo)
    score += community * 2

    print(f"Evaluación de {token.get('token_name', 'N/A')}: puntuación de riesgo = {score}")
    return score

def enviar_a_telegram(token):
    """
    Función simulada para enviar la señal a Telegram.
    En producción, se integraría la API de Telegram para enviar el mensaje real.
    """
    mensaje = (
        f"📈 *Señal de Trading Aprobada* 📉\n\n"
        f"*Token:* {token.get('token_name', 'N/A')}\n"
        f"*Liquidez:* ${token.get('liquidity', 'N/A')}\n"
        f"*Antigüedad:* {calcular_antiguedad(token.get('creation_time', '')):.2f} horas\n"
        f"*Auditoría:* {token.get('audit', 'N/A')}\n"
        f"*Señal aprobada con riesgo bajo*"
    )
    print("Enviando a Telegram:")
    print(mensaje)
    # Aquí se podría usar la API de Telegram (por ejemplo, con python-telegram-bot)

def filtrar_senales(api_url):
    """
    Consulta datos de tokens y aplica el filtro anti-rugpull.
    """
    tokens = obtener_datos_token(api_url)
    if not tokens:
        print("No se obtuvieron datos.")
        return

    for token in tokens:
        risk_score = evaluar_rugpull(token)
        if risk_score <= RISK_THRESHOLD:
            enviar_a_telegram(token)
        else:
            print(f"Token {token.get('token_name', 'N/A')} DESCARTADO (riesgo: {risk_score})\n")

# ================= MAIN =================

if __name__ == "__main__":
    # URL ficticia o real para obtener señales
    API_URL = "https://api.ejemplo.com/senales-token"  # Reemplaza con una URL real si está disponible
    filtrar_senales(API_URL)
