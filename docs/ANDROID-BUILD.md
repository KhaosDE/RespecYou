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

### Schritt für Schritt (Windows, PowerShell)

Du kannst den **ganzen** Projektordner kopieren. Die `.gitignore` im Repo hält alles heraus, was
nicht hineingehört: `node_modules`, `build`, `.gradle`, `.idea`, `local.properties`, `www` und
jede `*.jks`/`*.keystore`.

```powershell
# 1. Repository holen (einmalig; sonst nur die letzten zwei Zeilen)
cd $HOME\Documents
git clone https://github.com/KhaosDE/RespecYou.git
cd RespecYou
git checkout main
git pull

# 2. Capacitor-Projekt hineinkopieren – Pfad links anpassen
$quelle = "C:\Pfad\zu\deinem\RespecYou-Capacitor"
New-Item -ItemType Directory -Force -Path app | Out-Null
Copy-Item "$quelle\*" -Destination app -Recurse -Force

# 3. Kontrolle: was würde übertragen werden?
git add app
git status --short | Measure-Object -Line      # Anzahl Dateien
git status --short | Select-String -Pattern "node_modules|\.jks|\.keystore|local.properties"
```

Die letzte Zeile muss **leer** bleiben. Erscheint dort etwas, brich ab (`git reset`) und melde dich,
bevor du weitermachst. Die Anzahl der Dateien liegt normalerweise bei 60 bis 200 – sind es
Tausende, sind node_modules mit dabei.

```powershell
# 4. Übertragen
git commit -m "Add the Capacitor project"
git push
```

Unter macOS oder Linux ist es dasselbe mit `cp -r /pfad/zum/projekt/. app/` statt `Copy-Item`.

**Ohne Git**: Du kannst den Ordner auch über die GitHub-Weboberfläche hochladen (Add file →
Upload files, Ordner hineinziehen). Lösche vorher `node_modules`, `build`, `.gradle` und den
Keystore aus der Kopie, denn beim Weg über den Browser greift die `.gitignore` nicht.

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

## Lokal bauen statt über Actions

Geht genauso, wenn Android Studio auf dem Rechner steht. Der Unterschied: Der Keystore bleibt
lokal, es braucht keine Secrets. Unter Windows heißt der Gradle-Aufruf `.\gradlew.bat`, nicht
`./gradlew`.

```powershell
# im RespecYou-Repository
python tools\build.py

# im Capacitor-Projekt
Remove-Item www\* -Recurse -Force
Copy-Item <repo>\dist\android\www\* -Destination www -Recurse
# versionName und versionCode in android\app\build.gradle setzen
npx cap sync android
cd android
.\gradlew.bat assembleRelease `
  "-Pandroid.injected.signing.store.file=C:\Pfad\zu\respecyou.jks" `
  "-Pandroid.injected.signing.store.password=..." `
  "-Pandroid.injected.signing.key.alias=..." `
  "-Pandroid.injected.signing.key.password=..."
```

Die fertige Datei liegt unter `android\app\build\outputs\apk\release\`.

Release samt APK anlegen, wenn die GitHub-CLI installiert ist:

```powershell
gh release create 1.5 RespecYou-v1.5.apk `
  --title "RespecYou 1.5 (Android, Test)" `
  --notes-file docs\release-notes\1.5.md
```

Sonst über die Weboberfläche: Releases → Draft a new release, Tag `1.5`, Text aus
`docs/release-notes/1.5.md` einfügen, APK hineinziehen.

## Ein Release über Actions bauen

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
