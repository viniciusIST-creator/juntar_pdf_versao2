import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfMerger, PdfReader
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PDFMergerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Merger – Vinicius Coelho")
        self.geometry("1100x600")

        self.arquivos = []

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ===== TOPO =====
        topo = ctk.CTkFrame(self)
        topo.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ctk.CTkButton(topo, text="Adicionar PDFs", command=self.adicionar_pdfs, width=140).pack(side="left", padx=5)
        ctk.CTkButton(topo, text="Remover", command=self.remover_pdf, width=100).pack(side="left", padx=5)
        ctk.CTkButton(topo, text="Juntar PDFs", command=self.juntar_pdfs, width=140).pack(side="left", padx=5)

        # ===== LISTA (ESQUERDA) =====
        self.lista = tk.Listbox(
            self,
            bg="#1e1e1e",
            fg="white",
            selectbackground="#3a7ebf",
            activestyle="none",
            font=("Segoe UI", 10)
        )
        self.lista.grid(row=1, column=0, sticky="ns", padx=10, pady=10)
        self.lista.bind("<<ListboxSelect>>", self.atualizar_preview)

        # Drag & drop
        self.lista.bind("<ButtonPress-1>", self.drag_start)
        self.lista.bind("<B1-Motion>", self.drag_motion)

        # ===== PREVIEW (DIREITA) =====
        self.preview = ctk.CTkTextbox(self, width=400)
        self.preview.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.preview.insert("end", "Selecione um PDF para visualizar informações")
        self.preview.configure(state="disabled")

    # ===== FUNÇÕES =====

    def adicionar_pdfs(self):
        arquivos = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        for f in arquivos:
            if f not in self.arquivos:
                self.arquivos.append(f)
                paginas = len(PdfReader(f).pages)
                self.lista.insert("end", f"{os.path.basename(f)} ({paginas} páginas)")
        self.atualizar_preview()

    def remover_pdf(self):
        if not self.lista.curselection():
            return
        idx = self.lista.curselection()[0]
        self.lista.delete(idx)
        self.arquivos.pop(idx)
        self.atualizar_preview()

    def juntar_pdfs(self):
        if not self.arquivos:
            messagebox.showwarning("Aviso", "Nenhum PDF selecionado")
            return

        destino = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not destino:
            return

        merger = PdfMerger()
        for pdf in self.arquivos:
            merger.append(pdf)

        merger.write(destino)
        merger.close()

        messagebox.showinfo("Sucesso", "PDFs unidos com sucesso!")

    def atualizar_preview(self, event=None):
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")

        if not self.arquivos:
            self.preview.insert("end", "Nenhum PDF carregado.")
            self.preview.configure(state="disabled")
            return

        if self.lista.curselection():
            idx = self.lista.curselection()[0]
        else:
            idx = 0

        pdf = self.arquivos[idx]
        reader = PdfReader(pdf)

        self.preview.insert("end", f"ARQUIVO SELECIONADO\n")
        self.preview.insert("end", f"{os.path.basename(pdf)}\n\n")
        self.preview.insert("end", f"Páginas: {len(reader.pages)}\n\n")
        self.preview.insert("end", "ORDEM FINAL:\n")

        for i, arq in enumerate(self.arquivos, start=1):
            self.preview.insert("end", f"{i}. {os.path.basename(arq)}\n")

        self.preview.configure(state="disabled")

    # ===== DRAG & DROP =====

    def drag_start(self, event):
        self.drag_index = self.lista.nearest(event.y)

    def drag_motion(self, event):
        i = self.lista.nearest(event.y)
        if i != self.drag_index:
            self.arquivos.insert(i, self.arquivos.pop(self.drag_index))
            texto = self.lista.get(self.drag_index)
            self.lista.delete(self.drag_index)
            self.lista.insert(i, texto)
            self.lista.selection_set(i)
            self.drag_index = i
            self.atualizar_preview()


if __name__ == "__main__":
    app = PDFMergerApp()
    app.mainloop()
