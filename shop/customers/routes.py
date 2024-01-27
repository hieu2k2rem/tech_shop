from flask import render_template, session, request, redirect, url_for, flash, current_app, make_response
from shop import app, db, photos, bcrypt, login_manager
from flask_login import login_required, current_user, logout_user, login_user
from .forms import CustomerRegisterForm, CustomerLoginForm
from .models import Register, CustomerOrder
import secrets
import os
from shop.admin.routes import is_logged_in
from shop.products.models import Addproduct

import stripe

from flask_mail import Mail, Message

# Tạo đối tượng Mail
mail = Mail(app)

# Cấu hình cho Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Thay bằng địa chỉ SMTP của bạn
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'admin@gmail.com'
app.config['MAIL_PASSWORD'] = 'admin'
app.config['MAIL_DEFAULT_SENDER'] = 'tech_shop@example.com'  # Địa chỉ email mặc định


buplishable_key ='pk_test_51OZDCUFQcGRedjIkYUpIDZs83d95c019OoSiLcGHXP6YGmpRWIZvmyAanLdRUiKXPnSFa9TOoEVYd46fT6ksPID00066PHkhku'
stripe.api_key ='sk_test_51OZDCUFQcGRedjIkL31s5wBLEZoHJB4l8DvmfYJ17vUodH6vX3Twp51yM9BvXQmnYiIumEoCZAYdGhcSHxusJkC500F38p1xrF'

@app.route('/payment',methods=['POST'])
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
      email=request.form['stripeEmail'],
      source=request.form['stripeToken'],
    )
    charge = stripe.Charge.create(
      customer=customer.id,
      description='Myshop',
      amount=amount,
      currency='usd',
    )
    orders =  CustomerOrder.query.filter_by(customer_id = current_user.id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return render_template('customer/thank.html')

@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.name.data, email=form.email.data, password=hash_password, country=form.country.data, state=form.state.data, city=form.city.data, contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customerLogin'))

    return render_template('customer/register.html', form=form)


@app.route('/customer/login', methods=['GET','POST'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are login now!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('incorrect email or password', 'danger')
        return redirect(url_for('customerLogin'))
    return render_template('customer/login.html', form=form)

@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))

def updateshoppingcart():
    for key, shopping in session['Shoppingcart'].items():
        session.modified = True
        del shopping['image']
        del shopping['colors']
    return updateshoppingcart


@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshoppingcart
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully', 'success')
            return redirect(url_for('orders', invoice=invoice))
        except Exception as e:
            print(e)
            flash('Some thing went wrong while get order', 'danger')
            return redirect(url_for('getCart'))

def send_order_email(recipient, invoice, subTotal, tax, grandTotal):
    # Tạo đối tượng Message
    msg = Message('Thông báo đơn hàng #' + invoice,
                  recipients=[recipient],
                  sender=app.config['MAIL_DEFAULT_SENDER'])

    # Nội dung email
    msg.body = f'''
    Cảm ơn bạn đã đặt hàng!

    Đơn hàng của bạn có mã hóa đơn #{invoice} đã được thanh toán thành công.

    Tổng cộng: ${grandTotal}
    (Subtotal: ${subTotal}, Tax: ${tax})

    Cảm ơn bạn đã mua sắm tại cửa hàng của chúng tôi!
    '''

    # Gửi email
    mail.send(msg)

@app.route('/ordes/<invoice>')
def orders(invoice):
    if current_user.is_authenticated:
        subTotal = 0
        grandTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount'] / 100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))
    else:
        return redirect(url_for('customerLogin'))

    # Gửi email thông báo đơn hàng
    # send_order_email(customer.email, invoice, subTotal, tax, grandTotal)


    return render_template('customer/order.html', invoice=invoice, tax=tax, subTotal=subTotal,grandTotal=grandTotal, customer=customer, orders=orders)





import pdfkit


@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method == "POST":
            customer = Register.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(
                CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount'] / 100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = float("%.2f" % (1.06 * subTotal))

            rendered = render_template('customer/pdf.html', invoice=invoice, tax=tax, grandTotal=grandTotal,
                                       customer=customer, orders=orders)

            # Đường dẫn đến wkhtmltopdf
            wkhtmltopdf_path = r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'

            # Cấu hình pdfkit với đường dẫn wkhtmltopdf
            pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

            # Sử dụng cấu hình khi tạo PDF từ chuỗi HTML
            pdf = pdfkit.from_string(rendered, False, configuration=pdfkit_config)

            response = make_response(pdf)
            response.headers['content-Type'] = 'application/pdf'
            response.headers['content-Disposition'] = 'inline; filename=' + invoice + '.pdf'
            return response

    return redirect(url_for('orders'))






@app.route('/admin/deletecustomer/<int:id>', methods=['POST'])
def deletecustomer(id):
    if not is_logged_in():
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    customer = Register.query.get_or_404(id)
    if request.method == 'POST':
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + customer.profile))
        except Exception as e:
            print(e)

        db.session.delete(customer)
        db.session.commit()
        flash(f'The product {customer.name} was deleted from your database', 'success')
        return redirect(url_for('customer'))
    flash('Cant delete the customer', 'danger')
    return redirect(url_for('customer'))

@app.route('/admin/delete_all_products', methods=['POST'])
def delete_all_customers():
    if not is_logged_in():
        flash('Please login first', 'danger')
        return redirect(url_for('login'))

    # Xóa toàn bộ customer từ cơ sở dữ liệu
    try:
        Register.query.delete()
        db.session.commit()
        flash('All customers deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting customers: {str(e)}', 'danger')

    return redirect(url_for('customer'))


# Trang admin: Search customer theo name, username, email, address
@app.route('/admin/admin_result_customer')
def customer_result():

    searchword = request.args.get('q_customer')
    customers = Register.query.filter(
        Register.name.icontains(searchword) | Register.username.icontains(searchword)
        | Register.email.icontains(searchword) | Register.address.icontains(searchword))
    return render_template('admin/admin_result_customer.html', customers=customers)




# Trang xóa invoice của Admin
@app.route('/admin/deleteproduct/<int:id>', methods=['POST'])
def deleteinvoice(id):
    if not is_logged_in():
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    invoice = CustomerOrder.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(invoice)
        db.session.commit()
        flash(f'The product {invoice.invoice} was deleted frpm your database', 'success')
        return redirect(url_for('admin'))
    flash('Cant delete the invoice', 'danger')
    return redirect(url_for('admin'))

# Trang admin: Search invoice theo invoice
@app.route('/admin/admin_result_invoice')
def invoice_result():

    searchword = request.args.get('q_invoice')
    invoices = CustomerOrder.query.filter(
        CustomerOrder.invoice.contains(searchword))
    return render_template('admin/admin_result_invoice.html', invoices=invoices)


@app.route('/admin/delete_all_invoices', methods=['POST'])
def delete_all_invoices():
    if not is_logged_in():
        flash('Please login first', 'danger')
        return redirect(url_for('login'))

    # Xóa toàn bộ invoice từ cơ sở dữ liệu
    try:
        CustomerOrder.query.delete()
        db.session.commit()
        flash('All invoices deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting invoices: {str(e)}', 'danger')

    return redirect(url_for('invoice'))


