# hospital_billing_fixed.py
# Final Version — Displays all patient details + bills (works even if old DB exists)

import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox

# -----------------------------------
# 1. Fresh Database Setup
# -----------------------------------
def setup_database():
    # Remove old database so every run is clean
    if os.path.exists("hospital_billing.db"):
        os.remove("hospital_billing.db")

    conn = sqlite3.connect("hospital_billing.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE Patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE Services (
        service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        cost REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE Bills (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        service_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
        FOREIGN KEY (service_id) REFERENCES Services(service_id)
    )
    """)

    # Insert sample data
    cursor.executemany("INSERT INTO Patients (name, age, gender) VALUES (?, ?, ?)", [
        ("Rahul Sharma", 30, "Male"),
        ("Priya Singh", 25, "Female"),
        ("Amit Verma", 45, "Male")
    ])

    cursor.executemany("INSERT INTO Services (service_name, cost) VALUES (?, ?)", [
        ("X-Ray", 500.00),
        ("Blood Test", 300.00),
        ("MRI Scan", 2500.00),
        ("Consultation", 400.00)
    ])

    cursor.executemany("INSERT INTO Bills (patient_id, service_id, quantity) VALUES (?, ?, ?)", [
        (1, 1, 1),
        (1, 4, 2),
        (2, 2, 1),
        (2, 4, 1),
        (3, 3, 1),
        (3, 4, 1)
    ])

    conn.commit()
    conn.close()

# -----------------------------------
# 2. Query - All Bills
# -----------------------------------
def get_all_bills():
    conn = sqlite3.connect("hospital_billing.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        p.name AS Patient_Name,
        p.age AS Age,
        p.gender AS Gender,
        s.service_name AS Service,
        b.quantity AS Quantity,
        s.cost AS Cost,
        (s.cost * b.quantity) AS Total
    FROM Bills b
    JOIN Patients p ON b.patient_id = p.patient_id
    JOIN Services s ON b.service_id = s.service_id
    ORDER BY p.name
    """)

    data = cursor.fetchall()
    conn.close()
    return data


# -----------------------------------
# 3. GUI
# -----------------------------------
def show_all_bills():
    records = get_all_bills()
    for i in tree.get_children():
        tree.delete(i)
    for row in records:
        tree.insert("", tk.END, values=row)
    if not records:
        messagebox.showwarning("Empty", "No billing records found.")
    else:
        messagebox.showinfo("Success", "All patient billing details loaded successfully!")

def show_total_bills():
    conn = sqlite3.connect("hospital_billing.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        p.name,
        SUM(s.cost * b.quantity) AS Total_Bill
    FROM Bills b
    JOIN Patients p ON b.patient_id = p.patient_id
    JOIN Services s ON b.service_id = s.service_id
    GROUP BY p.name
    """)
    data = cursor.fetchall()
    conn.close()

    totals_text = "\n".join([f"{name}: ₹{total:.2f}" for name, total in data])
    messagebox.showinfo("Total Bill per Patient", totals_text)


# -----------------------------------
# 4. Main GUI Setup
# -----------------------------------
def main():
    setup_database()

    global tree
    root = tk.Tk()
    root.title("🏥 Hospital Billing System")
    root.geometry("950x500")

    ttk.Label(root, text="Hospital Billing Details", font=("Arial", 16, "bold")).pack(pady=10)

    columns = ("Name", "Age", "Gender", "Service", "Quantity", "Cost", "Total")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(fill="both", expand=True, pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Show All Bills", command=show_all_bills).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Show Total per Patient", command=show_total_bills).grid(row=0, column=1, padx=10)
    ttk.Button(btn_frame, text="Exit", command=root.destroy).grid(row=0, column=2, padx=10)

    root.mainloop()


# -----------------------------------
# 5. Run
# -----------------------------------
if __name__ == "__main__":
    main()
