import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
from free_translator import FreeTranslator

class TranslatorApp:
    LANGUAGES = ["en", "ru", "fr", "it"]

    def __init__(self, root):
        self.root = root
        self.root.title("Free Translator")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Source Language").grid(row=0, column=0, padx=5, pady=5)
        self.source_lang = tk.StringVar(value=self.LANGUAGES[0])
        source_menu = ttk.Combobox(self.root, textvariable=self.source_lang, values=self.LANGUAGES, state="readonly")
        source_menu.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Target Language").grid(row=1, column=0, padx=5, pady=5)
        self.target_lang = tk.StringVar(value=self.LANGUAGES[1])
        target_menu = ttk.Combobox(self.root, textvariable=self.target_lang, values=self.LANGUAGES, state="readonly")
        target_menu.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Choose Input File", command=self.choose_input_file).grid(row=2, column=0, padx=5, pady=5)
        self.input_file_label = tk.Label(self.root, text="")
        self.input_file_label.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Choose Output File", command=self.choose_output_file).grid(row=3, column=0, padx=5, pady=5)
        self.output_file_label = tk.Label(self.root, text="")
        self.output_file_label.grid(row=3, column=1, padx=5, pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=2, pady=10)

        tk.Button(self.root, text="Start Translation", command=self.start_translation).grid(row=5, column=0, columnspan=2, pady=10)

    def choose_input_file(self):
        file_path = filedialog.askopenfilename()
        self.input_file_label.config(text=file_path)

    def choose_output_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        self.output_file_label.config(text=file_path)

    def update_progress(self, value):
        self.progress["value"] = value
        self.root.update_idletasks()

    def start_translation(self):
        source = self.source_lang.get()
        target = self.target_lang.get()
        input_file = self.input_file_label.cget("text")
        output_file = self.output_file_label.cget("text")

        if not source or not target or not input_file or not output_file:
            messagebox.showerror("Error", "Please fill in all fields and select files.")
            return

        def translate():
            try:
                translator = FreeTranslator(source=source, target=target)
                translator.translate_file(input_file, output_file, self.update_progress)
                messagebox.showinfo("Success", "Translation completed!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        threading.Thread(target=translate).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
