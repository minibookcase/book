from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

# Load the data from the Excel file
def load_books():
    df = pd.read_excel('books_info_output.xlsx', dtype=str)  # 強制所有欄位為字符串格式
    return df.to_dict('records')

# Save the data back to the Excel file
def save_books_to_excel(books):
    df = pd.DataFrame(books)
    df = df.astype(str)  # 將所有數據轉換為字符串格式
    df.to_excel('books_info_output.xlsx', index=False)

@app.route('/')
def index():
    books = load_books()
    return render_template('index.html', books=books)


@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    if request.method == 'POST':
        borrower = request.form.get('borrower')
        isbn = request.form.get('isbn')
        books = load_books()
        
        for book in books:
            if book['ISBN'] == isbn and book['借閱狀態'] == '在架上':
                book['借閱狀態'] = '已借出'
                book['借閱人'] = borrower
                save_books_to_excel(books)
                return render_template('borrow.html', books=books, success_message="借閱成功！")
        return render_template('borrow.html', books=books, error_message="未找到該ISBN的書籍或書籍已借出！")
    books = load_books()
    return render_template('borrow.html', books=books)

@app.route('/return', methods=['GET', 'POST'])
def return_book():
    books = load_books()
    if request.method == 'POST':
        isbn = request.form.get('isbn')
        if isbn:
            for book in books:
                if book['ISBN'] == isbn and book['借閱狀態'] == '已借出':
                    book['借閱狀態'] = '在架上'
                    book['借閱人'] = ''
                    save_books_to_excel(books)
                    return render_template('return.html', books=books, success_message="歸還成功！")
            return render_template('return.html', books=books, error_message="未找到該ISBN的借出書籍！")
        
        query = request.form.get('isbn') or request.form.get('book_name') or request.form.get('borrower')
        
        if 'search' in request.form:
            filtered_books = [book for book in books if query.lower() in str(book['ISBN']).lower() or (book['借閱人'] and query.lower() in str(book['借閱人']).lower())]
            return render_template('return.html', books=filtered_books)
        
        elif 'return' in request.form:
            selected_books = request.form.getlist('selected_books')
            for book in books:
                if book['ISBN'] in selected_books:
                    book['借閱狀態'] = '在架上'
                    book['借閱人'] = ''
            save_books_to_excel(books)
            return redirect(url_for('index'))
    
    return render_template('return.html', books=books)

@app.route('/search', methods=['GET', 'POST'])
def search():
    books = load_books()
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()

        if isbn:
            books = [book for book in books if isbn.lower() in book['ISBN'].lower()]
        elif title:
            books = [book for book in books if title.lower() in book['書名'].lower()]

    return render_template('search.html', books=books)

@app.route('/borrowed_list')
def borrowed_list():
    books = load_books()
    borrowed_books = [book for book in books if book['借閱狀態'] == '已借出']
    return render_template('borrowed_list.html', books=borrowed_books)


if __name__ == '__main__':
    app.run(debug=True)
