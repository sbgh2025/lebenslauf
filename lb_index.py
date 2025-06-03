import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def run_script(script_path):
    try:
        subprocess.run(["python3", script_path], check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Fehler", f"Skript konnte nicht ausgeführt werden:\n{script_path}")
    except FileNotFoundError:
        messagebox.showerror("Fehler", f"Skript wurde nicht gefunden:\n{script_path}")

class IndexApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lebenslauf-Datenbank System")
        self.geometry("850x700")
        self.configure(padx=20, pady=20)

        # Hauptüberschrift
        tk.Label(self, text="Bitte wählen Sie eine Kategorie:", font=("Arial", 16, "bold")).pack(pady=10)

        # Container für Hauptbereiche
        self.sections = {}

        # Hauptbuttons
        self.create_main_button("🗄️ Datenbank", [
            ("Datenbank erstellen", "/absoluter/pfad/zu/lb_datenbank.py"),
            ("Datenbankinhalt anzeigen", "/absoluter/pfad/zu/lb_db_inhalt.py"),
        ])

        self.create_main_button("📋 Grundtabellen befüllen", [
            ("Bewerber", "/absoluter/pfad/zu/tbl_bewerber.py"),
            ("Firma", "/absoluter/pfad/zu/tbl_firma.py"),
            ("Arbeitgeber", "/absoluter/pfad/zu/tbl_arbeitgeber.py"),
            ("Tätigkeit", "/absoluter/pfad/zu/tbl_taetigkeit.py"),
            ("Ausbildung", "/absoluter/pfad/zu/tbl_ausbildung.py"),
            ("Schwerpunkte", "/absoluter/pfad/zu/tbl_ab_schwerpunkt.py"),
            ("Kenntnisse", "/absoluter/pfad/zu/tbl_kenntnisse.py"),
            ("Interessen", "/absoluter/pfad/zu/tbl_interessen.py"),
        ])

        self.create_main_button("🔗 Kombitabellen (Verknüpfungen)", [
            ("Bewerbung", "/absoluter/pfad/zu/tbl_bewerbung.py"),
            ("Bewerber ↔ Arbeitgeber", "/absoluter/pfad/zu/tbl_bwg_ag.py"),
            ("Bewerber ↔ Arbeitgeber ↔ Tätigkeit", "/absoluter/pfad/zu/tbl_bwg_ag_t.py"),
            ("Bewerber ↔ Ausbildung", "/absoluter/pfad/zu/tbl_bwg_ab.py"),
            ("Bewerber ↔ Ausbildung ↔ Schwerpunkt", "/absoluter/pfad/zu/tbl_bwg_ab_swp.py"),
            ("Bewerber ↔ Kenntnisse", "/absoluter/pfad/zu/tbl_bwg_k.py"),
            ("Bewerber ↔ Interessen", "/absoluter/pfad/zu/tbl_bwg_i.py"),
        ])

    def create_main_button(self, title, buttons):
        # Hauptbutton
        main_button = tk.Button(
            self,
            text=title,
            font=("Arial", 13, "bold"),
            bg="lightgray",
            relief=tk.RAISED,
            command=lambda: self.toggle_section(title)
        )
        main_button.pack(fill=tk.X, pady=5)

        # Versteckter Frame für Unterbuttons
        section_frame = tk.Frame(self)
        self.sections[title] = section_frame  # speichern zum Ein-/Ausblenden

        # Unterbuttons hinzufügen
        for label, path in buttons:
            tk.Button(
                section_frame,
                text=label,
                command=lambda p=path: run_script(p),
                bg="lightblue",
                font=("Arial", 11),
                anchor="w"
            ).pack(fill=tk.X, pady=2, padx=10)

    def toggle_section(self, title):
        # Aktuelle Sichtbarkeit toggeln
        frame = self.sections[title]
        if frame.winfo_ismapped():
            frame.pack_forget()
        else:
            # Alle anderen schließen
            for other_frame in self.sections.values():
                other_frame.pack_forget()
            frame.pack(fill=tk.X, padx=10, pady=5)

if __name__ == "__main__":
    app = IndexApp()
    app.mainloop()
