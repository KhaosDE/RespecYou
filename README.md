# RespecYou

**Skill dich neu · Raus aus der Komfortzone**

RespecYou ist keine weitere Sport-Tracking-App. Es gibt bereits genug davon – Strava, Apple Fitness, Health Connect, die Uhr am Handgelenk. RespecYou konkurriert nicht mit ihnen, sondern ist das **Bindeglied dazwischen**: eine kleine, persönliche Motivationsschicht, die dich dazu bringt, die Tools zu nutzen, die du schon hast, und deine eigenen Ziele wirklich zu erreichen.

Im Kern ist RespecYou ein Level-Up-System für dein reales Leben: Du legst eigene Ziele fest (vom Workout bis zur Alltagsgewohnheit), sammelst dafür XP, steigst Level auf und schaltest dabei Belohnungen frei – digitale wie eigene, echte.

## Warum RespecYou?

Die meisten Fitness-Apps scheitern nicht an fehlenden Funktionen, sondern daran, dass sie nach zwei Wochen langweilig werden. RespecYou setzt bewusst auf spielerische Motivation statt auf reine Datenerfassung:

- **Deine Ziele, nicht vorgegebene.** Du definierst selbst, was für dich zählt – kein starres Programm.
- **Kleine Schritte zählen.** Der eingebaute Aktivitäten-Katalog (nach Kategorien sortiert: Ausdauer, Kraft, Beweglichkeit & Entspannung, Alltag, Sport & Spiel, Sonstiges) ist eine optionale Ergänzung für Inspiration – nicht Pflicht.
- **Fortschritt fühlt sich gut an.** XP, Level, Ränge, Achievements und ein wachsender Begleiter machen sichtbar, was sonst unsichtbar bleibt.
- **Echte Belohnungen.** Neben den digitalen Anreizen kannst du dir selbst reale Belohnungen setzen, die sich mit steigendem Level freischalten.

## Features

- **XP & Level-System** mit wachsendem Rang/Titel (vom "Neuling" bis "Unaufhaltsam")
- **Eigene Ziele** mit individuellem XP-Wert und optionalem Wochenziel
- **Aktivitäten-Katalog** mit über 50 Vorschlägen in 6 Kategorien – als Zusatzquelle für die Wochenchallenge, nicht als Zwang
- **Wochenchallenge & Tages-Motivation** mit wählbarem Schwierigkeitsgrad
- **Achievements** für Meilensteine, einzelne Aktivitäten, Serien und mehr
- **Khaos**, dein Begleiter: ein flauschiges Pixelmonster, das mit deinem Level sichtbar wächst (alle 10 Level eine neue Form). Männlich oder weiblich wählbar, vier Farben schalten sich mit dem Level frei – dein Fortschritt bleibt dabei immer erhalten
- **Perks**: Streak-Freeze (rettet eine verpasste Serie), Doppel-XP-Tage, eine "Legendär"-Challenge-Stufe
- **Erinnerungen je Ziel**: Uhrzeit und Wochentage pro Ziel, Khaos meldet sich nur, wenn das Ziel heute noch offen ist (Android-App; Smartwatches spiegeln die Benachrichtigung)
- **Belohnungsvertrag** als Kern: Du legst zuerst fest, was du dir gönnst, arbeitest darauf hin, löst die Belohnung ein und siehst deine Bilanz. Vorschläge helfen beim Anlegen, überwiegend solche, die nichts kosten
- **Themes**: mehrere freischaltbare Farbdarstellungen im Retro-Terminal-Look
- **Automatischer XP-Gewinn aus echten Aktivitätsdaten** – auf Android über Health Connect (Handy/Watch/Samsung Health), auf iPhone über eine leichtgewichtige Bridge, die Schritte/Kalorien aus der Health-App abholt (siehe unten)

## Plattformen

- **Android**: native App (Capacitor), signierte Releases hier im Repo unter [Releases](../../releases)
- **iOS**: als Progressive Web App (PWA) unter **https://khaosde.github.io/RespecYou/** – in Safari öffnen und über "Zum Home-Bildschirm" installieren, läuft danach wie eine native App inkl. Offline-Nutzung

### iPhone-Bridge

Da Apple HealthKit keinen Web-Zugriff erlaubt, holt sich die iOS-Version Schritt- und Kaloriendaten über einen einmalig eingerichteten iOS-Kurzbefehl, der täglich automatisch die Health-App-Daten in einen privaten GitHub Gist schreibt. Die App liest diesen Gist beim Öffnen aus. Einrichtung erfolgt direkt in der App unter ⚙ Menü → 📱 iPhone-Bridge.

## Technik

Eine gemeinsame Quelle, zwei getrennte Plattform-Fassungen mit eigenen Versionsnummern:

```
src/index.html              gemeinsame Quelle (die ganze App)
VERSION                     Versionsnummern, getrennt für android und ios
tools/build.py              erzeugt beide Fassungen
  -> docs/                  iOS/Web (PWA, GitHub Pages)
  -> dist/android/www/      Android (in das lokale Capacitor-Projekt nach www/ kopieren)
tools/khaos_gen.py          erzeugt die Khaos-Pixelraster (Ausgabe in src/index.html einsetzen)
tools/preview.py            baut eine einzelne, in sich geschlossene Datei zum Verschicken (--test
                            fügt einen Knopf zum Zurücksetzen hinzu)
```

Nach jeder Änderung an `src/index.html` einmal `python3 tools/build.py` ausführen – erst dann sind
`docs/` und `dist/` aktuell. Was sich zwischen den Fassungen unterscheidet:

| | Android | iOS/Web |
|---|---|---|
| Erinnerungen je Ziel | ja (geplante Benachrichtigungen) | nein, technisch nicht möglich |
| Health-Daten | Health Connect | iPhone-Bridge über Kurzbefehl |
| Update-Suche in der App | ja (APK aus den Releases) | nein, Store bzw. Neuladen |
| Auslieferung | Capacitor-Build, signiertes APK | GitHub Pages, „Zum Home-Bildschirm“ |

Daten bleiben lokal auf dem Gerät (`localStorage`), keine Cloud-Anbindung außer der optionalen iPhone-Bridge.

## Support

Feedback oder Ideen? In der App unter ⚙ Menü → ✉ Feedback senden.
