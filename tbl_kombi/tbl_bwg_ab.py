import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect("/absoluter/pfad/zu/lebenslauf.db")
cursor = conn.cursor()

# Hauptfenster
root = tk.Tk()
root.title("Bewerbung <-> Ausbildung verknüpfen")
root.geometry("950x550")

# GUI-Elemente
tk.Label(root, text="Bewerbung:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Ausbildung (Mehrfachauswahl):").grid(row=1, column=0, padx=10, pady=5, sticky="ne")

combo_bewerbung = ttk.Combobox(root, state="readonly", width=60)
combo_bewerbung.grid(row=0, column=1, padx=10, pady=5)

listbox_ab = tk.Listbox(root, selectmode=tk.MULTIPLE, width=60, height=8)
listbox_ab.grid(row=1, column=1, padx=10, pady=5)

bewerbung_map = {}
ausbildung_map = {}

# Combobox und Listbox befüllen
def refresh_comboboxes():
    global bewerbung_map, ausbildung_map
    # Bewerbungen laden
    cursor.execute("""
        SELECT b.bwg_id, be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name
        FROM tbl_bewerbung b
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
    """)
    bewerbungen = cursor.fetchall()
    bewerbung_map = {text: bwg_id for bwg_id, text in bewerbungen}
    combo_bewerbung["values"] = list(bewerbung_map.keys())

    # Ausbildungen laden
    cursor.execute("""
        SELECT ab_id, ab_name_staette, ab_name_ausbildung, ab_datum_von, ab_datum_bis
        FROM tbl_ausbildung
        ORDER BY ab_datum_von DESC
    """)
    ausbildungen = cursor.fetchall()
    ausbildung_map.clear()
    listbox_ab.delete(0, tk.END)

    for ab_id, staette, ausbildung, von, bis in ausbildungen:
        display_text = f"{staette} – {ausbildung} ({von} bis {bis or 'heute'})"
        ausbildung_map[display_text] = ab_id
        listbox_ab.insert(tk.END, display_text)

# TreeView zur Anzeige vorhandener Verknüpfungen
tree = ttk.Treeview(root, columns=("Bewerbung", "Ausbildung"), show="headings")
tree.heading("Bewerbung", text="Bewerbung")
tree.heading("Ausbildung", text="Ausbildung")
tree.column("Bewerbung", width=400)
tree.column("Ausbildung", width=400)
tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT ba.bwg_ab_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name,
               ab.ab_name_staette || ' – ' || ab.ab_name_ausbildung || ' (' || ab.ab_datum_von || ' bis ' || IFNULL(ab.ab_datum_bis, 'heute') || ')'
        FROM tbl_bwg_ab ba
        JOIN tbl_bewerbung b ON ba.bwg_ab_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_ausbildung ab ON ba.bwg_ab_ab_id = ab.ab_id
        ORDER BY be.bw_nachname, ab.ab_datum_von DESC
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1], row[2]))

# Verknüpfung hinzufügen
def add_ab_record():
    b_text = combo_bewerbung.get()
    selected_indices = listbox_ab.curselection()

    if not b_text or not selected_indices:
        messagebox.showwarning("Fehler", "Bitte Bewerbung und mindestens eine Ausbildung auswählen.")
        return

    bwg_id = bewerbung_map[b_text]
    selected_ab_ids = [ausbildung_map[listbox_ab.get(i)] for i in selected_indices]

    for ab_id in selected_ab_ids:
        cursor.execute("INSERT INTO tbl_bwg_ab (bwg_ab_bwg_id, bwg_ab_ab_id) VALUES (?, ?)", (bwg_id, ab_id))

    conn.commit()
    reload_data()

# Verknüpfung löschen
def delete_ab_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Fehler", "Bitte einen Eintrag auswählen.")
        return
    bwg_ab_id = selected[0]
    if messagebox.askyesno("Löschen", "Diesen Eintrag wirklich löschen?"):
        cursor.execute("DELETE FROM tbl_bwg_ab WHERE bwg_ab_id = ?", (bwg_ab_id,))
        conn.commit()
        reload_data()

# Buttons
tk.Button(root, text="Zuordnung hinzufügen", command=add_ab_record).grid(row=2, column=0, padx=10, pady=10, sticky="w")
tk.Button(root, text="Ausgewählte Zuordnung löschen", command=delete_ab_record).grid(row=2, column=1, padx=10, pady=10, sticky="e")

# Startinitialisierung
refresh_comboboxes()
reload_data()

root.mainloop()
