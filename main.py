import tkinter as tk
import sqlite3
import csv
import hashlib
from tkinter import ttk, messagebox, filedialog

def get_password():
    global password_admin, password_exit
    passwordsfile = open('passwords.txt', 'r')
    password_admin = passwordsfile.readline().strip()
    password_exit = passwordsfile.readline().strip()
    passwordsfile.close()

def verify_password(entered_password, stored_value):
    salt, stored_hash = stored_value.split("$")
    entered_hash = hashlib.pbkdf2_hmac("sha256", entered_password.encode(), salt.encode(), 100_000).hex()
    return entered_hash == stored_hash

def change_password():
    def save():
        passfile = open('passwords.txt', 'w')
        passfile.write(npassadmin.get()+'\n')
        passfile.write(npassexit.get())
        passfile.close()
        popup.destroy()
        get_password()

    popup = tk.Toplevel()
    popup.title("Password Manager")
    popup.geometry("800x400")
    popup.configure(background="#D9D9D9")
    ttk.Label(popup, text="Password Manager", font=("Arial", 25, "bold")).place(relx=0.5, rely=0.2, anchor="center")
    npassadmin=tk.StringVar()
    npassadmin.set(password_admin)
    npassexit=tk.StringVar()
    npassexit.set(password_exit)
    ttk.Label(popup, text='Admin Password:', font=("Arial", 20)).place(relx=0.2, rely=0.4, anchor='center')
    admin = ttk.Entry(popup, textvariable=npassadmin, font=("Arial", 20))
    admin.place(relx=0.65, rely=0.4, anchor='center')
    ttk.Label(popup, text='Exit Password:', font=("Arial", 20)).place(relx=0.2, rely=0.6, anchor='center')
    exit = ttk.Entry(popup, textvariable=npassexit, font=("Arial", 20))
    exit.place(relx=0.65, rely=0.6, anchor='center')
    ttk.Button(popup, text='Save', command=save, style='TButton').place(relx=.5, rely=.85, anchor='center')

con = sqlite3.connect('database.db')
cursor = con.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS student (USN_No char(20), Name char(100), Class int, Section char(1), House char(20), voted char(10) DEFAULT 'Not Voted')")
cursor.execute("CREATE TABLE IF NOT EXISTS nominees (Name varchar(100), Position char(50), House char(20), Votecount int)")

def show_login():
    menu_frame.pack_forget()
    login_frame.pack(fill="both", expand="yes")
    password_entry.focus()

def show_voting():
    menu_frame.pack_forget()
    window.title("STUDENT COUNCIL ELECTIONS")
    ask_class()

def show_voters():
    admin_frame.pack_forget()
    voters_frame.pack(fill="both", expand="yes")
    load_voters()

def show_nominees():
    admin_frame.pack_forget()
    nominee_frame.pack(fill="both", expand="yes")
    load_nominees()

def show_admin():
    get_password()
    entered = password_entry.get()
    if verify_password(entered, password_admin):
        login_frame.pack_forget()
        admin_frame.pack(fill="both", expand="yes")
        window.title('ADMIN PANEL')
        password_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Incorrect Password")
        password_entry.delete(0, tk.END)

def show_menu():
    for frame in (login_frame, admin_frame, voting_frame, details_frame):
        frame.pack_forget()
    menu_frame.pack(fill="both", expand="yes")
    window.title("STUDENT COUNCIL ELECTIONS")

def back_menu():
    for frame in (voters_frame, nominee_frame, winners_table_frame):
        frame.pack_forget()
    admin_frame.pack(fill="both", expand="yes")
    window.title('ADMIN PANEL')

def show_winners():
    def table():
        popup.destroy()
        admin_frame.pack_forget()
        show_winners_table()
        window.title("Winners Table")

    def printable():
        popup.destroy()
        admin_frame.pack_forget()
        show_winners_together()

    popup = tk.Toplevel()
    popup.title("Choose Format")
    popup.geometry("1000x240")
    popup.grab_set()
    popup.configure(background="#D9D9D9")
    ttk.Label(popup, text="How would you like to view winners?", font=("Helvetica", 20)).pack(pady=10)
    btn_frame = ttk.Frame(popup)
    btn_frame.pack(pady=5)
    ttk.Button(btn_frame, text="View in table format", command=table, style='TButton').pack(side="left", padx=10)
    ttk.Button(btn_frame, text="View in printable format", command=printable, style='TButton').pack(side="left", padx=10)

def show_winners_together():
    def export_winners_to_csv():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save as CSV"
        )
        if not file_path:
            return

        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)

            writer.writerow(['Post', 'Name', 'Class & Section', 'House', 'Votes'])

            cursor.execute(
                "SELECT DISTINCT position FROM nominees WHERE position NOT IN ('House Captain', 'House Vice Captain')")
            dist_positions = [row[0] for row in cursor.fetchall()]

            for position in dist_positions:
                cursor.execute(
                    "SELECT Name, Votecount FROM nominees WHERE Position = ? ORDER BY Votecount DESC LIMIT 1",
                    (position,)
                )
                nametemp = cursor.fetchall()
                winner_name = nametemp[0][0]
                max_votes = nametemp[0][1]

                cursor.execute("SELECT Name, Class, Section, House FROM student WHERE Name=?", (winner_name,))
                name, class_, section, house = cursor.fetchone()

                writer.writerow([position, name, str(class_) + str(section), house, max_votes])

            # Export house sections
            houses = ['Ruby', 'Sapphire', 'Topaz', 'Emerald']
            for h in houses:
                writer.writerow([])
                writer.writerow([h])

                cursor.execute(
                    "SELECT Name, Votecount FROM nominees WHERE House = ? AND Position = 'House Captain' "
                    "ORDER BY Votecount DESC LIMIT 1", (h,)
                )
                captaintemp = cursor.fetchall()
                captain = captaintemp[0][0]
                cap_votes = captaintemp[0][1]

                cursor.execute("SELECT Name, Class, Section, House FROM student WHERE Name=?", (captain,))
                name, class_, section, house = cursor.fetchone()

                writer.writerow(['House Captain', name, str(class_) + str(section), house, cap_votes])

                # House Vice Captain
                cursor.execute(
                    "SELECT Name, Votecount FROM nominees WHERE House = ? AND Position = 'House Vice Captain' "
                    "ORDER BY Votecount DESC LIMIT 1", (h,)
                )
                vicecaptaintemp = cursor.fetchall()
                vcaptain = vicecaptaintemp[0][0]
                v_votes = vicecaptaintemp[0][1]

                cursor.execute("SELECT Name, Class, Section, House FROM student WHERE Name=?", (vcaptain,))
                name, class_, section, house = cursor.fetchone()

                writer.writerow(['House Vice Captain', name, str(class_) + str(section), house, v_votes])

            messagebox.showinfo("CSV File saved!!", "Successfully exported CSV file.")

    winners_printable_frame = ttk.Frame(window)
    winners_printable_frame.pack(fill="both", expand="yes")

    container = ttk.Frame(winners_printable_frame)
    container.pack(fill="both", expand=True)

    winners_canvas = tk.Canvas(container)
    winners_canvas.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=winners_canvas.yview)
    scrollbar.pack(side="right", fill="y")
    winners_canvas.configure(yscrollcommand=scrollbar.set)

    all_winners_frame = ttk.Frame(winners_canvas)

    def on_frame_configure(event):
        winners_canvas.configure(scrollregion=winners_canvas.bbox("all"))
        winners_canvas.itemconfig(winners_window, width=event.width)

    winners_window = winners_canvas.create_window((0, 0), window=all_winners_frame, anchor="nw")
    winners_canvas.bind("<Configure>", on_frame_configure)
    all_winners_frame.bind("<Configure>", on_frame_configure)

    start_row = 1
    for col, heading in enumerate(['Post', 'Name', "Class & Section", 'House', "Votes"]):
        label = ttk.Label(all_winners_frame, text=heading, background="grey", padding=5, anchor="center", borderwidth=1,
                          font=("Helvetica", 24, "bold"))
        label.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

    cursor.execute(
        "select distinct position from nominees where position not in ('House Captain', 'House Vice Captain')")
    dist_positions = [row[0] for row in cursor.fetchall()]
    for i, position in enumerate(dist_positions):
        cursor.execute("SELECT Name, Votecount FROM nominees WHERE Position = ? ORDER BY Votecount DESC LIMIT 1",
                       (position,))
        nametemp = cursor.fetchall()
        winner = nametemp[0][0]
        maxvotes = str(nametemp[0][1])
        cursor.execute('select * from student where Name=?', (winner,))
        detailstemp = cursor.fetchall()
        winner_details = detailstemp[0]
        ttk.Label(all_winners_frame, text=position, font=("Helvetica", 20, "bold"), relief="solid", anchor="center",
                  borderwidth=0.5, padding=(5, 3)).grid(row=start_row + 1, column=0, sticky="nsew")
        Name = winner_details[1]
        ttk.Label(all_winners_frame, text=Name, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=1, sticky="nsew")
        ClassSec = str(winner_details[2]) + winner_details[3]
        ttk.Label(all_winners_frame, text=ClassSec, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=2, sticky="nsew")
        House = winner_details[4]
        ttk.Label(all_winners_frame, text=House, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=3, sticky="nsew")
        Votes = maxvotes
        ttk.Label(all_winners_frame, text=Votes, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=4, sticky="nsew")
        start_row += 1

    for h in ['Ruby', 'Sapphire', 'Topaz', 'Emerald']:
        if h=='Ruby':
            ttk.Label(all_winners_frame, text=h, font=("Helvetica", 30, "bold"), background="#E0115F", anchor="center",padding=10).grid(row=start_row + 1, column=0, columnspan=5, sticky="nsew")
        elif h=='Sapphire':
            ttk.Label(all_winners_frame, text=h, font=("Helvetica", 30, "bold"), background="#0F52BA", anchor="center",padding=10).grid(row=start_row + 1, column=0, columnspan=5, sticky="nsew")
        elif h=='Topaz':
            ttk.Label(all_winners_frame, text=h, font=("Helvetica", 30, "bold"), background="#F5BF0F", anchor="center",padding=10).grid(row=start_row + 1, column=0, columnspan=5, sticky="nsew")
        elif h=='Emerald':
            ttk.Label(all_winners_frame, text=h, font=("Helvetica", 30, "bold"), background="#50C878", anchor="center",padding=10).grid(row=start_row + 1, column=0, columnspan=5, sticky="nsew")
        start_row += 1
        cursor.execute(
            "select Name, Votecount from nominees where House = '{}' AND Position='House Captain' ORDER BY Votecount DESC LIMIT 1".format(
                h))
        captaintemp = cursor.fetchall()
        captain = captaintemp[0][0]
        capmaxvotes = str(captaintemp[0][1])
        cursor.execute('select * from student where Name=?', (captain,))
        capdetailstemp = cursor.fetchall()
        capdetails = capdetailstemp[0]
        ttk.Label(all_winners_frame, text='House Captain', font=("Helvetica", 20, "bold"), relief="solid",
                  anchor="center", borderwidth=0.5, padding=(5, 3)).grid(row=start_row + 1, column=0, sticky="nsew")
        Name = capdetails[1]
        ttk.Label(all_winners_frame, text=Name, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=1, sticky="nsew")
        ClassSec = str(capdetails[2]) + capdetails[3]
        ttk.Label(all_winners_frame, text=ClassSec, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=2, sticky="nsew")
        House = capdetails[4]
        ttk.Label(all_winners_frame, text=House, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=3, sticky="nsew")
        Votes = capmaxvotes
        ttk.Label(all_winners_frame, text=Votes, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=4, sticky="nsew")
        start_row += 1

        cursor.execute(
            "select Name, Votecount from nominees where House = '{}' AND Position='House Vice Captain' ORDER BY Votecount DESC LIMIT 1".format(
                h))
        vicecaptaintemp = cursor.fetchall()
        vicecaptain = vicecaptaintemp[0][0]
        vicecapmaxvotes = str(vicecaptaintemp[0][1])
        cursor.execute('select * from student where Name=?', (vicecaptain,))
        vicecapdetailstemp = cursor.fetchall()
        vicecapdetails = vicecapdetailstemp[0]
        ttk.Label(all_winners_frame, text='House Vice Captain', font=("Helvetica", 20, "bold"), relief="solid",
                  anchor="center", borderwidth=0.5, padding=(5, 3)).grid(row=start_row + 1, column=0, sticky="nsew")
        Name = vicecapdetails[1]
        ttk.Label(all_winners_frame, text=Name, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=1, sticky="nsew")
        ClassSec = str(vicecapdetails[2]) + vicecapdetails[3]
        ttk.Label(all_winners_frame, text=ClassSec, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=2, sticky="nsew")
        House = vicecapdetails[4]
        ttk.Label(all_winners_frame, text=House, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=3, sticky="nsew")
        Votes = vicecapmaxvotes
        ttk.Label(all_winners_frame, text=Votes, relief="solid", anchor="center", borderwidth=0.5, padding=(5, 3),
                  font=("Helvetica", 20)).grid(row=start_row + 1, column=4, sticky="nsew")
        start_row += 1
    for header in range(len(['Post', 'Name', "Class & Section", 'House', "Votes"])):
        all_winners_frame.grid_columnconfigure(header, weight=1)
    ttk.Button(all_winners_frame, text="Exit",
               command=lambda: (winners_printable_frame.pack_forget(), admin_frame.pack(fill="both", expand=True)),
               style='TButton').grid(row=start_row + 2, column=0, columnspan=5, pady=5)
    ttk.Button(all_winners_frame, text="Export CSV", command=export_winners_to_csv).grid(row=start_row + 1, column=0, columnspan=5, pady=5)

def show_winners_table():
    admin_frame.pack_forget()
    winners_table_frame.pack(fill="both", expand="yes")
    window.title('WINNERS')
    load_winner()

def load_winner():
    winners_tree.delete(*winners_tree.get_children())
    cursor.execute('''
    SELECT n.Name, n.Position, n.Votecount, v.Class, v.Section
    FROM nominees n
    JOIN student v ON v.Name = n.Name
    JOIN (
        SELECT position, MAX(Votecount) AS max_votes
        FROM nominees
        WHERE position NOT IN ('House Captain', 'House Vice Captain')
        GROUP BY position
    ) AS winners
    ON n.Position = winners.position AND n.Votecount = winners.max_votes
''')
    for row in cursor.fetchall():
        winners_tree.insert("", "end", values=row)
    cursor.execute('''SELECT n.Name, n.Position, n.Votecount, n.House, v.Class, v.Section FROM nominees n JOIN student v ON n.Name = v.Name
    JOIN (SELECT Position, House, MAX(Votecount) AS max_votes FROM nominees WHERE Position IN ('House Captain', 'House Vice Captain')
    GROUP BY Position, House) AS winners ON n.Position = winners.Position AND n.House = winners.House AND n.Votecount = winners.max_votes ORDER BY n.House, n.Position''')
    for row in cursor.fetchall():
        if row[3] == 'Ruby':
            winners_tree.insert("", "end", values=row[:3] + row[4:], tags=('Red',))
        if row[3] == 'Sapphire':
            winners_tree.insert("", "end", values=row[:3] + row[4:], tags=('Blue',))
        if row[3] == 'Topaz':
            winners_tree.insert("", "end", values=row[:3] + row[4:], tags=('Yellow',))
        if row[3] == 'Emerald':
            winners_tree.insert("", "end", values=row[:3] + row[4:], tags=('Green',))

def load_voters():
    voters_tree.delete(*voters_tree.get_children())
    cursor.execute("SELECT * FROM student")
    for row in cursor.fetchall():
        voters_tree.insert("", "end", values=row)

def add_voter():
    popup = tk.Toplevel(window)
    popup.configure(background="#D9D9D9")
    popup.title("Add Voter")
    entries = {}
    house_choices = ['Ruby', 'Emerald', 'Sapphire', 'Topaz']

    for col in ['USN_No', 'Name', 'Class', 'Section']:
        ttk.Label(popup, text=col).pack()
        e = ttk.Entry(popup)
        e.pack(padx=5, pady=5)
        entries[col] = e

    ttk.Label(popup, text="House").pack()
    house_var = tk.StringVar()
    house_dropdown = ttk.Combobox(popup, textvariable=house_var, values=house_choices, state="readonly")
    house_dropdown.pack(padx=5, pady=5)
    entries['House'] = house_var

    def save():
        usn = entries['USN_No'].get().strip()
        name = entries['Name'].get().strip()
        class_ = entries['Class'].get().strip()
        section = entries['Section'].get().strip()
        house = entries['House'].get().strip()

        if usn == "" or name == "" or class_ == "" or section == "" or house == "":
            messagebox.showerror("Error", "All fields must be filled.")
            return

        cursor.execute("SELECT USN_No from student")
        dist_usn = [i[0] for i in cursor.fetchall()]
        if usn in dist_usn:
            messagebox.showerror("Error", "Duplicate USN.")
            return

        for char in name:
            if not (char.isalpha() or char.isspace()):
                messagebox.showerror("Error", "Name must contain only alphabetic characters and spaces.")
                return

        if not class_.isdigit():
            messagebox.showerror("Error", "Class must contain only numbers.")
            return

        if len(section) != 1 or not section.isalpha():
            messagebox.showerror("Error", "Section must be a single alphabet character.")
            return

        if house not in house_choices:
            messagebox.showerror("Error", f"House must be one of: {', '.join(house_choices)}.")
            return

        cursor.execute(
            "INSERT INTO student (USN_No, Name, Class, Section, House) VALUES (?, ?, ?, ?, ?)",
            [usn, name, class_, section, house]
        )
        con.commit()
        popup.destroy()
        load_voters()

    ttk.Button(popup, text="Save", command=save).pack(pady=10)

def edit_voter(event=None):
    sel = voters_tree.selection()
    if not sel:
        return
    old = voters_tree.item(sel[0])['values']
    popup = tk.Toplevel(window)
    popup.configure(background="#D9D9D9")
    popup.title("Edit Voter")
    entries = {}
    for i, col in enumerate(["USN_No", "Name", "Class", "Section", "House", "voted"]):
        if col=='House':
            ttk.Label(popup, text='House').pack()
            e = ttk.Combobox(popup, values=['Ruby', 'Sapphire', 'Topaz', 'Emerald'], width=10)
            e.insert(0, old[i])
            e.pack(padx=5, pady=5)
        else:
            tk.Label(popup, text=col).pack()
            e = ttk.Entry(popup)
            e.insert(0, old[i])
            e.pack(padx=5, pady=5)
            if col == "voted":
                e.config(state='disabled')
        entries[col] = e

    def save():
        new = [entries[c].get() for c in entries]
        new[2] = int(new[2])
        del new[5]
        del old[5]

        cursor.execute("""
            UPDATE student SET USN_No=?, Name=?, Class=?, Section=?, House=?
             WHERE USN_No=? AND Name=? AND Class=? AND Section=? AND House=?
        """, new + old)
        con.commit()
        popup.destroy()
        voters_tree.selection_remove(voters_tree.selection())
        load_voters()

    tk.Button(popup, text="Save", command=save).pack()

def load_voters_from_csv():
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")],
        title="Select Voter CSV File"
    )
    if not file_path:
        return

    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            expected_columns = {'USN_No', 'Name', 'Class', 'Section', 'House'}
            csv_columns = set(reader.fieldnames)

            if not expected_columns.issubset(csv_columns):
                raise ValueError(
                    "CSV must contain only these columns: usn_no, name, class, section, house.\nNo extra columns like 'voted' are allowed.")

            cursor.execute("DELETE FROM student")

            for row in reader:
                cursor.execute(
                    "INSERT INTO student (USN_No, Name, Class, Section, House) VALUES (?, ?, ?, ?, ?)",
                    (row['USN_No'], row['Name'], row['Class'], row['Section'], row['House'])
                )
                con.commit()

        con.commit()
        load_voters()
        messagebox.showinfo("Success", "Voters loaded successfully from CSV.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV:\n{e}")
    cursor.execute("UPDATE nominees SET Votecount=0")
    con.commit()
    cursor.execute("UPDATE student SET voted='Not Voted'")
    con.commit()
    load_nominees()
    load_voters()

def delete_voter():
    sel = voters_tree.selection()
    if not sel:
        return
    val = voters_tree.item(sel[0])['values']
    cursor.execute("DELETE FROM student WHERE USN_No=? AND Name=? AND Class=? AND Section=? AND House=?", val[:5])
    con.commit()
    load_voters()


def load_nominees():
    nominee_tree.delete(*nominee_tree.get_children())
    cursor.execute("SELECT * FROM nominees")
    for row in cursor.fetchall():
        nominee_tree.insert("", "end", values=row)


def add_nominee():
    popup = tk.Toplevel(window)
    popup.configure(background="#D9D9D9")
    popup.title("Add Nominee")
    entries = {}
    house_choices = ['Ruby', 'Emerald', 'Sapphire', 'Topaz']

    for col in ["Name", "Position"]:
        ttk.Label(popup, text=col).pack()
        e = ttk.Entry(popup)
        e.pack(padx=5, pady=5)
        entries[col] = e

    ttk.Label(popup, text="House").pack()
    house_var = tk.StringVar()
    house_dropdown = ttk.Combobox(popup, textvariable=house_var, values=house_choices, state="readonly")
    house_dropdown.pack(padx=5, pady=5)
    entries['House'] = house_var

    def save():
        name = entries['Name'].get().strip()
        position = entries['Position'].get().strip()
        house = entries['House'].get().strip()

        if name == "" or position == "" or house == "":
            messagebox.showerror("Error", "All fields must be filled.")
            return

        for char in name:
            if not (char.isalpha() or char.isspace()):
                messagebox.showerror("Error", "Name must contain only alphabetic characters and spaces.")
                return

        if house not in house_choices:
            messagebox.showerror("Error", f"House must be one of: {', '.join(house_choices)}.")
            return

        cursor.execute(
            "INSERT INTO nominees (Name, Position, House, Votecount) VALUES (?, ?, ?, 0)",
            [name, position, house]
        )
        con.commit()
        popup.destroy()
        load_nominees()

    ttk.Button(popup, text="Save", command=save).pack(pady=10)


def edit_nominee(event=None):
    sel = nominee_tree.selection()
    if not sel:
        return
    old = nominee_tree.item(sel[0])['values']
    popup = tk.Toplevel(window)
    popup.configure(background="#D9D9D9")
    popup.title("Edit Nominee")
    entries = {}
    for i, col in enumerate(["Name", "Position", "House", "Votecount"]):
        if col=='House':
            tk.Label(popup, text=col).pack()
            e = ttk.Combobox(popup, values=['Ruby', 'Emerald', 'Sapphire', 'Topaz'], width=10)
            e.insert(0, old[i])
            e.pack(padx=5, pady=5)
        else:
            tk.Label(popup, text=col).pack()
            e = ttk.Entry(popup)
            e.insert(0, old[i])
            e.pack(padx=5, pady=5)
            if col == "Position" or col == 'Votecount':
                e.config(state='disabled')
        entries[col] = e

    def save():
        new = [entries[c].get() for c in entries]
        cursor.execute("""
            UPDATE nominees SET Name=?, House=?
            WHERE Name=? AND Position=? AND House=?
        """, [new[0], new[2]] + old[:3])
        con.commit()
        popup.destroy()
        load_nominees()

    ttk.Button(popup, text="Save", command=save).pack()


def delete_nominee():
    sel = nominee_tree.selection()
    if not sel:
        return
    val = nominee_tree.item(sel[0])['values']
    print(val)
    cursor.execute("DELETE FROM nominees WHERE Name=? AND Position=? AND House=?", val[:3])
    con.commit()
    load_nominees()


def clear_votes():
    response = messagebox.askyesno("Confirm", "Are you sure you want to clear all votes?")
    if response:
        cursor.execute("UPDATE nominees SET Votecount=0")
        con.commit()
        cursor.execute("UPDATE student SET voted='Not Voted'")
        con.commit()
        load_nominees()
        load_voters()
    else:
        return


def show_candidates():
    popup = tk.Toplevel(window)
    popup.title("Show Candidates")
    popup.configure(background="#D9D9D9")
    positions = []
    cursor.execute("SELECT distinct position FROM nominees")
    for pos in cursor.fetchall():
        positions.append(pos[0])

    for i in positions:
        ttk.Label(popup, text=i, font=("Helvetica", 20, "bold")).pack()
        cursor.execute("SELECT name FROM nominees WHERE Position='{}'".format(i))
        L = cursor.fetchall()
        temp = []
        for j in L:
            temp.append(j)
        for k in temp:
            ttk.Label(popup, text=k[0], font=("Helvetica", 18)).pack()


def ask_class():
    details_frame.pack(fill="both", expand="yes")
    cursor.execute("SELECT distinct Class from student order by Class asc")
    distinct_classes = [row[0] for row in cursor.fetchall()]
    ttk.Label(details_frame, text="Class", font=("Arial", 30)).place(relx=0.2, rely=0.2, anchor="center")
    ttk.Combobox(details_frame, textvariable=chosen_class, values=distinct_classes, width=7, font=("Arial", 25), state="readonly").place(relx=0.4, rely=0.2,
                                                                                                   anchor="center")
    ttk.Button(details_frame, text='next', command=ask_section, style="TButton").place(relx=0.7, rely=0.2, anchor="center")


def ask_section():
    cursor.execute("SELECT distinct Section from student where Class=? order by Section asc", [chosen_class.get()])
    distinct_sections = [row[0] for row in cursor.fetchall()]
    ttk.Label(details_frame, text="Section", font=("Arial", 30)).place(relx=0.2, rely=0.35, anchor="center")
    ttk.Combobox(details_frame, textvariable=chosen_section, values=distinct_sections, width=7, font=("Arial", 25), state="readonly").place(relx=0.4,
                                                                                                      rely=0.35,
                                                                                                      anchor="center")
    ttk.Button(details_frame, text='next', command=ask_name, style="TButton").place(relx=0.7, rely=0.35, anchor="center")


def ask_name():
    cursor.execute("SELECT name from student WHERE Class=? and Section=? and voted='Not Voted' order by name asc",
                   [chosen_class.get(), chosen_section.get()])
    distinct_names = [row[0] for row in cursor.fetchall()]
    ttk.Label(details_frame, text="Name", font=("Arial", 30)).place(relx=0.2, rely=0.5, anchor="center")
    ttk.Combobox(details_frame, textvariable=chosen_name, values=distinct_names, width=10, font=("Arial", 25), state="readonly").place(relx=0.4, rely=0.5, anchor="center")
    ttk.Button(details_frame, text='Find house', command=show_house, style="TButton").place(relx=0.7, rely=0.5, anchor="center")

def show_house():
    global chosen_house
    cursor.execute("SELECT House from student where Class=? and Section=? and Name=?",
                   [chosen_class.get(), chosen_section.get(), chosen_name.get()])
    distinct_house = [row[0] for row in cursor.fetchall()]

    if distinct_house == []:
        messagebox.showerror("Error", "Please enter all of the information")
        return
    else:
        chosen_house = distinct_house[0]
    ttk.Label(details_frame, text="House:", font=("Arial", 30)).place(relx=0.2, rely=0.65, anchor="center")
    ttk.Label(details_frame, text='{}'.format(distinct_house[0]), font=("Arial", 30)).place(relx=0.4, rely=0.65, anchor="center")
    ttk.Button(details_frame, text='Submit', command=voting, style="TButton").place(relx=0.7, rely=0.65, anchor="center")

def voting():
    for widget in details_frame.winfo_children():
        widget.destroy()
    details_frame.pack_forget()
    voting_frame.pack(side="left", fill="both", expand=True)
    cursor.execute("SELECT distinct position from nominees")
    distinct_positions = [row[0] for row in cursor.fetchall()]
    positions = distinct_positions
    votes = {}
    candidates = {}
    vote_vars = {}
    position_frames = {}
    for dist_pos in distinct_positions:
        candidates[dist_pos] = ''
        frame = ttk.Frame(window)
        position_frames[dist_pos] = frame
    for a in candidates:
        if a == 'House Captain' or a == 'House Vice Captain':
            cursor.execute("SELECT name FROM nominees WHERE Position='{}' AND House='{}'".format(a, chosen_house))
            candidates[a] = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute("SELECT name FROM nominees WHERE Position='{}'".format(a))
            candidates[a] = [row[0] for row in cursor.fetchall()]

    def show_frame(index):
        global current_index
        current_index = index
        for frame in position_frames.values():
            frame.pack_forget()
        position_frames[positions[index]].pack(fill=tk.BOTH, expand=True)

    def submit_votes():

        for position, var in vote_vars.items():
            votes[position] = var.get()

        confirm = messagebox.askyesno("Confirm Vote",
                                      "Are you sure you want to submit your vote? You cannot vote again.")
        if not confirm:
            return
        for widget in voting_frame.winfo_children():
            widget.destroy()
        for i in votes:
            cursor.execute('UPDATE nominees SET Votecount=Votecount+1 WHERE Position=? AND Name=?', [i, votes[i]])
        cursor.execute("UPDATE student SET voted='Voted' WHERE Class=? AND Section=? AND Name=? AND House=?",
                       [chosen_class.get(), chosen_section.get(), chosen_name.get(), chosen_house])
        con.commit()

        for i in [chosen_class, chosen_section, chosen_name]:
            i.set('')
        for var in vote_vars.values():
            var.set("")

        messagebox.showinfo("Vote Submitted", "Thank you for voting!")

        def create_exitmenu():
            def vote_again():
                for widget in voting_frame.winfo_children():
                    widget.destroy()
                voting_frame.pack_forget()
                window.title("STUDENT COUNCIL ELECTIONS")
                ask_class()

            def exit_voting():
                get_password()
                global password

                def exit():
                    exit_entered = exit_password_entry.get()
                    if verify_password(exit_entered, password_exit):
                        for widget in voting_frame.winfo_children():
                            widget.destroy()
                        voting_frame.pack_forget()
                        show_menu()
                    else:
                        messagebox.showerror("Error", "Incorrect Password")
                        exit_password_entry.delete(0, tk.END)

                def exitmenu():
                    for widget in voting_frame.winfo_children():
                        widget.destroy()
                    create_exitmenu()

                for widget in voting_frame.winfo_children():
                    widget.destroy()
                ttk.Label(voting_frame, text="ENTER PASSWORD", font=("Arial", 40, "bold")).place(relx=0.5, rely=0.2,
                                                                                                 anchor="center")
                exit_password_entry = ttk.Entry(voting_frame, show="*", font=("Arial", 25))
                exit_password_entry.place(relx=0.4, rely=0.45, anchor="center")
                exit_password_entry.focus()
                exit_password_entry.bind("<Return>", lambda event: exit())
                ttk.Button(voting_frame, text="Exit", command=exit, style="TButton").place(relx=0.725, rely=0.45, anchor="center")
                ttk.Button(voting_frame, text="Back", command=exitmenu, style="TButton").place(relx=0.17, rely=0.85, anchor="center")

            ttk.Label(voting_frame, text="DO YOU WANT TO?", font=("Arial", 40, "bold")).place(relx=0.5, rely=0.4,
                                                                                              anchor="center")
            ttk.Button(voting_frame, text="Exit", command=exit_voting, style="TButton", width=7).place(relx=0.385, rely=0.613, anchor="center")
            ttk.Button(voting_frame, text="Submit Again", command=vote_again, style="TButton").place(relx=0.61, rely=0.613,
                                                                                    anchor="center")
        create_exitmenu()

    def next_with_validation(current_index):
        pos = positions[current_index]
        if vote_vars[pos].get() == "":
            messagebox.showwarning("Incomplete", f"Please vote for {pos} before continuing.")
        else:
            show_frame(current_index + 1)

    for i, position in enumerate(positions):
        frame = ttk.Frame(voting_frame)
        position_frames[position] = frame

        ttk.Label(frame, text=position, font=("Arial", 50, "bold")).pack(pady=(50, 20))

        var = tk.StringVar()
        vote_vars[position] = var

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=30)

        for candidate in candidates[position]:
            ttk.Radiobutton(
                btn_frame,
                text=candidate,
                value=candidate,
                variable=var,
                style="Formal.TRadiobutton"
            ).pack(side="left", padx=30)

        nav_frame = ttk.Frame(frame)
        nav_frame.pack(pady=50)

        if i > 0:
            ttk.Button(nav_frame, text="Previous", command=lambda idx=i: show_frame(idx - 1), style="TButton").pack(side="left", padx=20)
        else:
            ttk.Label(nav_frame, text="", width=10).pack(side="left", padx=20)


        if i < len(positions) - 1:
            ttk.Button(nav_frame, text="Next", command=lambda idx=i: next_with_validation(idx), style="TButton").pack(side="right", padx=20)
        else:
            ttk.Button(nav_frame, text="Submit", command=submit_votes, style="TButton").pack(side="right", padx=20)

    show_frame(0)


window = tk.Tk()
window.configure(background="#F4F7FB")
window.title("STUDENT COUNCIL ELECTIONS")
window.attributes('-fullscreen', True)


style = ttk.Style()
style.theme_use("clam")

# Overall background
style.configure("TFrame", background="#F4F7FB")
style.configure("TLabel", font=("Arial", 25), background="#F4F7FB", foreground="#1F2937")

# Standard buttons
style.configure(
    "TButton",
    font=("Arial", 25, "bold"),
    padding=(14, 10),
    background="#E5E7EB",
    foreground="#1F2937",
    borderwidth=0,
    relief="flat"
)
style.map(
    "TButton",
    background=[("active", "#D1D5DB"), ("pressed", "#C7CDD6")]
)

# Large menu/admin buttons
style.configure(
    "Formal.TButton",
    font=("Arial", 30, "bold"),
    padding=20,
    background="#2563EB",
    foreground="white",
    borderwidth=0,
    relief="flat"
)
style.map(
    "Formal.TButton",
    background=[("active", "#1D4ED8"), ("pressed", "#1E40AF")]
)

# Voting candidate options
style.configure(
    "Formal.TRadiobutton",
    font=("Arial", 30),
    padding=10,
    background="#F4F7FB",
    foreground="#1F2937"
)

# Dropdowns
style.configure(
    "TCombobox",
    font=("Arial", 25),
    padding=8,
    fieldbackground="white",
    background="white",
    foreground="#1F2937"
)

# Tables
style.configure(
    "Treeview",
    rowheight=36,
    font=("Arial", 16),
    background="white",
    fieldbackground="white",
    foreground="#1F2937"
)
style.configure(
    "Treeview.Heading",
    font=("Arial", 18, "bold"),
    background="#1E3A8A",
    foreground="white",
    relief="flat"
)
style.map(
    "Treeview",
    background=[("selected", "#BFDBFE")],
    foreground=[("selected", "#1E3A8A")]
)

# Smaller back buttons
style.configure(
    "Small.TButton",
    font=("Arial", 16, "bold"),
    padding=10,
    background="#E5E7EB",
    foreground="#1F2937",
    borderwidth=0
)


menu_frame = ttk.Frame(window)
menu_frame.pack(fill="both", expand="yes")

ttk.Label(menu_frame, text="STUDENT COUNCIL ELECTIONS", font=("Arial", 60, "bold"), justify='center').place(relx=0.5, rely=0.3,anchor="center")
ttk.Button(menu_frame, text="ADMIN", command=show_login, style='Formal.TButton').place(relx=0.5, rely=0.55, anchor="center")
ttk.Button(menu_frame, text="VOTING", command=show_voting, style='Formal.TButton').place(relx=0.5, rely=0.7, anchor="center")
ttk.Button(menu_frame, text='EXIT', command=lambda: window.destroy(), style='Formal.TButton').place(relx=0.5, rely=0.85, anchor="center")

login_frame = ttk.Frame(window)
ttk.Label(login_frame, text="Enter Password", font=("Arial", 40, "bold")).place(relx=0.5, rely=0.2, anchor="center")
password_entry = ttk.Entry(login_frame, show="*", font=("Arial", 25))
password_entry.place(relx=0.35, rely=0.5, anchor="center")
ttk.Button(login_frame, text="Login", command=show_admin, style='Formal.TButton').place(relx=0.73, rely=0.5, anchor="center")
password_entry.bind("<Return>", lambda e: show_admin())
ttk.Button(login_frame, text="Back", command=show_menu, style='Formal.TButton').place(relx=0.15, rely=0.9, anchor="center")

admin_frame = ttk.Frame(window)

ttk.Label(admin_frame, text="ADMIN PANEL", font=("Arial", 35, "bold")).place(relx=0.5, rely=0.17,anchor="center")
ttk.Button(admin_frame, text="View Voters", command=show_voters, style='Formal.TButton').place(relx=0.5, rely=0.31, anchor="center")
ttk.Button(admin_frame, text="View Candidates", command=show_nominees, style='Formal.TButton').place(relx=0.5, rely=0.43, anchor="center")
ttk.Button(admin_frame, text="View Winners", command=show_winners, style='Formal.TButton').place(relx=0.5, rely=0.55, anchor="center")
ttk.Button(admin_frame, text="Clear Votecount", command=clear_votes, style='Formal.TButton').place(relx=0.5, rely=0.67, anchor="center")
ttk.Button(admin_frame, text="Change Passwords", command=change_password, style='Formal.TButton').place(relx=0.5, rely=0.79, anchor="center")
ttk.Button(admin_frame, text="Exit", command=show_menu, style='Formal.TButton').place(relx=0.1, rely=0.9, anchor="center")

voters_frame = ttk.Frame(window)

voters_buttons = ttk.Frame(voters_frame)
voters_buttons.pack(side=tk.TOP, fill=tk.X, pady=5)
ttk.Button(voters_buttons, text="Add", command=add_voter, style='TButton').pack(side=tk.LEFT, padx=(5,2))
ttk.Button(voters_buttons, text="CSV import", command=load_voters_from_csv, style='TButton').pack(side=tk.LEFT, padx=2)
ttk.Button(voters_buttons, text="Delete", command=delete_voter, style='TButton').pack(side=tk.LEFT, padx=2)

voters_filter_frame = ttk.Frame(voters_buttons)
voters_filter_frame.pack(side=tk.LEFT, expand=True, padx=20)

house_var = tk.StringVar()
section_var = tk.StringVar()
class_var = tk.StringVar()
voted_var = tk.StringVar()

ttk.Label(voters_filter_frame, text="Class", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
ttk.Entry(voters_filter_frame, textvariable=class_var, width=7, font=("Arial", 14)).pack(side=tk.LEFT, padx=5)

ttk.Label(voters_filter_frame, text="Section", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
ttk.Entry(voters_filter_frame, textvariable=section_var, width=7, font=("Arial", 14)).pack(side=tk.LEFT, padx=5)

ttk.Label(voters_filter_frame, text="House", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
ttk.Combobox(voters_filter_frame, textvariable=house_var, values=["Emerald", "Ruby", "Sapphire", "Topaz"], width=9, font=("Arial", 14), state="readonly").pack(side=tk.LEFT, padx=5)

ttk.Label(voters_filter_frame, text="If Voted", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
ttk.Combobox(voters_filter_frame, textvariable=voted_var, values=["Yes", "No"], width=7, font=("Arial", 14), state="readonly").pack(side=tk.LEFT, padx=5)


def apply_filters():
    query = "SELECT * FROM student WHERE 1=1"
    params = []

    if class_var.get():
        query += " AND Class=?"
        params.append(class_var.get())

    if section_var.get():
        query += " AND Section=?"
        params.append(section_var.get())

    if house_var.get():
        query += " AND House=?"
        params.append(house_var.get())

    if voted_var.get() == "Yes":
        query += " AND voted='Voted'"
    elif voted_var.get() == "No":
        query += " AND voted='Not Voted'"

    voters_tree.delete(*voters_tree.get_children())
    cursor.execute(query, params)
    for row in cursor.fetchall():
        voters_tree.insert("", "end", values=row)

voters_filter_buttons = ttk.Frame(voters_buttons)
voters_filter_buttons.pack(side=tk.LEFT, expand=True)
ttk.Button(voters_filter_buttons, text="Apply", command=apply_filters, style='TButton').pack(side=tk.LEFT, padx=5)
ttk.Button(voters_filter_buttons, text="Clear",
           command=lambda: [class_var.set(""), section_var.set(""), voted_var.set(""), house_var.set(""),
                            load_voters()], style='TButton').pack(side=tk.LEFT)

voters_tree = ttk.Treeview(voters_frame, columns=("USN_No", "Name", "Class", "Section", "House", "voted"),
                           show="headings")
for col in ("USN_No", "Name", "Class", "Section", "House", "voted"):
    voters_tree.heading(col, text=col)
    voters_tree.column(col, width=120, anchor="center")
voters_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 35))
voters_tree.bind("<Double-1>", edit_voter)
votersvsb = ttk.Scrollbar(voters_tree, orient="vertical", command=voters_tree.yview)
voters_tree.configure(yscrollcommand=votersvsb.set)
votersvsb.pack(side="right", fill="y")

voters_back_frame = ttk.Frame(voters_frame)
voters_back_frame.pack(side=tk.BOTTOM, pady=10)
ttk.Button(voters_back_frame, text="Back", command=back_menu, style='Small.TButton').pack(side=tk.LEFT)


position_var = tk.StringVar()
nom_house_var = tk.StringVar()
nominee_frame = ttk.Frame(window)
nominee_buttons = ttk.Frame(nominee_frame)
nominee_buttons.pack(side=tk.TOP, fill=tk.X, pady=5)
ttk.Button(nominee_buttons, text="Add Nominee", command=add_nominee, style='TButton').pack(side=tk.LEFT, padx=(5, 2))
ttk.Button(nominee_buttons, text="Delete", command=delete_nominee, style='TButton').pack(side=tk.LEFT, padx=2)

nominee_filter_frame = ttk.Frame(nominee_buttons)
nominee_filter_frame.pack(side=tk.LEFT, expand=True, padx=20)
ttk.Label(nominee_filter_frame, text="Position", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
ttk.Entry(nominee_filter_frame, textvariable=position_var, width=10, font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
ttk.Label(nominee_filter_frame, text="House Nominees", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
ttk.Combobox(nominee_filter_frame, textvariable=nom_house_var, values=["Emerald", "Ruby", "Sapphire", "Topaz"], width=9, font=("Arial", 14), state="readonly").pack(side=tk.LEFT, padx=5)


def nom_apply_filters():
    query = "SELECT * FROM nominees WHERE 1=1"
    params = []

    if position_var.get():
        query += " AND Position=?"
        params.append(position_var.get())

    if nom_house_var.get():
        query += " AND House=? AND position in ('House Captain','House Vice Captain')"
        params.append(nom_house_var.get())

    nominee_tree.delete(*nominee_tree.get_children())
    cursor.execute(query, params)
    for row in cursor.fetchall():
        nominee_tree.insert("", "end", values=row)

nominee_filter_buttons = ttk.Frame(nominee_buttons)
nominee_filter_buttons.pack(side=tk.LEFT, expand=True)
ttk.Button(nominee_filter_buttons, text="Apply", command=nom_apply_filters, style='TButton').pack(side=tk.LEFT, padx=5)
ttk.Button(nominee_filter_buttons, text="Clear",
           command=lambda: [position_var.set(""), nom_house_var.set(""), load_nominees()], style='TButton').pack(side=tk.LEFT)

nominee_tree = ttk.Treeview(nominee_frame, columns=("Name", "Position", "House", "Votecount"), show="headings")
for col in ("Name", "Position", "House", "Votecount"):
    nominee_tree.heading(col, text=col)
    nominee_tree.column(col, width=120, anchor="center")
nominee_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 30))
nominee_tree.bind("<Double-1>", edit_nominee)
nomineevsb = ttk.Scrollbar(nominee_tree, orient="vertical", command=nominee_tree.yview)
nominee_tree.configure(yscrollcommand=nomineevsb.set)
nomineevsb.pack(side="right", fill="y")

nominee_back_frame = ttk.Frame(nominee_frame)
nominee_back_frame.pack(side=tk.BOTTOM, pady=10)
ttk.Button(nominee_back_frame, text="Back", command=back_menu, style='Small.TButton').pack(side=tk.LEFT)


winners_printable_frame = ttk.Frame(window)
winners_table_frame = ttk.Frame()
winners_tree = ttk.Treeview(winners_table_frame, columns=("name", "position", "votecount", "class", "section"), show="headings")
for col in ("name", "position", "votecount", "class", "section"):
    winners_tree.heading(col, text=col)
    winners_tree.column(col, width=200, anchor="center")
winners_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 35))
winners_tree.tag_configure("Red", background="#FFCCCC")
winners_tree.tag_configure("Blue", background="#CCE0FF")
winners_tree.tag_configure("Green", background="#CCFFCC")
winners_tree.tag_configure("Yellow", background="#FFFFCC")
winners_back_frame = ttk.Frame(winners_table_frame)
winners_back_frame.pack(side=tk.BOTTOM, pady=10)
ttk.Button(winners_back_frame, text="Back", command=back_menu, style='Small.TButton').pack(side=tk.LEFT)

details_frame = ttk.Frame(window)
voting_frame = ttk.Frame(window)
chosen_class = tk.StringVar()
chosen_section = tk.StringVar()
chosen_name = tk.StringVar()
chosen_house = tk.StringVar()

window.mainloop()
con.close()

