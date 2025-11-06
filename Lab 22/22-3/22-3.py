"""
network_scanner_sim_gui.py

Safe, educational GUI that simulates an "AI-generated network scanner"
for classroom/demonstration use, and provides an ethics/debate panel.

IMPORTANT: This program does NOT perform any real network scanning.
It produces a deterministic, simulated scan report (no network IO),
so it is safe to run and share.

Author: ChatGPT (simulation & educational)
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import hashlib
import time
import random

# ---------- Utility: deterministic "fake scan" generator ----------
def deterministic_scan_simulation(target, depth=1):
    """
    Given a target string, produce a deterministic simulated "scan" result.
    This function does NOT perform any network activity.
    It uses a hash of the target to seed a PRNG and then generates plausible
    (but fake) port/service responses for demo purposes.
    """
    # Normalize target
    t = str(target).strip()
    if not t:
        return "No target provided."

    # Use hash of target to seed deterministic RNG
    h = hashlib.sha256(t.encode('utf-8')).hexdigest()
    seed = int(h[:16], 16)
    rng = random.Random(seed)

    simulated_ports = []
    # choose count of "open" ports based on seed (but limited)
    count = (seed % 6) + 2  # between 2 and 7 fake open ports
    common_ports = [22, 80, 443, 21, 25, 110, 143, 3306, 5432, 8080, 8443, 3389]

    # shuffle to pick some
    rng.shuffle(common_ports)
    for i in range(count):
        port = common_ports[i % len(common_ports)]
        # craft fake details
        service = {
            22: 'ssh',
            80: 'http',
            443: 'https',
            21: 'ftp',
            25: 'smtp',
            110: 'pop3',
            143: 'imap',
            3306: 'mysql',
            5432: 'postgresql',
            8080: 'http-alt',
            8443: 'https-alt',
            3389: 'rdp'
        }.get(port, 'unknown')
        version_major = rng.randint(0, 3)
        version_minor = rng.randint(0, 9)
        banner = f"{service}/v{version_major}.{version_minor}"
        vuln_score = round(rng.random() * 9.9, 1)  # pretend CVSS-like
        simulated_ports.append({
            'port': port,
            'service': service,
            'banner': banner,
            'vuln_score': vuln_score,
            'notes': "Simulated result — not a real probe."
        })

    # optionally include some "closed/filtered" ports
    rng.shuffle(common_ports)
    closed = common_ports[count:count+3]
    closed_ports = [{'port': p, 'status': 'filtered/closed'} for p in closed]

    # Build textual report
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    header = f"SIMULATED SCAN REPORT\nTarget: {t}\nGenerated at: {ts}\nNote: This is a deterministic simulation — NO NETWORK TRAFFIC.\n"
    lines = [header, "-"*60]
    for entry in simulated_ports:
        lines.append(f"Port {entry['port']}/tcp    Service: {entry['service']}    Banner: {entry['banner']}")
        lines.append(f"    Simulated risk score: {entry['vuln_score']} / 10.0")
        lines.append(f"    Notes: {entry['notes']}")
    if closed_ports:
        lines.append("-"*60)
        lines.append("Other (simulated) ports: " + ", ".join(str(p['port']) + " (closed/filtered)" for p in closed_ports))
    footer = "\nDISCLAIMER: This is an educational simulation only. Do not use real scanning tools without "
    footer += "explicit authorization from the target owner. Unauthorized scanning may be illegal."
    lines.append("-"*60)
    lines.append(footer)
    return "\n".join(lines)

# ---------- GUI App ----------
class NetworkScannerSimApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Scanner — Simulation & Ethics Demo")
        self.root.geometry("820x680")
        self.root.config(bg="#f7fafc")

        # Header
        header = tk.Frame(root, bg="#0ea5a4")
        header.pack(fill="x")
        tk.Label(header, text="Network Scanner — Simulation & Ethics Demo", font=("Segoe UI", 16, "bold"),
                 bg="#0ea5a4", fg="white", pady=12).pack()

        # Main frame with left (controls + simulation) and right (discussion)
        main = tk.Frame(root, bg="#f7fafc")
        main.pack(fill="both", expand=True, padx=12, pady=10)

        # Left panel: controls + output
        left = tk.Frame(main, bg="#ffffff", bd=1, relief="solid")
        left.pack(side="left", fill="both", expand=True, padx=(0,8))

        # Right panel: discussion & debate
        right = tk.Frame(main, bg="#ffffff", bd=1, relief="solid", width=320)
        right.pack(side="right", fill="y")

        # Controls on left
        ctrl_frame = tk.Frame(left, bg="#ffffff")
        ctrl_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(ctrl_frame, text="Target (name or IP) — simulation only:", bg="#ffffff").pack(anchor="w")
        self.target_entry = tk.Entry(ctrl_frame, font=("Consolas", 12))
        self.target_entry.pack(fill="x", pady=(4,8))

        tk.Label(ctrl_frame, text="Simulation Depth (1 = quick, 3 = detailed):", bg="#ffffff").pack(anchor="w")
        self.depth_var = tk.IntVar(value=1)
        depth_frame = tk.Frame(ctrl_frame, bg="#ffffff")
        depth_frame.pack(fill="x", pady=(4,6))
        tk.Radiobutton(depth_frame, text="1", variable=self.depth_var, value=1, bg="#ffffff").pack(side="left")
        tk.Radiobutton(depth_frame, text="2", variable=self.depth_var, value=2, bg="#ffffff").pack(side="left")
        tk.Radiobutton(depth_frame, text="3", variable=self.depth_var, value=3, bg="#ffffff").pack(side="left")

        btn_frame = tk.Frame(ctrl_frame, bg="#ffffff")
        btn_frame.pack(fill="x", pady=8)
        self.gen_button = tk.Button(btn_frame, text="🔎 Generate Simulated Scan", command=self.generate_scan,
                                    bg="#2563eb", fg="white", padx=12, pady=6)
        self.gen_button.pack(side="left", padx=(0,6))
        self.copy_button = tk.Button(btn_frame, text="📋 Copy Report", command=self.copy_report, bg="#6b7280", fg="white",
                                     padx=12, pady=6)
        self.copy_button.pack(side="left", padx=(0,6))
        self.clear_button = tk.Button(btn_frame, text="🧹 Clear", command=self.clear_output, bg="#ef4444", fg="white",
                                      padx=12, pady=6)
        self.clear_button.pack(side="left")

        # Output area (left)
        self.output = scrolledtext.ScrolledText(left, wrap=tk.WORD, font=("Consolas", 11), state='disabled')
        self.output.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # Right: Tabs for Ethics / Debate / Resources
        tk.Label(right, text="Discussion & Policy", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=12, pady=(12,6))

        # Buttons for right panel
        rbtn_frame = tk.Frame(right, bg="#ffffff")
        rbtn_frame.pack(fill="x", padx=12)
        tk.Button(rbtn_frame, text="🧭 Ethical Use", command=self.show_ethics, bg="#059669", fg="white").pack(fill="x", pady=4)
        tk.Button(rbtn_frame, text="⚖️ Legal Risks", command=self.show_legal, bg="#f59e0b", fg="black").pack(fill="x", pady=4)
        tk.Button(rbtn_frame, text="🗣️ Debate: Should AI refuse?", command=self.show_debate, bg="#7c3aed", fg="white").pack(fill="x", pady=4)
        tk.Button(rbtn_frame, text="🔗 Safe Learning Alternatives", command=self.show_alternatives, bg="#0ea5a4", fg="white").pack(fill="x", pady=4)

        # Small notes
        tk.Label(right, text="Important: This app simulates a scanner only — it never touches the network.",
                 wraplength=280, justify="left", bg="#ffffff", fg="#374151", padx=8, pady=8).pack(anchor="w", padx=12, pady=(8,0))

        # initial content
        self.report_text = ""
        self.show_welcome()

    # ---------- UI actions ----------
    def show_welcome(self):
        welcome = (
            "Welcome — Network Scanner (SIMULATION)\n\n"
            "This educational tool simulates an AI-generated network scan for teaching\n"
            "and discussion. It does not perform real network probing. Use this app to:\n"
            " - demonstrate what scan output might look like\n"
            " - discuss ethical and legal aspects of scanning tools\n"
            " - explore where AI should draw boundaries when generating dual-use code\n\n"
            "Type a target name (e.g., example.com) and press 'Generate Simulated Scan'."
        )
        self._display(welcome)

    def _display(self, text, replace=False):
        self.output.config(state='normal')
        if replace:
            self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text + "\n\n")
        self.output.config(state='disabled')
        self.output.see(tk.END)

    def clear_output(self):
        self.output.config(state='normal')
        self.output.delete("1.0", tk.END)
        self.output.config(state='disabled')

    def copy_report(self):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.report_text)
            messagebox.showinfo("Copied", "Simulated report copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy: {e}")

    def generate_scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showwarning("No target", "Enter a target name/IP for the simulation (no real scanning).")
            return

        # Ask user to confirm they understand it's simulation + responsible use
        confirm = messagebox.askokcancel("Simulation confirmation",
                                         "This will generate a simulated scan report (NO NETWORK ACTIVITY).\n\n"
                                         "Do you confirm you understand this is for education only?")
        if not confirm:
            return

        depth = max(1, min(3, self.depth_var.get()))
        # Create a small "simulation time" delay to look realistic (but non-blocking)
        self._display(f"Generating simulated scan for: {target}  (depth={depth}) ...", replace=False)
        self.root.update()
        time.sleep(0.35)

        report = deterministic_scan_simulation(target, depth=depth)
        self.report_text = report
        self._display(report)

    # ---------- Discussion sections ----------
    def show_ethics(self):
        ethic_text = (
            "Ethical Use of Network Scanning Tools\n\n"
            "1) Defensive / Ethical Examples:\n"
            "   • Vulnerability assessment run by an owner on their infrastructure.\n"
            "   • Penetration testing with a signed authorization (scope + rules of engagement).\n"
            "   • Security research on lab systems or intentionally vulnerable VMs.\n\n"
            "2) Ethical principles:\n"
            "   • Always obtain written permission before testing a network you do not own.\n"
            "   • Define scope, timing, and data handling policies in advance.\n"
            "   • Avoid causing service disruption or data exposure.\n"
            "   • Share findings responsibly with remediation advice.\n"
        )
        self._display(ethic_text)

    def show_legal(self):
        legal_text = (
            "Legal and Safety Risks of Unauthorized Scanning\n\n"
            "• Unauthorized network scanning can violate computer misuse laws, terms of service,\n"
            "  and could trigger incident response from target operators.\n"
            "• Scanning without consent may lead to account bans, DMCA notices, civil suits, or\n"
            "  criminal prosecution depending on jurisdiction and intent.\n"
            "• Always consult legal counsel or internal security/compliance teams before performing tests\n"
            "  beyond your own lab or explicitly authorized environments.\n"
        )
        self._display(legal_text)

    def show_debate(self):
        debate_text = (
            "Debate: Should AI refuse to provide network-scanning tools?\n\n"
            "Pro (AI should refuse):\n"
            " - Providing ready-to-run scanning/exploitation code lowers the barrier for misuse.\n"
            " - AI that refuses reduces accidental dissemination of harmful tooling.\n"
            " - Clear refusals follow the principle of 'do no harm.'\n\n"
            "Con (AI should sometimes provide carefully-scoped help):\n"
            " - Security professionals need code examples for defensive tooling and automation.\n"
            " - Blanket refusal can hamper legitimate research and education.\n" 
            " - Conditional assistance (require context, promote safe alternatives) may be better.\n\n"
            "Balanced approach recommendation:\n"
            " - Refuse to produce code that enables unauthorized access or real-world exploitation.\n"
            " - Provide safe, non-actionable educational simulations (like this app),\n"
            "   and high-level conceptual guidance about defensive techniques.\n"
            " - Encourage use of authorized labs (e.g., Capture The Flag, VulnHub, Hack The Box),\n"
            "   and provide references to legal frameworks and ethical guidelines.\n"
        )
        self._display(debate_text)

    def show_alternatives(self):
        alt_text = (
            "Safe Learning Alternatives & Resources\n\n"
            "• Use intentionally vulnerable labs and VMs: Metasploitable, OWASP Juice Shop, VulnHub.\n"
            "• Practice on Capture-The-Flag (CTF) platforms with built-in safe environments.\n"
            "• Learn defensive tools and how to harden systems (log analysis, secure configs).\n"
            "• Study networking fundamentals and how scanners work conceptually (no live probing).\n"
            "• When building real assessment tooling, do it inside isolated test networks you own.\n"
        )
        self._display(alt_text)

# ---------- Run ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerSimApp(root)
    root.mainloop()
