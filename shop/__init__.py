import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import IMAGES, UploadSet, configure_uploads
import os
from flask_login import LoginManager
from flask_migrate import Migrate




basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rem2002@localhost/hieu_shopdb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
app.config['SECRET_KEY'] = 'hfi7weytf87we6tr83yre983253eh'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.app_context().push()

migrate = Migrate(app, db)
with app.app_context():
    if db.engine.url.drivername == "sqlite":
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customerLogin'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u"Please login first"

from shop.admin import routes
from shop.products import routes
from shop.carts import carts
from shop.customers import routes

# from flask import Flask, render_template, request, session
# from flask_mail import Mail, Message
# import random
# import string
#
# app = Flask(__name__)
# app.secret_key = 'your_secret_key'
#
# # Cấu hình Flask-Mail
# app.config['MAIL_SERVER'] = 'your_mail_server'
# app.config['MAIL_PORT'] = 587  # Port của mail server
# app.config['MAIL_USERNAME'] = 'your_username'  # Tên người dùng SMTP
# app.config['MAIL_PASSWORD'] = 'your_password'  # Mật khẩu SMTP
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
#
# mail = Mail(app)
#
#
# # Function để tạo mã OTP
# def generate_otp():
#     otp = ''.join(random.choices(string.digits, k=6))
#     return otp
#
#
# # Route để gửi OTP qua email
# @app.route('/send_otp', methods=['POST'])
# def send_otp():
#     if request.method == 'POST':
#         email = request.form['email']  # Lấy địa chỉ email từ form
#         otp = generate_otp()
#
#         # Lưu mã OTP trong session
#         session['otp'] = otp
#
#         # Gửi email chứa mã OTP đến địa chỉ email nhập từ form
#         msg = Message('Mã OTP của bạn', sender='your_email@example.com', recipients=[email])
#         msg.body = f'Mã OTP của bạn là: {otp}.'
#
#         try:
#             mail.send(msg)
#             return "Mã OTP đã được gửi đi!"
#         except Exception as e:
#             return str(e)
#
#     return "Lỗi"
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
