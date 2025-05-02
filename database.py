import sqlite3
import json

def create_table():
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS materi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT,
            filename TEXT,
            tanggal TEXT,
            deskripsi TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS tugas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            kelas TEXT,
            pdf TEXT,
            gambar TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Fungsi untuk materi
def tambah_materi(judul, filename, tanggal, deskripsi):
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute("INSERT INTO materi (judul, filename, tanggal, deskripsi) VALUES (?, ?, ?, ?)",
              (judul, filename, tanggal, deskripsi))
    conn.commit()
    conn.close()

def get_all_materi():
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute("SELECT * FROM materi ORDER BY id DESC")
    hasil = c.fetchall()
    conn.close()
    return hasil

def hapus_materi_by_filename(filename):
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute("DELETE FROM materi WHERE filename = ?", (filename,))
    conn.commit()
    conn.close()

# Fungsi untuk tugas siswa
def tambah_tugas(nama, kelas, pdf, list_gambar):
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    gambar_json = json.dumps(list_gambar)
    c.execute("INSERT INTO tugas (nama, kelas, pdf, gambar) VALUES (?, ?, ?, ?)",
              (nama, kelas, pdf, gambar_json))
    conn.commit()
    conn.close()

def get_all_tugas():
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tugas ORDER BY id DESC")
    hasil = c.fetchall()
    tugas_list = []
    for t in hasil:
        tugas_list.append({
            'id': t[0],
            'nama': t[1],
            'kelas': t[2],
            'pdf': t[3],
            'gambar': json.loads(t[4])
        })
    conn.close()
    return tugas_list

def hapus_tugas_by_id(tugas_id):
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute("DELETE FROM tugas WHERE id = ?", (tugas_id,))
    conn.commit()
    conn.close()

def get_tugas_by_id(tugas_id):
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tugas WHERE id = ?", (tugas_id,))
    t = c.fetchone()
    conn.close()
    if t:
        return {
            'id': t[0],
            'nama': t[1],
            'kelas': t[2],
            'pdf': t[3],
            'gambar': json.loads(t[4])
        }
    return None

print("wellll")