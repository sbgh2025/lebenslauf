import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect("/home/birgit/PycharmProjects/LebenslaufTest/src/lb_datenbank/lebenslauf.db")
cursor = conn.cursor()

# Hauptfenster
root = tk.Tk()
root.title("Bewerbung <-> Interessen verknüpfen")
root.geometry("950x550")

# GUI-Elemente
tk.Label(root, text="Bewerbung:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Interessen (Mehrfachauswahl):").grid(row=1, column=0, padx=10, pady=5, sticky="ne")

combo_bewerbung = ttk.Combobox(root, state="readonly", width=60)
combo_bewerbung.grid(row=0, column=1, padx=10, pady=5)

listbox_interessen = tk.Listbox(root, selectmode=tk.MULTIPLE, width=60, height=8)
listbox_interessen.grid(row=1, column=1, padx=10, pady=5)

bewerbung_map = {}
interessen_map = {}

# Combobox und Listbox befüllen
def refresh_comboboxes():
    global bewerbung_map, interessen_map
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

    # Interessen laden
    cursor.execute("""
        SELECT i_id, i_name
        FROM tbl_interessen
        ORDER BY i_name
    """)
    interessen = cursor.fetchall()
    interessen_map.clear()
    listbox_interessen.delete(0, tk.END)

    for i_id, i_name in interessen:
        interessen_map[i_name] = i_id
        listbox_interessen.insert(tk.END, i_name)

# TreeView zur Anzeige vorhandener Verknüpfungen
tree = ttk.Treeview(root, columns=("Bewerbung", "Interessen"), show="headings")
tree.heading("Bewerbung", text="Bewerbung")
tree.heading("Interessen", text="Interessen")
tree.column("Bewerbung", width=400)
tree.column("Interessen", width=400)
tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT bi.bwg_i_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name,
               GROUP_CONCAT(i.i_name, ', ')  -- mehrere Interessen anzeigen
        FROM tbl_bwg_i bi
        JOIN tbl_bewerbung b ON bi.bwg_i_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_interessen i ON bi.bwg_i_i_id = i.i_id
        GROUP BY bi.bwg_i_id
        ORDER BY be.bw_nachname
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1], row[2]))

# Verknüpfung hinzufügen
def add_i_record():
    b_text = combo_bewerbung.get()
    selected_indices = listbox_interessen.curselection()

    if not b_text or not selected_indices:
        messagebox.showwarning("Fehler", "Bitte Bewerbung und mindestens ein Interesse auswählen.")
        return

    bwg_id = bewerbung_map[b_text]
    selected_i_ids = [interessen_map[listbox_interessen.get(i)] for i in selected_indices]

    for i_id in selected_i_ids:
        cursor.execute("INSERT INTO tbl_bwg_i (bwg_i_bwg_id, bwg_i_i_id) VALUES (?, ?)", (bwg_id, i_id))

    conn.commit()
    reload_data()

# Verknüpfung löschen
def delete_i_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Fehler", "Bitte einen Eintrag auswählen.")
        return
    bwg_i_id = selected[0]
    if messagebox.askyesno("Löschen", "Diesen Eintrag wirklich löschen?"):
        cursor.execute("DELETE FROM tbl_bwg_i WHERE bwg_i_id = ?", (bwg_i_id,))
        conn.commit()
        reload_data()

# Buttons
tk.Button(root, text="Zuordnung hinzufügen", command=add_i_record).grid(row=2, column=0, padx=10, pady=10, sticky="w")
tk.Button(root, text="Ausgewählte Zuordnung löschen", command=delete_i_record).grid(row=2, column=1, padx=10, pady=10, sticky="e")

# Startinitialisierung
refresh_comboboxes()
reload_data()

root.mainloop()
