import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect("/absoluter/pfad/zu/lebenslauf.db")
cursor = conn.cursor()

# Tabelle erstellen (falls noch nicht vorhanden)
cursor.execute("""
CREATE TABLE IF NOT EXISTS tbl_ausbildung (
    ab_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ab_datum_von DATE NOT NULL,
    ab_datum_bis DATE,
    ab_name_staette TEXT NOT NULL,
    ab_name_ausbildung TEXT NOT NULL,
    ab_abschluss TEXT,
    ab_zeit TEXT
);
""")
conn.commit()

# GUI-Fenster
root = tk.Tk()
root.title("Ausbildung verwalten")
root.geometry("1200x500")

# Eingabefelder
labels = [
    "Datum von", "Datum bis", "Ausbildungsstätte", "Ausbildung",
    "Abschluss", "Zeitraum"
]
entries = {}

# Eingabefelder und Labels linksbündig anordnen
for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=5, pady=2, sticky="w")
    entries[label] = entry

# Treeview zur Anzeige der Datensätze
tree = ttk.Treeview(root, columns=labels, show="headings")
for label in labels:
    tree.heading(label, text=label)
    tree.column(label, width=150)
tree.grid(row=0, column=2, rowspan=10, padx=10, pady=10)

def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM tbl_ausbildung")
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=row[1:])

def add_record():
    data = [entries[label].get().strip() for label in labels]
    if not data[0] or not data[2] or not data[3]:
        messagebox.showwarning("Pflichtfelder", "Datum von, Ausbildungsstätte und Ausbildung sind erforderlich.")
        return
    cursor.execute("""
        INSERT INTO tbl_ausbildung 
        (ab_datum_von, ab_datum_bis, ab_name_staette, ab_name_ausbildung, ab_abschluss, ab_zeit)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    reload_data()
    clear_fields()

def update_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte einen Datensatz auswählen.")
        return
    ab_id = selected[0]
    data = [entries[label].get().strip() for label in labels]
    cursor.execute("""
        UPDATE tbl_ausbildung SET
        ab_datum_von = ?, ab_datum_bis = ?, ab_name_staette = ?, 
        ab_name_ausbildung = ?, ab_abschluss = ?, ab_zeit = ?
        WHERE ab_id = ?
    """, data + [ab_id])
    conn.commit()
    reload_data()
    clear_fields()

def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte einen Datensatz auswählen.")
        return
    ab_id = selected[0]
    if messagebox.askyesno("Löschen", "Datensatz wirklich löschen?"):
        cursor.execute("DELETE FROM tbl_ausbildung WHERE ab_id = ?", (ab_id,))
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
            messagebox.showerror("Fehler", f"CSV-Datei muss diese Spalten enthalten:\n{expected_headers}")
            return

        rows_imported = 0
        for row in reader:
            row = [field.strip() for field in row]
            if len(row) == len(expected_headers):
                cursor.execute("""
                    INSERT INTO tbl_ausbildung 
                    (ab_datum_von, ab_datum_bis, ab_name_staette, ab_name_ausbildung, ab_abschluss, ab_zeit)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, row)
                rows_imported += 1

        conn.commit()
        reload_data()
        messagebox.showinfo("Import abgeschlossen", f"{rows_imported} Datensätze importiert.")

# Buttons links unter den Eingabefeldern
tk.Button(root, text="Hinzufügen", command=add_record).grid(row=6, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Aktualisieren", command=update_record).grid(row=7, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Löschen", command=delete_record).grid(row=8, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Felder leeren", command=clear_fields).grid(row=9, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="CSV importieren", command=import_from_csv).grid(row=10, column=0, pady=10, padx=10, sticky="w")

# Treeview-Auswahlbindung
tree.bind("<<TreeviewSelect>>", on_select)

# Initiales Laden der Daten
reload_data()
root.mainloop()
