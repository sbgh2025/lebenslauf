import sqlite3

def fetch_all(cursor, table):
    cursor.execute(f"SELECT * FROM {table}")
    return cursor.fetchall()

def get_column_names(cursor, table):
    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
    return [desc[0] for desc in cursor.description]

def print_table(cursor, table):
    print(f"\nInhalt der Tabelle: {table}")
    rows = fetch_all(cursor, table)
    if not rows:
        print("-> Keine Daten vorhanden.")
        return
    columns = get_column_names(cursor, table)
    print(" | ".join(columns))
    print("-" * 80)
    for row in rows:
        print(" | ".join(str(r) if r is not None else "" for r in row))

def print_bewerbung(cursor):
    # Hier werden Bewerbung + Bewerber + Firma mit Texten statt IDs ausgegeben
    cursor.execute("""
        SELECT b.bwg_id, bw.bw_vorname || ' ' || bw.bw_nachname AS Bewerber,
               f.f_stellenbezeichnung || ' bei ' || f.f_name || ' (' || f.f_datum || ')' AS Firma
        FROM tbl_bewerbung b
        JOIN tbl_bewerber bw ON b.bwg_bw_id = bw.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        ORDER BY b.bwg_id
    """)
    rows = cursor.fetchall()
    print("\nInhalt der Tabelle: tbl_bewerbung (mit aufgelösten Fremdschlüsseln)")
    print("ID | Bewerber | Firma")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]}")

def print_bwg_ag(cursor):
    # Bewerbung - Arbeitgeber mit Namen auflösen
    cursor.execute("""
        SELECT bwg.bwg_ag_id, b.bwg_id, ag.ag_name, ag.ag_datum_von, ag.ag_datum_bis
        FROM tbl_bwg_ag bwg
        JOIN tbl_bewerbung b ON bwg.bwg_ag_bwg_id = b.bwg_id
        JOIN tbl_arbeitgeber ag ON bwg.bwg_ag_ag_id = ag.ag_id
        ORDER BY bwg.bwg_ag_id
    """)
    rows = cursor.fetchall()
    print("\nInhalt der Tabelle: tbl_bwg_ag (Bewerbung <-> Arbeitgeber)")
    print("ID | Bewerbung_ID | Arbeitgeber_Name | Von | Bis")
    print("-" * 80)
    for r in rows:
        print(" | ".join(str(x) if x is not None else "" for x in r))

def print_bwg_ag_t(cursor):
    # Tätigkeiten zu Bewerbung-Arbeitgeber-Zuordnung
    cursor.execute("""
        SELECT t.bwg_ag_t_id, b.bwg_ag_id, ta.t_name
        FROM tbl_bwg_ag_t t
        JOIN tbl_bwg_ag b ON t.bwg_ag_t_bwg_ag_id = b.bwg_ag_id
        JOIN tbl_taetigkeit ta ON t.bwg_ag_t_t_id = ta.t_id
        ORDER BY t.bwg_ag_t_id
    """)
    rows = cursor.fetchall()
    print("\nInhalt der Tabelle: tbl_bwg_ag_t (Tätigkeiten zu Bewerbung-Arbeitgeber)")
    print("ID | bwg_ag_ID | Tätigkeit")
    print("-" * 80)
    for r in rows:
        print(" | ".join(str(x) if x is not None else "" for x in r))

def print_bwg_ab(cursor):
    # Ausbildung zu Bewerbung mit aufgelösten IDs
    cursor.execute("""
        SELECT bwg_ab.bwg_ab_id, b.bwg_id, ab.ab_name_staette, ab.ab_name_ausbildung
        FROM tbl_bwg_ab bwg_ab
        JOIN tbl_bewerbung b ON bwg_ab.bwg_ab_bwg_id = b.bwg_id
        JOIN tbl_ausbildung ab ON bwg_ab.bwg_ab_ab_id = ab.ab_id
        ORDER BY bwg_ab.bwg_ab_id
    """)
    rows = cursor.fetchall()
    print("\nInhalt der Tabelle: tbl_bwg_ab (Bewerbung <-> Ausbildung)")
    print("ID | Bewerbung_ID | Ausbildungsstätte | Ausbildung")
    print("-" * 80)
    for r in rows:
        print(" | ".join(str(x) if x is not None else "" for x in r))

def print_bwg_ab_swp(cursor):
    # Ausbildungsschwerpunkte für Bewerbungen mit Auflösung
    cursor.execute("""
        SELECT s.bwg_ab_swp_id, ab.bwg_ab_id, swp.ab_swp_name
        FROM tbl_bwg_ab_swp s
        JOIN tbl_bwg_ab ab ON s.bwg_ab_swp_bwg_ab_id = ab.bwg_ab_id
        JOIN tbl_ab_schwerpunkt swp ON s.bwg_ab_swp_ab_swp_id = swp.ab_swp_id
        ORDER BY s.bwg_ab_swp_id
    """)
    rows = cursor.fetchall()
    print("\nInhalt der Tabelle: tbl_bwg_ab_swp (Ausbildungsschwerpunkte)")
    print("ID | bwg_ab_ID | Schwerpunkt")
    print("-" * 80)
    for r in rows:
        print(" | ".join(str(x) if x is not None else "" for x in r))

def print_bwg_k(cursor):
    # Kenntnisse mit Namen ausgeben
    cursor.execute("""
        SELECT bwg_k.bwg_k_id, b.bwg_id, k.k_name, k.k_stufe
        FROM tbl_bwg_k bwg_k
        JOIN tbl_bewerbung b ON bwg_k.bwg_k_bwg_id = b.bwg_id
        JOIN tbl_kenntnisse k ON bwg_k.bwg_k_k_id = k.k_id
        ORDER BY bwg_k.bwg_k_id
    """)
    rows = cursor.fetchall()
    print("\nInhalt der Tabelle: tbl_bwg_k (Kenntnisse)")
    print("ID | Bewerbung_ID | Kenntnis | Stufe")
    print("-" * 80)
    for r in rows:
        print(" | ".join(str(x) if x is not None else "" for x in r))

def print_bwg_i(cursor):
    # Interessen mit Namen ausgeben
    cursor.execute("""
        SELECT bwg_i.bwg_i_id, b.bwg_id, i.i_name
        FROM tbl_bwg_i bwg_i
        JOIN tbl_bewerbung b ON bwg_i.bwg_i_bwg_id = b.bwg_id
        JOIN tbl_interessen i ON bwg_i.bwg_i_i_id = i.i_id
        ORDER BY bwg_i.bwg_i_id
    """)
    rows = cursor.fetchall()
    print("\nInhalt der Tabelle: tbl_bwg_i (Interessen)")
    print("ID | Bewerbung_ID | Interesse")
    print("-" * 80)
    for r in rows:
        print(" | ".join(str(x) if x is not None else "" for x in r))


def main():
    db_path = "lebenslauf.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabellen ohne IDs, nur reine Daten
    simple_tables = [
        "tbl_bewerber", "tbl_firma", "tbl_arbeitgeber", "tbl_taetigkeit",
        "tbl_ausbildung", "tbl_ab_schwerpunkt", "tbl_kenntnisse", "tbl_interessen"
    ]

    print("---- Reine Tabelleninhalte (ohne Fremdschlüssel-Auflösung) ----")
    for table in simple_tables:
        print_table(cursor, table)

    # Tabellen mit Fremdschlüsseln und Auflösung der IDs
    print("\n---- Tabelleninhalte mit aufgelösten Fremdschlüsseln ----")
    print_bewerbung(cursor)
    print_bwg_ag(cursor)
    print_bwg_ag_t(cursor)
    print_bwg_ab(cursor)
    print_bwg_ab_swp(cursor)
    print_bwg_k(cursor)
    print_bwg_i(cursor)

    conn.close()

if __name__ == "__main__":
    main()
