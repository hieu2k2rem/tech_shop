from flask import redirect, render_template, url_for, flash, request, session, current_app
from shop import db, app
from shop.products.models import Addproduct
from shop.products.routes import barnds, categories
import json


def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@app.route('/addcart', methods=['POST'])
def AddCart():
    # Trước tiên, nó cố gắng lấy các thông tin từ request như product_id, quantity, và colors từ form đã gửi.
    # Sau đó, nó dùng product_id để truy vấn thông tin sản phẩm từ cơ sở dữ liệu(assumedly SQLAlchemy,
    # với Addproduct.query.filter_by(id=product_id).first()). Nếu các thông tin cần thiết được nhận và request method là POST, nó tạo một dictionary
    # DictItems chứa thông tin sản phẩm dưới dạng một dictionary Python. Sau đó, nếu session đã có giỏ hàng('Shoppingcart'),
    # nó in ra giỏ hàng hiện tại, ngược lại, nó tạo một giỏ hàng mới và chuyển hướng đến trang trước đó(request.referrer).
    # Mọi lỗi trong quá trình này sẽ được in ra console để debugging. Cuối cùng, sau mỗi quá trình, nó luôn chuyển hướng người dùng đến trang trước đó(request.referrer).
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        colors = request.form.get('colors')
        product = Addproduct.query.filter_by(id=product_id).first()
        if product_id and quantity and colors and request.method == "POST":
            DictItems = {product_id:{'name': product.name, 'price': product.price, 'discount': product.discount,
                                     'color': colors, 'quantity': quantity, 'image':product.image1, 'colors': product.colors}}

            # Kiểm tra xem 'Shoppingcart' có trong session không, sau đó kiểm tra xem product_id cso trong session['Shoppingcart'] hay không
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1

                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)


    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)

@app.route('/carts')
def getCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    subtotal = 0
    grandtotal = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount']/100) * float(product['price'])
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
        tax = ("%.2f" % (.06 * float(subtotal)))
        grandtotal = float("%.2f" % (1.06 * subtotal))

    return render_template('products/carts.html', tax=tax, grandtotal=grandtotal, barnds=barnds(), categories=categories())


@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('home'))
    except Exception as e:
        print(e)


@app.route('/updatecart/<int:code>', methods=['POST'])
def updateCart(code):
    if 'Shoppingcart' not in session and len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    item['color'] = color
                    flash('Item is updated')
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCart'))


@app.route('/deletecart/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session and len(session['Shopppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))



@app.route('/clearcart')
def clearCart():
    try:
        # Không dùng cách này để clear session, vì như này sẽ xóa hết tất cả session,
        # session chúng ta muốn xóa chỉ là 'Shoppingcart'
        # session.clear()

        session.pop('Shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)


