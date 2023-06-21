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
            # print(session['id_admin'])
            return redirect(url_for('dashboard'))
            #return "<p>ini berhasil</p>"
        
        if cow =="gagal":
            # print("iniclientgagal")
            return redirect(url_for('index'))
            return flash("login gagal")


    # if request.method == 'POST' and request.form['username']:
    #     try:
    #         hash_password = sha256(request.form['password'].encode()).hexdigest()
    #         user = Admin.get(
    #             (Admin.nama == request.form['username']) & 
    #             (Admin.password == hash_password))
    #     except Admin.DoesNotExist:
    #         flash('username atau password salah')
    #     else:
    #         auth_user(user)
    #         return redirect(url_for('dashboard'))
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

@app.route('/riwayattransaksi')
@redirect_to_login
def riwayattransaksi():
    
    return render_template('riwayattransaksi.html')

@app.route('/tambah', methods=['GET','POST'])
@redirect_to_login
def tambah():
    if request.method == 'POST':
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
        alamatserver = "http://localhost:5055/api/karyawans"

        headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
        kirimdata = requests.post(alamatserver, data=data_dump_json, headers=headers)

        redirect(url_for('dashboard'))    
    return render_template('tambah.html')

@app.route('/update/<string:id>', methods=['GET', 'POST'])
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

            return redirect(url_for('dashboard'))
        except:
            flash('data yang anda masukkan kurang')
        # result = "helo"
    alamatserver = f"http://localhost:5055/api/karyawanbyid/{id}"
    # headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
    datas = requests.get(alamatserver)

    rows = json.loads(datas.text)

    print(rows)
    # id_karyawan = rows.id
    # print(id_karyawan)

    return render_template('edit.html', rows=rows)

@app.route('/updatesave/<string:id>', methods=['POST'])
def updatesave(id):
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

            redirect(url_for('dashboard'))
        except:
            flash('data yang anda masukkan kurang')
 
@app.route('/delete', methods=['GET', 'POST'])
@redirect_to_login
def delete():
    return redirect('dashboard')

@app.route('/logout', methods=['GET','POST'])
def logout():
    if request.method == 'POST':
        hapus_session = {
            'session_hapus' : True
        }

        dataHapusSession_json = json.dumps(hapus_session)
        alamatserver = "http://localhost:5055/api/logout"

        headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
        kirimdata = request.post(alamatserver, data=dataHapusSession_json, headers=headers)
        
    session.pop('nama', None)
    flash('You are now logged out','success')
    return redirect(url_for('index'))


if __name__ == '__main__':
	app.run(
		debug=True,
		host='0.0.0.0'
		)