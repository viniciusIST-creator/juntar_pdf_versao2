import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, Canvas, Scrollbar
from PyPDF2 import PdfMerger, PdfReader
from pdf2image import convert_from_path
from PIL import Image, ImageTk
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PDFMergerApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("PDF Merger – Vinicius Coelho")
        self.geometry("1200x700")

        self.arquivos = []
        self.preview_imgs = []
        self.zoom = 1.0

        self._build_ui()

    # ---------------- UI ---------------- #

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Topo
        topo = ctk.CTkFrame(self)
        topo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)

        ctk.CTkButton(topo, text="Adicionar PDFs", command=self.adicionar_pdfs).pack(side="left", padx=5)
        ctk.CTkButton(topo, text="Remover", command=self.remover_pdf).pack(side="left", padx=5)
        ctk.CTkButton(topo, text="Juntar PDFs", command=self.juntar).pack(side="left", padx=5)

        ctk.CTkButton(topo, text="Zoom +", command=lambda: self.alterar_zoom(0.1)).pack(side="right", padx=5)
        ctk.CTkButton(topo, text="Zoom -", command=lambda: self.alterar_zoom(-0.1)).pack(side="right", padx=5)

        # Lista
        self.lista = tk.Listbox(self, bg="#1e1e1e", fg="white", selectbackground="#444")
        self.lista.grid(row=1, column=0, sticky="ns", padx=5, pady=5)
        self.lista.bind("<<ListboxSelect>>", self.atualizar_preview)

        # Drag & drop
        self.lista.bind("<ButtonPress-1>", self.drag_start)
        self.lista.bind("<B1-Motion>", self.drag_motion)

        # Preview
        preview_frame = ctk.CTkFrame(self)
        preview_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.canvas = Canvas(preview_frame, bg="#1e1e1e", highlightthickness=0)
        self.scrollbar = Scrollbar(preview_frame, orient="vertical", command=self.canvas.yview)

        self.scroll_frame = ctk.CTkFrame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    # ---------------- Funções ---------------- #

    def adicionar_pdfs(self):
        arquivos = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        for f in arquivos:
            if f not in self.arquivos:
                self.arquivos.append(f)
                paginas = len(PdfReader(f).pages)
                self.lista.insert("end", f"{os.path.basename(f)} ({paginas} págs)")

        self.atualizar_preview()

    def remover_pdf(self):
        if not self.lista.curselection():
            return
        idx = self.lista.curselection()[0]
        self.lista.delete(idx)
        self.arquivos.pop(idx)
        self.atualizar_preview()

    def juntar(self):
        if not self.arquivos:
            return

        destino = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not destino:
            return

        merger = PdfMerger()
        for pdf in self.arquivos:
            merger.append(pdf)
        merger.write(destino)
        merger.close()

        # Preview do PDF FINAL
        self.preview_pdf(destino)

    def atualizar_preview(self, event=None):
        if not self.lista.curselection():
            return
        idx = self.lista.curselection()[0]
        self.preview_pdf(self.arquivos[idx])

    def preview_pdf(self, pdf_path):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        self.preview_imgs.clear()

        imagens = convert_from_path(pdf_path, dpi=int(120 * self.zoom))

        for img in imagens:
            img.thumbnail((700, 1200))
            tk_img = ImageTk.PhotoImage(img)
            self.preview_imgs.append(tk_img)

            lbl = ctk.CTkLabel(self.scroll_frame, image=tk_img, text="")
            lbl.pack(pady=5)

        self.canvas.yview_moveto(0)

    def alterar_zoom(self, delta):
        self.zoom = max(0.5, min(2.0, self.zoom + delta))
        self.atualizar_preview()

    # ---------------- Drag & Drop ---------------- #

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
