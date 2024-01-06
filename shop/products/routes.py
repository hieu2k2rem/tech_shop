
from flask import render_template, redirect, url_for, flash, request, session, current_app
from shop import db, app, photos
from .models import Brand, Category, Addproduct
from .forms import Addproducts
import secrets, os

# Viết hàm để hiển thị navbar brand và categories
def barnds():
    barnds = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    return barnds

def categories():
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return categories




@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=8)
    return render_template('products/index.html', products=products, barnds=barnds(), categories=categories())

@app.route('/product/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html', product=product, barnds=barnds(), categories=categories())

@app.route('/brand/<int:id>')
def get_brand(id):
    get_brand = Brand.query.filter_by(id=id).first_or_404()
    page = request.args.get('page', 1, type=int)
    get_brand_prod = Addproduct.query.filter_by(brand=get_brand).paginate(page=page, per_page=4)
    return render_template('products/index.html', get_brand_prod=get_brand_prod, barnds=barnds(), categories=categories(), get_brand=get_brand)

@app.route('/category/<int:id>')
def get_cate(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cate_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=4)
    return render_template('products/index.html', get_cate_prod=get_cate_prod, categories=categories(), barnds=barnds(), get_cat=get_cat)

@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method=="POST":
        # ('brand') lấy từ name='brand' trong (input form) addbrand.html
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The Brand {getbrand} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addbrand'))

    return render_template('products/addbrand.html', brands='brands')

@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method=='POST':
        updatebrand.name = brand
        flash('Your brand has been updated', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html', title="Update Brand page", updatebrand=updatebrand)

@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(brand)
        db.session.commit()
        flash(f'The brand {brand.name} was deleted from your database', 'success')
        return redirect(url_for('admin'))
    flash(f"The brand {brand.name} can't be deleted", 'warning')
    return redirect(url_for('admin'))


@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if request.method=="POST":
        # category này là dữ liệu được nhập từ form addbrand (name="brand") (do không tạo forms)
        getcategory = request.form.get('category')
        cat = Category(name=getcategory)
        db.session.add(cat)
        flash(f'The Category {getcategory} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addcategory'))

    return render_template('products/addbrand.html')

@app.route('/updatecategory/<int:id>', methods=['GET', 'POST'])
def updatecategory(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method=='POST':
        updatecategory.name = category
        flash('Your category has been updated', 'success')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('products/updatebrand.html', title="Update Category page", updatecategory=updatecategory)


@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    category = Category.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(category)
        db.session.commit()
        flash(f'The category {category.name} was deleted from your database', 'success')
        return redirect(url_for('admin'))
    flash(f"The brand {category.name} can't be deleted", 'warning')
    return redirect(url_for('admin'))


@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addproducts(request.form)
    if request.method == 'POST':
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        desc = form.discription.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

        addpro = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors, desc=desc, brand_id =brand, category_id=category, image1=image1, image2=image2, image3=image3)
        db.session.add(addpro)
        flash(f'The product {name} has been added to your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('products/addproduct.html', title='Add Product Page', form=form, brands=brands, categories=categories)


@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Addproduct.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = Addproducts(request.form)
    if request.method == 'POST':
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.brand_id = brand
        product.category_id = category
        product.colors = form.colors.data
        product.desc = form.discription.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image1))
                product.image1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image2))
                product.image2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image3))
                product.image3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        db.session.commit()
        flash(f'Your product has been updated', 'success')
        return redirect (url_for('admin'))

    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.discription.data = product.desc

    return render_template('products/updateproduct.html', title='Update Product Page', form=form, brands=brands, categories=categories, product=product)

@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method=='POST':
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image3))
        except Exception as e:
            print(e)

        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} was deleted frpm your database', 'success')
        return redirect(url_for('admin'))
    flash('Cant delete the product', 'danger')
    return redirect(url_for('admin'))
