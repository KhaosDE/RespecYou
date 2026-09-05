# RespecYou

**Versprich dir was. Zieh es durch. Hol es dir.**

Du hast schon Apps, die messen – Strava, Apple Fitness, Health Connect, die Uhr am Handgelenk.
RespecYou ist die, die dich losgehen lässt. Es ist kein weiterer Tracker, sondern die Schicht
darüber: Du sagst dir selbst etwas Echtes zu, und die App nimmt dich beim Wort.

Der Ablauf ist umgekehrt zu dem, was andere Apps machen. Zuerst legst du fest, was du dir gönnst,
wenn du es durchziehst. Danach, was du dafür regelmäßig tun musst. Ab dann zeigt dir der
Startbildschirm immer dein nächstes Versprechen und wie weit du noch davon entfernt bist. Ist es
erreicht, holst du dir die Belohnung mit einem Tipp ab – sie wandert mit Datum ins Archiv, und
deine Bilanz zählt mit: verdient und eingelöst.

## Warum das anders ist

Gewohnheits-Apps setzen darauf, dass die Belohnung im Kopf entsteht: eine Serie, ein Abzeichen,
ein zufriedenes Haustier. Selbstverpflichtungs-Apps gibt es auch, aber die arbeiten mit Strafe und
nehmen dir Geld ab, wenn du versagst. Dazwischen liegt nichts. Genau dort sitzt RespecYou.

- **Du versprichst, die App erinnert.** Nicht an einen Mangel, sondern an ein Guthaben:
  „Das hast du dir verdient und noch nicht geholt.“
- **Deine Ziele, nicht vorgegebene.** Vom Workout bis zur Alltagsgewohnheit, mit eigenem XP-Wert.
  Der Katalog mit über 50 Aktivitäten ist Vorschlag, nicht Vorgabe.
- **Keine doppelte Erfassung.** RespecYou misst nichts selbst, sondern holt Schritte und Kalorien
  aus Health Connect bzw. der Health-App. Uhr und Strava zählen mit.
- **Erinnerungen, die passen.** Uhrzeit und Wochentage pro Ziel, still wenn das Ziel heute schon
  erledigt ist.
- **Nichts verlässt dein Gerät.** Kein Konto, keine Anmeldung, keine Cloud.

## Features

- **Belohnungsvertrag** als Kern: Versprechen festlegen, Fortschritt sehen, einlösen, Bilanz führen.
  Vorschläge beim Anlegen, überwiegend solche, die nichts kosten
- **Erinnerungen je Ziel** mit Uhrzeit und Wochentagen (Android-App; Smartwatches spiegeln die
  Benachrichtigung automatisch)
- **Eigene Ziele** mit individuellem XP-Wert und optionalem Wochenziel
- **XP & Level-System** mit wachsendem Rang vom „Neuling“ bis „Unaufhaltsam“
- **Khaos**, dein Begleiter: ein flauschiges Pixelmonster in drei Entwicklungsformen – Fellknäuel,
  dann Hörner und Schwanz, zuletzt Flügel und Mähne. Männlicher oder weiblicher Körperbau frei
  wählbar, vier Farben schalten sich mit dem Level frei
- **Aktivitäten-Katalog** mit über 50 Vorschlägen in 6 Kategorien
- **Wochenchallenge & Tages-Motivation** mit wählbarem Schwierigkeitsgrad
- **Achievements** für Meilensteine, einzelne Aktivitäten, Serien und mehr
- **Perks**: Streak-Freeze rettet eine verpasste Serie, Doppel-XP-Tage, eine „Legendär“-Challenge-Stufe
- **Themes**: mehrere freischaltbare Farbdarstellungen im Retro-Terminal-Look
- **Automatischer XP-Gewinn aus echten Aktivitätsdaten** – auf Android über Health Connect
  (Handy/Watch/Samsung Health), auf iPhone über eine leichtgewichtige Bridge (siehe unten)

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

## Konzept

Die Überlegungen hinter der App liegen unter `notes/`:

- `konzept-check-2026-09.html` – Marktlage, Wettbewerb, was für ein bezahltes Produkt fehlt,
  Preismodell und Steuerfragen
- `konzept-belohnungsvertrag.html` – warum der Belohnungsvertrag das Alleinstellungsmerkmal ist
  und was das für Produkt und Store bedeutet

## Support

Feedback oder Ideen? In der App unter ⚙ Menü → ✉ Feedback senden.
