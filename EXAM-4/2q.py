# 2q_gui.py
# Synthetic Healthcare Dataset Generator with GUI (Tkinter)

import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# -------------------------------
# DATA GENERATION & PROCESSING
# -------------------------------

np.random.seed(42)

def generate_synthetic_healthcare(n=200, missing_frac=0.1):
    age = np.random.randint(18, 90, size=n).astype(float)
    systolic_bp = np.random.normal(120, 15, size=n).astype(float)
    diastolic_bp = np.random.normal(80, 10, size=n).astype(float)
    cholesterol = np.random.normal(200, 40, size=n).astype(float)
    glucose = np.random.normal(100, 30, size=n).astype(float)
    bmi = np.random.normal(27, 5, size=n).astype(float)

    gender = np.random.choice(['M', 'F', 'Other'], size=n, p=[0.48, 0.48, 0.04])
    diagnosis = np.random.choice(['Healthy', 'Diabetes', 'Hypertension', 'Both'],
                                 size=n, p=[0.5, 0.2, 0.25, 0.05])

    df = pd.DataFrame({
        'age': age,
        'systolic_bp': systolic_bp,
        'diastolic_bp': diastolic_bp,
        'cholesterol': cholesterol,
        'glucose': glucose,
        'bmi': bmi,
        'gender': gender,
        'diagnosis': diagnosis
    })

    numeric_cols = ['age', 'systolic_bp', 'diastolic_bp', 'cholesterol', 'glucose', 'bmi']
    for col in numeric_cols:
        mask = np.random.rand(n) < missing_frac
        df.loc[mask, col] = np.nan

    cat_mask = np.random.rand(n) < (missing_frac / 2)
    df.loc[cat_mask, 'diagnosis'] = np.nan

    return df

def impute_numeric_with_median(df, numeric_cols):
    df_copy = df.copy()
    medians = df_copy[numeric_cols].median()
    df_copy[numeric_cols] = df_copy[numeric_cols].fillna(medians)
    return df_copy

def min_max_scale(df, numeric_cols):
    scaled = df[numeric_cols].copy()
    for col in numeric_cols:
        col_min = scaled[col].min()
        col_max = scaled[col].max()
        if pd.isna(col_min) or pd.isna(col_max):
            scaled[col] = 0.0
        elif col_max == col_min:
            scaled[col] = 0.0
        else:
            scaled[col] = (scaled[col] - col_min) / (col_max - col_min)
    return scaled


# -------------------------------
# GUI SECTION
# -------------------------------

class HealthcareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Healthcare Dataset Generator")
        self.root.geometry("800x600")
        self.df_scaled = None

        # Input fields
        tk.Label(root, text="Number of Samples (n):").pack()
        self.n_entry = tk.Entry(root)
        self.n_entry.insert(0, "300")
        self.n_entry.pack()

        tk.Label(root, text="Missing Fraction (0–1):").pack()
        self.miss_entry = tk.Entry(root)
        self.miss_entry.insert(0, "0.12")
        self.miss_entry.pack()

        tk.Button(root, text="Generate Dataset", command=self.generate).pack(pady=5)
        tk.Button(root, text="Save to CSV", command=self.save_csv).pack(pady=5)

        self.text = tk.Text(root, height=20, wrap='none')
        self.text.pack(fill="both", expand=True)

    def generate(self):
        try:
            n = int(self.n_entry.get())
            missing = float(self.miss_entry.get())
            df = generate_synthetic_healthcare(n, missing)
            numeric_cols = ['age', 'systolic_bp', 'diastolic_bp', 'cholesterol', 'glucose', 'bmi']
            df_imputed = impute_numeric_with_median(df, numeric_cols)
            scaled = min_max_scale(df_imputed, numeric_cols)
            df_imputed[numeric_cols] = scaled
            self.df_scaled = df_imputed

            # Display sample
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, "Sample of Processed Dataset:\n")
            self.text.insert(tk.END, df_imputed.head(10).to_string(index=False))
            self.text.insert(tk.END, "\n\nRanges after scaling:\n")

            for col in numeric_cols:
                col_min = df_imputed[col].min()
                col_max = df_imputed[col].max()
                self.text.insert(tk.END, f"{col}: min={col_min:.3f}, max={col_max:.3f}\n")

            messagebox.showinfo("Success", "Dataset generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_csv(self):
        if self.df_scaled is None:
            messagebox.showwarning("Warning", "No dataset to save! Generate first.")
            return
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                     filetypes=[("CSV Files", "*.csv")],
                                                     title="Save processed dataset as")
            if file_path:
                self.df_scaled.to_csv(file_path, index=False)
                messagebox.showinfo("Saved", f"File saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = HealthcareApp(root)
    root.mainloop()
# End of 2q_gui.py