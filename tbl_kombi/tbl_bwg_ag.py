import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect("/absoluter/pfad/zu/lebenslauf.db")
cursor = conn.cursor()

# Hauptfenster
root = tk.Tk()
root.title("Bewerbung <-> Arbeitgeber verknüpfen")
root.geometry("950x550")

# GUI-Elemente
tk.Label(root, text="Bewerbung:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Arbeitgeber (Mehrfachauswahl):").grid(row=1, column=0, padx=10, pady=5, sticky="ne")

combo_bewerbung = ttk.Combobox(root, state="readonly", width=60)
combo_bewerbung.grid(row=0, column=1, padx=10, pady=5)

listbox_ag = tk.Listbox(root, selectmode=tk.MULTIPLE, width=60, height=8)
listbox_ag.grid(row=1, column=1, padx=10, pady=5)

bewerbung_map = {}
arbeitgeber_map = {}

# Combobox und Listbox befüllen
def refresh_comboboxes():
    global bewerbung_map, arbeitgeber_map
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

    # Arbeitgeber laden
    cursor.execute("""
        SELECT ag_id, ag_name, ag_datum_von FROM tbl_arbeitgeber
        ORDER BY ag_datum_von DESC
    """)
    arbeitgeber = cursor.fetchall()
    arbeitgeber_map.clear()
    listbox_ag.delete(0, tk.END)

    for ag_id, ag_name, ag_datum_von in arbeitgeber:
        display_text = f"{ag_name} ({ag_datum_von})"
        arbeitgeber_map[display_text] = ag_id
        listbox_ag.insert(tk.END, display_text)

# TreeView zur Anzeige vorhandener Verknüpfungen
tree = ttk.Treeview(root, columns=("Bewerbung", "Arbeitgeber"), show="headings")
tree.heading("Bewerbung", text="Bewerbung")
tree.heading("Arbeitgeber", text="Arbeitgeber")
tree.column("Bewerbung", width=400)
tree.column("Arbeitgeber", width=400)
tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# TreeView Daten aktualisieren
def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT ba.bwg_ag_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name,
               ag.ag_name || ' (' || ag.ag_datum_von || ')'
        FROM tbl_bwg_ag ba
        JOIN tbl_bewerbung b ON ba.bwg_ag_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_arbeitgeber ag ON ba.bwg_ag_ag_id = ag.ag_id
        ORDER BY be.bw_nachname, ag.ag_datum_von DESC
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1], row[2]))

# Verknüpfung hinzufügen
def add_ag_record():
    b_text = combo_bewerbung.get()
    selected_indices = listbox_ag.curselection()

    if not b_text or not selected_indices:
        messagebox.showwarning("Fehler", "Bitte Bewerbung und mindestens einen Arbeitgeber auswählen.")
        return

    bwg_id = bewerbung_map[b_text]
    selected_ag_ids = [arbeitgeber_map[listbox_ag.get(i)] for i in selected_indices]

    for ag_id in selected_ag_ids:
        cursor.execute("""
            INSERT INTO tbl_bwg_ag (bwg_ag_ag_id, bwg_ag_bwg_id) VALUES (?, ?)
        """, (ag_id, bwg_id))

    conn.commit()
    reload_data()

# Verknüpfung löschen
def delete_ag_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Fehler", "Bitte einen Eintrag auswählen.")
        return
    bwg_ag_id = selected[0]
    if messagebox.askyesno("Löschen", "Diesen Eintrag wirklich löschen?"):
        cursor.execute("DELETE FROM tbl_bwg_ag WHERE bwg_ag_id = ?", (bwg_ag_id,))
        conn.commit()
        reload_data()

# Buttons
tk.Button(root, text="Zuordnung hinzufügen", command=add_ag_record).grid(row=2, column=0, padx=10, pady=10, sticky="w")
tk.Button(root, text="Ausgewählte Zuordnung löschen", command=delete_ag_record).grid(row=2, column=1, padx=10, pady=10, sticky="e")

# Startinitialisierung
refresh_comboboxes()
reload_data()

root.mainloop()
