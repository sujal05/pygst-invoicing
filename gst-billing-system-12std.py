'''program developed and tested on MariaDB server (a fork of MySQL)'''
import mysql.connector          # connect python with MySQL server
from prettytable import PrettyTable         # generate and customize indented tables

# supply appropriate connection parameters to connect to your MySQL DB
connection = mysql.connector.connect(host='localhost',database='gstin',user='sujal',password='sujal')

# initialize cursor to perform DB operations --> use buffer to pre-fetchall
cursor = connection.cursor(buffered=True)

# create necessary database tables
try:
    c_table = '''create table if not exists customers(id int unsigned primary key auto_increment, party varchar(100) not null, address varchar(400) not null, mobile bigint(11) unsigned zerofill, email varchar(100) default NULL)'''
    
    p_table = '''create table if not exists items
    (id int unsigned primary key auto_increment, name varchar(225) not null default 'Plug', model varchar(255) default 'N/A', serial varchar(255) default 'N/A', price decimal(11,2) unsigned not null default 0, gstrate decimal(4,2) unsigned not null default 0)''' # --- > total 6

    i_table = '''create table if not exists invoice (aid int primary key auto_increment, id int unsigned not null, date date not null, party_id int unsigned not null, item_id int unsigned not null, qty int(6) unsigned not null default 1, foreign key (party_id) references customers(id), foreign key (item_id) references items(id));'''

    # party -> party_id
    # item  -> item_id
  
    cursor.execute(c_table)
    cursor.execute(p_table)
    cursor.execute(i_table)

except mysql.connector.Error as error:
    print("Failed to create table in MySQL: {}".format(error))

# maintain a clean viewport
def clear():
    for _ in range(65):
        print()

# fetch last invoice id from DB
def last_bill_no():
    cursor.execute('select max(id) from invoice')
    record = cursor.fetchone()
    return record

def truncate(chr,len):
        string = chr[:len] + (chr[len:] and '..')
        return string

# find items from ID --> used in billing()
def find_item(no):
    cursor.execute('select * from items where id ={}'.format(no))
    record = cursor.fetchone()
    return record

# collect and insert customer data to DB;
def clients():
    for i in range(1):
        # inv = int(input("Draft Invoice No: "))
        party = input("Party Name: ")
        # date = input("Date of Invoice: ")
        address = input("Client Address: ")
        mobile = int(input("Client Mobile: "))
        email = input("Email ID (optional): ")
        c_query = f'''insert into customers (party,address,mobile,email) values('{party}','{address}',{mobile},'{email}')'''
        cursor.execute(c_query)
        
        connection.commit()
    
    return party, mobile
    
# write GST formulas for CGST, SGST and total amount (inc. GST and qty)
def calc_gst(p,rate,qty):
    CGST = ((rate/2)/100)*(p*qty)
    SGST = CGST
    SGST = round(SGST,2)
    amount = ((p*qty) + CGST + SGST)
    amount = round(amount,2)
    return CGST, SGST, amount


 #  function name       : add_item
 #  purpose             : add new products in DB
def add_item():
    clear()
    print('Add New Item - Screen')
    print('-'*30)
    name = input('Enter New Item Name: ')
    model    = input("Model No: ")
    serial   = input("Sr No. ")
    price = float(input("Enter Price before GST: "))
    gstrate = float(input("Rate of GST: "))

    query = f'''SELECT * FROM items WHERE name LIKE "%{name}%"''' # LIKE --> used to query specified letters in 'name' column 
    cursor.execute(query)
    record=cursor.fetchone()
    if record==None:
        query = f'''insert into items(name,model,serial,price,gstrate) values("{name}","{model}","{serial}",{price},{gstrate});'''
        cursor.execute(query)
        connection.commit()
        print('\n\nNew Item added successfully.....\nPress any key to continue....')
    else:
        print('\n\nItem Name already Exist.....\nPress any key to continue....')
    wait= input()


#   function name       : modify_item
#   purpose             : change item details in items table
def modify_item():
    clear()
    print('Modify Item Details - Screen')
    print('-'*30)
    item_id = int(input('Enter Product ID: '))
    item_name = input('New Product Name: ')
    item_price = float(input('New Price: '))
    model = input("New Model No.: ")
    serial = input("New Sr. no: ")
    rate = float(input("New GST Rate: "))
    query = f'''update items set name = "{item_name}", price ={item_price}, model = "{model}", serial = "{serial}",gstrate = {rate} where id={item_id}'''
    cursor.execute(query)
    connection.commit()
    print('\nRecord Updated Successfully............')


#   function name           : item_list
#   purpose                 : To display all the items in items table
def item_list():
    pta = PrettyTable()
    clear()
    query="select * from items"
    cursor.execute(query)
    records = cursor.fetchall()
    n = cursor.rowcount         # count no. of rows in query
    
    if n<=0:
        print("There are currently no items to list.")
    else:
        pta.field_names = ["ID","Name","MODEL","Sr","Price","GST"]
        for row in records:
            pta.add_row([row[0],truncate(row[1],28),truncate(row[2],13),truncate(row[3],18),row[4],str(row[5])+'%'])
        print(pta)
    print('\nPress any key to continue.....')
    wait = input()
    return              # empty return to end the function


#   function name           : billing
#   purpose                 : inserts transaction data into invoice table (qty,bill_no,date, etc.)
def billing():
    pta = PrettyTable()
    clear()

    # store items data and qty in nested list
    items = []

    bill_no = last_bill_no()
    if bill_no[0]==None:
        bill_no = 1001          # start invoicing with no 1001
    else:
        bill_no = bill_no[0]+1
    
    name,phone = clients()          # call and assign function values to appropriate no. of variables
    cursor.execute("SELECT max(id) FROM customers;")    # find last customer to later insert into invoice table for joining
    party_id = cursor.fetchone()

    date = input("Bill date (YYYY-MM-DD): ")            # input custom invoice date in allowed range

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


# print static invoice contents - company,gstin,phone,mail etc
    clear()
    print('             Company Name             ')
    print('           Gurugram, Harayana            ')
    print('       Phone: 099XXXXXXXX, Email: manager@company.in         ')
    print('                 GSTIN: 07AEXXXXXXXXXXX\n')
    print(f'Bill No :{bill_no}  |  Date :{date}')
    print(f'Customer Name: {name}  |  Phone: {phone}')
    total = 0
    pta.field_names = ["Item ID","Product","MODEL","SERIAL","Price(₹)","Qty","GST","CGST/SGST","Amount(₹)"]
    for item in items:
        CGST, SGST, amount = calc_gst(item[4],item[5],item[6])
        pta.add_row([item[0],item[1],item[2],item[3],item[4],item[6],str(item[5])+'%',str(CGST)+'/'+str(SGST),amount])
        
        total += amount
    print(pta)
    print(f'Total Payable amount: ₹{total}')
    print('\nPress any key to continue........')
    
    #insert data into tables
    for item in items:
        query=f'''insert into invoice(id,date,party_id,item_id,qty) values({bill_no},"{date}",{party_id[0]},{item[0]},{item[6]});'''
        cursor.execute(query)
        connection.commit()
    wait= input()


#   function      : Date_wise_sell
#   purpose       : Create a report on date wise sell or sell between two dates
def date_wise_sell():
    pta = PrettyTable()
    clear()
    print('Invoices Between Date -- Screen')
    print('-'*100)
    start_date = input('Enter Start Date (yyyy-mm-dd): ')
    end_date   = input('Enter End Date (yyyy-mm-dd): ')
    query = f'''select i.id,i.date,party,mobile from invoice i,customers c where i.date between "{start_date}" and "{end_date}" and i.party_id = c.id;'''
    cursor.execute(query)
    records = cursor.fetchall()
    clear()
    print(f'''--- Invoice(s) between {start_date} and {end_date} ---''')
    pta.field_names = ["Invoice","Customer","Phone","Date"]
    for row in records:
        pta.add_row([row[0],row[2],row[3],row[1]])
    print(pta)
    print('\n\nPress any key to continue....')
    wait= input()


# function name        : bill information
# purpose               : display details of any bill
def bill_information():
    pta = PrettyTable()
    clear()
    bill_no = input('Enter Invoice Number :')
    query = f'''select i.id,c.party,c.id,c.mobile,i.date,i.item_id,p.name,p.model,p.serial,p.price,i.qty,p.gstrate from invoice i,customers c,items p \
           where i.party_id = c.id AND p.id= i.item_id AND \
           i.id ={bill_no};'''
    cursor.execute(query) 
    records = cursor.fetchall()
    n = cursor.rowcount
    clear()
    print("Invoice No :",bill_no)
    print('-'*30)
    if n<=0:
        print('Invoice {} does not exist'.format(bill_no))
    else:
        print('Customer Name: {}, {}  |  Phone: {}'.format(records[0][1],records[0][2],records[0][3]))
        print('Invoice Date : {}'.format(records[0][4]))
        pta.field_names = ["ID","Product","MODEL","SERIAL","Price(₹)","Qty","GST","CGST/SGST","Amount(₹)"]
        total = 0
        for row in records:
            CGST, SGST, amount = calc_gst(row[9],row[11],row[10])
            pta.add_row([row[5],row[6],row[7],row[8],row[9],row[10],str(row[11])+'%',str(CGST)+'/'+str(SGST),amount])
            total+=amount
        print(pta)
        print(f'Total amount paid: ₹{total}')
    print('\nPress any key to continue....')
    wait = input()
    return


#  function name    : amount_collected
#  purpose          : Function to display amount collected between two dates
def amount_collected():
    clear()
    start_date = input('Enter start Date (yyyy-mm-dd) :')
    end_date   = input('Enter End   Date (yyyy-mm-dd) :')
    clear()
    print('Amount collected between: {} and {}'.format(start_date,end_date))
    print('-'*30)
    query = f'''select p.price,p.gstrate,i.qty from invoice i,items p where i.item_id = p.id and date between '{start_date}' and '{end_date}';'''
    cursor.execute(query)
    result = cursor.fetchall()
    total = 0
    for row in result:
        CGST, SGST, amount = calc_gst(row[0],row[1],row[2])
        total+=amount
    print(f"Total amount collected: ₹{total}")
    print('\nPress any key to continue.....')
    wait= input()


#### search products with name
def search_item():
    pta = PrettyTable()
    clear()
    item_name =input('Search Item Name :')
    sql =f'select * from items where name like "%{item_name}%";'
    cursor.execute(sql)
    records = cursor.fetchall()
    clear()
    print('Items with:',item_name)
    print('-'*30)
    pta.field_names = ["ID","Name","MODEL","SERIAL","Price","GST"]
    for row in records:
        pta.add_row([row[0],row[1],row[2],row[3],row[4],str(row[5])+'%'])
    print(pta)
    print('\nPress any key to continue....')
    wait= input()


#####   search for customers with name
def search_customer():
    pta = PrettyTable()
    clear()
    cust_name =input('Search customer name: ')
    sql ='select * from customers where party like "%{}%";'.format(cust_name)
    cursor.execute(sql)
    records = cursor.fetchall()
    clear()
    print('Customer Names with :',cust_name)
    pta.field_names = ["ID","Name","Address","Phone","Email"]
    for row in records:
        pta.add_row([row[0],row[1],truncate(row[2],28),row[3],row[4]])
    print(pta)
    print('\nPress any key to continue....')
    wait= input()

#  function name    : search_menu
#  purpose          : Display search menu on the screen
def search_menu():
    while True:
        clear()
        print('      S E A R C H    M E N U ')
        print('-'*30)
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
        print('-'*30)
        print('1.   Item List')
        print('2.   Invoices Between Date')
        print('3.   Bill information')
        print('4.   Amount Collected b/w')
        print('5.   Back to main menu')
        choice = int(input('\n\nEnter your choice (1..5): '))
        if choice==1:
            item_list()
        if choice==2:
            date_wise_sell()
        if choice==3:
            bill_information()
        if choice==4:
            amount_collected()
        if choice==5:
            break


#  function name        : main_menu
#  purpose              : defines structure of program
def main_menu():
    while True:
        clear()
        print('      M A I N   M E N U')
        print('-'*30)
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

# allows program to run independently, checks if program is a module (doesn't runs modules);
if __name__=="__main__":
    clear()
    main_menu()

    if connection.is_connected():
        cursor.close()          # closing cursor before terminating program
        connection.close()      # finally close the connection to commit any unsaved changes
        print("Querying data to server....")
        print("MySQL now disconnected\nas there are no further processes.")