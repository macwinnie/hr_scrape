# Über den Arbeitgeber informiert bleiben

Deutsche Firmen geben über das [Handelsregister](https://www.handelsregister.de) einige Informationen über sich selbst preis.

Mit dem folgenden kleinen Snippet ist es Mac-Nutzern möglich, sich selbst z.B. über den eigenen Arbeitgeber auf dem Laufenden zu halten.

## Funktionsweise

Das Python-Skript ruft die Veröffentlichungen, welche zu einem Register-Eintrag gehören, ab und überprüft, ob es diese schon kennt.

Um sich Einträge zu merken, nutzt es eine SQLite Datenbank.

Für alle neuen Einträge wird neben dem Datenbankeintrag auch eine System-Notification abgesetzt.

## Vorbereitung

### Installationen

Damit das Skript erfolgreich läuft, benötigst du auf deinem Mac ein paar Hilfs-Tools. Führe bitte folgende Befehle im Terminal aus:

```sh
brew install terminal-notifier
# sudo gem install terminal-notifier
pip3 install args beautifulsoup4 pync python-dotenv requests
```

Den terminal-notifier nutzen wir, um dir Notifications am Mac zu senden. Bei der ersten Notification musst du diese noch zulassen – aber das Prozedere kennst du bestimmt schon.

### Anlegen der Skript- und Config-Files

Das Skript und das Config-File legst du am besten mit den folgenden Shell-Zeilen an (die Session am besten danach nicht beenden, weiter unten gibt's noch ein paar weitere Befehle hinterher):

```sh
base_path_hr="${HOME}/.handelsregister/"
script_file="${base_path_hr}fetch.py"

git clone https://github.com/macwinnie/hr_scrape.git "${base_path_hr}"

cat << EOF > "${base_path_hr}.env"
titel   = "demo"
aktion  = "ggrzhagen"
regart  = ""
gkz     = ""
regnr   = ""
gkz_alt = ""
EOF

chmod a+x "${script_file}"
```

### Online-Recherche

Wissen muss man für die weitere Konfiguration ein paar Informationen, die man am besten über die [Suche im Handelsregister](https://www.handelsregister.de/rp_web/mask.do?Typ=n) und einem anschließenden Klick auf dem richtigen Ergebnis auf den `VÖ` Link (Veröffentlichungen). Die URL, welche am Ende geladen wurde, gibt alle notwendigen Informationen:

* `aktion` (dürfte meist `ggrzhagen` sein)
* `gkz`
* `regart`
* `regnr`
* `gkz_alt`
* `titel` – der Titel, welcher in den Notifications angezeigt wird

Diese Parameter müssen über eine `.env` Datei definiert sein. Diese haben wir mit den Code-Zeilen oben im Pfad `~/.handelsregister/.env` angelegt. Bearbeitet könnte sie dann in etwa so aussehen:

```
aktion  = "ggrzhagen"
regart  = "HRB"
gkz     = "12345"
regnr   = "54321"
gkz_alt = ""
```

## Informiert bleiben

### Cronjob – regelmäßig laufen lassen

Mit den folgenden Skript-Zeilen in der Terminal-Sitzung von oben kannst du dir dann einen Cronjob einstellen, der jeden Werktag um z.B. 11:30 Uhr Vormittags eine Anfrage an das Handelsregister stellt und dich bei neuen Infos per Mac-Notification informiert:

```sh
cron_string="30 11 * * 1-5"

crontab -l | { cat; echo "${cron_string}  ${script_file}"; } | crontab -

```

### Weitere Adaption und mehrere Register-Abfragen

Das Skript ist grundsätzlich so gebaut, dass es auch ohne `.env` Datei auskommt. In dem Fall muss man mit Skript-Parametern arbeiten. Hier kurz die Übersetzung der Parameter:

| Parameter | ENV Variable |
| --------- | ------------ |
| `-a`      | `aktion`     |
| `-z`      | `gkz`        |
| `-r`      | `regart`     |
| `-n`      | `regnr`      |
| `-k`      | `gkz_alt`    |
| `-t`      | `titel`      |

Die Standard-Werte sind jeweils leere Strings, so dass man den Aufruf wie oben im Beispiel `.env` auch so realisieren kann:

```sh
"${script_file}" -a "ggrzhagen" -z "12345" -r "HRB" -n "54321" -t "demo"
```

Dadurch lassen sich mehrere Abfragen analog zu oben definieren und terminieren, falls man über mehrere Unternehmen informiert bleiben möchte.

## Lizenz

Publiziert unter [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
