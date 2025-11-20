import tkinter as tk
from tkinter import messagebox

def calculate_emi(principal, annual_interest_rate, tenure_years):
    """
    Calculate the Equated Monthly Installment (EMI) for a loan.

    Args:
        principal (float): Loan amount.
        annual_interest_rate (float): Annual interest rate (percent).
        tenure_years (float): Loan period in years.

    Returns:
        float: EMI rounded to 2 decimals.
    """
    P = principal
    R = annual_interest_rate / 12 / 100
    N = tenure_years * 12

    if R == 0:
        return round(P / N, 2)

    emi = (P * R * (1 + R) ** N) / ((1 + R) ** N - 1)
    return round(emi, 2)


# ------------------------ GUI WINDOW ------------------------

root = tk.Tk()
root.title("Loan EMI Calculator")
root.geometry("420x350")
root.resizable(False, False)

# Heading
tk.Label(root, text="Loan EMI Calculator", font=("Arial", 18, "bold")).pack(pady=15)

# Input Frame
frame = tk.Frame(root)
frame.pack(pady=10)

# Principal
tk.Label(frame, text="Loan Amount (P):", font=("Arial", 12)).grid(row=0, column=0, pady=8, sticky="w")
entry_principal = tk.Entry(frame, width=25)
entry_principal.grid(row=0, column=1)

# Annual Interest
tk.Label(frame, text="Annual Interest Rate (%):", font=("Arial", 12)).grid(row=1, column=0, pady=8, sticky="w")
entry_interest = tk.Entry(frame, width=25)
entry_interest.grid(row=1, column=1)

# Tenure
tk.Label(frame, text="Tenure in Years:", font=("Arial", 12)).grid(row=2, column=0, pady=8, sticky="w")
entry_years = tk.Entry(frame, width=25)
entry_years.grid(row=2, column=1)

# Result Label
label_result = tk.Label(root, text="Your EMI: ₹0.00", font=("Arial", 15, "bold"))
label_result.pack(pady=15)


# ------------------------ EMI Button Logic ------------------------

def on_calculate():
    try:
        P = float(entry_principal.get())
        R = float(entry_interest.get())
        Y = float(entry_years.get())

        emi = calculate_emi(P, R, Y)
        label_result.config(text=f"Your EMI: ₹{emi}")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values!")


# Button
tk.Button(
    root,
    text="Calculate EMI",
    font=("Arial", 14),
    command=on_calculate,
    width=20,
    bg="black",
    fg="white"
).pack(pady=5)


# ------------------------ RUN WINDOW ------------------------
root.mainloop()


# ------------------------ TEST CASES ------------------------

# Uncomment to test without GUI:
# print(calculate_emi(500000, 10, 10))
# print(calculate_emi(120000, 0, 1))
# print(calculate_emi(300000, 18, 5))
# print(calculate_emi(750000, 8, 30))
# print(calculate_emi(1000, 5, 1))
