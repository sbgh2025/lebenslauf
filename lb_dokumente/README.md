# 🗂 Lebenslauf-Datenbank-System mit Python, SQLite & GUI

Dieses Projekt umfasst ein vollständiges System zur Verwaltung und Bearbeitung von Lebensläufen mit Python, SQLite und Tkinter. Es unterstützt Datenbankverwaltung, GUI-basierte Eingabe, CSV-Import sowie den Export professioneller Lebensläufe nach Excel.

---

## 🔧 Technologien

- Python 3
- SQLite (`sqlite3`)
- Tkinter (GUI)
- OpenPyXL (Excel-Export)

---

## 📁 Datenbankstruktur

Die zentrale SQLite-Datenbank `lebenslauf.db` besteht aus logisch verknüpften Tabellen:

| Tabelle                 | Inhalt                                                                             |
|-------------------------|------------------------------------------------------------------------------------|
| `tbl_bewerber`          | Persönliche Daten                                                                  |
| `tbl_firma`             | Zielunternehmen                                                                    |
| `tbl_bewerbung`         | Verknüpfung Bewerber ↔ Firma                                                       |
| `tbl_arbeitgeber`       | Berufliche Stationen                                                               |
| `tbl_bwg_ag`            | Verknüpfung Bewerber ↔ Arbeitgeber                                                 |
| `tbl_taetigkeit`        | Tätigkeiten                                                                        |
| `tbl_bwg_ag_t`          | Verknüpfung Bewerbung ↔ Arbeitgeber ↔ Tätigkeit          |
| `tbl_ausbildung`        | Ausbildungsstationen                                                               |
| `tbl_bwg_ab`            | Verknüpfung Bewerber ↔ Ausbildungsstation                                          |
| `tbl_ab_schwerpunkt`    | Ausbildungsschwerpunkte                                                            |
| `tbl_bwg_ab_swp`        | Verknüpfung Bewerbung ↔ Ausbildungsstätte ↔ Schwerpunkt  |
| `tbl_kenntnisse`        | Fachliche Kenntnisse                                                               |
| `tbl_bwg_k`             | Verknüpfung Bewerbung ↔ Kenntnisse                                                 |
| `tbl_interessen`        | Persönliche Interessen                                                             |
| `tbl_bwg_i`             | Verknüpfung Bewerbung ↔ Interessen                                                 |


**Aufruf des Programms per Skript:**

```bash
python lb_index.py
```
**Datenbankerstellung per Skript:**

```bash
python lb_datenbank.py
```
**Ansicht vom Inhalt der Datenbank per Skript:**

```bash
python lb_db_inhalt.py
```


### Unterstützte CSV-Formate

```csv
# tbl_bewerber
Vorname,Nachname,Geburtsdatum,Straße,PLZ,Ort,E-Mail,Telefon

# tbl_firma
Datum,Stellenbezeichnung,Firmenname,Straße,PLZ,Ort,E-Mail,Telefon

# tbl_arbeitgeber
Datum von,Datum bis,Firmenname,Zeitraum,Funktion,Ort,Leihfirma,Bemerkung

# tbl_taetigkeit
Tätigkeit

# tbl_ausbildung
Datum von,Datum bis,Ausbildungsstätte,Ausbildung,Abschluss,Zeitraum

# tbl_ab_schwerpunkt
Schwerpunkt

# tbl_kenntnisse
Kenntnis,Stufe

# tbl_interessen
Interesse
```

### Funktionen des GUI-Frontends


Ein Tkinter-Frontend erlaubt das **Hinzufügen**, **Bearbeiten**, **Anzeigen und Löschen** und **CSV-Importieren** von Datensätzen.

## 🔗 Verknüpfungstabellen

Zur Modellierung komplexer Beziehungen zwischen Bewerbungen, Arbeitgebern, Tätigkeiten, Ausbildungen, Kenntnissen und Interessen dienen mehrere Verknüpfungstabellen:

| Tabelle               | Zweck                                                                  |
|------------------------|------------------------------------------------------------------------|
| `tbl_bwg_ag`           | Bewerbung ↔ Arbeitgeber                                                |
| `tbl_bwg_ag_t`         | Bewerbung ↔ Arbeitgeber ↔ Tätigkeit (bis zu 3 Tätigkeiten)             |
| `tbl_bwg_ab`           | Bewerbung ↔ Ausbildungsstation                                         |
| `tbl_bwg_ab_swp`       | Bewerbung ↔ Ausbildungsstätte ↔ Schwerpunkt (bis zu drei Schwerpunkte) |
| `tbl_bwg_k`            | Bewerbung ↔ Kenntnisse                                                 |
| `tbl_bwg_i`            | Bewerbung ↔ Interessen                                                 |

---

## 📤 Lebenslauf-Export (Excel)

Ein separates Skript exportiert einen vollständigen Lebenslauf im `.xlsx`-Format inklusive **Profilfoto**, **Unterschrift** und strukturierter Darstellung aller Daten.

### Verwendete Datenquellen

- Bewerberdaten
- Arbeitgeber und Tätigkeiten
- Ausbildungsstationen und Schwerpunkte
- Kenntnisse & Interessen

### Excel-Struktur

1. Titel: *Lebenslauf*
2. Persönliche Daten + Foto
3. Berufserfahrung + Tätigkeiten
4. Ausbildung + Schwerpunkte
5. Kenntnisse + Einstufungen
6. Interessen
7. Ort, Datum, Unterschrift (optional)

**Export starten:**

```bash
python lebenslauf_erstellen.py
```

> Die Datei wird als `Lebenslauf_Bewerbung_<ID>_<Datum>.xlsx` gespeichert.

---

## ⚙️ Voraussetzungen

- Python 3.x
- Module: `tkinter`, `sqlite3`, `csv`, `openpyxl`

**Installation (sofern nötig):**

```bash
pip install openpyxl
```

---

## 🛠 Zukünftige Erweiterungen

- Datumvalidierung
- Such- und Sortierfunktionen
- PDF-Export
- Benutzerverwaltung

---



