import xlsxwriter
import xlrd
import sqlite3

name = "Учебники с накладными 2020-21 учгод.xlsx"  # input("Введите название файла: ")
name_of_BD = 'BDnew2018.db'  # input("Введите название базы данных: ")
# print("В базу данных занесены следующие строки: ")
book = xlrd.open_workbook(name)
# print(book.sheet_names())
sheet = book.sheet_by_index(0)  # номер листа
num_rows = sheet.nrows
num_col = sheet.ncols
author = None
name = None
subject = None
date = None
yeartown = None
number = None
quantity = None
price = None
notes = None
clas = None
decomission = None
numberinlist = None
publisher = None
set_1 = None
consignment = None
summ=None
# sum="Общая сумма"
for col in range(num_col):
    val = sheet.cell(0, col).value
    if val == "Автор":
        author = col
    elif val == "Учебник":
        name = col
    elif val == "Предмет":
        subject = col
    elif val =="Дата":
        date = col
    elif val == "Год издания":  # "Год и город"
        yeartown = col
    elif val == "Номер издания":
        number = col
    elif val == "Количество (шт./компл.)":
        quantity = col
    elif val == "Цена за ед. (шт./компл.) с НДС":  # "Цена"
        price = col
    elif val == "Примечания":
        notes = col
    elif val == "Класс":
        clas = col
    elif val == "Списание":
        decomission = col
    elif val == "Инвентарный номер":  # "Номер в списке"
        numberinlist = col
    elif val == "Издательство":
        publisher = col
    elif val == "Комплект штука":
        set_1 = col
    elif val == "Накладные":
        consignment = col
    elif val=="Сумма с НДС":
        summ=col
con = sqlite3.connect(name_of_BD)
cursoro = con.cursor()

for row in range(1, num_rows):
    M = [" "] * 17
    M[0] = int(cursoro.execute('SELECT id FROM books').fetchall()[-1][-1]) + 1
    if author != None:
        M[1] = str(sheet.cell(row, author).value)
    if name != None:
        M[2] = str(sheet.cell(row, name).value)
    if subject != None:
        M[3] = str(sheet.cell(row, subject).value)
    if consignment!=None:#if date != None:
        M[4] = str(sheet.cell(row, consignment).value)[-10:]
    if yeartown != None:
        M[5] = str(sheet.cell(row, yeartown).value)
    if number != None:
        M[6] = str(sheet.cell(row, number).value)
    if quantity != None:
        try:
            M[7] = int(sheet.cell(row, quantity).value)
        except ValueError:
            M[7]=-1
    if price != None:
        try:
            M[8] = float(sheet.cell(row, price).value)
        except ValueError:
            M[8]="-"
    if notes != None:
        M[9] = str(sheet.cell(row, notes).value)
    if clas != None:
        M[10] = str(sheet.cell(row, clas).value)
    if decomission != None:
        M[11] = str(sheet.cell(row, decomission).value)
    if numberinlist != None:
        M[12] = str(sheet.cell(row, numberinlist).value)
    if publisher != None:
        M[13] = str(sheet.cell(row, publisher).value)
    if summ==None and M[7] != " " and M[8] != " ":
        M[14] = int(M[7]) * float(M[8])
    else:
        if summ==None:
            M[14] = 0
        else:
            try:
                M[14]=float(sheet.cell(row, summ).value)
            except ValueError:
                M[14]=0
    if set_1 != None:
        M[15] = str(sheet.cell(row, set_1).value)
    if consignment != None:
        M[16] = str(sheet.cell(row, consignment).value)[:-14]
    #print(M)
    cursoro.execute('INSERT INTO books (id, author, name, subject, date, yeartown, number,\
            quantity, price, notes, class, decomission, numberinlist, publisher, sum, set_1, consignment)\
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(M))
# cell = sheet.cell(0, col)  # where row=row number and col=column number
# print(cell.value)  # to print the cell contents

con.commit()
con.close()
