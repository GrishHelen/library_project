import datetime
import sqlite3
import os
import urllib
from collections import namedtuple
from flask import Flask, render_template, redirect, url_for, request, g
from data.forms import NewTeacher, NewStudent, TakeBook, GiveBook, NewBook
from data.db_session import create_session, global_init

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
PROFS = {"dir": "Директор", "zamdir": "Заместитель директора", "bibl": "Педагог-библиотекарь",
         "extra": "Организатор дополнительного образования", "prim": "Учитель начальных классов",
         "vospit": "Воспитатель", "speech": "Логопед", "psyco": "Педагог-психолог", "izo": "Учитель ИЗО",
         "music": "Учитель музыки", "mxk": "Учитель МХК", "obj": "Учитель ОБЖ", "pe": "Учитель физкультуры",
         "math": "Учитель математики", "inf": "Учитель информатики", "phys": "Учитель физики",
         "ruslit": "Учитель русского языка и литературы", "rus": "Учитель русского языка",
         "geogr": "Учитель географии", "bio": "Учитель биологии", "chem": "Учитель химии",
         "histobch": "Учитель истории и обществознания", "obch": "Учитель обществознания", "hist": "Учитель истории",
         "eng": "Учитель английского языка", "french": "Учитель французского языка", "student": "Ученик",
         "latin": "Учитель латинского языка", "german": "Учитель немецкого языка", "other": "Другое"}
Message = namedtuple('Message', "id author name subject date yeartown number quantity price notes clas "
                                "decomission numberinlist publisher sum set_1 consignment code datecon")
messages = []
found = []
M = tuple()
database = 'BD2.db'  # BD2.db - учебная литература, BD1.db - удожественная литература
V = 0  # не трогать. это для добавления книг (проблема со сканером штрих-кода)


@app.route('/index')
@app.route("/", methods=["GET"])
def index():
    global database
    a = list(map(int, request.args.getlist('a')))
    x = [-1, f'{len(a)} шт.', 0, 0]
    con = sqlite3.connect(database)
    cursoro = con.cursor()
    show_all = [x] + list(cursoro.execute('SELECT * FROM books').fetchall())
    ask = [False, False]
    for ind in a:
        i = list(show_all[ind])
        i[7] = str(i[7]).strip()
        i[14] = str(i[14]).strip()
        if i[7] != '':
            x[2] += int(i[7])
        else:
            ask[0] = True
        if i[14] != '':
            x[3] += float(i[14])
        else:
            ask[1] = True
    if ask[0]:
        x[2] = str(x[2]) + ' ?'
    if ask[1]:
        x[3] = str(x[3]) + ' ?'
    con.close()
    return render_template("index.html", show_all=show_all, db=database, checked=a)


@app.route("/db_hudoz", methods=["GET"])
def db_hudoz():
    global database
    database = 'BD1.db'
    return redirect(url_for("index"))


@app.route("/db_ucheb", methods=["GET"])
def db_ucheb():
    global database
    database = 'BD2.db'
    return redirect(url_for("index"))


@app.route("/find", methods=["GET"])
def find():
    return render_template("find.html", found=found, db=database)


@app.route("/addbook", methods=["GET"])
def adbook():
    global V
    V = 0
    slovar = {'author': '', 'name': '', 'subject': '', 'date': '', 'yeartown': '', 'number': '', 'quantity': '',
              'price': '', 'notes': '', 'clas': '', 'decomission': '', 'numberinlist': '', 'publisher': '',
              'set_1': '', 'consignment': '', 'code': '', 'datecon': ''}
    return render_template("addbook.html", messages=messages, db=database, s=slovar)


@app.route("/deletebook", methods=["GET"])
def deletebook():
    global database, V
    V = 0
    con = sqlite3.connect(database)
    cursoro = con.cursor()
    table = cursoro.execute('SELECT * FROM books').fetchall()
    con.close()
    return render_template("deletebook.html", table=table, db=database)


@app.route("/change", methods=["GET"])
def change():
    global changing, database
    con = sqlite3.connect(database)
    cursoro = con.cursor()
    changing = cursoro.execute('SELECT * FROM books').fetchall()
    con.close()
    return render_template("change.html", changing=changing, db=database)


@app.route("/error", methods=["GET"])
def error():
    global database
    return render_template('error.html', M=M, db=database)


@app.route("/add_message", methods=["GET", "POST"])
def add_message():
    global database
    slovar = {}
    author = request.form["author"]
    slovar["author"] = author
    name = request.form["name"]
    slovar["name"] = name
    subject = request.form["subject"]
    slovar["subject"] = subject
    date = request.form["date"]
    slovar["date"] = date
    yeartown = request.form["yeartown"]
    slovar["yeartown"] = yeartown
    number = request.form["number"]
    slovar["number"] = number
    quantity = request.form["quantity"]
    slovar["quantity"] = quantity
    price = request.form["price"]
    slovar["price"] = price
    notes = request.form["notes"]
    slovar["notes"] = notes
    clas = request.form["clas"]
    slovar["clas"] = clas
    decomission = request.form["decomission"]
    slovar["decomission"] = decomission
    numberinlist = request.form["numberinlist"]
    slovar["numberinlist"] = numberinlist
    publisher = request.form["publisher"]
    slovar["publisher"] = publisher
    set_1 = request.form["set_1"]
    slovar["set_1"] = set_1
    consignment = request.form["consignment"]
    slovar["consignment"] = consignment
    datecon = request.form["datecon"]
    slovar["datecon"] = datecon
    try:
        sum = int(quantity) * float(price)
    except Exception:
        sum = ''
        slovar['sum'] = sum

    code = request.form["code"]
    try:
        code = int(code)
        url = f'https://barcode.tec-it.com/barcode.ashx?data={code}&code=&multiplebarcodes=false&' \
              f'translate-esc=true&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&' \
              f'bgcolor=%23ffffff&codepage=Default&qunit=Mm&quiet=0'
        filename = f'book_codes/{code}.jpg'
        img = urllib.request.urlopen(url).read()
        with open(filename, 'wb') as file:
            file.write(img)
    except Exception:
        pass
    slovar['code'] = code

    con = sqlite3.connect(database)
    cursoro = con.cursor()
    id = sorted(list(cursoro.execute('SELECT id FROM books').fetchall()))[-1][0] + 1

    usual_publishers = list(set(cursoro.execute('SELECT publisher FROM books').fetchall()))
    cc = set([i[0] for i in list(cursoro.execute('SELECT code from books').fetchall())])
    if str(code).strip() != '' and code is not None and int(code) in cc:
        return render_template("addbook.html", messages=messages, db=database, s=slovar,
                               wrong='Книга с таким штрих-кодом уже есть в базе данных')
    if (publisher,) in usual_publishers:
        messages.append(Message(id, author, name, subject, date, yeartown, number, quantity, price, notes, clas,
                                decomission, numberinlist, publisher, sum, set_1, consignment, code, datecon))
        cursoro.execute('INSERT INTO books (id, author, name, subject, date, yeartown, number, quantity, price, '
                        'notes, clas, decomission, numberinlist, publisher, sum, set_1, consignment, code, datecon) '
                        'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        tuple(Message(id, author, name, subject, date, yeartown, number, quantity, price, notes, clas,
                                      decomission, numberinlist, publisher, sum, set_1, consignment, code, datecon)))
        con.commit()
        con.close()
        return redirect(url_for("adbook"))
    else:
        global M
        con.close()
        M = tuple(Message(id, author, name, subject, date, yeartown, number, quantity, price, notes, clas,
                          decomission, numberinlist, publisher, sum, set_1, consignment, code, datecon))
        return redirect(url_for('error'))


@app.route("/yes_add", methods=["POST"])
def yes_add():
    global M, messages, database
    if str(M[2]).strip() == '':
        return redirect(url_for("adbook"))
    messages.append(Message(M[0], M[1], M[2], M[3], M[4], M[5], M[6], M[7], M[8], M[9], M[10], M[11], M[12], M[13],
                            M[14], M[15], M[16], M[17], M[18]))
    con = sqlite3.connect(database)
    cursoro = con.cursor()
    cursoro.execute('INSERT INTO books (id, author, name, subject, date, yeartown, number, quantity, price, notes, '
                    'clas, decomission, numberinlist, publisher, sum, set_1, consignment, code, datecon) '
                    'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(M))
    con.commit()
    con.close()
    url = f'https://barcode.tec-it.com/barcode.ashx?data={M[17]}&code=&multiplebarcodes=false&' \
          f'translate-esc=true&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&' \
          f'bgcolor=%23ffffff&codepage=Default&qunit=Mm&quiet=0'
    filename = f'book_codes/{M[17]}.jpg'
    img = urllib.request.urlopen(url).read()
    with open(filename, 'wb') as file:
        file.write(img)
    return redirect(url_for("adbook"))


@app.route("/delete", methods=["POST"])
def delete():
    global table, database
    number = request.form["number"]
    con = sqlite3.connect(database)
    cursoro = con.cursor()
    if "-" in number:
        p = number.split("-")
        for k in range(int(p[0]), int(p[1]) + 1):
            cursoro.execute("DELETE FROM books WHERE id={}".format(str(k)))
    else:
        cursoro.execute("DELETE FROM books WHERE id={}".format(number))
    con.commit()
    table = cursoro.execute('SELECT * FROM books').fetchall()
    con.close()
    return redirect(url_for("deletebook"))


@app.route('/dell/<number>', methods=['GET', 'POST'])
def dell(number):
    global table, database, V
    con = sqlite3.connect(database)
    cursoro = con.cursor()
    if "-" in number:
        p = number.split("-")
        for k in range(int(p[0]), int(p[1]) + 1):
            cursoro.execute("DELETE FROM books WHERE id={}".format(str(k)))
    else:
        cursoro.execute("DELETE FROM books WHERE id={}".format(number))
    con.commit()
    table = cursoro.execute('SELECT * FROM books').fetchall()
    con.close()
    return deletebook()


@app.route("/change_it", methods=["POST"])
def change_it():
    global changing, database, V
    author = request.form["author"]
    name = request.form["name"]
    subject = request.form["subject"]
    date = request.form["date"]
    yeartown = request.form["yeartown"]
    number = request.form["number"]
    quantity = request.form["quantity"]
    price = request.form["price"]
    notes = request.form["notes"]
    clas = request.form["clas"]
    decomission = request.form["decomission"]
    numberinlist = request.form["numberinlist"]
    publisher = request.form["publisher"]
    set_1 = request.form["set_1"]
    consignment = request.form["consignment"]
    code = request.form["code"]
    id_book = int(request.form["id"])
    datecon = request.form["datecon"]

    con = sqlite3.connect(database)
    cursoro = con.cursor()

    if author:
        cursoro.execute('UPDATE books SET author = "{}" where id = {}'.format(author, id_book))
    if name:
        cursoro.execute('UPDATE books SET name = "{}" where id = {}'.format(name, id_book))
    if subject:
        cursoro.execute('UPDATE books SET subject = "{}" where id = {}'.format(subject, id_book))
    if date:
        cursoro.execute('UPDATE books SET date = {} where id = {}'.format(date, id_book))
    if yeartown:
        cursoro.execute('UPDATE books SET yeartown = "{}" where id = {}'.format(yeartown, id_book))
    if number:
        cursoro.execute('UPDATE books SET number = "{}" where id = {}'.format(number, id_book))
    if quantity:
        cursoro.execute('UPDATE books SET quantity = {} where id = {}'.format(int(quantity), id_book))
    if price:
        cursoro.execute('UPDATE books SET price = {} where id = {}'.format(float(price), id_book))
    if notes:
        cursoro.execute('UPDATE books SET notes = "{}" where id = {}'.format(notes, id_book))
    if clas:
        cursoro.execute('UPDATE books SET clas = "{}" where id = {}'.format(clas, id_book))
    if decomission:
        cursoro.execute('UPDATE books SET decomission = "{}" where id = {}'.format(decomission, id_book))
    if numberinlist:
        cursoro.execute('UPDATE books SET numberinlist = "{}" where id = {}'.format(numberinlist, id_book))
    if publisher:
        cursoro.execute('UPDATE books SET publisher = "{}" where id = {}'.format(publisher, id_book))
    if set_1:
        cursoro.execute('UPDATE books SET set_1 = "{}" where id = {}'.format(set_1, id_book))
    if consignment:
        cursoro.execute('UPDATE books SET consignment = "{}" where id = {}'.format(consignment, id_book))
    if code:
        url = f'https://barcode.tec-it.com/barcode.ashx?data={code}&code=&multiplebarcodes=false&' \
              f'translate-esc=true&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&' \
              f'bgcolor=%23ffffff&codepage=Default&qunit=Mm&quiet=0'
        filename = f'book_codes/{code}.jpg'
        img = urllib.request.urlopen(url).read()
        with open(filename, 'wb') as file:
            file.write(img)
        cursoro.execute('UPDATE books SET code = "{}" where id = {}'.format(int(code), id_book))
    if datecon:
        cursoro.execute('UPDATE books SET datecon = "{}" where id = {}'.format(datecon, id_book))
    try:
        pr = float(cursoro.execute('SELECT price FROM books WHERE id={}'.format(id_book)).fetchone()[0])
        q = int(cursoro.execute('SELECT quantity FROM books WHERE id={}'.format(id_book)).fetchone()[0])
        cursoro.execute('UPDATE books SET sum = {} where id = {}'.format(pr * q, id_book))
    except Exception:
        pass
    con.commit()
    changing = cursoro.execute('SELECT * FROM books').fetchall()
    con.close()
    return render_template("change.html", changing=changing, messages=messages, db=database)


@app.route("/find_it", methods=["POST"])
def find_it():
    global found, database
    dict = {'id': 0, 'author': 1, 'name': 2, 'subject': 3, 'date': 4, 'yeartown': 5, 'number': 6, 'quantity': 7,
            'price': 8, 'notes': 9, 'class': 10, 'clas': 10, 'decomission': 11, 'numberlist': 12, 'publisher': 13,
            'sum set_1': 14,
            'consignment': 15, 'code': 16, 'datecon': 18}
    name = request.form["stolb"]
    typ = str(request.form["type"]).lower()
    name_1 = dict[name]
    con = sqlite3.connect(database)
    cursoro = con.cursor()
    all = cursoro.execute(f"SELECT * FROM books").fetchall()
    found = []
    for i in all:
        x = str(i[name_1]).lower()
        if x == typ or typ in x or x in typ:
            found.append(i)
        else:
            if x == typ:
                found.append(i)
    con.close()
    return redirect(url_for("find"))


@app.route('/giving', methods=['GET', 'POST'])
def giving():
    con = sqlite3.connect(database)
    cursoro = con.cursor()
    spisok = [list(i) for i in cursoro.execute('SELECT * from history').fetchall()]
    for sp in spisok:
        book = cursoro.execute(f'SELECT name from books WHERE code="{sp[1]}"').fetchall()
        if len(book) == 0:
            book = 'Не удалось найти книгу'
        else:
            book = book[0][0]
        sp.insert(2, book)
    con.close()
    cursoro = sqlite3.connect('people.db').cursor()
    for sp in spisok:
        fio = cursoro.execute(f'SELECT fio from numbers WHERE code="{sp[3]}"').fetchone()
        fio = sp[4].split('_')
        if fio[-1] == '-':
            fio.remove('-')
        fio = ' '.join(fio)
        sp[4] = fio
        sp[-1] = '.'.join(sp[-1].split('-')[::-1])
    return render_template('giving.html', db=database, history=spisok[::-1])


@app.route('/new_teacher', methods=['GET', 'POST'])
def new_teacher():
    form = NewTeacher()
    if request.method == "GET":
        return render_template('new_teacher.html', form=form, db=database, message='')
    if form.is_submitted():
        if str(form.father.data).strip() == '':
            form.father.data = '-'
        if str(form.surname.data).strip() == '':
            return render_template('new_teacher.html', form=form, db=database, message='Введите фамилию')
        if str(form.name.data).strip() == '':
            return render_template('new_teacher.html', form=form, db=database, message='Введите имя')
        if str(form.position.data).strip() == '':
            return render_template('new_teacher.html', form=form, db=database, message='Выберите должность')
        fio = form.surname.data + '_' + form.name.data + '_' + form.father.data
        id_new = form.name.data[0] + '.' + form.father.data[0] + '.' + form.surname.data + '_' + \
                 form.position.data
        code = form.code.data
        con = sqlite3.connect('people.db')
        cursoro = con.cursor()
        sp = list(cursoro.execute(f'SELECT * FROM numbers WHERE code="{code}"').fetchall())
        if len(sp) > 0:
            return render_template('new_teacher.html', form=form, db=database,
                                   message='Человек с таким номером пропускной карточки уже есть. '
                                           'Проверьте корректность введенных данных')
        sp = list(cursoro.execute('SELECT id FROM numbers WHERE id LIKE "{}%"'.format(id_new)).fetchall())
        if len(sp) == 1:
            id_new += '_1'
        elif len(sp) > 1:
            id_new += '_' + str(sorted([int(i.split('_')[-1]) for i in sp])[-1] + 1)
        cursoro.execute(f'INSERT INTO numbers (id, fio, position, code) '
                        f'VALUES ("{id_new}", "{fio}", "{form.position.data}", {code})')
        con.commit()
        con.close()
        url = f'https://barcode.tec-it.com/barcode.ashx?data={code}&code=&multiplebarcodes=false&' \
              f'translate-esc=true&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&' \
              f'bgcolor=%23ffffff&codepage=Default&qunit=Mm&quiet=0'
        filename = f'people_codes/{code}.jpg'
        img = urllib.request.urlopen(url).read()
        with open(filename, 'wb') as file:
            file.write(img)
        return redirect(f'/person_page/{code}')


@app.route('/new_student', methods=['GET', 'POST'])
def new_student():
    form = NewStudent()
    if request.method == "GET":
        return render_template('new_student.html', form=form, db=database, message='')
    if form.is_submitted():
        if str(form.father.data).strip() == '' or form.father.data is None:
            form.father.data = '-'
        if str(form.surname.data).strip() == '' or form.surname.data is None:
            return render_template('new_student.html', form=form, db=database, message='Введите фамилию')
        if str(form.name.data).strip() == '' or form.name.data is None:
            return render_template('new_student.html', form=form, db=database, message='Введите имя')
        if str(form.clas.data).strip() == '' or form.clas.data is None:
            return render_template('new_student.html', form=form, db=database,
                                   message='Введите, в каком Вы классе')
        fio = form.surname.data + '_' + form.name.data + '_' + form.father.data
        now = datetime.datetime.now()
        year = now.year
        if now.month >= 6:
            year += 1
        year -= int(form.clas.data)
        id_new = form.name.data[0] + '.' + form.father.data[0] + '.' + form.surname.data + '_' + \
                 str(year)
        code = form.code.data
        con = sqlite3.connect('people.db')
        cursoro = con.cursor()
        sp = list(cursoro.execute(f'SELECT * FROM numbers WHERE code="{code}"').fetchall())
        if len(sp) > 0:
            return render_template('new_teacher.html', form=form, db=database,
                                   message='Человек с таким номером пропускной карточки уже есть. '
                                           'Проверьте корректность введенных данных')
        sp = list(cursoro.execute('SELECT id FROM numbers WHERE id LIKE "{}%"'.format(id_new)).fetchall())
        if len(sp) == 1:
            id_new += '_1'
        elif len(sp) > 1:
            id_new += '_' + str(sorted([int(i.split('_')[-1]) for i in sp])[-1] + 1)
        cursoro.execute(f'INSERT INTO numbers (id, fio, position, code) '
                        f'VALUES ("{id_new}", "{fio}", "student", {code})')
        con.commit()
        con.close()
        url = f'https://barcode.tec-it.com/barcode.ashx?data={code}&code=&multiplebarcodes=false&' \
              f'translate-esc=true&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&' \
              f'bgcolor=%23ffffff&codepage=Default&qunit=Mm&quiet=0'
        filename = f'people_codes/{code}.jpg'
        img = urllib.request.urlopen(url).read()
        with open(filename, 'wb') as file:
            file.write(img)
        return redirect(f'/person_page/{code}')


@app.route('/give_book', methods=['GET', 'POST'])
def give_book():
    header = 'Выдать книгу'
    form = GiveBook()
    if request.method == 'GET':
        return render_template('take_give_book.html', form=form, db=database, message='', header=header)
    if form.is_submitted():
        if str(form.person_code.data).strip() == '' or form.person_code.data is None:
            return render_template('take_give_book.html', form=form, db=database,
                                   message='Введите номер пропусконой карточки человека')
        if str(form.book.data).strip() == '' or form.book.data is None:
            return render_template('take_give_book.html', form=form, db=database, message='Введите штрих-код книги')
        con = sqlite3.connect('people.db')
        cursoro = con.cursor()
        p = list(cursoro.execute(f'SELECT * FROM numbers WHERE code={form.person_code.data}').fetchall())
        if len(p) == 0:
            return render_template('take_give_book.html', form=form, db=database,
                                   message='Такого человека нет в базе данных')
        con = sqlite3.connect(database)
        cursoro = con.cursor()
        bo = list(cursoro.execute(f'SELECT * FROM books WHERE code={form.book.data}').fetchall())
        if len(bo) == 0:
            return render_template('take_give_book.html', form=form, db=database,
                                   message='Не удалось найти книгу в базе данных')
        fio = p[0][2]
        today = datetime.datetime.date(datetime.datetime.now())
        cursoro.execute(f'INSERT INTO history (person_fio, person_code, book, action, date) VALUES ("{fio}", '
                        f'{form.person_code.data}, "{form.book.data}", "выдать", "{today}")')
        con.commit()
        con.close()
        return redirect('/giving')


@app.route('/take_book', methods=['GET', 'POST'])
def take_book():
    header = 'Принять книгу'
    form = TakeBook()
    if request.method == 'GET':
        return render_template('take_give_book.html', form=form, db=database, message='', header=header)
    if form.is_submitted():
        if str(form.person_code.data).strip() == '' or form.person_code.data is None:
            return render_template('take_give_book.html', form=form, db=database,
                                   message='Введите номер пропусконой карточки человека')
        if str(form.book.data).strip() == '' or form.book.data is None:
            return render_template('take_give_book.html', form=form, db=database, message='Введите штрих-код книги')
        con = sqlite3.connect('people.db')
        cursoro = con.cursor()
        p = list(cursoro.execute('SELECT * FROM numbers WHERE code={}'.format(form.person_code.data)).fetchall())
        con.close()
        if len(p) == 0:
            return render_template('take_give_book.html', form=form, db=database,
                                   message='Такого человека нет в базе данных')
        con = sqlite3.connect(database)
        cursoro = con.cursor()
        bo = list(cursoro.execute(f'SELECT * FROM books WHERE code={form.book.data}').fetchall())
        if len(bo) == 0:
            return render_template('take_give_book.html', form=form, db=database,
                                   message='Не удалось найти книгу в базе данных')
        fio = p[0][2]
        today = datetime.datetime.date(datetime.datetime.now())
        cursoro.execute(f'INSERT INTO history (person_fio, person_code, book, action, date) '
                        f'VALUES ("{fio}", {form.person_code.data}, "{form.book.data}", "принять", "{today}")')
        con.commit()
        con.close()
        return redirect('/giving')


@app.route('/person_page/<pers_code>', methods=['GET', 'POST'])
def person_page(pers_code):
    con = sqlite3.connect('people.db')
    cursoro = con.cursor()
    p = cursoro.execute(f'SELECT * FROM numbers WHERE code={pers_code}').fetchall()
    con.close()
    if len(p) == 0:
        return render_template('any_error.html', err=f'Не удалось найти пользователя с кодом {pers_code}', db=database)
    id, pos, fio, code = p[0]
    position = PROFS[pos]
    fio = ' '.join(fio.split('_'))
    url = f'https://barcode.tec-it.com/barcode.ashx?data={code}&code=&multiplebarcodes=false&' \
          f'translate-esc=true&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&' \
          f'bgcolor=%23ffffff&codepage=Default&qunit=Mm&quiet=0'
    history = []
    con = sqlite3.connect('BD2.db')
    cursoro = con.cursor()
    spisok = [list(i) for i in cursoro.execute('SELECT * from history').fetchall()]
    for sp in spisok:
        if sp[2] != code:
            continue
        book = cursoro.execute(f'SELECT name from books WHERE code="{sp[1]}"').fetchall()
        if len(book) == 0:
            book = 'Не удалось найти книгу'
        else:
            book = book[0][0]
        sp.insert(2, book)
        sp[-1] = '.'.join(sp[-1].split('-')[::-1])
        history.append(sp)
    con.close()
    con = sqlite3.connect('BD1.db')
    cursoro = con.cursor()
    spisok = [list(i) for i in cursoro.execute('SELECT * from history').fetchall()]
    for sp in spisok:
        if sp[2] != code:
            continue
        book = cursoro.execute(f'SELECT name from books WHERE code="{sp[1]}"').fetchall()
        if len(book) == 0:
            book = 'Не удалось найти книгу'
        else:
            book = book[0][0]
        sp.insert(2, book)
        sp[-1] = '.'.join(sp[-1].split('-')[::-1])
        history.append(sp)
    history.sort(key=lambda i: -i[0])
    con.close()
    return render_template('person_page.html', id=id, position=position, fio=fio, code=code, img=url, giving=history,
                           db=database)


@app.route('/student_change/<pers_code>', methods=['GET', 'POST'])
def student_change(pers_code):
    con = sqlite3.connect('people.db')
    cursoro = con.cursor()
    p = list(cursoro.execute(f'SELECT * FROM numbers WHERE code={pers_code}').fetchall())
    if len(p) == 0:
        return render_template('any_error.html', err='Такого человека нет в базе данных')
    id, position, fio, code = p[0]
    if position != 'student':
        return redirect(f'/teacher_change/{pers_code}')

    form = NewStudent()
    if request.method == "GET":
        surname, name, father = fio.split('_')
        form.surname.data = surname
        form.name.data = name
        form.father.data = father
        form.code.data = code
        now = datetime.datetime.now()
        year = now.year
        if now.month >= 6:
            year += 1
        clas = year - int(id.split('_')[-1])
        form.clas.data = clas
        return render_template('new_student.html', form=form, db=database, message='')
    if request.method == "POST":
        if str(form.father.data).strip() == '' or form.father.data is None:
            form.father.data = '-'
        now = datetime.datetime.now()
        year = now.year
        if now.month >= 6:
            year += 1
        year -= int(form.clas.data)
        id = form.name.data[0] + '.' + form.father.data[0] + '.' + form.surname.data + '_' + str(year)
        fio = form.name.data + '_' + form.father.data + '_' + form.surname.data
        cursoro.execute(f"UPDATE numbers SET id='{id}', fio='{fio}', code={form.code.data} WHERE code={pers_code}")
        con.commit()
        con.close()
        if pers_code != form.code.data:
            os.remove(f'people_codes/{pers_code}.jpg')
            url = f'https://barcode.tec-it.com/barcode.ashx?data={form.code.data}&code=&multiplebarcodes=false&' \
                  f'translate-esc=true&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&' \
                  f'bgcolor=%23ffffff&codepage=Default&qunit=Mm&quiet=0'
            filename = f'people_codes/{form.code.data}.jpg'
            img = urllib.request.urlopen(url).read()
            with open(filename, 'wb') as file:
                file.write(img)
        return redirect(f'/person_page/{form.code.data}')


@app.route('/teacher_change/<pers_code>', methods=['GET', 'POST'])
def teacher_change(pers_code):
    con = sqlite3.connect('people.db')
    cursoro = con.cursor()
    p = list(cursoro.execute(f'SELECT * FROM numbers WHERE code={pers_code}').fetchall())
    if len(p) == 0:
        return render_template('any_error.html', err='Такого человека нет в базе данных', db=database)
    id, position, fio, code = p[0]
    if position == 'student':
        return redirect(f'/student_change/{pers_code}')

    form = NewTeacher()
    if request.method == "GET":
        id, position, fio, code = p[0]
        surname, name, father = fio.split('_')
        form.surname.data = surname
        form.name.data = name
        form.father.data = father
        form.code.data = code
        form.position.data = position

        return render_template('new_teacher.html', form=form, db=database, message='')
    if request.method == "POST":
        if str(form.father.data).strip() == '' or form.father.data is None:
            form.father.data = '-'
        id = form.name.data[0] + '.' + form.father.data[0] + '.' + form.surname.data + '_' + form.position.data
        fio = form.name.data + '_' + form.father.data + '_' + form.surname.data
        cursoro.execute(f"UPDATE numbers SET id='{id}', fio='{fio}', code={form.code.data}, "
                        f"position='{form.position.data}' WHERE code={pers_code}")
        con.commit()
        con.close()
        if pers_code != form.code.data:
            os.remove(f'people_codes/{pers_code}.jpg')
            url = f'https://barcode.tec-it.com/barcode.ashx?data={form.code.data}&code=&multiplebarcodes=false&' \
                  f'translate-esc=true&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&' \
                  f'bgcolor=%23ffffff&codepage=Default&qunit=Mm&quiet=0'
            filename = f'people_codes/{form.code.data}.jpg'
            img = urllib.request.urlopen(url).read()
            with open(filename, 'wb') as file:
                file.write(img)
        return redirect(f'/person_page/{form.code.data}')


@app.route('/all_users', methods=['GET'])
def all_users():
    con = sqlite3.connect('people.db')
    cursoro = con.cursor()
    p = list(cursoro.execute('SELECT * FROM numbers').fetchall())
    con.close()
    users = []
    for i in p:
        a = [i[0], PROFS[i[1]]]
        a.extend(i[2].split('_'))
        users.append(a)
        if i[1] == 'student':
            now = datetime.datetime.now()
            year = now.year
            if now.month >= 6:
                year += 1
            year -= int(i[0].split('_')[-1])
            a.append(year)
        else:
            a.append('')
        a.append(i[-1])
    return render_template('all_users.html', db=database, users=users)


@app.route('/book_page/<book_code>', methods=['GET', 'POST'])
def book_page(book_code):
    if str(book_code).strip() in ['None', '']:
        return render_template('any_error.html', db=database, err=f'Не удалось перейти на страницу книги. '
                                                                  f'У этой книги нет штрих-кода')
    cursoro = sqlite3.connect(database).cursor()
    p = list(cursoro.execute(f"SELECT * FROM books WHERE code={book_code}").fetchall())
    url = f'https://barcode.tec-it.com/barcode.ashx?data={book_code}&code=&multiplebarcodes=false&' \
          f'translate-esc=true&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&' \
          f'bgcolor=%23ffffff&codepage=Default&qunit=Mm&quiet=0'
    if len(p) == 0:
        if database == 'BD2.db':
            db = 'Учебная литература'
        else:
            db = 'Художественная литература'
        return render_template('any_error.html', db=database, err=f'Не удалось найти книгу с штрих-кодом {book_code} '
                                                                  f'в категории "{db}". Возможно, она не стоит на учете'
                                                                  f' или относится к другой категории.')
    p = list(p[0])
    for i in range(len(p)):
        if p[i] is None:
            p[i] = ''

    con = sqlite3.connect(database)
    cursoro = con.cursor()
    spisok = [list(i)[2:] for i in cursoro.execute(f'SELECT * from history WHERE book={book_code}').fetchall()]
    for i in range(len(spisok)):
        spisok[i][-1] = '.'.join(spisok[i][-1].split('-')[::-1])
        fio = spisok[i][1].split('_')
        if '-' in fio:
            fio.remove('-')
        spisok[i][1] = ' '.join(fio)
    con.close()
    spisok.sort(key=lambda i: -i[0])
    con.close()

    return render_template('book_page.html', message=p, db=database, img=url, giving=spisok)


@app.route('/book_change/<book_id>', methods=['GET', 'POST'])
def book_change(book_id):
    book_id = int(book_id)
    con = sqlite3.connect(database)
    cursoro = con.cursor()
    p = cursoro.execute(f'SELECT * FROM books WHERE id={book_id}').fetchall()
    con.close()
    if len(list(p)) == 0:
        if database == 'BD1.db':
            return render_template('any_error.html', err=f'Не удалось найти книгу с id={book_id} в базе данных '
                                                         f'Художественной литературы', db=database)
        else:
            return render_template('any_error.html', err=f'Не удалось найти книгу с id={book_id} в базе данных '
                                                         f'Учебной литературы', db=database)
    form = NewBook()
    p = p[0]
    if request.method == "GET":
        form.author.data = p[1]
        form.name.data = p[2]
        form.subject.data = p[3]
        form.clas.data = p[10]
        form.yeartown.data = p[5]
        form.publisher.data = p[13]
        form.number.data = p[6]
        form.date.data = p[4]
        form.quantity.data = p[7]
        form.price.data = p[8]
        form.sum.data = p[14]
        form.consignment.data = p[16]
        form.datecon.data = p[18]
        form.numberinlist.data = p[12]
        form.set_1.data = p[15]
        form.decomission.data = p[11]
        form.notes.data = p[9]
        form.code.data = p[17]
        return render_template('new_book.html', form=form, db=database, message='')
    if request.method == "POST":
        try:
            sum = int(form.quantity.data) * float(form.price.data)
        except Exception:
            sum = ''
        form.sum.data = sum
        con = sqlite3.connect(database)
        cursoro = con.cursor()
        cursoro.execute(f"UPDATE books SET author='{form.author.data}', name='{form.name.data}', "
                        f"subject='{form.subject.data}', clas='{form.clas.data}', yeartown='{form.yeartown.data}', "
                        f"publisher='{form.publisher.data}', number='{form.number.data}', date='{form.date.data}', "
                        f"quantity='{form.quantity.data}', price='{form.price.data}', sum='{form.sum.data}', "
                        f"consignment='{form.consignment.data}', datecon='{form.datecon.data}', "
                        f"numberinlist='{form.numberinlist.data}', set_1='{form.set_1.data}', "
                        f"decomission='{form.decomission.data}', notes='{form.notes.data}', code='{form.code.data}' "
                        f"WHERE id={book_id}")
        con.commit()
        con.close()
        if str(p[17]) != str(form.code.data):
            if str(p[17]).strip() not in ['None', '']:
                 os.remove(f'book_codes/{p[17]}.jpg')
            if str(form.code.data).strip() not in ['None', '']:
                url = f'https://barcode.tec-it.com/barcode.ashx?data={form.code.data}&code=&multiplebarcodes=false&' \
                      f'translate-esc=true&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=%23000000&' \
                      f'bgcolor=%23ffffff&codepage=Default&qunit=Mm&quiet=0'
                filename = f'book_codes/{form.code.data}.jpg'
                img = urllib.request.urlopen(url).read()
                with open(filename, 'wb') as file:
                    file.write(img)
        if str(form.code.data).strip() not in ['None', '']:
            return redirect(f'/book_page/{form.code.data}')
        else:
            return redirect('/change')


if __name__ == "__main__":
    app.run(host='127.0.0.1')
