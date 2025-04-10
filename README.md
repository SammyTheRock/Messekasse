# 📚 Messekassen-System
## 🧾 What is this even?

Dieses Messekassensystem wurde für Messen an Bord entwickelt, um den Verkauf von Waren (z. B. Snacks, Getränke, Merchandise) zu vereinfachen. Es ist ein minimalistisches, aber funktionales Kassensystem mit Fokus auf Einfachheit, Transparenz und gemeinschaftlicher Verwaltung.

✨ Hauptfunktionen:
- Darstellung der Nutzer (optimal zwischen 5 und 50 Nutzern), eines Leaderboards zur Motivation und einer Klingelliste
-  Login per Button (+ optional mit PIN)
-  Artikelverkauf nach Kategorien mit Warenkorb (Bei Anlegen einer "Specials"-Kategorie werden diese Specials besonders hervorgehoben. Eignet sich insbesondere für das Special "Klingeln🔔")
-  Verwaltung von Wallet-Guthaben (Einzahlungen, Ausgaben, Monatsabrechnung, Messebeiträge, Kaffeeflat)
-  Spezielle Funktion für Marinerechnungen (Gleichmäßige Teilung einer Rechnung auf ausgewählte Personen)
-  Monatsübersichten für Superuser
-  Mail-Erinnerungen bei negativem Saldo


🚀 Installation / Setup
1. 🔧 Voraussetzungen
    Python 3.9+
    Django 4.x
    Eine Datenbank (SQLite reicht zum Start)

2. 📥 Klonen und vorbereiten

```
git clone https://github.com/deinname/messekasse.git
cd messekasse
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. 🛠 Migration und Superuser anlegen
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
4. 📦 Medienordner und statische Dateien (optional)
```
mkdir media
python manage.py collectstatic
```
5. ▶️ Starten des Testservers
```
python manage.py runserver
```
Zugänglich unter http://localhost:8000

## 🤝 Beitrag leisten

Du möchtest helfen? Mega!
Ideen, wie du mitwirken kannst:

    Verbesserung der Benutzeroberfläche (z. B. mit Icons, Dark Mode, Barrierefreiheit)

    Erstellung eines Dockercontainers 

    Unit-Tests oder CI-Integration

    PDF-Export der Rechnungen oder QR-Code-Integration

    Feature-Vorschläge / Issues posten

    Übersetzungen (i18n)

    Dokumentation erweitern

👉 Bitte erstelle ein Issue, bevor du einen größeren Pull Request einreichst.
