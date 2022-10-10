import mysql.connector, decimal

# supply appropriate connection parameters to connect to your MySQL DB
connection = mysql.connector.connect(host='localhost',database='gstin',user='sujal',password='sujal')

cursor = connection.cursor(buffered=True)

# create database tables
try:
    c_table = '''create table if not exists customers(id int unsigned primary key auto_increment, party varchar(100) not null, address varchar(400) not null, mobile bigint(11) unsigned zerofill, email varchar(100) default NULL)'''
    
    p_table = '''create table if not exists items
    (id int unsigned primary key auto_increment, name varchar(225) not null default 'Plug', model varchar(255) default 'N/A', serial varchar(255) default 'N/A', price decimal(11,2) unsigned not null default 0, gstrate decimal(4,2) unsigned not null default 0)''' # --- > total 6

    i_table = '''create table if not exists invoice (id int unsigned primary key auto_increment, date date not null, party_id int unsigned not null, item_id int unsigned not null, qty int(6) unsigned not null default 1)'''

    # party -> customer_id
    # item  -> product_id
  
    cursor.execute(c_table)
    cursor.execute(p_table)
    cursor.execute(i_table)

except mysql.connector.Error as error:
    print("Failed to create table in MySQL: {}".format(error))

def clear():
    for _ in range(65):
        print()

'''
def last_bill_no():
    cursor.execute("SELECT inv FROM customers ORDER BY inv DESC LIMIT 1")
    print(cursor.fetchone()[0], "is the draft invoice no.")
'''

def last_bill_no():
    cursor.execute('select max(id) from invoice')
    record = cursor.fetchone()
    return record

def find_item(no):
    cursor.execute('select * from items where id ={}'.format(no))
    record = cursor.fetchone()
    return record

def clients():
    
    # inv = int(input("Draft Invoice No: "))
    party = input("Party Name: ")
    # date = input("Date of Invoice: ")
    address = input("Client Address: ")
    mobile = int(input("Client Mobile: "))
    email = input("Email ID (optional): ")
    c_query = f'''insert into customers (party,address,mobile,email) values('{party}','{address}',{mobile},'{email}')'''
    cursor.execute(c_query)
    
    connection.commit()
    

    # print(cursor.rowcount, "record(s) inserted.\n")
    return party, mobile
    

def calc_gst(p,rate,qty):
    CGST = p*((rate/2)/100)
    SGST = CGST
    amount = (p + CGST + SGST)*qty
    amount = round(amount,2)
    return CGST, SGST, amount

# def items():
    # inv      = int(input("Add to Invoice no: "))
    # prod     = input("Product Name: ")

    # price    = float(input("Enter Price before GST: "))
 

    # p_query = f'''insert into products (inv, prod,model,serial,qty,price,calcrate,amount) values({inv},'{prod}','{model}','{serial}',{qty},{price},{calcrate},{amount})'''
    # cursor.execute(p_query)
    
    # connection.commit()      
    # print(cursor.rowcount, "record(s) inserted.")

    # print()
    # print('           INVOICE')
    # print('-'*25)
    # print('Selling Price(₹) :',price)
    # print('CGST             :',CGST)
    # print('SGST             :',SGST)
    # print('Amount(₹)        :',amount)
    # print('-'*25)
    # print()

def add_item():
    clear()
    print('Add New Item - Screen')
    print('-'*100)
    name = input('Enter New Item Name: ')
    model    = input("Model No: ")
    serial   = input("Sr No. ")
    price = float(input("Enter Price before GST: "))
    gstrate = float(input("Rate of GST: "))

    query = f'''select * from items where name like "%{name}%"'''
    cursor.execute(query)
    record=cursor.fetchone()
    if record==None:
        query = f'''insert into items(name,model,serial,price,gstrate) values("{name}","{model}","{serial}",{price},{gstrate});'''
        cursor.execute(query)
        print('\n\nNew Item added successfully.....\nPress any key to continue....')
    else:
        print('\n\nItem Name already Exist.....\nPress any key to continue....')
    wait= input()

#   function name       : modify_item
#   purpose             : change item details in items table
def modify_item():
    clear()
    print('Modify Item Details - Screen')
    print('-'*100)
    item_id = int(input('Enter Product ID: '))
    item_name = input('New Product Name: ')
    item_price = float(input('New Price: '))
    model = input("New Model No.: ")
    serial = input("New Sr. no: ")
    rate = float("New GST Rate: ")
    query = f'''update items set name = "{item_name}", price ={item_price}, model = "{model}", serial = "{serial}",rate = {rate} where id={item_id}'''
    cursor.execute(query)
    print('\n\nRecord Updated Successfully............')

#   function name           : item_list
#   purpose                 : To display all the items in items tables
def item_list():
    clear()
    query="select * from items"
    cursor.execute(query)
    records = cursor.fetchall()
    for row in records:
        print(row)
    print('\nPress any key to continue.....')
    wait = input()

def billing():
    clear()
    items = []
    bill_no = last_bill_no()
    if bill_no[0]==None:
        bill_no = 1001
    else:
        bill_no = bill_no[0]+1
    
    clients()
    name,phone = clients()
    party_id = cursor.execute("SELECT max(id) FROM customers;")
    # name = input("Enter Party name: ")
    # phone = input('Enter Phone no: ')
    date = input("Bill date (YYYY-MM-DD): ")
    while True:
        no = int(input("Enter Item no. (0 to stop): "))
        if no <=0:
            break
        else:
            item = find_item(no)
            if item == None:
                print("Item not found.")
            else:
                qty = int(input("Order Quantity: "))
                item = list(item)
                item.append(qty)
                items.append(item)

    
    clear()
    print('                     Company Name              ')
    print('                     Gurugram, Harayana     ')
    print('                     Phone: 099XXXXXXXX, Email: manager@company.in ')
    print(f'Bill No :{bill_no}        Date :{date}')
    print('-'*100)
    print(f'Customer Name: {name}          Phone: {phone}')
    print('-'*100)
    print('Item Id       Item Name         MODEL        SERIAL      Price    GST     Qty          Amount ')
    print('-'*100)
    total = 0
    CGST, SGST, amount = calc_gst(item[4],item[5],item[6])
    for item in items:
        print('{:<10d} {:25s} {:.2f} {:>10d}          {:>.2f} \
            '.format(item[0],item[1],item[2],item[3],item[4],item[5],"CGST + SGST / ",CGST," + ",SGST,item[6],amount))
        # total = total + (price*qty)

        # gst = calc_gst(price,calcrate)
        # CGST,SGST,amount = gst
        # amount*=qty
        
        total += amount
    print('-'*100)
    print(f'Total Payable amount: {total}')
    print('\nPress any key to continue........')
    
    #insert data into tables
    # query = f'''insert into invoice(id,date,party_id,item_id,qty) values({bill_no},"{date}",{},{},{qty});'''
    # cursor.execute(query)
    for item in items:
        query=f'''insert into invoice(id,date,party_id,item_id,qty) values({bill_no},"{date}",{party_id[0]},{item[0]},{item[6]});'''
        cursor.execute(query)
    wait= input()

# try:
#     aborted = False
#     while not aborted:
#         clients()

#         print("Proceeding towards Products Invoice...\n")

#         items()
#         abort = input("Do you want to continue?: ")
#         if abort != chr(27):
#             continue
#         else:
#             aborted = True
#             print("DB updated;\n")
#             break

# except mysql.connector.Error as error:
#     print("Failed to insert data: {}".format(error))
# finally:
#     if connection.is_connected():
#         cursor.close()
#         connection.close()
#         print("Aborting....")
#         print("MySQL now disconnected")

#   function      : Date_wise_sell
#   purpose       : Create a report on date wise sell or sell between two dates
def date_wise_sell():
    clear()
    print('Invoices Between Date -- Screen')
    print('-'*100)
    start_date = input('Enter Start Date (yyyy-mm-dd): ')
    end_date   = input('Enter End Date (yyyy-mm-dd): ')
    query = f'''select invoice.id,invoice.date,party,mobile from invoice,customers where invoice.date between "{start_date}" and "{end_date}"'''
    cursor.execute(query)
    records = cursor.fetchall()
    clear()
    print('Bill No       Customer Name         Phone No         Bill Date')
    print('-'*100)
    for row in records:
        print('{:10d} {:30s} {:20s} {}'.format(row[0],row[2],row[3],row[1]))
    print('-'*100)
    print('\n\nPress any key to continue....')
    wait= input()


# function name        : bill information
# purpose               : display details of any bill
def bill_information():
    clear()
    bill_no = input('Enter Invoice Number :')
    query = f'''select i.id,c.name,c.mobile,i.date,i.item_id,i.qty,p.name,p.price from invoice i,customer c,items p \
           where i.party_id = c.id AND p.id= i.item_id AND \
           i.id ={bill_no};'''
    cursor.execute(query) 
    records = cursor.fetchall()
    n = cursor.rowcount
    clear()
    print("Invoice No :",bill_no)
    print('-'*100)
    if n<=0:
        print('Invoice {} does not exist'.format(bill_no))
    else:
        print('Customer Name: {}  Phone: {}'.format(records[0][1],records[0][2]))
        print('Invoice Date : {}'.format(records[0][3]))
        print('-'*100)
        print('{:10s} {:30s} {:20s} {:10s} {:30s}'.format('ID','Item Name','Qty','Price','Amount'))
        print('-'*100)
        for row in records:
            print('{:<10d} {:30s} {:<20d} {:.2f} {:>.2f}'.format(row[4],row[6],row[5],row[7],row[5]*row[7]))
        print('-'*100)
    print('\nPress any key to continue....')
    wait = input()


####
def search_item():
    clear()
    item_name =input('Search Item Name :')
    sql =f'select * from items where item_name like "%{item_name}%";'
    cursor.execute(sql)
    records = cursor.fetchall()
    clear()
    print('Items with :',item_name)
    print('-'*100)
    print('{:10s} {:30s} {:20s} {} {}'.format('Item ID','Name','MODEL','Price','GST'))
    print('-'*100)
    for row in records:
        print('{:<10d} {:30s} {:.2f} {} {}'.format(row[0],row[1],row[2],row[4],row[5]))
    print('-'*100)
    print('\nPress any key to continue....')
    wait= input()

#####
def search_customer():
    clear()
    cust_name =input('Search customer name :')
    sql ='select * from customers where name like "%{}%";'.format(cust_name)
    cursor.execute(sql)
    records = cursor.fetchall()
    clear()
    print('Customer Names with :',cust_name)
    print('-'*100)
    print('{:10s} {:30s} {:20s} {:20s}'.format('Customer ID','Name','Phone','Email'))
    print('-'*100)
    for row in records:
        print('{:<10d} {:30s} {:20s} {:20s}'.format(row[0],row[1],row[3],str(row[4])))
    print('-'*100)
    print('\nPress any key to continue....')
    wait= input()

#  function name    : search_menu
#  purpose          : Display search menu on the screen
def search_menu():
    while True:
        clear()
        print('      S E A R C H    M E N U ')
        print('-'*100)
        print('1.   Item Name')
        print('2.   Customer information')
        print('3.   Bill information')
        print('4.   Back to main Menu')
        choice = int(input('\n\nEnter your choice (1..4): '))
        if choice==1:
            search_item()
        if choice==2:
            search_customer()
        if choice==3:
            bill_information()
        if choice==4:
            break


#  function name    : report_menu
#  purpose          : Display report menu on the screen
def report_menu():
    while True:
        clear()
        print('   R E P O R T   M E N U ')
        print('-'*100)
        print('1.   Item List')
        print('2.   Invoices Between Date')
        print('3.   Bill information')
        print('4.   Back to main menu')
        choice = int(input('\n\nEnter your choice (1..4): '))
        if choice==1:
            item_list()
        if choice==2:
            date_wise_sell()
        if choice==3:
            bill_information()
        if choice==4:
            break


def main_menu():
    while True:
        clear()
        print('      M A I N   M E N U')
        print('-'*100)
        print('1.   Add New Product')
        print('2.   Modify Inventory')
        print('3.   Billing')
        print('4.   Search Menu')
        print('5.   Report Menu')
        print('6.   Exit')
        choice = int(input('\n\nEnter your choice (1..6): '))
        if choice==1:
            add_item()
        if choice==2:
            modify_item()
        if choice==3:
            billing()
        if choice==4:
            search_menu()
        if choice==5:
            report_menu()
        if choice==6:
            break


if __name__=="__main__":
    clear()
    main_menu()