from flask import render_template, session, request, redirect, url_for, flash
from flask_login import current_user

from .forms import RegistrationForm, LoginForm

from shop import app, db, bcrypt
from .models import User
from shop.products.models import Addproduct, Brand, Category
from shop.customers.models import Register, CustomerOrder
import os


@app.route('/admin')
def admin():
#     # Đẩu tiên, kiểm tra để user login
#   if 'email' not in session:
    if not is_logged_in():
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    products = Addproduct.query.order_by(Addproduct.id.desc()).all()
    return render_template('admin/index.html', title='Admin Page', products=products)

@app.route('/admin/brands')
def brands():
#   if 'email' not in session:
    if not is_logged_in():
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html', title="Brand Page", brands=brands)

@app.route('/admin/category')
def category():
#   if not is_logged_in():
    if 'username' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/category.html', title="Category Page", categories=categories)

@app.route('/admin/customer')
def customer():
#     # Đẩu tiên, kiểm tra để user login
#   if 'email' not in session:
    if not is_logged_in():
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    customers = Register.query.order_by(Register.id.desc()).all()
    return render_template('admin/customer.html', title='Customer Page', customers=customers)

@app.route('/admin/invoice')
def invoice():
    if not is_logged_in():
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    invoices = CustomerOrder.query.order_by(CustomerOrder.id.desc()).all()
    return render_template('admin/invoice.html', title='Invoice Page', invoices=invoices)


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm(request.form)
#     if request.method == 'POST' and form.validate():
#         hash_password = bcrypt.generate_password_hash(form.password.data)
#         user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hash_password)
#         db.session.add(user)
#         db.session.commit()
#         flash(f'Welcome  {form.name.data} Thank you for registering', 'success')
#         return redirect(url_for('login'))
#     return render_template('admin/register.html', form=form, title="Registration Page")

# @app.route('/login', methods=['GET','POST'])
# def login():
#     form = LoginForm(request.form)
#     if request.method == 'POST' and form.validate():
#         user = User.query.filter_by(email = form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             session['email'] = form.email.data
#             flash(f'Welcomne {form.email.data} You are logedin now', 'success')
#             return redirect(request.args.get('next') or url_for('admin'))
#         else:
#             flash('Wrong Password please try again', 'danger')
#
#     return render_template('admin/login.html', form=form, title='Login Page')


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField



# Dữ liệu mẫu về người dùng (admin)
admin_credentials = {'username': 'admin', 'password': 'adminpassword'}

# Hàm kiểm tra thông tin đăng nhập
def authenticate(username, password):
    return username == admin_credentials['username'] and password == admin_credentials['password']

# Hàm kiểm tra xem người dùng đã đăng nhập hay chưa
def is_logged_in():
    return 'username' in session

# Form đăng nhập sử dụng Flask-WTF
class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'required': True})
    password = PasswordField('Password', render_kw={'required': True})
    submit = SubmitField('Login')



# Route cho trang đăng nhập
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if authenticate(username, password):
            session['username'] = username
            flash(f'Welcomne {username} You are logedin now', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Wrong Password please try again', 'error')

    return render_template('admin/login_admin.html', form=form)

