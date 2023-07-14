from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from functools import wraps
from hashlib import sha256
import json, requests

# from db import *

app = Flask(__name__)
app.secret_key = 'asdiquwbebd12365sasdADASDdfn'

def get_curret_user():
    if session.get('logged_in'):
        return User.get(User.id == session['user_id'])

def auth_user(user):
    session['logged_in'] = True
    # session['user_id'] = user.id
    session['nama'] = user.nama

def get_curret_user():
    if session.get('logged_in'):
        return session['user_id']
    # session['user_id']

def redirect_to_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('nama'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def redirect_after_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('nama'):
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def format_rupiah(number):
    # Mengubah angka menjadi string dan menghapus karakter non-digit
    number = str(number).replace(',', '').replace('.', '')

    # Mengecek apakah angka valid
    if not number.isdigit():
        raise ValueError('Invalid number')

    # Mengubah string angka menjadi integer
    number = int(number)

    # Mengubah angka menjadi format rupiah
    rupiah = "Rp. {:,}".format(number).replace(',', '.')

    return rupiah


############################## routing ##################################

@app.route('/', methods=['GET','POST'])
@redirect_after_login
def index():
    if request.method == 'POST':
        form_username = request.form['username']
        form_password = request.form['password']

        data_login = {
            "username" : form_username,
            "password" : form_password
        }

        dataLogin_json = json.dumps(data_login)
        alamatserver = "http://localhost:5055/api/login"
        headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
        kirimdata = requests.post(alamatserver, data=dataLogin_json, headers=headers)
        cow = json.loads(kirimdata.text)
        # print(cow)

       
        if cow["message"] =="sukses":
            # print("iniclientberhasil")
            session['nama'] = form_username
            # print(session['username'])

            session["id_admin"] = cow["auth_user"]["admin_id"]
            print(session['id_admin'])
            return redirect(url_for('dashboard'))
            #return "<p>ini berhasil</p>"
        
        elif cow["message"] == "gagal":
            # print("iniclientgagal")
            flash('Masukkan data yang sudah terdaftar', 'alert-danger') 
            
    return render_template('index.html')

@app.route('/dashboard', methods=['GET','POST'])
@redirect_to_login
def dashboard():
    # if request.method == 'POST':
    #     return {"message" : "success"}
    
    alamatserver = "http://localhost:5055/api/karyawans"
    datas = requests.get(alamatserver)

    rows = json.loads(datas.text)

    return render_template('dashboard.html', rows=rows)

@app.route('/riwayattransaksi', methods=['GET','POST'])
@redirect_to_login
def riwayattransaksi():

    alamatserver = f"http://localhost:5055/api/semuahistoripesanan/"
    datas = requests.get(alamatserver)
    rows = json.loads(datas.text)

    return render_template('riwayattransaksi.html', rows=rows)


@app.route('/searchriwayat', methods=['GET', 'POST'])
@redirect_to_login
def searchriwayat():
    error = None
    form_input = request.form['forminput']
    if not form_input or not form_input.strip():
        error = 'Form harus terisi'
    if error != None:
        flash(error, 'alert-danger')
    
    try:
        if error is None:
            data_search = {
                'forminput': form_input
            }

            data_dump_json = json.dumps(data_search)
            alamatserver = "http://localhost:5055/api/searchHistoripesananbyid/"
            headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
            kirimdata = requests.get(alamatserver, data=data_dump_json, headers=headers)
            rows = json.loads(kirimdata.text)

            return render_template('riwayattransaksi.html', rows=rows)
    except:
        flash("ada yang error", 'alert-danger')



@app.route('/detail/<int:id>', methods=['GET', 'POST'])
@redirect_to_login
def detail(id):

	alamatserver = f"http://127.0.0.1:5055/api/detailpesanan/{id}"
	headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
	datas = requests.get(alamatserver, headers=headers)

	rows = json.loads(datas.text)

	detailPesanan = rows['detail']
	namaanak = rows['namanya']
	ttl_pemesanan = rows['ttl_pemesanan']
	totalPembayaran = rows['totalPembayaran']

	totalHarga = format_rupiah(totalPembayaran)
	print(totalHarga)

	return render_template('detail.html', detailPesanan=detailPesanan, namaanak=namaanak, ttl_pemesanan=ttl_pemesanan, totalHarga=totalHarga, format_rupiah=format_rupiah)

@app.route('/tambah', methods=['GET','POST'])
@redirect_to_login
def tambah():
    if request.method == 'POST':
        error = None
        id_admin = session["id_admin"]
        form_nama = request.form['nama']
        form_email = request.form['email']
        form_no_tlp = request.form['no_tlp']
        form_password = request.form['password']
        hash_password = sha256(form_password.encode()).hexdigest()

        if not form_nama or not form_nama.strip():
            error = 'Nama harus terisi'
        elif not form_email or not form_email.strip():
            error = 'Email harus terisi'
        elif not form_no_tlp or not form_no_tlp.strip():
            error = 'No telepon harus terisi'
        elif not form_password or not form_password.strip(): 
            error = 'Password harus terisi'
        
        if error != None:
            flash(error, 'alert-danger')

        try:
            if error is None:
                data_karyawan = {
                    'id_admin': id_admin,
                    'nama' : form_nama,
                    'email' : form_email,
                    'no_tlp' : form_no_tlp,
                    'password': hash_password
                }

                data_dump_json = json.dumps(data_karyawan)
                alamatserver = "http://localhost:5055/api/karyawans"
                headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
                kirimdata = requests.post(alamatserver, data=data_dump_json, headers=headers)

                flash("Data berhasil disimpan", 'alert-success')
                return redirect('dashboard')
        except:
            flash("ada yang error", 'errors')
    return render_template('tambah.html')

@app.route('/update/<string:id>', methods=['GET', 'POST'])
@redirect_to_login
def update(id):
    if request.method == "POST":
        try :
            id_admin = session["id_admin"]
            form_nama = request.form['nama']
            form_email = request.form['email']
            form_no_tlp = request.form['no_tlp']
            hash_password = sha256(request.form['password'].encode()).hexdigest()

            data_karyawan = {
                'id_admin': id_admin,
                'nama' : form_nama,
                'email' : form_email,
                'no_tlp' : form_no_tlp,
                'password': hash_password
            }

            data_dump_json = json.dumps(data_karyawan)
            alamatserver = f"http://localhost:5055/api/karyawanbyid/{id}"

            headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
            kirimdata = requests.put(alamatserver, data=data_dump_json, headers=headers)
            flash("Data berhasil diperbarui", 'alert-success')
            return redirect(url_for('dashboard'))
        except:
            flash('Data yang anda masukkan kurang', 'alert-danger')
            
    alamatserver = f"http://localhost:5055/api/karyawanbyid/{id}"
    headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
    datas = requests.get(alamatserver, headers=headers)

    rows = json.loads(datas.text)
    return render_template('edit.html', rows=rows)

@app.route('/delete/<string:id>', methods=['GET', 'POST'])
@redirect_to_login
def delete(id):
    if request.method == "GET":
        alamatserver = f"http://localhost:5055/api/karyawanbyid/{id}"
        headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
        kirimrequest = requests.delete(alamatserver, headers=headers)
        flash('Data berhasil dihapus', 'alert-success')
        return redirect(url_for('dashboard'))
    else:
        flash('maaf data dengan id tersebut tidak ditemukan')
    return render_template('dashboard.html')

@app.route('/logout', methods=['GET','POST'])
def logout():
    if request.method == 'GET':
        hapus_session = {
            'session_hapus' : True
        }

        dataHapusSession_json = json.dumps(hapus_session)
        alamatserver = "http://localhost:5055/api/logout"
        headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
        kirimdata = requests.get(alamatserver, data=dataHapusSession_json, headers=headers)
        
    session.pop('nama', None)
    flash('Anda berhasil logout','alert-success')
    return redirect(url_for('index'))


if __name__ == '__main__':
	app.run(
		debug=True,
		host='0.0.0.0',
        port=5056
		)