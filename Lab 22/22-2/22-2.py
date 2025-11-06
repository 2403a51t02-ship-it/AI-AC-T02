import tkinter as tk
from tkinter import scrolledtext

class IntellectualPropertyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Intellectual Property & Plagiarism Checker")
        self.root.geometry("750x600")
        self.root.config(bg="#f3f4f6")

        # --- Header ---
        tk.Label(
            root,
            text="Intellectual Property & Plagiarism — AI Code Attribution Demo",
            font=("Helvetica", 14, "bold"),
            bg="#1d4ed8",
            fg="white",
            pady=10
        ).pack(fill="x")

        # --- Scrollable Display Box ---
        self.output = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#ffffff",
            fg="#111827",
            padx=10,
            pady=10,
            state='disabled'
        )
        self.output.pack(padx=15, pady=15, fill="both", expand=True)

        # --- Button Frame ---
        button_frame = tk.Frame(root, bg="#f3f4f6")
        button_frame.pack(fill="x", padx=10, pady=5)

        self.gen_button = tk.Button(
            button_frame,
            text="🧩 Generate Image Compression Code",
            command=self.generate_code,
            font=("Arial", 11, "bold"),
            bg="#2563eb",
            fg="white",
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2"
        )
        self.gen_button.pack(side="left", padx=5)

        self.check_button = tk.Button(
            button_frame,
            text="🔍 Check for Plagiarism",
            command=self.check_plagiarism,
            font=("Arial", 11, "bold"),
            bg="#059669",
            fg="white",
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2"
        )
        self.check_button.pack(side="left", padx=5)

        self.discussion_button = tk.Button(
            button_frame,
            text="💬 Show Discussion",
            command=self.show_discussion,
            font=("Arial", 11, "bold"),
            bg="#f59e0b",
            fg="black",
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2"
        )
        self.discussion_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(
            button_frame,
            text="🧹 Clear",
            command=self.clear_output,
            font=("Arial", 11, "bold"),
            bg="#dc2626",
            fg="white",
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2"
        )
        self.clear_button.pack(side="right", padx=5)

        # Storage
        self.generated_code = ""

    def display(self, text, prefix=""):
        """Helper to display formatted text"""
        self.output.config(state='normal')
        if prefix:
            self.output.insert(tk.END, f"\n{prefix}\n", "header")
        self.output.insert(tk.END, f"{text}\n\n")
        self.output.config(state='disabled')
        self.output.see(tk.END)

    def clear_output(self):
        self.output.config(state='normal')
        self.output.delete(1.0, tk.END)
        self.output.config(state='disabled')

    def generate_code(self):
        """Simulated AI-generated image compression code"""
        self.generated_code = """# AI-Generated Image Compression Snippet
# Author: AI Assistant (example demonstration)
# Description: Compress an image using Pillow (open-source library)

from PIL import Image

def compress_image(input_path, output_path, quality=30):
    with Image.open(input_path) as img:
        img.save(output_path, "JPEG", optimize=True, quality=quality)

# Example usage
# compress_image("input.jpg", "output_compressed.jpg", quality=40)
"""
        self.display(self.generated_code, prefix="🧩 Generated Code Snippet:")

    def check_plagiarism(self):
        """Check if open-source libraries are used without attribution"""
        if not self.generated_code:
            self.display("⚠️ Please generate a code snippet first.")
            return

        if "PIL" in self.generated_code or "cv2" in self.generated_code:
            result = (
                "✅ Check Result:\n"
                "The code uses the 'Pillow' (PIL) library, which is open-source under the MIT License.\n"
                "Attribution line detected: '# Author: AI Assistant (example demonstration)'\n\n"
                "✅ Proper Attribution: YES\n"
                "⚠️ Recommendation: When using code involving open-source libraries, always mention the source or license."
            )
        else:
            result = (
                "⚠️ No known open-source library detected, but ensure originality and give credit if reused from any source."
            )
        self.display(result, prefix="🔍 Plagiarism & Attribution Check:")

    def show_discussion(self):
        """Show discussion points"""
        discussion_text = (
            "💡 Discussion: Intellectual Property & Plagiarism in AI\n\n"
            "1️⃣ How Copyright Violations Affect Developers:\n"
            "   • Developers risk legal consequences when reusing copyrighted code without permission.\n"
            "   • Violations damage reputation and can lead to DMCA takedowns or loss of trust.\n"
            "   • Companies may face lawsuits or product bans for IP infringement.\n\n"
            "2️⃣ Best Practices for Attribution when using AI-generated Code:\n"
            "   • Always mention the AI or model used to generate the code (e.g., 'Generated with OpenAI ChatGPT').\n"
            "   • If the AI code imports open-source libraries, cite their license (MIT, GPL, Apache, etc.).\n"
            "   • Avoid copying entire codebases; use snippets for learning or modification only.\n"
            "   • Review and test code for originality, especially in public repositories.\n"
            "   • When unsure, include a disclaimer and link to the original author or license.\n\n"
            "✅ Ethical Coding builds trust, protects you legally, and ensures fair recognition of others' work."
        )
        self.display(discussion_text, prefix="💬 Discussion:")


# -------- Run GUI --------
if __name__ == "__main__":
    root = tk.Tk()
    app = IntellectualPropertyApp(root)
    root.mainloop()
