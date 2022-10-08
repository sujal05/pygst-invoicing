import mysql.connector

connection = mysql.connector.connect(host='localhost',database='gstin',user='sujal',password='sujal')

cursor = connection.cursor()

# try:
#     sample_query = '''create table if not exists customers
#     (inv int primary key auto_increment, party varchar(100) not null, date date not null, address varchar(400) not null, mobile bigint(11))'''

#     cursor = connection.cursor()
#     result = cursor.execute(sample_query)
#     print("Sample test succeeded! fine")

# except mysql.connector.Error as error:
#     print("Failed to create table in MySQL: {}".format(error))
# finally:
#     if connection.is_connected():
#         cursor.close()
#         connection.close()
#         print("MySQL now disconnected")


try:
    create_table = '''create table if not exists products
    (inv int primary key auto_increment unsigned, prod varchar(225) not null default 'Plug', model varchar(255) default 'N/A', serial varchar(255) unique default 'N/A', qty int(6) not null unsigned default 1, price decimal(11,2) not null unsigned default 0, calcrate decimal(4,2) unsigned not null default 0, amount decimal(12,2) unsigned not null default 0)'''
    
    cursor.execute(create_table)
    print("Table creation successful.")

except mysql.connector.Error as error:
    print("Failed to create table in MySQL: {}".format(error))

try:
    aborted = False
    while not aborted:
        # inv = int(input("Invoice No: "))
        party = input("Party Name: ")
        date = input("Date of Invoice: ")
        address = input("Client Address: ")
        mobile = int(input("Client Mobile: "))
        c_query = '''insert into customers (party,date,address,mobile) values('{}','{}','{}',{})'''.format(party,date,address,mobile)
        cursor.execute(c_query)
        
        connection.commit()
        
        print(cursor.rowcount, "record(s) inserted.")

        abort = input("Do you want to continue?: ")
        if abort != chr(27):
            continue
        else:
            aborted = True
            break
            print("DB updated;\n")
    print("Proceeding towards Products Invoice...\n")

    def calc_gst(p,rate):
        CGST = p*((rate/2)/100)
        SGST = CGST
        amount = p + CGST + SGST
        return CGST, SGST, amount
    while not aborted:
        prod     = input("Product Name: ")
        model    = input("Model No: ")
        serial   = int(input("Sr No. "))
        qty      = int(input("Qty. "))
        price    = float(input("Enter Price before GST: "))
        calcrate = float(input("Rate of GST: "))
        gst = calc_gst(price,calcrate)
        CGST,SGST,amount = gst

        p_query = f'''insert into products (prod,model,serial,qty,price,calcrate,amount) values({prod},{model},{serial},{qty},{price},{calcrate},{amount})'''
        cursor.execute(p_query)
        
        connection.commit()
        


except mysql.connector.Error as error:
    print("Failed to insert data: {}".format(error))
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Aborting....")
        print("MySQL now disconnected")