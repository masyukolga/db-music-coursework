import mysql.connector
from tabulate import tabulate
from objects import *
import hashlib

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password=' ',
    port='3306',
    database='music_archive'
)

mycursor = mydb.cursor(buffered=True)


def hash(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


#Check existence

def check_if_exists(login, password_hash):
    mycursor.execute("SELECT * from users WHERE login = %s AND `password` = %s", (login, password_hash))
    mycursor.fetchone()
    return mycursor.rowcount > 0


def check_if_exists_login(login):
    query_vals = (login,)
    mycursor.execute("SELECT * from users WHERE login = %s", query_vals)
    mycursor.fetchone()
    if mycursor.rowcount <= 0:
        return False
    else:
        return True


def check_if_composer_exists(login):
    query_vals = (login,)

    mycursor.execute("SELECT * from composers WHERE `c_name` = %s", query_vals)
    mycursor.fetchone()
    return mycursor.rowcount > 0


def check_if_instrument_exists(instrument):
    query_vals = (instrument,)

    mycursor.execute("SELECT * from instruments WHERE `name` = %s", query_vals)
    mycursor.fetchone()
    if mycursor.rowcount <= 0:
        return False
    else:
        return True


def check_if_composition_exists(name, composer):
    query_vals = (name, composer)

    mycursor.execute("SELECT * from compositions WHERE `name` = %s AND composer_name = %s AND `status` = 1", query_vals)
    mycursor.fetchone()
    if mycursor.rowcount <= 0:
        return False
    else:
        return True


def get_user_id(login, password):
    query_vals = (login, password)
    try:
        mycursor.execute("SELECT id from users WHERE login = %s AND `password` = %s", query_vals)
        r = mycursor.fetchone()
        return r[0]
    except TypeError:
        print(" ")


def get_composer_name(user_id):
    val = (user_id,)
    mycursor.execute("SELECT `c_name` FROM composers WHERE id = %s", val)
    r = mycursor.fetchone()
    return r[0]


def get_user_name(user_id):
    val = (user_id,)
    mycursor.execute("SELECT `login` FROM users WHERE id = %s", val)
    r = mycursor.fetchone()
    return r[0]


def get_composer_id(composition_name, composer_name):
    query_vals = (composition_name, composer_name)
    mycursor.execute("SELECT composer_id from compositions WHERE name = %s AND composer_name = %s", query_vals)
    r = mycursor.fetchone()
    return r[0]


def get_composition_id(composition_name, composer_name):
    mycursor.execute("SELECT id from compositions WHERE name = %s AND composer_name = %s",
                     (composition_name, composer_name))
    r = mycursor.fetchone()
    return r[0]


def get_instrument_id(instrument_name):
    query_vals = (instrument_name,)
    mycursor.execute("SELECT id from instruments WHERE `name` = %s ", query_vals)
    r = mycursor.fetchone()
    return r[0]


def create_composition(user_id):
    composition = Composition()
    composition.name = input("Composition name: ")
    composition.comp_name = get_composer_name(user_id)
    while check_if_composition_exists(composition.name, composition.comp_name):
        print("Such exact composition of yours exists. Modify the name of your new one")
        composition.name = input("Composition name: ")

    composition.price = input("Composition price: ")
    print_instruments()
    composition.instrument = input("Instrument: ")
    composition.status = 1
    while not check_if_instrument_exists(composition.instrument):
        composition.instrument = input("Invalid option. Enter the instrument: ")
    composition.comp_name = get_composer_name(user_id)

    composition.comp_id = user_id
    mycursor.execute(
        "INSERT INTO compositions(`name`, price, composer_name,composer_id, status) VALUES (%s,%s,%s,%s,%s)",
        (composition.name, composition.price, composition.comp_name, composition.comp_id, composition.status))
    mydb.commit()
    composition_id = get_composition_id(composition.name, composition.comp_name)
    instrument_id = get_instrument_id(composition.instrument)
    mycursor.execute(
        "INSERT INTO instr_composition(instrument_id, composition_id) VALUES (%s,%s)", (instrument_id, composition_id))
    mydb.commit()
    print("Congrats! Check your email for adding the file and more details!")


def create_purchase(user_id):
    print("Creating new purchase")
    purchase = Purchase()
    composition_name = input("Select a composition name: ")
    composer_name = input("Specify composer's name: ")
    while not check_if_composition_exists(composition_name, composer_name):
        print("Composition not found. Try again or press 0 to exit")
        composition_name = input("Select a composition name: ")
        composer_name = input("Specify composer's name: ")

    composer_id = get_composer_id(composition_name, composer_name)
    purchase.user_id = user_id
    purchase.comp_id = composer_id
    purchase.c_id = get_composition_id(composition_name, composer_name)
    vals = (purchase.user_id, purchase.c_id)
    mycursor.execute(
        "INSERT INTO purchases(user_id, composition_id) VALUES (%s,%s)", vals)
    mydb.commit()
    print("Congrats! Check your email for confirmation letter!")


def print_instruments():
    mycursor.execute("SELECT `name` FROM instruments")
    data = mycursor.fetchall()
    h = ['instruments']
    print(tabulate(data, headers=h, tablefmt="pretty"))


def user_session(user_id):
    while True:
        print("Welcome to user session")
        print("1. Look for some compositions")
        print("2. My purchases")
        print("0. Log-out")

        user_option = input("Option: ")
        if user_option == "1":
            print("Look for some compositions")
            mycursor.execute("SELECT c.`name`, c.composer_name, c.price, comp.bio, instr.`name` FROM compositions c "
                             "JOIN composers comp ON (c.composer_name=comp.`c_name`)"
                             "LEFT JOIN instr_composition i ON (c.id=i.composition_id) "
                             "LEFT JOIN instruments instr ON(i.instrument_id = instr.id) WHERE c.`status` = 1")
            data = mycursor.fetchall()
            h = ['name', 'composer name', 'price', 'bio', 'instrument']
            print(tabulate(data, headers=h, tablefmt="pretty"))

            print("Do you want to purchase some compositions? 1 - Yes, 2 - No")
            answer = input("Write your answer: ")
            if answer == "1":
                create_purchase(user_id)
            elif answer == "2":
                print("Check out your favourite compositions anytime")
            else:
                print("Invalid option")

        if user_option == "2":
            print("My purchases")
            val = (user_id,)
            mycursor.execute(
                "SELECT c.`name`, c.composer_name, c.price "
                "FROM compositions c JOIN purchases p ON p.composition_id = c. id WHERE p.user_id = %s",
                val)
            data = mycursor.fetchall()
            h = ['Composition name', 'Composer name', 'Price']
            print(tabulate(data, headers=h, tablefmt="pretty"))

        if user_option == "0":
            break


def composer_session(user_id):
    while True:
        print("Welcome to composer session")
        print("1. Create a composition")
        print("2. Look at my compositions")
        print("3. Delete my composition")
        print("4. Look for all compositions")
        print("0. Log out")

        user_option = input("Option: ")
        if user_option == "1":
            print("Create a composition")
            create_composition(user_id)
        if user_option == "2":
            print("Look at my compositions")
            val = (user_id,)
            mycursor.execute(
                "SELECT name, composer_name, price FROM compositions WHERE composer_id = %s AND `status` = 1", val)
            data = mycursor.fetchall()
            h = ['name', 'composer name', 'price']
            print(tabulate(data, headers=h, tablefmt="pretty"))

        if user_option == "3":
            print("Delete a composition")
            name = input("Enter composition name: ")
            vals = (name,user_id)
            mycursor.execute("UPDATE compositions SET `status` = 0 WHERE `name` = %s AND composer_id = %s", vals)
            mydb.commit()

        if user_option == "4":
            user_session(user_id)

        if user_option == "0":
            break


def admin_auth():
    print("Admin Login")
    admin_name = input("Username: ")
    admin_password = input("Password: ")
    if admin_name == "admin":
        if admin_password == "password":
            admin_session()
        else:
            print("Incorrect password")
    else:
        print("Incorrect login")


def admin_session():
    while True:
        print("Admin menu: \n")
        print("1.Delete a user")
        print("2.Delete a composition")
        print("3.Update a role")
        print("4.Show all the users")
        print("5.Show all the composers")
        print("6.Add a new instrument")
        print("7.Show all the compositions")
        print("0.Log out")


        user_option = input(("Option: "))
        if user_option == "1":
            print("Delete a user")
            id = input("Enter user's id: ")
            vals = (id,)
            mycursor.execute("DELETE FROM purchases WHERE user_id = %s", vals)
            mydb.commit()
            mycursor.execute("DELETE FROM users WHERE id = %s", vals)
            mydb.commit()

        if user_option == "2":
            print("Delete a composition")
            id = input("Enter composition id: ")
            vals = (id,)
            mycursor.execute("UPDATE compositions SET `status` = 0 WHERE id = %s", vals)
            mydb.commit()
        if user_option == "3":
            print("Update a role")
            id = input("Enter composition id: ")
            vals = (id,)
            mycursor.execute("UPDATE users SET role_id = 2 WHERE id = %s", vals)
            mydb.commit()
            name = get_user_name(id)
            vals = (id, name)
            mycursor.execute("INSERT INTO `composers` (id, `c_name`) VALUES(%s, %s)", vals)
            mydb.commit()
        if user_option == "4":
            print("Show all the users")
            mycursor.execute("SELECT id, login, role_id FROM users")
            data = mycursor.fetchall()
            h = ['id', 'login', 'role_id']
            print(tabulate(data, headers=h, tablefmt="pretty"))
        if user_option == "5":
            print("Show all the composers")
            mycursor.execute("SELECT id, login FROM users WHERE role_id = 2")
            data = mycursor.fetchall()
            h = ['id', 'login', 'role_id']
            print(tabulate(data, headers=h, tablefmt="pretty"))
        if user_option == "6":
            print("Add a new instrument")
            instrument = input(("Enter the instrument: "))
            val = (instrument,)
            mycursor.execute("INSERT into instruments(`name`) VALUES (%s)", val)
            mydb.commit()
        if user_option == "0":
            break


def sign_in():
    print("Sign in")
    login = input("Login: ")
    password = hash(input("Password: "))
    user_id = get_user_id(login, password)
    query_vals = (login, password)

    if check_if_exists(login, password):
        mycursor.execute("SELECT role_id from users WHERE login = %s AND `password` = %s", query_vals)
        r = mycursor.fetchone()
        if r[0] == 2:
            composer_session(user_id)
        if r[0] == 1:
            user_session(user_id)
    else:
        print("User is not found, consider signing up")


def sign_up_user():
    print("Sign up page")
    user = User()
    user.login = input("Login: ")
    while check_if_exists_login(user.login):
        print("This login is taken, choose another one")
        user.login = input("Login: ")
    user.password = hash(input("Password: "))
    user.phone = input("Phone number: ")
    user.email = input("Email: ")
    query_vals = (user.login, user.password, user.email, user.phone)
    mycursor.execute("INSERT INTO users (login,`password`,email,phone,role_id) VALUES(%s, %s, %s, %s, 1)", query_vals)
    mydb.commit()
    user_id = get_user_id(user.login, user.password)
    print("Signed up successfully! Welcome!")
    user_session(user_id)


def sign_up_composer():
    print("Sign up page")
    composer = Composer()
    user = User()
    user.login = composer.login = input("Login: ")
    while check_if_exists_login(user.login) and check_if_composer_exists(user.login):
        print("This login is taken, choose another one")
        user.login = composer.login = input("Login: ")
    user.password = composer.password = hash(input("Password: "))
    user.phone = composer.phone = input("Phone number: ")

    user.email = composer.email = input("Email: ")

    val = (user.login, user.password)
    query_vals = (user.login, user.password, user.email, user.phone)
    mycursor.execute("INSERT INTO users (login,`password`,email, phone, role_id) VALUES(%s, %s, %s, %s, 2)", query_vals)
    mydb.commit()

    id = mycursor.lastrowid

    composer.bio = input("Tell everyone about yourself: ")
    query_vals_comp = (id, composer.login, composer.bio)
    mycursor.execute("INSERT INTO `composers` (id, `c_name`, bio) VALUES(%s, %s, %s)", query_vals_comp)
    mydb.commit()
    user_id = get_user_id(user.login, user.password)
    composer_session(user_id)


def main():
    print("Welcome to the music archive!\n")
    while True:
        print("Choose your option: ")
        print("1. Log in")
        print("2. Sign up")
        print("0. Exit")

        user_option = input("Option: ")
        if user_option == "0":
            break
        if user_option == "1":
            sign_in()
        elif user_option == "2":
            print("1. Sign up as an user")
            print("2. Sign up as a composer")

            user_option2 = input("Option: ")
            if user_option2 == "1":
                sign_up_user()
            elif user_option2 == "2":
                sign_up_composer()
            else:
                print("Invalid option")
        elif user_option == "3":
            admin_auth()
        else:
            print("Invalid option")


if __name__ == '__main__':
    main()
