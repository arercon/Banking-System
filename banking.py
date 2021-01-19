import random, sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("""Create table if not exists card(
            id INTEGER,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0)""")
#cur.execute("delete from card")
conn.commit()

class CreditCard:
    MII = "400000"
    mode = 'default'

    def create_account(self):
        self.acc_num = self.MII + ''.join(str(random.randint(0,9)) for _ in range(9))
        self.pin = ''.join(str(random.randint(0,9)) for _ in range(4))
        self.acc_num = self.acc_num + self.luhn_algorithm(self.acc_num)
        self.id = ''.join(str(random.randint(0,9)) for _ in range(8))
        self.balance = 0
        cur.execute("Insert into card(id, number, pin) values(?, ?, ?)", (self.id, self.acc_num, self.pin))
        conn.commit()
        print(f"\nYour card has been created\nYour card number:\n{self.acc_num}\n"
                f"Your card PIN:\n{self.pin}")
        return (self.acc_num, self.pin)

    def login(self):
        self.input_num = input("\nEnter your card number:\n")
        self.input_pin = input("Enter your PIN:\n")
        if cur.execute("SELECT EXISTS(SELECT 1 FROM CARD WHERE number = ?)", (self.input_num,)).fetchone()[0] and \
                (''.join(cur.execute("SELECT PIN FROM CARD WHERE NUMBER = ?", (self.input_num,)).fetchone())== self.input_pin):
            print("\nYou have successfully logged in!\n")
            self.admin_id = cur.execute("SELECT ID FROM CARD WHERE NUMBER = ?", (self.input_num,)).fetchone()[0]
            self.mode = 'account_menu'
            self.account_menu('')
        else:
            print("\nWrong card number or PIN!")
            self.main('')

    def account_menu(self, string):
        if string == '1':
            cur.execute('Select balance from card where id = ?', (self.admin_id,))
            print("Balance: "+ str(cur.fetchone()[0]))
            self.account_menu('')
        elif string == '2':
            self.add_income = int(input("Add income: "))
            self.balance += self.add_income
            cur.execute('Update card set balance = (?) where id = (?)', (self.balance, self.admin_id))
            conn.commit()
        elif string == '3':
            self.transfer()
        elif string == '4':
            cur.execute("Delete from card where id = ?", (self.admin_id,))
            conn.commit()
            print("The account has been closed!")
        elif string == '5':
            print("\nYou have successfully logged out!")
            self.mode = 'default'
        elif string == '0':
            print("\nBye!")
        else:
            print("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n"
                  "5. Log out\n0. Exit")

    def transfer(self):
        self.trans_num = input("\nTransfer\nEnter card number:")
        self.control_digit = self.trans_num[-1]
        if self.luhn_algorithm(self.trans_num[:-1]) == self.control_digit:
            if cur.execute('SELECT EXISTS(SELECT 1 FROM CARD WHERE number = ?)', (self.trans_num,)).fetchone()[0]:
                self.trans_amount = int(input("Enter how much money you want to transfer:"))
                if self.trans_amount <= self.balance:
                    cur.execute("Update card set balance = balance - ? where id = ?",
                    (self.trans_amount, self.admin_id))
                    cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?",
                    (self.trans_amount, self.trans_num))
                    conn.commit()
                    print("Success!")
                    print("")
                else:
                    print("Not enough money!")
                    self.account_menu('')
            else:
                print("Such a card does not exist.")
                self.account_menu('')
        else:
            print("Probably you made a mistake in the card number. Please try again!")
            self.account_menu('')


    def main(self, string):
        self.mode = 'default'
        if string == '1':
            self.acc_num, self.pin = self.create_account()
            self.ui('')
        elif string == '2':
            self.login()
        elif string == '0':
            print("\nBye!")
        else:
            print("\n1. Create an account\n2. Log into account\n0. Exit")

    def ui(self, string):
        if self.mode == 'default':
            self.main(string)
        elif self.mode == 'account_menu':
            self.account_menu(string)
            
    def luhn_algorithm(self, num):
        self.digits = [int(x) for x in num]
        for i in range(len(self.digits)):
            if i % 2 == 0:
                self.digits[i] *= 2
                if self.digits[i] > 9:
                    self.digits[i] -= 9
        self.checksum = 10-(sum(self.digits)%10)
        if self.checksum == 10:
            self.checksum = 0
        return str(self.checksum)

new_card = CreditCard()
command = ''
new_card.main(command)
while command != '0':
    command = input()
    new_card.ui(command)
