# Android-APK über GitHub Actions bauen

Ziel: Kein lokaler Build mehr. Ein Versions-Tag genügt, GitHub baut das signierte APK und hängt
es ans Release. Der Signaturschlüssel bleibt geheim und liegt nie im Repository.

Der Workflow dazu ist `.github/workflows/android-release.yml`. Er läuft erst, wenn die beiden
Voraussetzungen unten erfüllt sind, und bricht sonst mit einer klaren Meldung ab.

---

## Voraussetzung 1: Capacitor-Projekt nach `app/`

Dein Capacitor-Projekt liegt bisher nur auf deinem Rechner. Es muss ins Repository, sonst kann
GitHub nichts bauen. Struktur danach:

```
app/
  package.json
  package-lock.json
  capacitor.config.json     (oder .ts)
  android/                  komplettes Android-Projekt
  www/                      wird beim Build überschrieben, nicht pflegen
```

So schiebst du es rein (auf deinem Rechner, im geklonten Repo):

```bash
git checkout main && git pull
mkdir app
# Inhalt deines Capacitor-Projekts nach app/ kopieren – ohne node_modules,
# ohne build-Ordner, ohne local.properties und ohne den Keystore
git add app
git commit -m "Add the Capacitor project"
git push
```

Die `.gitignore` im Repo hält die Ordner heraus, die nicht hineingehören: `node_modules`,
`build`, `.gradle`, `local.properties`, `www` und jede `*.jks`/`*.keystore`.

**Der Keystore darf nicht ins Repository.** Er kommt als Secret rein, siehe unten.

### Was der Workflow annimmt

| Annahme | Falls bei dir anders |
|---|---|
| `webDir` in der Capacitor-Konfiguration ist `www` | Pfad im Schritt „Web-Fassung übernehmen“ anpassen |
| `versionName` und `versionCode` stehen in `app/android/app/build.gradle` | Schritt „Version setzen“ anpassen |
| Gradle-Wrapper liegt unter `app/android/gradlew` | Arbeitsverzeichnis anpassen |

---

## Voraussetzung 2: Vier Secrets anlegen

Unter **Settings → Secrets and variables → Actions → New repository secret**:

| Name | Inhalt |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | Dein Keystore als Base64-Text |
| `ANDROID_KEYSTORE_PASSWORD` | Passwort des Keystores |
| `ANDROID_KEY_ALIAS` | Alias des Schlüssels |
| `ANDROID_KEY_PASSWORD` | Passwort des Schlüssels (oft identisch mit dem Keystore-Passwort) |

Keystore in Base64 umwandeln, unter Windows in PowerShell:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Pfad\zu\respecyou.jks")) | Set-Clipboard
```

Unter macOS oder Linux:

```bash
base64 -w0 respecyou.jks | pbcopy      # macOS
base64 -w0 respecyou.jks               # Linux, Ausgabe kopieren
```

Danach einfügen. Der Text ist lang, das ist normal.

**Nutze denselben Keystore wie bei 1.4.** Mit einem anderen Schlüssel verweigert Android das
Update über die installierte App, sie müsste erst deinstalliert werden.

Secrets sind für niemanden lesbar, auch nicht für mich. In den Logs erscheinen sie maskiert.

---

## Ein Release bauen

1. Versionsnummern in `VERSION` setzen (`android=1.6`, `ios=…`), committen, pushen.
2. Tag setzen und pushen:
   ```bash
   git tag 1.6
   git push origin 1.6
   ```
3. Der Workflow startet von selbst. Unter **Actions** siehst du den Lauf.
4. Ist auf GitHub bereits ein Release mit diesem Tag angelegt, wird das APK dort angehängt.
   Sonst legt der Workflow eines an, das du danach mit Text füllst.

Ohne Tag testen: unter **Actions → Android Release → Run workflow**, Versionsnummer eintragen.
Das APK liegt dann als Artefakt beim Lauf, 30 Tage lang, und wird an kein Release gehängt.

### Versionsnummern

`versionName` kommt aus dem Tag beziehungsweise der Eingabe. Der `versionCode` wird daraus
berechnet: `major × 10000 + minor × 100 + patch`, aus 1.6 wird also 10600. Das steigt mit jeder
Version zuverlässig an. Prüf einmalig, dass der `versionCode` deiner installierten 1.4 kleiner
als 10500 ist – sonst lässt Android das Update nicht zu und die Formel muss angepasst werden.

---

## Wenn der Lauf fehlschlägt

| Meldung | Ursache |
|---|---|
| `app/package.json fehlt` | Capacitor-Projekt ist noch nicht unter `app/` |
| `Secret … ist nicht gesetzt` | Eines der vier Secrets fehlt |
| `Keystore was tampered with, or password was incorrect` | Base64 unvollständig kopiert oder falsches Passwort |
| `SDK location not found` | `local.properties` wurde mit eingecheckt – muss raus |
| `Kein APK gefunden` | Gradle-Build lief durch, legt die Datei aber woanders ab; Pfad im Workflow anpassen |

Die vollständigen Logs stehen unter Actions beim jeweiligen Lauf.
