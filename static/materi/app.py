from flask import Flask, render_template, request, redirect, send_from_directory, session, url_for
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'rahasia'
UPLOAD_FOLDER_MATERI = 'static/materi'
UPLOAD_FOLDER_TUGAS = 'static/tugas'
app.config['UPLOAD_FOLDER_MATERI'] = UPLOAD_FOLDER_MATERI
app.config['UPLOAD_FOLDER_TUGAS'] = UPLOAD_FOLDER_TUGAS

# BIKIN FOLDER KALO BELUM ADA
os.makedirs(UPLOAD_FOLDER_MATERI, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_TUGAS, exist_ok=True)

# DATABASE
def buat_db():
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
            teks TEXT,
            pdf TEXT,
            gambar TEXT,
            tanggal TEXT
        )
    ''')
    conn.commit()
    conn.close()

buat_db()

# -------------------- HALAMAN SISWA --------------------
@app.route('/')
def index():
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute("SELECT * FROM materi ORDER BY id DESC")
    materi = c.fetchall()
    conn.close()
    return render_template('siswa.html', materi=materi)

# -------------------- LOGIN GURU --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'guru' and request.form['password'] == '123':
            session['guru'] = True
            return redirect('/guru')
    return render_template('login.html')

# -------------------- HALAMAN GURU --------------------
@app.route('/guru')
def guru():
    if not session.get('guru'):
        return redirect('/login')
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute("SELECT * FROM materi ORDER BY id DESC")
    materi = c.fetchall()
    conn.close()
    return render_template('guru.html', materi=materi)

# -------------------- UPLOAD MATERI --------------------
@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('guru'):
        return redirect('/login')

    judul = request.form['judul']
    deskripsi = request.form['deskripsi']
    files = request.files.getlist('file')  # Ambil semua file yang dikirim
    tanggal = datetime.now().strftime('%Y-%m-%d %H:%M')

    conn = sqlite3.connect('materi.db')
    c = conn.cursor()

    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER_MATERI, filename))
            c.execute("INSERT INTO materi (judul, filename, tanggal, deskripsi) VALUES (?, ?, ?, ?)",
                      (judul, filename, tanggal, deskripsi))

    conn.commit()
    conn.close()

    return redirect('/guru')

# -------------------- HAPUS MATERI --------------------
@app.route('/hapus/<namafile>')
def hapus(namafile):
    if not session.get('guru'):
        return redirect('/login')
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    if namafile.startswith("nofile_"):
        id = namafile.replace("nofile_", "")
        c.execute("DELETE FROM materi WHERE id = ?", (id,))
    else:
        c.execute("DELETE FROM materi WHERE filename = ?", (namafile,))
        try:
            os.remove(os.path.join(UPLOAD_FOLDER_MATERI, namafile))
        except:
            pass
    conn.commit()
    conn.close()
    return redirect('/guru')

@app.route('/download/<namafile>')
def download(namafile):
    return send_from_directory(UPLOAD_FOLDER_MATERI, namafile)

# -------------------- UPLOAD TUGAS (SISWA) --------------------
@app.route('/kumpul', methods=['GET', 'POST'])
def kumpul():
    if request.method == 'POST':
        nama = request.form['nama']
        kelas = request.form['kelas']
        teks = request.form['teks']
        pdf = request.files.get('pdf')
        gambar = request.files.getlist('gambar')

        filename_pdf = ''
        if pdf and pdf.filename != '':
            filename_pdf = secure_filename(pdf.filename)
            pdf.save(os.path.join(UPLOAD_FOLDER_TUGAS, filename_pdf))

        gambar_filenames = []
        for g in gambar:
            if g and g.filename != '':
                fname = secure_filename(g.filename)
                g.save(os.path.join(UPLOAD_FOLDER_TUGAS, fname))
                gambar_filenames.append(fname)

        tanggal = datetime.now().strftime('%Y-%m-%d %H:%M')
        conn = sqlite3.connect('materi.db')
        c = conn.cursor()
        c.execute("INSERT INTO tugas (nama, kelas, teks, pdf, gambar, tanggal) VALUES (?, ?, ?, ?, ?, ?)",
                  (nama, kelas, teks, filename_pdf, ','.join(gambar_filenames), tanggal))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('kumpul_tugas.html')

# -------------------- LIHAT TUGAS (GURU) --------------------
@app.route('/lihat_tugas')
def lihat_tugas():
    if not session.get('guru'):
        return redirect('/login')
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tugas ORDER BY id DESC")
    tugas = c.fetchall()
    conn.close()
    return render_template('lihat_tugas.html', tugas=tugas)

@app.route('/hapus_tugas/<int:id>', methods=['POST'])
def hapus_tugas(id):
    # kode hapus file dan data dari database
    ...
    if not session.get('guru'):
        return redirect('/login')
    conn = sqlite3.connect('materi.db')
    c = conn.cursor()
    c.execute("SELECT pdf, gambar FROM tugas WHERE id = ?", (id,))
    data = c.fetchone()
    if data:
        if data[0]:
            try: os.remove(os.path.join(UPLOAD_FOLDER_TUGAS, data[0]))
            except: pass
        if data[1]:
            for img in data[1].split(','):
                try: os.remove(os.path.join(UPLOAD_FOLDER_TUGAS, img))
                except: pass
    c.execute("DELETE FROM tugas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/lihat_tugas')

@app.route('/download_tugas/<namafile>')
def download_tugas(namafile):
    return send_from_directory(UPLOAD_FOLDER_TUGAS, namafile)

# -------------------- LOGOUT --------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=3000)