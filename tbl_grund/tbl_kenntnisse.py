import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect("/home/birgit/PycharmProjects/LebenslaufTest/src/lb_datenbank/lebenslauf.db")
cursor = conn.cursor()

# Tabelle erstellen, falls nicht vorhanden
cursor.execute("""
CREATE TABLE IF NOT EXISTS tbl_kenntnisse (
    k_id INTEGER PRIMARY KEY AUTOINCREMENT,
    k_name TEXT NOT NULL,
    k_stufe TEXT NOT NULL
)
""")
conn.commit()

# Tkinter-Fenster
root = tk.Tk()
root.title("Kenntnisse verwalten")
root.geometry("800x400")

# Label + Eingabefelder
tk.Label(root, text="Kenntnis:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_name = tk.Entry(root, width=30)
entry_name.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Stufe:").grid(row=0, column=2, padx=10, pady=5, sticky="e")
entry_level = tk.Entry(root, width=30)
entry_level.grid(row=0, column=3, padx=10, pady=5)

# Treeview für Übersicht
tree = ttk.Treeview(root, columns=("Kenntnis", "Stufe"), show="headings")
tree.heading("Kenntnis", text="Kenntnis")
tree.heading("Stufe", text="Stufe")
tree.column("Kenntnis", width=300)
tree.column("Stufe", width=200)
tree.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

# Funktionen
def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM tbl_kenntnisse")
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1], row[2]))

def add_record():
    name = entry_name.get().strip()
    level = entry_level.get().strip()
    if not name or not level:
        messagebox.showwarning("Eingabefehler", "Bitte sowohl Kenntnis als auch Stufe eingeben.")
        return
    cursor.execute("INSERT INTO tbl_kenntnisse (k_name, k_stufe) VALUES (?, ?)", (name, level))
    conn.commit()
    reload_data()
    entry_name.delete(0, tk.END)
    entry_level.delete(0, tk.END)

def update_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Auswahl fehlt", "Bitte einen Eintrag auswählen.")
        return
    k_id = selected[0]
    name = entry_name.get().strip()
    level = entry_level.get().strip()
    if not name or not level:
        messagebox.showwarning("Eingabefehler", "Bitte sowohl Kenntnis als auch Stufe eingeben.")
        return
    cursor.execute("UPDATE tbl_kenntnisse SET k_name = ?, k_stufe = ? WHERE k_id = ?", (name, level, k_id))
    conn.commit()
    reload_data()
    entry_name.delete(0, tk.END)
    entry_level.delete(0, tk.END)

def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Auswahl fehlt", "Bitte einen Eintrag auswählen.")
        return
    k_id = selected[0]
    if messagebox.askyesno("Löschen", "Kenntnis wirklich löschen?"):
        cursor.execute("DELETE FROM tbl_kenntnisse WHERE k_id = ?", (k_id,))
        conn.commit()
        reload_data()
        entry_name.delete(0, tk.END)
        entry_level.delete(0, tk.END)

def on_select(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])["values"]
        entry_name.delete(0, tk.END)
        entry_name.insert(0, values[0])
        entry_level.delete(0, tk.END)
        entry_level.insert(0, values[1])

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
        if headers != ["Kenntnis", "Stufe"]:
            messagebox.showerror("Fehler", "CSV-Datei muss die Spalten 'Kenntnis' und 'Stufe' enthalten.")
            return

        rows_imported = 0
        for row in reader:
            if len(row) == 2:
                name = row[0].strip()
                level = row[1].strip()
                if name and level:
                    cursor.execute("INSERT INTO tbl_kenntnisse (k_name, k_stufe) VALUES (?, ?)", (name, level))
                    rows_imported += 1

        conn.commit()
        reload_data()
        messagebox.showinfo("Import abgeschlossen", f"{rows_imported} Kenntnisse importiert.")

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
