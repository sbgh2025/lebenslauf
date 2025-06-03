import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import csv
from tkinter import filedialog


# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect("/home/birgit/PycharmProjects/LebenslaufTest/src/lb_datenbank/lebenslauf.db")


cursor = conn.cursor()

# Tabelle erstellen (falls noch nicht vorhanden)
cursor.execute("""
CREATE TABLE IF NOT EXISTS tbl_bewerber (
    bw_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bw_vorname TEXT NOT NULL,
    bw_nachname TEXT NOT NULL,
    bw_geburtsdatum DATE,
    bw_strasse TEXT,
    bw_plz INTEGER,
    bw_ort TEXT,
    bw_mail TEXT,
    bw_telefon TEXT
)
""")
conn.commit()

# Tkinter Fenster
root = tk.Tk()
root.title("Bewerberverwaltung")
root.geometry("1500x500")

# Eingabefelder
labels = [
    "Vorname", "Nachname", "Geburtsdatum", "Straße", "PLZ",
    "Ort", "E-Mail", "Telefon"
]
entries = {}

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky="e")
    entry = tk.Entry(root, width=30)
    entry.grid(row=i, column=1)
    entries[label] = entry

# Treeview für die Anzeige
tree = ttk.Treeview(root, columns=labels, show="headings")
for label in labels:
    tree.heading(label, text=label)
    tree.column(label, width=100)
tree.grid(row=0, column=3, rowspan=10, padx=10)

def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM tbl_bewerber")
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=row[1:])

def add_record():
    data = [entries[label].get() for label in labels]
    if not data[0] or not data[1]:
        messagebox.showwarning("Pflichtfelder", "Vor- und Nachname sind erforderlich.")
        return
    cursor.execute("""
        INSERT INTO tbl_bewerber 
        (bw_vorname, bw_nachname, bw_geburtsdatum, bw_strasse, bw_plz, bw_ort, bw_mail, bw_telefon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    reload_data()
    clear_fields()

def update_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte einen Datensatz auswählen.")
        return
    bw_id = selected[0]
    data = [entries[label].get() for label in labels]
    cursor.execute("""
        UPDATE tbl_bewerber SET
        bw_vorname = ?, bw_nachname = ?, bw_geburtsdatum = ?, bw_strasse = ?,
        bw_plz = ?, bw_ort = ?, bw_mail = ?, bw_telefon = ?
        WHERE bw_id = ?
    """, data + [bw_id])
    conn.commit()
    reload_data()
    clear_fields()

def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte einen Datensatz auswählen.")
        return
    bw_id = selected[0]
    if messagebox.askyesno("Löschen", "Datensatz wirklich löschen?"):
        cursor.execute("DELETE FROM tbl_bewerber WHERE bw_id = ?", (bw_id,))
        conn.commit()
        reload_data()
        clear_fields()

def on_select(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])["values"]
        for i, label in enumerate(labels):
            entries[label].delete(0, tk.END)
            entries[label].insert(0, values[i])

def clear_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)


def import_from_csv():
    # Wählen der CSV-Datei
    filepath = filedialog.askopenfilename(
        title="CSV-Datei auswählen",
        filetypes=[("CSV-Dateien", "*.csv")]
    )

    if not filepath:
        return  # Abgebrochen

    # Öffnen und Lesen der CSV-Datei
    with open(filepath, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)  # Erste Zeile als Header (überspringen)

        # Überprüfen, ob die CSV die richtigen Spalten hat
        expected_headers = [
            "Vorname", "Nachname", "Geburtsdatum", "Straße",
            "PLZ", "Ort", "E-Mail", "Telefon"
        ]

        if headers != expected_headers:
            messagebox.showerror("Falsche CSV-Datei", "Die CSV-Datei hat nicht das erwartete Format.")
            return

        # Einfügen der Daten in die Tabelle
        rows_imported = 0
        for row in reader:
            # Entfernen von führenden und nachfolgenden Leerzeichen in den Feldern
            row = [field.strip() for field in row]

            # Überprüfen, ob die Zeile die richtige Anzahl von Feldern hat
            if len(row) == len(expected_headers):
                cursor.execute("""
                    INSERT INTO tbl_bewerber 
                    (bw_vorname, bw_nachname, bw_geburtsdatum, bw_strasse, bw_plz, bw_ort, bw_mail, bw_telefon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, row)
                rows_imported += 1
            else:
                # Zeile überspringen, aber keine Fehlermeldung
                continue

        conn.commit()
        if rows_imported > 0:
            messagebox.showinfo("Import erfolgreich",
                                f"Die Daten wurden erfolgreich aus der Datei {filepath} importiert.")
        else:
            messagebox.showwarning("Keine Daten importiert", "Es wurden keine gültigen Daten aus der Datei importiert.")

        reload_data()  # Daten nach dem Import neu laden


# Buttons
# Buttons
tk.Button(root, text="Hinzufügen", command=add_record).grid(row=8, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Aktualisieren", command=update_record).grid(row=9, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Löschen", command=delete_record).grid(row=10, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Felder leeren", command=clear_fields).grid(row=10, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="CSV importieren", command=import_from_csv).grid(row=11, column=0, pady=5, padx=10, sticky="w")

# Startdaten laden
reload_data()

root.mainloop()
