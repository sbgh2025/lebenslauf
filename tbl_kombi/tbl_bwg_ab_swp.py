import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Verbindung zur Datenbank
conn = sqlite3.connect("/absoluter/pfad/zu/lebenslauf.db")
cursor = conn.cursor()

root = tk.Tk()
root.title("Bewerbung/Arbeitgeber <-> Ausbildung/Schwerpunkt")
root.geometry("1000x600")

# Label
tk.Label(root, text="Bewerbung/Arbeitgeber-Zuordnung:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Schwerpunkte (bis zu 3 auswählen):").grid(row=1, column=0, padx=10, pady=5, sticky="ne")

# Combobox für Bewerbung/Arbeitgeber-Zuordnung
combo_bwg_ab = ttk.Combobox(root, state="readonly", width=70)
combo_bwg_ab.grid(row=0, column=1, padx=10, pady=5)

# Listbox für Schwerpunkte (Mehrfachauswahl)
listbox_schwerpunkte = tk.Listbox(root, selectmode=tk.MULTIPLE, width=70, height=8)
listbox_schwerpunkte.grid(row=1, column=1, padx=10, pady=5)

bwg_ab_map = {}
schwerpunkt_map = {}

def refresh_data():
    global bwg_ab_map, schwerpunkt_map
    # Bewerbung/Arbeitgeber-Zuordnungen
    cursor.execute("""
        SELECT ba.bwg_ab_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name || ' (' || ab.ab_name_staette || ' – ' || ab.ab_name_ausbildung || ')'
        FROM tbl_bwg_ab ba
        JOIN tbl_bewerbung b ON ba.bwg_ab_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_ausbildung ab ON ba.bwg_ab_ab_id = ab.ab_id
        ORDER BY be.bw_nachname
    """)
    results = cursor.fetchall()
    bwg_ab_map = {text: bwg_ab_id for bwg_ab_id, text in results}
    combo_bwg_ab["values"] = list(bwg_ab_map.keys())

    # Schwerpunkte
    cursor.execute("SELECT ab_swp_id, ab_swp_name FROM tbl_ab_schwerpunkt ORDER BY ab_swp_name")
    results = cursor.fetchall()
    schwerpunkt_map = {}
    listbox_schwerpunkte.delete(0, tk.END)
    for ab_swp_id, ab_swp_name in results:
        schwerpunkt_map[ab_swp_name] = ab_swp_id
        listbox_schwerpunkte.insert(tk.END, ab_swp_name)

# TreeView
tree = ttk.Treeview(root, columns=("Zuordnung", "Schwerpunkt"), show="headings")
tree.heading("Zuordnung", text="Bewerbung/Arbeitgeber")
tree.heading("Schwerpunkt", text="Schwerpunkt")
tree.column("Zuordnung", width=450)
tree.column("Schwerpunkt", width=450)
tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

def reload_tree():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT bas.bwg_ab_swp_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name || ' (' || ab.ab_name_staette || ' – ' || ab.ab_name_ausbildung || ')',
               swp.ab_swp_name
        FROM tbl_bwg_ab_swp bas
        JOIN tbl_bwg_ab ba ON bas.bwg_ab_swp_bwg_ab_id = ba.bwg_ab_id  -- Hier den richtigen Spaltennamen verwenden
        JOIN tbl_bewerbung b ON ba.bwg_ab_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_ausbildung ab ON ba.bwg_ab_ab_id = ab.ab_id
        JOIN tbl_ab_schwerpunkt swp ON bas.bwg_ab_swp_ab_swp_id = swp.ab_swp_id
        ORDER BY be.bw_nachname
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1], row[2]))

def add_schwerpunkt():
    selected_bwg_ab = combo_bwg_ab.get()
    selected_indices = listbox_schwerpunkte.curselection()

    if not selected_bwg_ab or not selected_indices:
        messagebox.showwarning("Fehler", "Bitte eine Zuordnung und bis zu 3 Schwerpunkte auswählen.")
        return

    if len(selected_indices) > 3:
        messagebox.showwarning("Fehler", "Es dürfen maximal 3 Schwerpunkte ausgewählt werden.")
        return

    bwg_ab_id = bwg_ab_map[selected_bwg_ab]
    selected_swp_ids = [schwerpunkt_map[listbox_schwerpunkte.get(i)] for i in selected_indices]

    for swp_id in selected_swp_ids:
        cursor.execute("INSERT INTO tbl_bwg_ab_swp (bwg_ab_swp_bwg_ab_id, bwg_ab_swp_ab_swp_id) VALUES (?, ?)", (bwg_ab_id, swp_id))

    conn.commit()
    reload_tree()

def delete_entry():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Fehler", "Bitte einen Schwerpunkt auswählen.")
        return
    bwg_ab_swp_id = selected[0]
    if messagebox.askyesno("Löschen", "Eintrag wirklich löschen?"):
        cursor.execute("DELETE FROM tbl_bwg_ab_swp WHERE bwg_ab_swp_id = ?", (bwg_ab_swp_id,))
        conn.commit()
        reload_tree()

# Buttons
tk.Button(root, text="Schwerpunkte zuordnen", command=add_schwerpunkt).grid(row=2, column=0, padx=10, pady=10, sticky="w")
tk.Button(root, text="Ausgewählten Schwerpunkt löschen", command=delete_entry).grid(row=2, column=1, padx=10, pady=10, sticky="e")

# Initial
refresh_data()
reload_tree()

root.mainloop()
