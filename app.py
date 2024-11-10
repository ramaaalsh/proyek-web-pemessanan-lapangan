from curses import flash
import datetime
from io import BytesIO
import locale
import os
from posixpath import dirname, join
import re
import bcrypt
from bson import ObjectId
from flask import Flask, jsonify, make_response, render_template, request, redirect, url_for, session, flash
from flask.cli import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from pymongo import MongoClient
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# from distutils.command import build
app = Flask(__name__)
app.secret_key = 'sjdcasjbcsabfh'

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  str(os.environ.get("DB_NAME"))

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

db = client.gor_sinta
users_collection = db.users
bookings_collection = db.bookings
payments_collection = db.payments
dataLapangan_collection = db.dataLapangan
dataGaleri_collection = db.dataGaleri
dataKontak_collection = db.dataKontak
dataTentang_collection = db.dataTentang
dataReview_collection = db.dataReview
dataPembayaran_collection = db.dataPembayaran
dataAdmin_collection = db.dataAdmin
# Inisialisasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Set the locale to Indonesian
locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        user = User()
        user.id = str(user_data['_id'])
        return user
    return None

def set_login_time():
    session['login_time'] = datetime.utcnow()
# Fungsi untuk memeriksa waktu login
def check_login_time():# Periksa apakah waktu login sudah ditetapkan
    if 'login_time' in session:
        login_time = session['login_time']
        current_time = datetime.now(timezone.utc)  # Ubah ke objek waktu yang sadar zona waktu
        time_difference = current_time - login_time
        if time_difference.total_seconds() > LOGOUT_TIME_SECONDS:
            session.clear()
            flash('Anda telah logout otomatis karena tidak aktif.')
            return redirect(url_for('login'))
LOGOUT_TIME_SECONDS = 1800  
def is_valid_admin():
    return 'admin_id' in session
@app.route('/')
def index():
    dataLapangan = dataLapangan_collection.find({})
    dataGaleri = dataGaleri_collection.find({})
    dataKontak = dataKontak_collection.find_one()
    dataTentang = dataTentang_collection.find_one()
    dataReview = dataReview_collection.find({})
    dataGaleri = dataGaleri_collection.find({})
    alert_message = session.pop('alert_message', 'Selamat Datang di Gor Shinta semoga Anda senang')
    return render_template('index.html', alert_message=alert_message, dataLapangan=dataLapangan, dataGaleri=dataGaleri, dataKontak=dataKontak, dataTentang=dataTentang, dataReview=dataReview)
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        fullname = request.form['fullname']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password1 = request.form['password1'].encode('utf-8')
        password2 = request.form['password2'].encode('utf-8')
        hash_password = bcrypt.hashpw(password1, bcrypt.gensalt())
        if not fullname or not phone_number or not email or not password1 or not password2:
            flash('Semua kolom harus diisi')
            return redirect(url_for('register'))
        if len(password1) < 8:
            flash('Kata Sandi minimal 8 karakter')
            return redirect(url_for('register'))
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('email tidak valid')
            return redirect(url_for('register'))
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            flash('nomor telepon tidak valid')
            return redirect(url_for('register'))
        if password1 != password2:
            flash('Kata sandi tidak cocok')
            return redirect(url_for('register'))
        if users_collection.find_one({'email': email}): 
            flash('email sudah terdaftar')
            return redirect(url_for('register'))
        new_user = {
            'fullname': fullname,
            'phone_number': phone_number,
            'email': email,
            'password': hash_password
        }
        user_id = users_collection.insert_one(new_user).inserted_id
        set_login_time()
        session['user_id'] = str(user_id)
        session['email'] = email
        session['fullname'] = fullname
        session['phone_number'] = phone_number
        return redirect(url_for('login'))
# Fungsi untuk memeriksa waktu login
def check_login_time():# Periksa apakah waktu login sudah ditetapkan
    if 'login_time' in session:
        login_time = session['login_time']
        current_time = datetime.now(timezone.utc)  # Ubah ke objek waktu yang sadar zona waktu
        time_difference = current_time - login_time
        if time_difference.total_seconds() > LOGOUT_TIME_SECONDS:
            session.clear()
            flash('Anda telah logout otomatis karena tidak aktif.')
            return redirect(url_for('login'))
LOGOUT_TIME_SECONDS = 1800  
def is_valid_admin():
    return 'admin_id' in session
@app.route('/')
def index():
    dataLapangan = dataLapangan_collection.find({})
    dataGaleri = dataGaleri_collection.find({})
    dataKontak = dataKontak_collection.find_one()
    dataTentang = dataTentang_collection.find_one()
    dataReview = dataReview_collection.find({})
    dataGaleri = dataGaleri_collection.find({})
    alert_message = session.pop('alert_message', 'Selamat Datang di Gor Shinta semoga Anda senang')
    return render_template('index.html', alert_message=alert_message, dataLapangan=dataLapangan, dataGaleri=dataGaleri, dataKontak=dataKontak, dataTentang=dataTentang, dataReview=dataReview)
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        fullname = request.form['fullname']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password1 = request.form['password1'].encode('utf-8')
        password2 = request.form['password2'].encode('utf-8')
        hash_password = bcrypt.hashpw(password1, bcrypt.gensalt())
        if not fullname or not phone_number or not email or not password1 or not password2:
            flash('Semua kolom harus diisi')
            return redirect(url_for('register'))
        if len(password1) < 8:
            flash('Kata Sandi minimal 8 karakter')
            return redirect(url_for('register'))
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('email tidak valid')
            return redirect(url_for('register'))
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            flash('nomor telepon tidak valid')
            return redirect(url_for('register'))
        if password1 != password2:
            flash('Kata sandi tidak cocok')
            return redirect(url_for('register'))
        if users_collection.find_one({'email': email}): 
            flash('email sudah terdaftar')
            return redirect(url_for('register'))
        new_user = {
            'fullname': fullname,
            'phone_number': phone_number,
            'email': email,
            'password': hash_password
        }
        user_id = users_collection.insert_one(new_user).inserted_id
        set_login_time()
        session['user_id'] = str(user_id)
        session['email'] = email
        session['fullname'] = fullname
        session['phone_number'] = phone_number
        return redirect(url_for('login'))
# Simpan data pemesanan ke sesi
        session['booking_data'] = {
            'fullname': fullname,
            'phone_number': phone_number,
            'email': email,
            'selected_date': selected_date,
            'selected_time': selected_time,
            'selected_sport': selected_sport,
            'selected_court': selected_court,
            'selected_price': selected_price,
            'selected_duration': selected_duration
        }
        
        # Simpan pesan alert ke sesi
        session['alert_message'] = 'Berhasil dipesan. Silahkan pilih metode pembayaran.'
        
        # Alihkan ke halaman pembayaran
        return redirect(url_for('payment'))
    
    return render_template('selectTime.html', fullname=fullname, phone_number=phone_number, email=email, dataLapangan=dataLapangan, alert_message=alert_message)
@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    dataPembayaran = list(db.dataPembayaran.find({}))
    fullname = session.get('fullname')
    booking_data = session.get('booking_data')
    alert_message = session.pop('alert_message', 'Silahkan pilih metode pembayaran.')
    
    if not booking_data:
        alert_message = 'Tidak ada data pemesanan yang ditemukan. Silakan lakukan pemesanan terlebih dahulu.'
        return redirect(url_for('selectTime'))
    
    if request.method == 'POST':
        payment_type = request.form.get('payment_type')
        payment_method = request.form.get('payment_method')
        payment_proof = request.files.get('payment_proof')
        
        if not payment_type or not payment_method:
            session['alert_message'] = 'Pilih metode pembayaran terlebih dahulu.'
            return redirect(url_for('payment'))
        
        if payment_proof:
            nama_file_asli = payment_proof.filename
            nama_file_foto = secure_filename(nama_file_asli)
            file_path = f'./static/img/{nama_file_foto}'
            payment_proof.save(file_path)
        else:
            nama_file_foto = None
# Simpan data pembayaran dan pemesanan ke MongoDB
        payment_data = {
            'fullname': booking_data['fullname'],
            'phone_number': booking_data['phone_number'],
            'email': booking_data['email'],
            'selected_date': booking_data['selected_date'],
            'selected_time': booking_data['selected_time'],
            'selected_sport': booking_data['selected_sport'],
            'selected_court': booking_data['selected_court'],
            'selected_price': booking_data['selected_price'],
            'selected_duration': booking_data['selected_duration'],
            'payment_type': payment_type,
            'payment_method': payment_method,
            'payment_proof': nama_file_foto
        }
        
        result = db.payments.insert_one(payment_data)
        payment_id = result.inserted_id
# Simpan data pemesanan ke sesi
        session['booking_data'] = {
            'fullname': fullname,
            'phone_number': phone_number,
            'email': email,
            'selected_date': selected_date,
            'selected_time': selected_time,
            'selected_sport': selected_sport,
            'selected_court': selected_court,
            'selected_price': selected_price,
            'selected_duration': selected_duration
        }
        
        # Simpan pesan alert ke sesi
        session['alert_message'] = 'Berhasil dipesan. Silahkan pilih metode pembayaran.'
        
        # Alihkan ke halaman pembayaran
        return redirect(url_for('payment'))
    
    return render_template('selectTime.html', fullname=fullname, phone_number=phone_number, email=email, dataLapangan=dataLapangan, alert_message=alert_message)
@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    dataPembayaran = list(db.dataPembayaran.find({}))
    fullname = session.get('fullname')
    booking_data = session.get('booking_data')
    alert_message = session.pop('alert_message', 'Silahkan pilih metode pembayaran.')
    
    if not booking_data:
        alert_message = 'Tidak ada data pemesanan yang ditemukan. Silakan lakukan pemesanan terlebih dahulu.'
        return redirect(url_for('selectTime'))
    
    if request.method == 'POST':
        payment_type = request.form.get('payment_type')
        payment_method = request.form.get('payment_method')
        payment_proof = request.files.get('payment_proof')
        
        if not payment_type or not payment_method:
            session['alert_message'] = 'Pilih metode pembayaran terlebih dahulu.'
            return redirect(url_for('payment'))
        
        if payment_proof:
            nama_file_asli = payment_proof.filename
            nama_file_foto = secure_filename(nama_file_asli)
            file_path = f'./static/img/{nama_file_foto}'
            payment_proof.save(file_path)
        else:
            nama_file_foto = None
# Simpan data pembayaran dan pemesanan ke MongoDB
        payment_data = {
            'fullname': booking_data['fullname'],
            'phone_number': booking_data['phone_number'],
            'email': booking_data['email'],
            'selected_date': booking_data['selected_date'],
            'selected_time': booking_data['selected_time'],
            'selected_sport': booking_data['selected_sport'],
            'selected_court': booking_data['selected_court'],
            'selected_price': booking_data['selected_price'],
            'selected_duration': booking_data['selected_duration'],
            'payment_type': payment_type,
            'payment_method': payment_method,
            'payment_proof': nama_file_foto
        }
        
        result = db.payments.insert_one(payment_data)
        payment_id = result.inserted_id
