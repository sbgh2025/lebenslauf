import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect("/absoluter/pfad/zu/lebenslauf.db")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# Tabelle zur Sicherheit erstellen
cursor.execute("""
CREATE TABLE IF NOT EXISTS tbl_bewerbung (
    bwg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bwg_bw_id INTEGER NOT NULL,
    bwg_f_id INTEGER NOT NULL,
    FOREIGN KEY (bwg_bw_id) REFERENCES tbl_bewerber(bw_id),
    FOREIGN KEY (bwg_f_id) REFERENCES tbl_firma(f_id)
)
""")
conn.commit()

# Fenster
root = tk.Tk()
root.title("Bewerbungen verwalten")
root.geometry("950x500")

# Labels und Comboboxen
tk.Label(root, text="Bewerber:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Firma:").grid(row=1, column=0, padx=10, pady=5, sticky="e")

combo_bewerber = ttk.Combobox(root, state="readonly", width=60)
combo_firma = ttk.Combobox(root, state="readonly", width=60)

combo_bewerber.grid(row=0, column=1, padx=10, pady=5)
combo_firma.grid(row=1, column=1, padx=10, pady=5)

bewerber_map = {}
firma_map = {}

def refresh_comboboxes():
    global bewerber_map, firma_map
    cursor.execute("SELECT bw_id, bw_vorname || ' ' || bw_nachname FROM tbl_bewerber")
    bewerber = cursor.fetchall()
    cursor.execute("SELECT f_id, f_stellenbezeichnung || ' bei ' || f_name || ' (' || f_datum || ')' FROM tbl_firma")
    firmen = cursor.fetchall()

    bewerber_map = {text: bw_id for bw_id, text in bewerber}
    firma_map = {text: f_id for f_id, text in firmen}

    combo_bewerber["values"] = list(bewerber_map.keys())
    combo_firma["values"] = list(firma_map.keys())

# TreeView
tree = ttk.Treeview(root, columns=("Bewerber", "Firma"), show="headings")
tree.heading("Bewerber", text="Bewerber")
tree.heading("Firma", text="Firma")
tree.column("Bewerber", width=300)
tree.column("Firma", width=500)
tree.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT b.bwg_id, bw.bw_vorname || ' ' || bw.bw_nachname, 
               f.f_stellenbezeichnung || ' bei ' || f.f_name || ' (' || f.f_datum || ')'
        FROM tbl_bewerbung b
        JOIN tbl_bewerber bw ON b.bwg_bw_id = bw.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1], row[2]))

def add_record():
    b_text = combo_bewerber.get()
    f_text = combo_firma.get()
    if not b_text or not f_text:
        messagebox.showwarning("Fehler", "Bitte sowohl einen Bewerber als auch eine Firma auswählen.")
        return
    bw_id = bewerber_map[b_text]
    f_id = firma_map[f_text]
    cursor.execute("INSERT INTO tbl_bewerbung (bwg_bw_id, bwg_f_id) VALUES (?, ?)", (bw_id, f_id))
    conn.commit()
    reload_data()

def update_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Fehler", "Bitte eine Bewerbung auswählen.")
        return
    bwg_id = selected[0]
    b_text = combo_bewerber.get()
    f_text = combo_firma.get()
    if not b_text or not f_text:
        messagebox.showwarning("Fehler", "Bitte sowohl einen Bewerber als auch eine Firma auswählen.")
        return
    bw_id = bewerber_map[b_text]
    f_id = firma_map[f_text]
    cursor.execute("""
        UPDATE tbl_bewerbung SET bwg_bw_id = ?, bwg_f_id = ?
        WHERE bwg_id = ?
    """, (bw_id, f_id, bwg_id))
    conn.commit()
    reload_data()

def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Fehler", "Bitte eine Bewerbung auswählen.")
        return
    bwg_id = selected[0]
    if messagebox.askyesno("Löschen", "Bewerbung wirklich löschen?"):
        cursor.execute("DELETE FROM tbl_bewerbung WHERE bwg_id = ?", (bwg_id,))
        conn.commit()
        reload_data()

def on_select(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])["values"]
        combo_bewerber.set(values[0])
        combo_firma.set(values[1])

# Buttons
tk.Button(root, text="Hinzufügen", command=add_record).grid(row=5, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Aktualisieren", command=update_record).grid(row=6, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Löschen", command=delete_record).grid(row=7, column=0, pady=5, padx=10, sticky="w")

tree.bind("<<TreeviewSelect>>", on_select)

# Initiales Laden
refresh_comboboxes()
reload_data()
root.mainloop()
