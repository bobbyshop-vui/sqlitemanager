import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import os
app = Flask(__name__)

# Thư mục chứa các file SQLite
DB_FOLDER = 'databases'

# Tạo thư mục databases nếu chưa tồn tại
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

@app.route('/delete_db/<filename>', methods=['POST'])
def delete_db(filename):
    # Đường dẫn tới cơ sở dữ liệu
    db_path = os.path.join(DB_FOLDER, filename)

    # Kiểm tra nếu file không tồn tại
    if not os.path.exists(db_path):
        return f"Database {filename} not found.", 404

    try:
        # Xóa file cơ sở dữ liệu
        os.remove(db_path)
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error deleting database: {str(e)}", 500
@app.route('/')
def index():
    # Liệt kê các file SQLite trong thư mục
    files = [f for f in os.listdir(DB_FOLDER) if f.endswith('.sqlite')]
    return render_template('index.html', files=files)
@app.route('/db/<filename>')
def view_db(filename):
    # Đường dẫn thực tế tới cơ sở dữ liệu SQLite
    db_path = os.path.join(DB_FOLDER, filename)

    # Tính toán đường dẫn tuyệt đối của thư mục chứa ứng dụng
    absolute_base_path = os.path.abspath(os.path.join(os.getcwd(), DB_FOLDER))

    # Tạo đường dẫn tuyệt đối của file cơ sở dữ liệu
    fixed_path = os.path.join(absolute_base_path, filename)

    # Kiểm tra nếu file không tồn tại
    if not os.path.exists(db_path):
        return f"Database {filename} not found.", 404

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Lấy danh sách các bảng trong cơ sở dữ liệu
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Lấy thông tin về các cột của từng bảng
    table_info = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        table_info[table_name] = columns

    # Lấy các bản ghi của từng bảng
    rows = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT * FROM {table_name}")
        rows[table_name] = cursor.fetchall()

    conn.close()

    # Trả về template và truyền đường dẫn cố định của file cơ sở dữ liệu
    return render_template('view_db.html', filename=filename, db_path=fixed_path, tables=tables, table_info=table_info, rows=rows)
@app.route('/run_sql/<filename>', methods=['GET', 'POST'])
def run_sql(filename):
    db_path = os.path.join(DB_FOLDER, filename)
    if request.method == 'POST':
        query = request.form['query']
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            return redirect(url_for('view_db', filename=filename))
        except Exception as e:
            error = str(e)
            return render_template('view_db.html', filename=filename, error=error)
    return redirect(url_for('view_db', filename=filename))

@app.route('/create_db', methods=['GET', 'POST'])
def create_db():
    if request.method == 'POST':
        db_name = request.form['db_name']
        if db_name:
            # Tạo file SQLite mới
            db_path = os.path.join(DB_FOLDER, db_name + '.sqlite')
            if not os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                conn.close()
                return redirect(url_for('index'))
            else:
                error = "Database already exists!"
                return render_template('create_db.html', error=error)
    return render_template('create_db.html')

if __name__ == '__main__':
    app.run(debug=True)
