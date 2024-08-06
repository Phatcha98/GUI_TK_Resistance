import tkinter as tk
from tkinter import *
import pandas as pd
import tkinter.messagebox as messagebox
import serial
from datetime import datetime
import psycopg2
import time
from functools import partial

window = tk.Tk()
window.option_add('*font','impack 10') 
window.title("Flux Resistance")
window.geometry("710x620")

port = 'COM3'
baudrate = 9600
bytesize = serial.EIGHTBITS
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE

measurement_data = None
measurement = None
ser = None
is_measurement_ended = False
is_measurement_started = False
selected_entry = None

def read_measurement():
    try:
        global ser, measurement_data, is_measurement_ended, is_measurement_started
        ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, xonxoff=True)
        measurement_data = ser.readline()
        ser.close()
        if is_measurement_started and not is_measurement_ended:
            update_measurement()
    except serial.SerialException as e:
        messagebox.showerror("Serial Port Error", str(e))

def update_measurement():
    global measurement_data, measurement, is_measurement_ended, is_measurement_started
    if is_measurement_started and not is_measurement_ended:
        measurement_data = ser.readline()
        if measurement_data:
            measurement = float(measurement_data.decode())
            measurement_gui = "{:.2f}".format(measurement)
            if selected_entry:
                selected_entry.delete(0, tk.END)
                selected_entry.insert(tk.END, measurement_gui)
            window.after_idle(update_measurement)

def stop_measurement():
    global ser, is_measurement_ended
    if ser is not None:
        ser.close()
        ser = None
    is_measurement_ended = True

def start_measurement():
    global is_measurement_ended, is_measurement_started
    is_measurement_ended = False
    is_measurement_started = True
    read_measurement()
        
def handle_measurement(event=None):
    global measurement_data, measurement, is_measurement_started, selected_entry, ser
    if selected_entry is not None:
        ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, xonxoff=True)
        measurement_data = ser.readline()
        ser.close()
        if measurement_data:
            measurement = float(measurement_data.decode())
            measurement_gui = "{:.2f}".format(measurement)
            selected_entry.delete(0, tk.END)
            selected_entry.insert(tk.END, measurement_gui)
            if selected_entry in entry_fields1:
                entry_index = entry_fields1.index(selected_entry)
                if entry_index < len(entry_vars1):
                    entry_vars1[entry_index].set(measurement_gui)
            elif selected_entry in entry_fields2:
                entry_index = entry_fields2.index(selected_entry)
                if entry_index < len(entry_vars2):
                    entry_vars2[entry_index].set(measurement_gui)
            elif selected_entry in entry_fields3:
                entry_index = entry_fields3.index(selected_entry)
                if entry_index < len(entry_vars3):
                    entry_vars3[entry_index].set(measurement_gui)
            elif selected_entry in entry_fields4:
                entry_index = entry_fields4.index(selected_entry)
                if entry_index < len(entry_vars4):
                    entry_vars4[entry_index].set(measurement_gui)

def handle_entry_focus(event=None):
    global selected_entry
    selected_entry = event.widget
    handle_measurement() 

entry_vars1 = [tk.StringVar() for _ in range(5)]
entry_vars2 = [tk.StringVar() for _ in range(5)]
entry_vars3 = [tk.StringVar() for _ in range(5)]
entry_vars4 = [tk.StringVar() for _ in range(5)]

no_labels1 = [tk.Label(window, text=f"{i+1}") for i in range(5)]
no_labels2 = [tk.Label(window, text=f"{i+1}") for i in range(5)]
no_labels3 = [tk.Label(window, text=f"{i+1}") for i in range(5)]
no_labels4 = [tk.Label(window, text=f"{i+1}") for i in range(5)]

entry_fields1 = []
entry_fields2 = []
entry_fields3 = []
entry_fields4 = []

def create_entry_fields():
    if not entry_fields1:
        for i, no_label in enumerate(no_labels1):
            no_label.grid(row=i + 7, column=0, sticky='E')
            entry_field = tk.Entry(window, textvariable=entry_vars1[i], width=27)
            entry_field.grid(row=i + 7, column=1, sticky='W')
            entry_field.bind("<FocusIn>", handle_entry_focus)
            entry_fields1.append(entry_field)

    if not entry_fields2:
        for i, no_label in enumerate(no_labels2):
            no_label.grid(row=i + 13, column=0, sticky='E')
            entry_field = tk.Entry(window, textvariable=entry_vars2[i], width=27)
            entry_field.grid(row=i + 13, column=1, sticky='W')
            entry_field.bind("<FocusIn>", handle_entry_focus)
            entry_fields2.append(entry_field)

    if not entry_fields3:
        for i, no_label in enumerate(no_labels3):
            no_label.grid(row=i + 7, column=4, sticky='E')
            entry_field = tk.Entry(window, textvariable=entry_vars3[i], width=27)
            entry_field.grid(row=i + 7, column=5, sticky='W')
            entry_field.bind("<FocusIn>", handle_entry_focus)
            entry_fields3.append(entry_field) 

    if not entry_fields4:
        for i, no_label in enumerate(no_labels4):
            no_label.grid(row=i + 13, column=4, sticky='W')
            entry_field = tk.Entry(window, textvariable=entry_vars4[i], width=27)
            entry_field.grid(row=i + 13, column=5, sticky='W')
            entry_field.bind("<FocusIn>", handle_entry_focus)
            entry_fields4.append(entry_field)

    mg1 = []
    for i in range(5):
        label = tk.Label(window, text="mg.")
        label.grid(row=i + 7, column=3, sticky='W')
        mg1.append(label)

    mg2 = []
    for i in range(5):
        label = tk.Label(window, text="mg.")
        label.grid(row=i + 13, column=3, sticky='W')
        mg2.append(label)

    mg3 = []
    for i in range(5):
        label = tk.Label(window, text="mg.")
        label.grid(row=i + 7, column=6, sticky='W')
        mg3.append(label)

    mg4 = []
    for i in range(5):
        label = tk.Label(window, text="mg.")
        label.grid(row=i + 13, column=6, sticky='W')
        mg4.append(label)

    if entry_fields1:
        entry_fields1[0].focus_set()

    print(len(entry_fields1))

calculate_button_clicked = False
result_labels = []

def calculate_button_click():
    global calculate_button_clicked
    calculate_button_clicked = True
    calculate_differences()

def calculate_differences():
    for label in result_labels:
        label.destroy()
    result_labels.clear()  
    try:
        entry_value1 = float(entry_vars1[0].get())
        entry_value11 = float(entry_vars3[0].get())
        if entry_value1 and entry_value11:
            result_label1 = tk.Label(window, text="{:.2f}".format(entry_value1 - entry_value11))
            result_label1.grid(row=7, column=7)
            result_labels.append(result_label1)
    except ValueError:
        result_label1 = tk.Label(window, text="")
        result_label1.grid(row=7, column=7)
        result_labels.append(result_label1)

    try:
        entry_value2 = float(entry_vars1[1].get())
        entry_value12 = float(entry_vars3[1].get())
        if entry_value2 and entry_value12:
            result_label2 = tk.Label(window, text="{:.2f}".format(entry_value2 - entry_value12))
            result_label2.grid(row=8, column=7)
            result_labels.append(result_label2)
    except ValueError:
        result_label2 = tk.Label(window, text="")
        result_label2.grid(row=8, column=7)
        result_labels.append(result_label2)

    try:
        entry_value3 = float(entry_vars1[2].get())
        entry_value13 = float(entry_vars3[2].get())
        if entry_value3 and entry_value13:
            result_label3 = tk.Label(window, text="{:.2f}".format(entry_value3 - entry_value13))
            result_label3.grid(row=9, column=7)
            result_labels.append(result_label3)
    except ValueError:
        result_label3 = tk.Label(window, text="")
        result_label3.grid(row=9, column=7)
        result_labels.append(result_label3)

    try:
        entry_value4 = float(entry_vars1[3].get())
        entry_value14 = float(entry_vars3[3].get())
        if entry_value4 and entry_value14:
            result_label4 = tk.Label(window, text="{:.2f}".format(entry_value4 - entry_value14))
            result_label4.grid(row=10, column=7)
            result_labels.append(result_label4)
    except ValueError:
        result_label4 = tk.Label(window, text="")
        result_label4.grid(row=10, column=7)
        result_labels.append(result_label4)

    try:
        entry_value5 = float(entry_vars1[4].get())
        entry_value15 = float(entry_vars3[4].get())
        if entry_value5 and entry_value15:
            result_label5 = tk.Label(window, text="{:.2f}".format(entry_value5 - entry_value15))
            result_label5.grid(row=11, column=7)
            result_labels.append(result_label5)
    except ValueError:
        result_label5 = tk.Label(window, text="")
        result_label5.grid(row=11, column=7)
        result_labels.append(result_label5)

    try:
        entry_value6 = float(entry_vars2[0].get())
        entry_value16 = float(entry_vars4[0].get())
        if entry_value6 and entry_value16:
            result_label6 = tk.Label(window, text="{:.2f}".format(entry_value6 - entry_value16))
            result_label6.grid(row=13, column=7)
            result_labels.append(result_label6)
    except ValueError:
        result_label6 = tk.Label(window, text="")
        result_label6.grid(row=13, column=7)
        result_labels.append(result_label6)

    try:
        entry_value7 = float(entry_vars2[1].get())
        entry_value17 = float(entry_vars4[1].get())
        if entry_value7 and entry_value17:
            result_label7 = tk.Label(window, text="{:.2f}".format(entry_value7 - entry_value17))
            result_label7.grid(row=14, column=7)
            result_labels.append(result_label7)
    except ValueError:
        result_label7 = tk.Label(window, text="")
        result_label7.grid(row=14, column=7)
        result_labels.append(result_label7)

    try:
        entry_value8 = float(entry_vars2[2].get())
        entry_value18 = float(entry_vars4[2].get())
        if entry_value8 and entry_value18:
            result_label8 = tk.Label(window, text="{:.2f}".format(entry_value8 - entry_value18))
            result_label8.grid(row=15, column=7)
            result_labels.append(result_label8)
    except ValueError:
        result_label8 = tk.Label(window, text="")
        result_label8.grid(row=15, column=7)
        result_labels.append(result_label8)

    try:
        entry_value9 = float(entry_vars2[3].get())
        entry_value19 = float(entry_vars4[3].get())
        if entry_value9 and entry_value19:
            result_label9 = tk.Label(window, text="{:.2f}".format(entry_value9 - entry_value19))
            result_label9.grid(row=16, column=7)
            result_labels.append(result_label9)
    except ValueError:
        result_label9 = tk.Label(window, text="")
        result_label9.grid(row=16, column=7)
        result_labels.append(result_label9)

    try:
        entry_value10 = float(entry_vars2[4].get())
        entry_value20 = float(entry_vars4[4].get())
        if entry_value10 and entry_value20:
            result_label10 = tk.Label(window, text="{:.2f}".format(entry_value10 - entry_value20))
            result_label10.grid(row=17, column=7)
            result_labels.append(result_label10)
    except ValueError:
        result_label10 = tk.Label(window, text="")
        result_label10.grid(row=17, column=7)
        result_labels.append(result_label10)
    
calculate_button = tk.Button(window, text="Calculate", command=calculate_button_click, bg="#FF99FF")
calculate_button.grid(row=19, column=7)

for entry_field in entry_fields1 + entry_fields2 + entry_fields3 + entry_fields4:
    entry_field.bind("<FocusOut>", lambda event: calculate_differences())

for entry_field in entry_fields1 + entry_fields2 + entry_fields3 + entry_fields4:
    entry_field.bind("<Button-1>", handle_measurement)

Label9 = tk.Label(window, text="Weight Before", bg="#91a7ff",width=12)
Label9.grid(row=4,column=1, \
padx=6, pady=6, ipadx=6, ipady=6) 
Label10 = tk.Label(window, text="Weight After", bg="#00FF7F",width=12)
Label10.grid(row=4, column=5, \
padx=6, pady=6, ipadx=6, ipady=6) 
Label11 = tk.Label(window, text="Amount Flux", bg="#FFFF00",width=12)
Label11.grid(row=4, column=7, \
padx=6, pady=6, ipadx=6, ipady=6) 

Label1 = tk.Label(window, text="Product:")
Label1.grid(row=0, column=0)
Label1_text = tk.StringVar()
el1 = tk.Entry(window, textvariable=Label1_text, width=60)
el1.grid(row=0, column=1, columnspan=5, sticky='W', padx=3, pady=3, ipadx=3, ipady=3)

Label2 = tk.Label(window, text="Lot no:")
Label2.grid(row=1, column=0)
Label2_text = tk.StringVar()
el2 = tk.Entry(window, textvariable=Label2_text, width=60)
el2.grid(row=1, column=1, columnspan=5, sticky='W', padx=3, pady=3, ipadx=3, ipady=3)

Label3 = tk.Label(window, text="Link position:")
Label3.grid(row=2, column=0)
Label3_text = tk.StringVar()
el3 = tk.Entry(window, textvariable=Label3_text, width=60)
el3.grid(row=2, column=1, columnspan=5, sticky='W', padx=3, pady=3, ipadx=3, ipady=3)

win = tk.Label(window)
win.grid(row=3, column=0)

Label5 = tk.Label(window, text="Non-Cover FR-4")
Label5.grid(row=6, column=1)
Label6 = tk.Label(window, text="Cover FR-4")
Label6.grid(row=12, column=1)

Label5 = tk.Label(window, text="Non-Cover FR-4")
Label5.grid(row=6, column=5)
Label6 = tk.Label(window, text="Cover FR-4")
Label6.grid(row=12, column=5)

win = tk.Label(window)
win.grid(row=18, column=0)

Label7 = tk.Label(window, text="Operator ID:")
Label7.grid(row=19, column=0)
Label7_text = tk.StringVar()
el7 = tk.Entry(window, textvariable=Label7_text, width=25)
el7.grid(row=19, column=1, columnspan=5, sticky='WE', padx=3, pady=3, ipadx=3, ipady=3)

win = tk.Label(window)
win.grid(row=20, column=0)

Label8 = tk.Label(window, text="Machine:")
Label8.grid(row=21, column=0)
Label8_text = tk.StringVar()
el8 = tk.Entry(window, textvariable=Label8_text, width=25)
el8.grid(row=21, column=1, columnspan=5, sticky='WE', padx=3, pady=3, ipadx=3, ipady=3)

win = tk.Label(window)
win.grid(row=22, column=0)

ym = time.strftime("%Y/%m/%d")
class Clock:
    def __init__(self):
        self.time1 = ''
        self.time2 = time.strftime('%H:%M:%S')
        self.mFrame = Frame()
        self.mFrame.grid(row=0,column=7,sticky='E') 

        self.watch = Label(self.mFrame, text=self.time2)
        self.watch.pack()

        self.changeLabel() 

    def changeLabel(self): 
        self.time2 = time.strftime('%H:%M:%S')
        self.watch.configure(text=self.time2)
        self.mFrame.after(200, self.changeLabel) 

C=Clock()
Label(window,text=ym).grid(row=1, column=7,sticky='E')


entry_fields = entry_fields1 + entry_fields2

def add_to_database():
    dt0 = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    df1 = Label1_text.get()
    df2 = Label2_text.get()
    df3 = Label3_text.get()
    df7 = Label7_text.get()
    df8 = Label8_text.get()
    df10 = "Non-Cover FR-4"
    df11 = "Cover FR-4"
    before = 'Before'
    after = 'After'

    no_1_non_1 = float(entry_vars1[0].get()) if entry_vars1[0].get() else None
    no_2_non_1 = float(entry_vars1[1].get()) if entry_vars1[1].get() else None
    no_3_non_1 = float(entry_vars1[2].get()) if entry_vars1[2].get() else None
    no_4_non_1 = float(entry_vars1[3].get()) if entry_vars1[3].get() else None
    no_5_non_1 = float(entry_vars1[4].get()) if entry_vars1[4].get() else None

    no_1_cover_2 = float(entry_vars2[0].get()) if entry_vars2[0].get() else None
    no_2_cover_2 = float(entry_vars2[1].get()) if entry_vars2[1].get() else None
    no_3_cover_2 = float(entry_vars2[2].get()) if entry_vars2[2].get() else None
    no_4_cover_2 = float(entry_vars2[3].get()) if entry_vars2[3].get() else None
    no_5_cover_2 = float(entry_vars2[4].get()) if entry_vars2[4].get() else None

    no_1_non_3 = float(entry_vars3[0].get()) if entry_vars3[0].get() else None
    no_2_non_3 = float(entry_vars3[1].get()) if entry_vars3[1].get() else None
    no_3_non_3 = float(entry_vars3[2].get()) if entry_vars3[2].get() else None
    no_4_non_3 = float(entry_vars3[3].get()) if entry_vars3[3].get() else None
    no_5_non_3 = float(entry_vars3[4].get()) if entry_vars3[4].get() else None

    no_1_cover_4 = float(entry_vars4[0].get()) if entry_vars4[0].get() else None
    no_2_cover_4 = float(entry_vars4[1].get()) if entry_vars4[1].get() else None
    no_3_cover_4 = float(entry_vars4[2].get()) if entry_vars4[2].get() else None
    no_4_cover_4 = float(entry_vars4[3].get()) if entry_vars4[3].get() else None
    no_5_cover_4 = float(entry_vars4[4].get()) if entry_vars4[4].get() else None

    connection = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="fujikura",
        database="postgres"
    )
    cursor = connection.cursor()

    query = "INSERT INTO public.\"ok2s_flux_resistance\" (create_date, lot_no, link_position, test, \"type\", no_1, no_2, no_3, no_4, no_5, op_id_1, mc) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    if any([no_1_non_1, no_2_non_1, no_3_non_1, no_4_non_1, no_5_non_1]):
        data_out1 = (dt0, df2, df3, before, df10, no_1_non_1, no_2_non_1, no_3_non_1, no_4_non_1, no_5_non_1, df7, df8)
        cursor.execute(query, data_out1)
        connection.commit()

    if any([no_1_cover_2, no_2_cover_2, no_3_cover_2, no_4_cover_2, no_5_cover_2]):
        data_out2 = (dt0, df2, df3, before, df11, no_1_cover_2, no_2_cover_2, no_3_cover_2, no_4_cover_2, no_5_cover_2, df7, df8)
        cursor.execute(query, data_out2)
        connection.commit()

    if any([no_1_non_3, no_2_non_3, no_3_non_3, no_4_non_3, no_5_non_3]):
        data_out3 = (dt0, df2, df3, after, df10, no_1_non_3, no_2_non_3, no_3_non_3, no_4_non_3, no_5_non_3, df7, df8)
        cursor.execute(query, data_out3)
        connection.commit()

    if any([no_1_cover_4, no_2_cover_4, no_3_cover_4, no_4_cover_4, no_5_cover_4]):
        data_out4 = (dt0, df2, df3, after, df11, no_1_cover_4, no_2_cover_4, no_3_cover_4, no_4_cover_4, no_5_cover_4, df7, df8)
        cursor.execute(query, data_out4)
        connection.commit()

    connection.close()

    messagebox.showerror("Saved", " Saved to database")

    entry_vars1[0].set("")
    entry_vars1[1].set("")
    entry_vars1[2].set("")
    entry_vars1[3].set("")
    entry_vars1[4].set("")

    entry_vars2[0].set("")
    entry_vars2[1].set("")
    entry_vars2[2].set("")
    entry_vars2[3].set("")
    entry_vars2[4].set("")

    entry_vars3[0].set("")
    entry_vars3[1].set("")
    entry_vars3[2].set("")
    entry_vars3[3].set("")
    entry_vars3[4].set("")

    entry_vars4[0].set("")
    entry_vars4[1].set("")
    entry_vars4[2].set("")
    entry_vars4[3].set("")
    entry_vars4[4].set("")


def reset():
    for label in result_labels:
        label.config(text="")
    result_labels.clear()

    entry_vars1[0].set("")
    entry_vars1[1].set("")
    entry_vars1[2].set("")
    entry_vars1[3].set("")
    entry_vars1[4].set("")

    entry_vars2[0].set("")
    entry_vars2[1].set("")
    entry_vars2[2].set("")
    entry_vars2[3].set("")
    entry_vars2[4].set("")

    entry_vars3[0].set("")
    entry_vars3[1].set("")
    entry_vars3[2].set("")
    entry_vars3[3].set("")
    entry_vars3[4].set("")

    entry_vars4[0].set("")
    entry_vars4[1].set("")
    entry_vars4[2].set("")
    entry_vars4[3].set("")
    entry_vars4[4].set("")
    

b1 = tk.Button(window, text="SAVE", bg="#00FF7F", command=add_to_database,width=12)
b1.grid(row=23,column=1, padx=3, pady=3, ipadx=3, ipady=3)  
b2 = tk.Button(window, text="RESET", bg="#FF9900", command=reset,width=12)
b2.grid(row=23,column=5, padx=3, pady=3, ipadx=3, ipady=3) 

create_entry_fields()
calculate_differences()
window.after_idle(update_measurement)
window.mainloop()




