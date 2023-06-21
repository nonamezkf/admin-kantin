import datetime

from admin_app import app

from peewee import *

DATABASE = 'dummy.db'
db = SqliteDatabase(DATABASE)

@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    db.close()
    return response

class BaseModel(Model):
	class Meta:
		database = db

class OrangTua(BaseModel):
	username = CharField(unique=True)
	password = CharField()
	role = TextField()
	nama = TextField()
	ttl = DateField('%d-%m-%Y')
	alamat = TextField()
	no_tlp = SmallIntegerField()
	join_at = DateTimeField(default=datetime.datetime.now())

class Anak(BaseModel):
	orangtua = ForeignKeyField(OrangTua, backref='anaks')
	nama = TextField()
	username = CharField()
	role = TextField()
	password = CharField()
	alamat = TextField()
	no_tlp = SmallIntegerField()
	saldo = IntegerField()
	tgl_lahir = DateField()

class Admin(BaseModel):
	role = TextField()
	nama = TextField()
	email = CharField()
	password = CharField()
	no_tlp = SmallIntegerField()

class Karyawan(BaseModel):
	admin = ForeignKeyField(Admin, backref='karyawans')
	nama = TextField()
	email = CharField()
	password = CharField()
	no_tlp = SmallIntegerField()

class PesananSiswa(BaseModel):
	anak = ForeignKeyField(Anak, backref='pesanansiswas')
	totalPembayaran = IntegerField()
	ttl_pemesanan = DateTimeField(default=datetime.datetime.now())

class DetailPesanan(BaseModel):
	pesanansiswa = ForeignKeyField(PesananSiswa, backref='detailpesanan')
	kuantitas = SmallIntegerField()
	harga = IntegerField()

def create_tables():
    with database:
        database.connect()
        database.create_tables([OrangTua, Anak, Admin, Karyawan, PesananSiswa, DetailPesanan])
        database.close()

# database.connect()
# database.create_tables([OrangTua, Anak, Admin, Karyawan, PesananSiswa, DetailPesanan])
