import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect("/absoluter/pfad/zu/lebenslauf.db")
cursor = conn.cursor()

# Tabelle erstellen (nur zur Sicherheit, falls sie noch nicht existiert)
cursor.execute("""
CREATE TABLE IF NOT EXISTS tbl_firma (
    f_id INTEGER PRIMARY KEY AUTOINCREMENT,
    f_datum DATE NOT NULL,
    f_stellenbezeichnung TEXT NOT NULL,
    f_name TEXT NOT NULL,
    f_strasse TEXT,
    f_plz INTEGER,
    f_ort TEXT,
    f_mail TEXT,
    f_telefon TEXT
)
""")
conn.commit()

# Tkinter GUI
root = tk.Tk()
root.title("Firmenverwaltung")
root.geometry("1500x500")

# Eingabefelder
labels = [
    "Datum", "Stellenbezeichnung", "Firmenname", "Straße", "PLZ",
    "Ort", "E-Mail", "Telefon"
]
entries = {}

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
    entry = tk.Entry(root, width=30)
    entry.grid(row=i, column=1, pady=2)
    entries[label] = entry

# Treeview für Anzeige
tree = ttk.Treeview(root, columns=labels, show="headings")
for label in labels:
    tree.heading(label, text=label)
    tree.column(label, width=140)
tree.grid(row=0, column=3, rowspan=15, padx=10, pady=10)

def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM tbl_firma")
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=row[1:])

def add_record():
    data = [entries[label].get() for label in labels]
    if not data[0] or not data[1] or not data[2]:
        messagebox.showwarning("Pflichtfelder", "Datum, Stellenbezeichnung und Firmenname sind erforderlich.")
        return
    cursor.execute("""
        INSERT INTO tbl_firma 
        (f_datum, f_stellenbezeichnung, f_name, f_strasse, f_plz, f_ort, f_mail, f_telefon)
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
    f_id = selected[0]
    data = [entries[label].get() for label in labels]
    cursor.execute("""
        UPDATE tbl_firma SET
        f_datum = ?, f_stellenbezeichnung = ?, f_name = ?, f_strasse = ?,
        f_plz = ?, f_ort = ?, f_mail = ?, f_telefon = ?
        WHERE f_id = ?
    """, data + [f_id])
    conn.commit()
    reload_data()
    clear_fields()

def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte einen Datensatz auswählen.")
        return
    f_id = selected[0]
    if messagebox.askyesno("Löschen", "Datensatz wirklich löschen?"):
        cursor.execute("DELETE FROM tbl_firma WHERE f_id = ?", (f_id,))
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
    filepath = filedialog.askopenfilename(
        title="CSV-Datei auswählen",
        filetypes=[("CSV-Dateien", "*.csv")]
    )
    if not filepath:
        return

    with open(filepath, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)

        expected_headers = labels

        if headers != expected_headers:
            messagebox.showerror("Falsche CSV-Datei", f"Die CSV-Datei hat nicht das erwartete Format:\n{expected_headers}")
            return

        rows_imported = 0
        for row in reader:
            row = [field.strip() for field in row]
            if len(row) == len(expected_headers):
                cursor.execute("""
                    INSERT INTO tbl_firma 
                    (f_datum, f_stellenbezeichnung, f_name, f_strasse, f_plz, f_ort, f_mail, f_telefon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, row)
                rows_imported += 1

        conn.commit()
        if rows_imported > 0:
            messagebox.showinfo("Import erfolgreich", f"{rows_imported} Datensätze importiert.")
        else:
            messagebox.showwarning("Keine Daten importiert", "Keine gültigen Zeilen gefunden.")

        reload_data()

# Buttons
tk.Button(root, text="Hinzufügen", command=add_record).grid(row=8, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Aktualisieren", command=update_record).grid(row=9, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Löschen", command=delete_record).grid(row=10, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Felder leeren", command=clear_fields).grid(row=11, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="CSV importieren", command=import_from_csv).grid(row=12, column=0, pady=5, padx=10, sticky="w")

tree.bind("<<TreeviewSelect>>", on_select)

reload_data()
root.mainloop()
