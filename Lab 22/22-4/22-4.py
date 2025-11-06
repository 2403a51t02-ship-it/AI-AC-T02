"""
ecg_ai_sim_gui.py

Educational GUI that simulates an AI ECG anomaly-detection workflow.

- This is a SAFE simulation only. It DOES NOT perform medical diagnosis.
- Do NOT use results for patient care.
- Purpose: teaching, demoing UI/workflow, discussing oversight and responsibility.

Run:
    python ecg_ai_sim_gui.py

Dependencies:
    - tkinter (standard)
    - numpy
    - matplotlib

Optional:
    - If you want to load real ECG CSV files, they should be simple 1-column CSVs
      of voltage samples (but again: DO NOT use outputs clinically).
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import hashlib
import random
import io
import csv
import time

# ---------------- Safety helpers ----------------
def simulated_model_predict(ecg_signal):
    """
    SAFE simulated "model" — deterministic pseudo-inference using a hash of the data.
    Returns a tuple: (label, confidence, explanation)
    label ∈ {'Normal (simulated)','Anomaly (simulated)'}
    confidence: float between 0.50 and 0.99 (simulated)
    explanation: short string describing why the simulator flagged it.
    IMPORTANT: This is NOT a medical model.
    """
    # Deterministic hash seed from the signal values summary
    s = np.array(ecg_signal, dtype=float)
    summary = f"{s.mean():.6f}-{s.std():.6f}-{len(s)}"
    h = hashlib.sha256(summary.encode('utf-8')).hexdigest()
    seed = int(h[:16], 16) % (2**31 - 1)
    rng = random.Random(seed)

    # Use a toy rule combined with randomness to make results plausible-looking
    # but NOT clinical: e.g., if std dev is high (simulated physiological variability),
    # the simulator is slightly more likely to call "Anomaly".
    std = float(np.std(s))
    mean = float(np.mean(s))
    score = (std * 10.0) + (abs(mean) * 5.0)  # arbitrary synthetic score
    # Convert to probability with sigmoid-like shaping (still arbitrary)
    prob = 1.0 / (1.0 + np.exp(-0.5 * (score - 0.8)))
    # Mix with rng to produce deterministic but variable confidence
    confidence = 0.5 + 0.49 * rng.random()  # between 0.5 and ~0.99
    # Final decision threshold (tunable, but purely illustrative)
    decision = prob * rng.random()

    if decision > 0.6:
        label = "Anomaly (simulated)"
        explanation = (
            "Simulated flag: higher-than-usual variability in ECG amplitude and/or irregular rhythm "
            "(this is a simulated reason; not clinical)."
        )
    else:
        label = "Normal (simulated)"
        explanation = "Simulated flag: signal variability within typical demo range (simulation only)."

    # Make confidence correlated roughly with prob (still arbitrary)
    confidence = round(min(0.99, 0.45 + prob * 0.5 + 0.05 * rng.random()), 2)
    return label, confidence, explanation

# ---------------- Synthetic ECG generator ----------------
def generate_synthetic_ecg(duration_sec=10, fs=250, heart_rate=60, noise_level=0.02):
    """
    Generate a synthetic ECG-like waveform (not physiologically perfect).
    - duration_sec: seconds of signal
    - fs: samples per second
    - heart_rate: beats per minute
    - noise_level: amplitude of additive gaussian noise
    Returns: numpy array of samples
    """
    t = np.linspace(0, duration_sec, int(duration_sec * fs))
    # Basic sine-based heartbeat approximation: sum of sinusoids, then add spikes for R-peaks
    hr_hz = heart_rate / 60.0
    base = 0.02 * np.sin(2 * np.pi * 1.0 * t)  # slow baseline wander
    pulse = 0.6 * np.sin(2 * np.pi * hr_hz * t)  # main heart rhythm
    # Add simulated R-peaks as narrow gaussians at beat times
    signal = base + pulse
    beat_times = np.arange(0, duration_sec, 60.0 / heart_rate)
    for bt in beat_times:
        idx = int(bt * fs)
        if 0 <= idx < len(t):
            width = int(0.02 * fs)  # narrow spike
            gauss = np.exp(-0.5 * ((np.arange(len(t)) - idx) / (width + 1e-6))**2)
            gauss = gauss * (0.8 + 0.3 * np.random.RandomState(idx).randn())
            signal += gauss
    # Add small noise
    signal += noise_level * np.random.RandomState(int(fs*duration_sec)).randn(len(t))
    # Normalize to small volt range
    signal = signal / np.max(np.abs(signal) + 1e-9) * 1.0
    return signal, t

# ---------------- GUI App ----------------
class ECGSimApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ECG Anomaly Detection — Educational Simulation")
        self.root.geometry("1000x700")
        self.root.config(bg="#f7fafc")

        header = tk.Frame(root, bg="#0b74de")
        header.pack(fill="x")
        tk.Label(header, text="ECG AI Demo — Simulation Only", font=("Segoe UI", 16, "bold"),
                 bg="#0b74de", fg="white", pady=10).pack()

        main = tk.Frame(root, bg="#f7fafc")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        # Left panel: plot and controls
        left = tk.Frame(main, bg="#ffffff", bd=1, relief="solid")
        left.pack(side="left", fill="both", expand=True, padx=(0,8))

        # Right panel: discussion & policy
        right = tk.Frame(main, bg="#ffffff", bd=1, relief="solid", width=340)
        right.pack(side="right", fill="y")

        # --- Controls on left ---
        ctrl = tk.Frame(left, bg="#ffffff")
        ctrl.pack(fill="x", padx=10, pady=8)

        tk.Label(ctrl, text="Data source (simulation only):", bg="#ffffff").grid(row=0, column=0, sticky="w")
        btn_frame = tk.Frame(ctrl, bg="#ffffff")
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6,8))

        self.load_btn = tk.Button(btn_frame, text="📂 Load ECG CSV", command=self.load_ecg_csv, bg="#2563eb", fg="white")
        self.load_btn.pack(side="left", padx=(0,6))
        self.gen_btn = tk.Button(btn_frame, text="✨ Generate Synthetic ECG", command=self.generate_and_plot, bg="#059669", fg="white")
        self.gen_btn.pack(side="left", padx=(0,6))

        # Info labels
        self.info_label = tk.Label(ctrl, text="No data loaded.", bg="#ffffff", fg="#374151", anchor="w", justify="left")
        self.info_label.grid(row=2, column=0, sticky="w", pady=(6,0))

        # --- Matplotlib figure ---
        fig = Figure(figsize=(7,4), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("ECG Signal (simulation)")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude (arb.units)")
        self.line, = self.ax.plot([], [], lw=0.9)
        self.canvas = FigureCanvasTkAgg(fig, master=left)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=6)

        # --- Model inference area ---
        infer_frame = tk.Frame(left, bg="#ffffff")
        infer_frame.pack(fill="x", padx=10, pady=6)
        self.run_btn = tk.Button(infer_frame, text="▶ Run Simulated AI Inference", command=self.run_inference, bg="#7c3aed", fg="white")
        self.run_btn.pack(side="left")
        self.explain_btn = tk.Button(infer_frame, text="🛈 Show Explainability", command=self.show_explainability, bg="#0ea5a4", fg="white")
        self.explain_btn.pack(side="left", padx=(6,0))

        # Result box
        self.result_text = tk.Label(left, text="Result: —", bg="#ffffff", fg="#111827", font=("Segoe UI", 12, "bold"), anchor="w", justify="left")
        self.result_text.pack(fill="x", padx=12, pady=(6,0))

        # --- Right: Discussion / Oversight / Responsibility ---
        tk.Label(right, text="Discussion & Oversight", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=12, pady=(12,6))
        rbtns = tk.Frame(right, bg="#ffffff")
        rbtns.pack(fill="x", padx=12, pady=(0,8))
        tk.Button(rbtns, text="⚖️ Should doctors rely fully on AI?", command=self.q1, bg="#f97316", fg="white").pack(fill="x", pady=4)
        tk.Button(rbtns, text="🔬 Mandatory oversight before deployment", command=self.q2, bg="#06b6d4", fg="white").pack(fill="x", pady=4)
        tk.Button(rbtns, text="🤝 How responsibility should be shared", command=self.q3, bg="#10b981", fg="white").pack(fill="x", pady=4)
        tk.Button(rbtns, text="📝 Export Report (text)", command=self.export_report, bg="#2563eb", fg="white").pack(fill="x", pady=8)

        # Text area for discussion
        self.discuss = scrolledtext.ScrolledText(right, wrap=tk.WORD, height=18, font=("Segoe UI", 10), state='disabled')
        self.discuss.pack(fill="both", expand=True, padx=12, pady=(6,12))

        # Internal state
        self.ecg_signal = None
        self.ecg_time = None
        self.last_prediction = None
        self.last_explanation = None

        # Initial synthetic plot
        self.generate_and_plot()

    # ---------- Data loading / plotting ----------
    def load_ecg_csv(self):
        path = filedialog.askopenfilename(title="Open ECG CSV", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, 'r', newline='') as f:
                reader = csv.reader(f)
                samples = []
                for row in reader:
                    if not row:
                        continue
                    # take first numeric column
                    val = None
                    for cell in row:
                        try:
                            val = float(cell)
                            break
                        except:
                            continue
                    if val is not None:
                        samples.append(val)
            if len(samples) < 10:
                messagebox.showwarning("Too short", "Loaded file has too few samples for a meaningful demo.")
                return
            # Create time axis assuming default fs=250 (for display only)
            fs = 250.0
            t = np.arange(len(samples)) / fs
            self.ecg_signal = np.array(samples, dtype=float)
            self.ecg_time = t
            self.info_label.config(text=f"Loaded CSV: {path}\nSamples: {len(samples)} (display assumes fs=250Hz)")
            self._plot_signal()
            self.last_prediction = None
            self.result_text.config(text="Result: —")
        except Exception as e:
            messagebox.showerror("Load error", f"Could not load CSV: {e}")

    def generate_and_plot(self):
        # Generate synthetic signal
        sig, t = generate_synthetic_ecg(duration_sec=10, fs=250, heart_rate=60 + np.random.randint(-10,11), noise_level=0.03)
        self.ecg_signal = sig
        self.ecg_time = t
        self.info_label.config(text=f"Synthetic ECG generated — duration {t[-1]:.1f}s, samples: {len(sig)}")
        self._plot_signal()
        self.last_prediction = None
        self.result_text.config(text="Result: —")

    def _plot_signal(self, highlight_ranges=None):
        self.ax.clear()
        self.ax.set_title("ECG Signal (simulation)")
        if self.ecg_time is None or self.ecg_signal is None:
            self.ax.text(0.5, 0.5, "No signal", ha="center")
            self.canvas.draw()
            return
        self.ax.plot(self.ecg_time, self.ecg_signal, lw=0.9)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude (arb.units)")
        # Optionally highlight ranges
        if highlight_ranges:
            for (start, end) in highlight_ranges:
                self.ax.axvspan(start, end, color='red', alpha=0.2)
        self.canvas.draw()

    # ---------- Inference & explainability (SIMULATED) ----------
    def run_inference(self):
        if self.ecg_signal is None:
            messagebox.showwarning("No data", "Load or generate an ECG signal first.")
            return
        label, confidence, explanation = simulated_model_predict(self.ecg_signal)
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.last_prediction = (label, confidence, ts)
        self.last_explanation = explanation
        # Update UI with a clear warning
        display = (
            f"SIMULATED MODEL OUTPUT (NOT FOR CLINICAL USE)\n\n"
            f"Label: {label}\n"
            f"Confidence (simulated): {confidence*100:.0f}%\n"
            f"Timestamp: {ts}\n\n"
            f"Note: This is an educational simulation only. Do not use for diagnosis."
        )
        self.result_text.config(text=f"Result: {label} ({confidence*100:.0f}%)")
        self._display_discussion_text(display)

    def show_explainability(self):
        if self.ecg_signal is None:
            messagebox.showwarning("No data", "Load or generate an ECG signal first.")
            return
        if self.last_explanation is None:
            messagebox.showinfo("No inference yet", "Run simulated AI inference first to get explainability.")
            return
        # For the demo, highlight a made-up segment (e.g., a few seconds) to show "explainability"
        # Choose deterministic span from hash of the signal summary
        s = np.array(self.ecg_signal)
        summary = f"{s.mean():.6f}-{s.std():.6f}-{len(s)}"
        h = hashlib.sha256(summary.encode('utf-8')).hexdigest()
        seed = int(h[:8], 16) % 10000
        rng = random.Random(seed)
        duration = self.ecg_time[-1]
        start = rng.uniform(0, max(0.1, duration - 2.0))
        end = min(duration, start + rng.uniform(0.2, 1.2))
        # Plot with highlight
        self._plot_signal(highlight_ranges=[(start, end)])
        explain_text = (
            "Explainability (simulated):\n\n"
            f"The model (simulated) indicates the region between {start:.2f}s and {end:.2f}s contributed\n"
            "most to the anomaly score. This is illustrative only — real explainability requires\n"
            "verified, validated methods (saliency maps, attention, feature importance) and careful\n"
            "clinical interpretation."
        )
        self._display_discussion_text(explain_text)

    # ---------- Discussion panels ----------
    def q1(self):
        # Should doctors rely fully on AI outputs?
        text = (
            "Should doctors rely fully on AI outputs?\n\n"
            "Short answer: NO.\n\n"
            "Key points:\n"
            " • AI can assist clinicians by highlighting patterns and saving time, but it should not\n"
            "   replace clinical judgment. AI outputs are probabilistic and can be wrong.\n"
            " • Human-in-the-loop: clinicians must review AI outputs, check raw signals, and consider\n"
            "   patient history, symptoms, and other tests before making decisions.\n"
            " • Over-reliance risks: automation bias, missed rare presentations, and propagation of model\n"
            "   training data biases into care. Always require clinician oversight.\n"
        )
        self._display_discussion_text(text)

    def q2(self):
        # Mandatory oversight before deployment
        text = (
            "Mandatory oversight before deployment in hospitals\n\n"
            "Regulatory & clinical validation checklist (high-level):\n"
            " 1) Clinical validation: prospective, peer-reviewed studies demonstrating safety and efficacy\n"
            "    across relevant patient populations.\n"
            " 2) Regulatory approval: comply with medical device regulations (e.g., FDA in the US, CE in EU).\n"
            " 3) Risk management: documented hazard analysis, failure modes, and mitigations (ISO 14971).\n"
            " 4) Data governance: provenance of training data, demographics, consent, and privacy safeguards.\n"
            " 5) Explainability and transparency: logs, versioning, model cards, and clear descriptions of\n"
            "    limitations and intended use cases.\n"
            " 6) Clinical workflow integration: interfaces for clinicians, human override, and escalation paths.\n"
            " 7) Post-market surveillance: monitoring performance, drift detection, incident reporting.\n"
            " 8) Training and accreditation: clinicians must be trained on tool limitations and interpretation.\n"
        )
        self._display_discussion_text(text)

    def q3(self):
        # How responsibility should be shared
        text = (
            "How should responsibility be shared?\n\n"
            "• Developers & Vendors:\n"
            "  - Responsible for building safe models, rigorous testing, documentation, and regulatory submissions.\n"
            "  - Provide clear indications of limitations, expected performance, and failure modes.\n\n"
            "• Clinicians & Healthcare Organizations:\n"
            "  - Responsible for validating tools in local workflows, obtaining patient consent if required,\n"
            "    ensuring staff training, and maintaining oversight.\n\n"
            "• Regulators & Institutions:\n"
            "  - Set standards, require evidence, audit deployments, and maintain reporting systems.\n\n"
            "• Shared responsibility model:\n"
            "  - Vendors should not be the only 'owners' of safety; institutions must implement governance,\n"
            "    clinicians must retain ultimate decision-making, and regulators must enforce safety.\n"
        )
        self._display_discussion_text(text)

    # ---------- Utility UI helpers ----------
    def _display_discussion_text(self, text):
        self.discuss.config(state='normal')
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        header = f"[{ts}] "
        self.discuss.insert(tk.END, header + text + "\n\n")
        self.discuss.see(tk.END)
        self.discuss.config(state='disabled')

    def export_report(self):
        if self.last_prediction is None:
            messagebox.showinfo("No result", "Run simulated inference first to export a report.")
            return
        label, confidence, ts = self.last_prediction
        report = (
            "ECG AI Demo — Simulated Report\n"
            f"Generated at: {ts}\n\n"
            f"Prediction (SIMULATED): {label}\n"
            f"Confidence (simulated): {confidence*100:.0f}%\n\n"
            f"Explanation (simulated):\n{self.last_explanation or 'n/a'}\n\n"
            "DISCLAIMER: This report is for educational/demo use only and is NOT clinical advice.\n"
        )
        path = filedialog.asksaveasfilename(title="Save report as text", defaultextension=".txt", filetypes=[("Text files","*.txt")])
        if path:
            try:
                with open(path, 'w') as f:
                    f.write(report)
                messagebox.showinfo("Saved", f"Simulated report saved to: {path}")
            except Exception as e:
                messagebox.showerror("Save error", f"Could not save file: {e}")

# ---------------- Run app ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ECGSimApp(root)
    root.mainloop()
