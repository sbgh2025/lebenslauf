import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect("/absoluter/pfad/zu/lebenslauf.db")
cursor = conn.cursor()

# Tabelle erstellen, falls nicht vorhanden
cursor.execute("""
CREATE TABLE IF NOT EXISTS tbl_interessen (
    i_id INTEGER PRIMARY KEY AUTOINCREMENT,
    i_name TEXT NOT NULL
)
""")
conn.commit()

# Tkinter-Fenster
root = tk.Tk()
root.title("Interessen verwalten")
root.geometry("700x500")

# Label + Eingabefeld
tk.Label(root, text="Interesse:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_name = tk.Entry(root, width=40)
entry_name.grid(row=0, column=1, padx=10, pady=5)

# Treeview für Übersicht
tree = ttk.Treeview(root, columns=("Interesse",), show="headings")
tree.heading("Interesse", text="Interesse")
tree.column("Interesse", width=500)
tree.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Funktionen
def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM tbl_interessen")
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1],))

def add_record():
    name = entry_name.get().strip()
    if not name:
        messagebox.showwarning("Eingabefehler", "Bitte eine Interesse eingeben.")
        return
    cursor.execute("INSERT INTO tbl_interessen (i_name) VALUES (?)", (name,))
    conn.commit()
    reload_data()
    entry_name.delete(0, tk.END)

def update_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Auswahl fehlt", "Bitte eine Interesse auswählen.")
        return
    i_id = selected[0]
    name = entry_name.get().strip()
    if not name:
        messagebox.showwarning("Eingabefehler", "Bitte eine Interesse eingeben.")
        return
    cursor.execute("UPDATE tbl_interessen SET i_name = ? WHERE i_id = ?", (name, i_id))
    conn.commit()
    reload_data()
    entry_name.delete(0, tk.END)

def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Auswahl fehlt", "Bitte eine Interesse auswählen.")
        return
    i_id = selected[0]
    if messagebox.askyesno("Löschen", "Interesse wirklich löschen?"):
        cursor.execute("DELETE FROM tbl_interessen WHERE i_id = ?", (i_id,))
        conn.commit()
        reload_data()
        entry_name.delete(0, tk.END)

def on_select(event):
    selected = tree.selection()
    if selected:
        name = tree.item(selected[0])["values"][0]
        entry_name.delete(0, tk.END)
        entry_name.insert(0, name)

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
        if headers != ["Interesse"]:
            messagebox.showerror("Fehler", "CSV-Datei muss genau eine Spalte namens 'Interesse' enthalten.")
            return

        rows_imported = 0
        for row in reader:
            if row:
                name = row[0].strip()
                if name:
                    cursor.execute("INSERT INTO tbl_interessen (i_name) VALUES (?)", (name,))
                    rows_imported += 1

        conn.commit()
        reload_data()
        messagebox.showinfo("Import abgeschlossen", f"{rows_imported} Interessen importiert.")

# Buttons
tk.Button(root, text="Hinzufügen", command=add_record).grid(row=2, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Aktualisieren", command=update_record).grid(row=3, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Löschen", command=delete_record).grid(row=4, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="CSV importieren", command=import_from_csv).grid(row=5, column=0, pady=10, padx=10, sticky="w")

# Auswahlbindung
tree.bind("<<TreeviewSelect>>", on_select)

# Initiales Laden
reload_data()
root.mainloop()
