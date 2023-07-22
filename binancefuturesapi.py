import numpy as np
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Test der Zugriffsrechte für Mäxlein

# Liste der Kryptowährungen
cryptocurrencies = ['XRPUSDT']

# Zeitkonfiguration für die Abfrage der Kursdaten
interval = '5m'
limit = 1152  # - approx 4 days --PK

# Berechne die Anzahl der Tage, die für die Abfrage der Kursdaten benötigt werden
if interval == '1m':
    days = limit // (24 * 60)
elif interval == '5m':
    days = limit // (24 * 12)
elif interval == '1h':
    days = limit // 24
else:
    days = limit

# Daten für den Plot sammeln
plot_data = {}

# Für jede Kryptowährung den Kursverlauf abrufen und zur Plot-Daten hinzufügen
for cryptocurrency in cryptocurrencies:
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': cryptocurrency,
        'interval': interval,
        'limit': limit
    }
    response = requests.get(url, params=params)
    data = json.loads(response.text)

    # Extrahiere das Datum und den Schlusskurs aus den API-Daten
    timestamps = [item[0] for item in data]
    dates = [datetime.fromtimestamp(timestamp / 1000)
             for timestamp in timestamps]
    close_prices = [float(item[4]) for item in data]

    # Füge die Daten zum Plot hinzu
    plot_data[cryptocurrency] = {'Date': dates, 'Close Price': close_prices}

# Erstelle den Plot des Kursverlaufs
plt.figure(figsize=(10, 6))

buy_points = []  # Liste für die "buy" Punkte
sell_points = []  # Liste für die "sell" Punkte

last_buy_price = 0  # Der Preis der letzten "buy" Position

for cryptocurrency, data in plot_data.items():
    # Plotte den Kursverlauf
    plt.plot(data['Date'], data['Close Price'],
             color='gray', label=cryptocurrency)

    length = 20 # Länge der Bollinger-Bänder --PK
    std_multiplier = 1.0 # multiplikator für die Standardabweichung --PK

    sell_percentage = 1.0086  # Das gewünschte Prozentziel für den Verkauf --PK

    close_prices = data['Close Price']
    # Berechne den einfachen gleitenden Durchschnitt (Simple Moving Average)
    sma = np.convolve(close_prices, np.ones(length) / length, mode='valid')
    upper_band = sma + std_multiplier * np.std(close_prices[-length:])
    lower_band = sma - std_multiplier * np.std(close_prices[-length:])
    # Plotte die drei Bollinger-Bänder - removed SMA from plot ´--PK
    # plt.plot(data['Date'][length-1:], sma, 'b--', label='Simple Moving Average')
    plt.plot(data['Date'][length-1:], upper_band,
             'r--', label='Upper Bollinger Band')
    plt.plot(data['Date'][length-1:], lower_band,
             'g--', label='Lower Bollinger Band')

    # Finde die "buy" und "sell" Punkte basierend auf den Bollinger-Band-Bedingungen
    for i in range(length - 1, len(data['Close Price'])):
        if data['Close Price'][i] < lower_band[i - (length - 1)]:
            # Wenn der Preis unter die untere Bollinger-Band-Linie fällt und es keine offene Position gibt, markiere es als "buy"
            if not buy_points and not sell_points:
                buy_points.append(data['Date'][i])
                last_buy_price = data['Close Price'][i]
        elif data['Close Price'][i] > last_buy_price * sell_percentage:  # - das kann angepasst werden --PK
            # Wenn der Preis um sell_percentage% von der letzten "buy" Position steigt und es offene Positionen gibt, markiere es als "sell"
            if buy_points and not sell_points:
                sell_points.append(data['Date'][i])

    # Markiere die "buy" Punkte im Plot
    plt.scatter(buy_points, [data['Close Price'][data['Date'].index(
        point)] for point in buy_points], color='green', label='Buy Points')
    # Markiere die "sell" Punkte im Plot
    plt.scatter(sell_points, [data['Close Price'][data['Date'].index(
        point)] for point in sell_points], color='red', label='Sell Points')

    # Verbinde die Punkte mit einem Quadrat
    for j in range(len(buy_points)):
        plt.plot([buy_points[j], sell_points[j]], [data['Close Price'][data['Date'].index(
            buy_points[j])], data['Close Price'][data['Date'].index(sell_points[j])]], color='Brown')

# Konfiguriere die x-Achse für die Beschriftung
if interval == '1m':
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y - %H:%M'))
elif interval == '5m':
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y - %H:%M'))
elif interval == '1h':
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y - %H:%M'))
else:
    plt.gca().xaxis.set_minor_locator(mdates.DayLocator())
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))

plt.gcf().autofmt_xdate()

# Beschriftungen und Titel hinzufügen
plt.xlabel('Datum')
plt.ylabel('Schlusskurs')

if interval == '1m':
    title = f'Kursverlauf der letzten {days} Tage mit Bollinger-Bändern'
elif interval == '5m':
    title = f'Kursverlauf der letzten {days} Tage mit Bollinger-Bändern'
elif interval == '1h':
    title = f'Kursverlauf der letzten {days} Tage mit Bollinger-Bändern'
else:
    title = f'Kursverlauf der letzten {days} Tage mit Bollinger-Bändern'

# Zeige die aktualisierte Legende an
plt.legend()

plt.title(title)

# Speichere den Plot als Bild im Dateinamen
plt.savefig('plot.png')

# Zeige den Plot an
plt.show()
