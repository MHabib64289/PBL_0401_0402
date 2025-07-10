from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'kunci-rahasia-yang-aman'

# Alamat API dari satu-satunya web service Anda
API_BASE_URL = "http://localhost:5051/cars"

# === Helper Function ===
def get_api_data(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Gagal koneksi ke API: {e}")
        flash("Tidak dapat terhubung ke web service. Pastikan service berjalan.", "danger")
        return []

# === ROUTE HALAMAN UTAMA ===
@app.route('/')
def index():
    rows = get_api_data(API_BASE_URL)
    return render_template('indexms.html', rows=rows)

# === CREATE CAR ===
@app.route('/createcar')
def createcar():
    return render_template('createcar.html')

@app.route('/createcarsave', methods=['POST'])
def createcarsave():
    try:
        datacar = {
            "carname": request.form.get('carName'),
            "carbrand": request.form.get('carBrand'),
            "carmodel": request.form.get('carModel'),
            "carprice": request.form.get('carPrice')
        }
        response = requests.post(f"{API_BASE_URL}/", json=datacar)
        response.raise_for_status()
        flash('Mobil berhasil ditambahkan!', 'success')
    except requests.exceptions.RequestException as e:
        flash(f'Gagal menambahkan mobil: {e}', 'danger')
    return redirect(url_for('index'))

# === READ CAR ===
@app.route('/readcar')
def readcar():
    rows = get_api_data(API_BASE_URL)
    return render_template('readcar.html', rows=rows)

# === UPDATE CAR ===
@app.route('/updatecar')
def updatecar():
    rows = get_api_data(API_BASE_URL)
    return render_template('updatecar.html', rows=rows)

@app.route('/updatecarsave', methods=['POST'])
def updatecarsave():
    try:
        car_id = request.form.get('id')
        # 'description' DIHILANGKAN DARI SINI
        datacar = {
            "carname": request.form.get('carname'),
            "carbrand": request.form.get('carbrand'),
            "carmodel": request.form.get('carmodel'),
            "carprice": request.form.get('carprice')
        }
        response = requests.put(f"{API_BASE_URL}/{car_id}", json=datacar)
        response.raise_for_status()
        flash(f'Mobil ID {car_id} berhasil diupdate!', 'success')
    except requests.exceptions.RequestException as e:
        flash(f'Gagal mengupdate mobil: {e}', 'danger')
    return redirect(url_for('updatecar'))

# === DELETE CAR ===
@app.route('/deletecar')
def deletecar():
    rows = get_api_data(API_BASE_URL)
    return render_template('deletecar.html', rows=rows)

@app.route('/deletecar/execute/<int:car_id>', methods=['POST'])
def deletecar_execute(car_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/{car_id}")
        response.raise_for_status()
        flash(f'Mobil ID {car_id} berhasil dihapus!', 'warning')
    except requests.exceptions.RequestException as e:
        flash(f'Gagal menghapus mobil: {e}', 'danger')
    return redirect(url_for('deletecar'))

# === SEARCH CAR ===
@app.route('/searchcar', methods=['GET', 'POST'])
def searchcar():
    results = []
    keyword = ""
    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()
        if keyword:
            search_url = f"{API_BASE_URL}/search/{keyword}"
            results = get_api_data(search_url)
            if not results:
                flash(f'Tidak ditemukan mobil dengan kata kunci: "{keyword}"', 'info')
        else:
            flash('Masukkan kata kunci pencarian.', 'info')

    return render_template('searchcar.html', results=results, keyword=keyword)

# === JALANKAN APP ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
