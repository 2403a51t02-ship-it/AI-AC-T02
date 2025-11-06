"""
loan_ai_explainable_gui.py

Educational GUI that simulates an explainable AI loan approval system.
- SAFE, classroom-friendly demo (NOT for real lending decisions).
- Shows feature inputs -> deterministic scoring -> decision with per-feature contributions.
- Includes discussion panels:
    * Risks of black-box AI in finance
    * How explainability supports fairness
- Excludes sensitive attributes from the decision by design (explained in UI).

Run:
    python loan_ai_explainable_gui.py

Dependencies:
    - tkinter (standard library)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import time

# ---------------------- Simple utility helpers ----------------------

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def norm(v, lo, hi):
    if hi == lo:
        return 0.0
    v = clamp(v, lo, hi)
    return (v - lo) / (hi - lo)

def fmt_pct(x):
    return f"{round(x*100)}%"

# ---------------------- Toy "model" (transparent) ----------------------

class ExplainableLoanModel:
    """
    A transparent, linear, feature-based scoring model for demo purposes.
    This is NOT a real credit model. Do NOT use in production.

    Decision score in [0,1] from normalized features and public weights.
    Sensitive attributes (e.g., age) are NOT used in the score to demonstrate fairness by design.
    """
    def __init__(self):
        # Publicly documented weights (sum of absolute values ≈ 1 for readability)
        # Positive weight increases approval likelihood; negative decreases.
        self.weights = {
            "income": 0.28,           # normalized monthly income
            "loan_amount": -0.24,     # normalized requested amount (bigger = riskier)
            "credit_score": 0.30,     # normalized credit score
            "dti": -0.22,             # normalized debt-to-income ratio (higher = riskier)
            "employment_years": 0.18, # normalized job stability
            # "age": 0.00,            # EXCLUDED from computation (sensitive attribute)
        }
        # Feature ranges for normalization (demo only)
        self.ranges = {
            "income": (10000, 300000),            # INR per month (example range)
            "loan_amount": (50000, 5000000),      # INR total requested
            "credit_score": (300, 900),           # typical credit score range (example)
            "dti": (0.0, 1.0),                    # debt-to-income ratio (0 to 1)
            "employment_years": (0, 40),          # years
            "age": (18, 75),                      # not used for decision
        }
        # Bias/offset to center the score (tunable)
        self.bias = 0.48
        # Approval threshold (demo)
        self.threshold = 0.50

    def compute(self, features: dict):
        """
        Compute a transparent decision.
        Returns:
            score (0..1), decision (True/False), contributions list [(name, value_norm, weight, contrib), ...]
        """
        contribs = []
        score = self.bias

        # Normalize features
        n = {}
        for k in ["income", "loan_amount", "credit_score", "dti", "employment_years"]:
            lo, hi = self.ranges[k]
            n[k] = norm(float(features[k]), lo, hi)

        # Linear combination
        for k, w in self.weights.items():
            c = n[k] * w
            contribs.append((k, n[k], w, c))
            score += c

        # Clamp and decide
        score = float(clamp(score, 0.0, 1.0))
        decision = score >= self.threshold

        # Sort contributions by absolute impact
        contribs.sort(key=lambda x: abs(x[3]), reverse=True)
        return score, decision, contribs, n

# ---------------------- GUI App ----------------------

class LoanAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI in Decision-Making — Explainable Loan Approval (Educational)")
        self.root.geometry("980x720")
        self.root.config(bg="#f7fafc")

        self.model = ExplainableLoanModel()
        self.last_result = None  # (score, decision, contribs, normalized)

        # Header
        header = tk.Frame(root, bg="#1e40af")
        header.pack(fill="x")
        tk.Label(header, text="Explainable Loan Approval — Educational Demo (NOT FOR REAL LENDING)",
                 font=("Segoe UI", 14, "bold"), bg="#1e40af", fg="white", pady=10).pack()

        # Main area split: left inputs/outputs, right discussion
        main = tk.Frame(root, bg="#f7fafc")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        left = tk.Frame(main, bg="#ffffff", bd=1, relief="solid")
        left.pack(side="left", fill="both", expand=True, padx=(0,8))

        right = tk.Frame(main, bg="#ffffff", bd=1, relief="solid", width=360)
        right.pack(side="right", fill="y")

        # ---------------- Inputs ----------------
        form = tk.Frame(left, bg="#ffffff")
        form.pack(fill="x", padx=12, pady=10)

        row = 0
        self.vars = {}

        def add_row(label, key, default, hint=""):
            nonlocal row
            tk.Label(form, text=label, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=4)
            v = tk.StringVar(value=str(default))
            self.vars[key] = v
            entry = ttk.Entry(form, textvariable=v, width=18)
            entry.grid(row=row, column=1, sticky="w", padx=6)
            if hint:
                tk.Label(form, text=hint, bg="#ffffff", fg="#6b7280").grid(row=row, column=2, sticky="w")
            row += 1

        add_row("Monthly Income (INR)", "income", 75000, "(range ~10k–300k)")
        add_row("Loan Amount (INR)", "loan_amount", 400000, "(range ~50k–50L)")
        add_row("Credit Score", "credit_score", 720, "(range 300–900)")
        add_row("Debt-to-Income Ratio", "dti", 0.35, "(0 to 1)")
        add_row("Employment Years", "employment_years", 4, "(0–40)")
        add_row("Age (NOT used)", "age", 29, "Sensitive attribute; excluded from decision")

        # Buttons
        btns = tk.Frame(left, bg="#ffffff")
        btns.pack(fill="x", padx=12, pady=(4,10))

        self.run_btn = ttk.Button(btns, text="▶ Generate Decision", command=self.run_decision)
        self.run_btn.pack(side="left", padx=(0,8))

        self.why_btn = ttk.Button(btns, text="🛈 Explain Decision", command=self.show_explanation)
        self.why_btn.pack(side="left", padx=(0,8))

        self.export_btn = ttk.Button(btns, text="📝 Export Report", command=self.export_report)
        self.export_btn.pack(side="left")

        # Result panel
        result_frame = tk.LabelFrame(left, text="Decision Result", bg="#ffffff")
        result_frame.pack(fill="x", padx=12, pady=(0,10))
        self.result_label = tk.Label(result_frame, text="No decision yet.", bg="#ffffff", fg="#111827",
                                     font=("Segoe UI", 11, "bold"), anchor="w", justify="left")
        self.result_label.pack(fill="x", padx=10, pady=8)

        # Contributions list
        contrib_frame = tk.LabelFrame(left, text="Feature Contributions (explainability)", bg="#ffffff")
        contrib_frame.pack(fill="both", expand=True, padx=12, pady=(0,12))
        self.contrib_text = scrolledtext.ScrolledText(contrib_frame, wrap=tk.WORD, font=("Consolas", 10),
                                                     height=14, state="disabled")
        self.contrib_text.pack(fill="both", expand=True, padx=8, pady=8)

        # ---------------- Right side: Discussion ----------------
        tk.Label(right, text="Discussion & Analysis", font=("Segoe UI", 12, "bold"),
                 bg="#ffffff").pack(anchor="w", padx=12, pady=(12,6))

        rbtns = tk.Frame(right, bg="#ffffff")
        rbtns.pack(fill="x", padx=12, pady=(0,8))

        ttk.Button(rbtns, text="🔍 Is the process explainable?",
                   command=self.panel_explainable).pack(fill="x", pady=4)
        ttk.Button(rbtns, text="⚠️ Risks of Black-Box AI",
                   command=self.panel_blackbox_risks).pack(fill="x", pady=4)
        ttk.Button(rbtns, text="⚖️ How explainability supports fairness",
                   command=self.panel_fairness).pack(fill="x", pady=4)

        self.discuss = scrolledtext.ScrolledText(right, wrap=tk.WORD, font=("Segoe UI", 10),
                                                 height=22, state="disabled")
        self.discuss.pack(fill="both", expand=True, padx=12, pady=(6,12))

        self._append_discussion(
            "Welcome! This demo shows a transparent, explainable scoring approach. "
            "It is NOT a real credit model. Please do not use it for actual lending decisions."
        )

    # ---------------- Actions ----------------

    def _get_features(self):
        try:
            f = {
                "income": float(self.vars["income"].get()),
                "loan_amount": float(self.vars["loan_amount"].get()),
                "credit_score": float(self.vars["credit_score"].get()),
                "dti": float(self.vars["dti"].get()),
                "employment_years": float(self.vars["employment_years"].get()),
                "age": float(self.vars["age"].get()),  # not used
            }
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid numeric values.")
            return None
        # basic sanity clamp
        for k, (lo, hi) in self.model.ranges.items():
            f[k] = clamp(f[k], lo, hi)
        return f

    def run_decision(self):
        f = self._get_features()
        if not f:
            return
        score, decision, contribs, normalized = self.model.compute(f)
        self.last_result = (score, decision, contribs, normalized, f)

        decision_text = "APPROVED ✅" if decision else "DECLINED ❌"
        self.result_label.config(
            text=f"Decision: {decision_text}\n"
                 f"Score: {score:.2f} (threshold {self.model.threshold:.2f})\n"
                 f"Note: Age is NOT used in decision (sensitive attribute excluded)."
        )

        # Auto-fill contributions
        self._show_contribs(contribs, normalized)

    def _show_contribs(self, contribs, normalized):
        self.contrib_text.config(state="normal")
        self.contrib_text.delete("1.0", tk.END)
        self.contrib_text.insert(tk.END,
            "Feature                 Value (norm)   Weight     Contribution\n"
            "----------------------------------------------------------------\n"
        )
        for name, nval, w, c in contribs:
            self.contrib_text.insert(
                tk.END, f"{name:20s}  {nval:>6.2f}        {w:+.2f}      {c:+.3f}\n"
            )
        self.contrib_text.insert(tk.END, "\nLegend: contribution = normalized_value × weight (higher absolute value = larger impact)\n")
        self.contrib_text.insert(tk.END, "Transparency note: All weights, ranges, and threshold are openly documented in this demo.\n")
        self.contrib_text.config(state="disabled")

    def show_explanation(self):
        if not self.last_result:
            messagebox.showinfo("No decision", "Run a decision first.")
            return
        score, decision, contribs, normalized, f = self.last_result
        top = contribs[0]
        name, nval, w, c = top
        reason = (
            f"Top driver: '{name}' with contribution {c:+.3f}.\n"
            f"- Normalized {name} = {nval:.2f}\n"
            f"- Weight = {w:+.2f} (public)\n\n"
            "This means this feature had the largest absolute effect on your score."
        )
        self._append_discussion(
            "Explainability result:\n"
            f"Decision score = {score:.2f} ➜ {'APPROVED' if decision else 'DECLINED'}\n"
            + reason
            + "\n\nNote: Sensitive attribute 'age' is excluded by design for fairness."
        )

    def export_report(self):
        if not self.last_result:
            messagebox.showinfo("No decision", "Run a decision first.")
            return
        score, decision, contribs, normalized, f = self.last_result
        lines = []
        lines.append("Explainable Loan Decision — Educational Report")
        lines.append(time.strftime("Generated at: %Y-%m-%d %H:%M:%S"))
        lines.append("")
        lines.append("Inputs:")
        for k in ["income", "loan_amount", "credit_score", "dti", "employment_years", "age"]:
            lines.append(f"  {k}: {f[k]}")
        lines.append("")
        lines.append(f"Decision: {'APPROVED' if decision else 'DECLINED'}")
        lines.append(f"Score: {score:.2f} (threshold {self.model.threshold:.2f})")
        lines.append("Note: Age is excluded from decision.")
        lines.append("")
        lines.append("Feature contributions (name, norm_value, weight, contribution):")
        for name, nval, w, c in contribs:
            lines.append(f"  {name}, {nval:.2f}, {w:+.2f}, {c:+.3f}")
        lines.append("")
        lines.append("DISCLAIMER: This is an educational simulation only — not a real credit model.")
        text = "\n".join(lines)

        path = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fobj:
                fobj.write(text)
            messagebox.showinfo("Saved", f"Report saved to: {path}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    # ---------------- Discussion Panels ----------------

    def _append_discussion(self, text):
        self.discuss.config(state="normal")
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.discuss.insert(tk.END, f"[{ts}] {text}\n\n")
        self.discuss.config(state="disabled")
        self.discuss.see(tk.END)

    def panel_explainable(self):
        self._append_discussion(
            "Is the decision process explainable to users?\n\n"
            "• In this demo, yes: the full scoring formula is published, feature ranges are known,\n"
            "  and the contribution of each feature is displayed. Users can see which inputs moved\n"
            "  the result most and why.\n"
            "• In practice, explainability should provide user-understandable reasons (plain language),\n"
            "  access to key factors that affected the decision, and actionable guidance on how to improve.\n"
            "• Explainability should NEVER reveal proprietary details that enable gaming the system or\n"
            "  leak private data — balance transparency with security and privacy."
        )

    def panel_blackbox_risks(self):
        self._append_discussion(
            "What risks arise if AI decisions are a 'black box'?\n\n"
            "• Hidden bias and discrimination may go undetected (e.g., proxy variables for protected classes).\n"
            "• Users cannot contest or understand adverse outcomes; erodes trust and may violate regulations.\n"
            "• Hard to audit: regulators, compliance teams, and internal auditors lack visibility into errors.\n"
            "• Drift risk: model behavior can degrade over time with no clear signal as to why.\n"
            "• Legal/exposure risk: opaque decisions in credit can violate fair lending and consumer rights laws."
        )

    def panel_fairness(self):
        self._append_discussion(
            "How explainability ensures fairness in financial decisions?\n\n"
            "• Feature-level reasons show whether decisions depend on appropriate, non-sensitive factors.\n"
            "• Documentation of inputs, weights, and thresholds enables auditing for disparate impact.\n"
            "• User-facing explanations support adverse action notices and due process.\n"
            "• Governance: explainability helps compliance teams set controls, run periodic fairness tests,\n"
            "  and retrain or remediate models when inequities are found.\n"
            "• Design for fairness: exclude protected attributes (like age, race, gender) and test for proxies."
        )

# ---------------------- Run ----------------------

if __name__ == "__main__":
    root = tk.Tk()
    # Native-themed widgets if available
    try:
        root.call("tk", "scaling", 1.0)
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass
    app = LoanAIApp(root)
    root.mainloop()
