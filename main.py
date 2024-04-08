from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

class Base(DeclarativeBase):
  pass
# Create the extension
db = SQLAlchemy(model_class=Base)


app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
# initialize the app with the extension
db.init_app(app)

class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    
# Create table schema in the database. Requires application context.    
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    result = db.session.execute(db.select(Book).order_by(Book.title))
    all_books = result.scalars()
    return render_template('index.html', all_books = all_books)


@app.route("/add",  methods=["GET", "POST"])
def add():
    if request.method == 'POST':
        new_book = {
            'title': request.form['title'], 
            'author': request.form['author'],
            'rating': request.form['rating'],
        }
        new_book = Book(title=new_book['title'], author=new_book['author'], rating=new_book['rating']) #el id es opcional 
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html')

@app.route('/edit', methods=["GET", "POST"])
def edit():
    if request.method == 'POST':
        book_id = request.form['id']
        rating_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        rating_to_update.rating = request.form['rating']
        db.session.commit() 
        return redirect(url_for('home'))
    book_id = request.args.get('id')
    book_selected = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    return render_template('edit.html', book = book_selected) 

@app.route('/delete', methods=["GET", "POST"])
def delete():
    book_id = request.args.get('id')
    book_deleted = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    db.session.delete(book_deleted)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

