import mysql.connector, decimal

connection = mysql.connector.connect(host='localhost',database='gstin',user='sujal',password='sujal')

cursor = connection.cursor(buffered=True)

try:
    c_table = '''create table if not exists customers(inv int primary key auto_increment, party varchar(100) not null, date date not null, address varchar(400) not null, mobile bigint(11) unsigned zerofill)'''
    
    p_table = '''create table if not exists products
    (product_id int unsigned primary key auto_increment,inv int unsigned not null, prod varchar(225) not null default 'Plug', model varchar(255) default 'N/A', serial varchar(255) default 'N/A', qty int(6) unsigned not null default 1, price decimal(11,2) unsigned not null default 0, calcrate decimal(4,2) unsigned not null default 0, amount decimal(12,2) unsigned not null default 0)'''

    
    cursor.execute(c_table)
    cursor.execute(p_table)

except mysql.connector.Error as error:
    print("Failed to create table in MySQL: {}".format(error))

def clients():
    # inv = int(input("Invoice No: "))
    party = input("Party Name: ")
    date = input("Date of Invoice: ")
    address = input("Client Address: ")
    mobile = int(input("Client Mobile: "))
    c_query = '''insert into customers (party,date,address,mobile) values('{}','{}','{}',{})'''.format(party,date,address,mobile)
    cursor.execute(c_query)
    
    connection.commit()
    
    print(cursor.rowcount, "record(s) inserted.\n")
    cursor.execute("SELECT inv FROM customers ORDER BY inv DESC LIMIT 1")
    print(cursor.fetchone()[0], "is the draft invoice no.")

def calc_gst(p,rate):
    CGST = p*((rate/2)/100)
    SGST = CGST
    amount = p + CGST + SGST
    amount = round(amount,2)
    return CGST, SGST, amount

def items():
    inv      = int(input("Add to Invoice no: "))
    prod     = input("Product Name: ")
    model    = input("Model No: ")
    serial   = input("Sr No. ")
    qty      = int(input("Qty. "))
    price    = float(input("Enter Price before GST: "))
    calcrate = float(input("Rate of GST: "))
    gst = calc_gst(price,calcrate)
    CGST,SGST,amount = gst
    amount*=qty

    p_query = f'''insert into products (inv, prod,model,serial,qty,price,calcrate,amount) values({inv},'{prod}','{model}','{serial}',{qty},{price},{calcrate},{amount})'''
    cursor.execute(p_query)
    
    connection.commit()      
    print(cursor.rowcount, "record(s) inserted.")

try:
    aborted = False
    while not aborted:
        clients()

        print("Proceeding towards Products Invoice...\n")

        items()
        abort = input("Do you want to continue?: ")
        if abort != chr(27):
            continue
        else:
            aborted = True
            print("DB updated;\n")
            break

except mysql.connector.Error as error:
    print("Failed to insert data: {}".format(error))
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Aborting....")
        print("MySQL now disconnected")