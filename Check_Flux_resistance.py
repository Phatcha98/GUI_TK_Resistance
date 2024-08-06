import tkinter as tk
from tkinter import *
import pandas as pd
import tkinter.messagebox as messagebox
from datetime import datetime
import psycopg2
import time

window = tk.Tk()
window.option_add('*font','impack 13') 
window.title("Check Flux Resistance")
window.geometry("600x310")

win = tk.Label(window)
win.grid(row=0, column=0)

Label1 = tk.Label(window, text="Lot no:")
Label1.grid(row=1, column=0)
Label1_text = tk.StringVar()
el1 = tk.Entry(window, textvariable=Label1_text, width=25)
el1.grid(row=1, column=1, columnspan=5, sticky='WE', padx=3, pady=3, ipadx=3, ipady=3)

win = tk.Label(window)
win.grid(row=2, column=0)

Label2 = tk.Label(window, text="Operator ID:")
Label2.grid(row=3, column=0)
Label2_text = tk.StringVar()
el2 = tk.Entry(window, textvariable=Label2_text, width=25)
el2.grid(row=3, column=1, columnspan=5, sticky='WE', padx=3, pady=3, ipadx=3, ipady=3)

win = tk.Label(window)
win.grid(row=5, column=0)

Label3 = tk.Label(window, text="Appearance check")
Label3.grid(row=4, column=2)

check1 = StringVar()
ok_1 = Radiobutton(window,text ="OK", indicatoron=0,variable=check1,value="OK",bg='#33FF66',width=12)
ok_1.grid(row=6 ,column=1,\
padx=3, pady=3, ipadx=3, ipady=3)
ng_1 = Radiobutton(window,text ="NG", indicatoron=0,variable=check1,value="NG",bg='#FF0000',width=12)
ng_1.grid(row=6 ,column=4,\
padx=3, pady=3, ipadx=3, ipady=3)

win = tk.Label(window)
win.grid(row=7, column=0)

def save():
    check = check1.get()
    dt0 = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    dt1 = Label1_text.get()
    dt2 = Label2_text.get()

    connection = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="fujikura",
        database="postgres"
    )
    cursor = connection.cursor()
    
    cursor.execute("SELECT lot_no FROM public.\"ok2s_flux_resistance\" WHERE lot_no = %s", (dt1,))
    result = cursor.fetchone()

    if result is not None:
        if check == "OK":
            cursor.execute("UPDATE public.\"ok2s_flux_resistance\" SET app_check = %s, app_check_date = %s, op_id_2 = %s WHERE lot_no = %s", (True, dt0, dt2, dt1))
            connection.commit()
            messagebox.showinfo("Success", "Data saved and app_check updated.")
        else:
            cursor.execute("UPDATE public.\"ok2s_flux_resistance\" SET app_check = %s, app_check_date = %s, op_id_2 = %s WHERE lot_no = %s", (False, dt0, dt2, dt1))
            connection.commit()
            messagebox.showinfo("Success", "Data saved and app_check updated.")
    else:
        messagebox.showinfo("Error", "Lot no not found")

    connection.close()
    ok_1.deselect()
    ng_1.deselect()

    for widget in window.winfo_children():
        if isinstance(widget,Entry):  
            widget.delete(0,'end') 
            widget.insert(0,'') 
    pass

def reset():
    ok_1.deselect()
    ng_1.deselect()
    for widget in window.winfo_children():
            if isinstance(widget,Entry):  
                widget.delete(0,'end') 
                widget.insert(0,'') 
    pass


b7=Button(window,text="SAVE",width=12,bg="#00bcd4", command=save)
b7.grid(row=8,column=1,\
padx=3, pady=3, ipadx=3, ipady=3) 

b8=Button(window,text="RESET",width=12,bg="#FF9900",command=reset)
b8.grid(row=8,column=4,\
padx=3, pady=3, ipadx=3, ipady=3) 

window.mainloop()