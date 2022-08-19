import tkinter
from tkinter import Label, Button, Entry, END, WORD, Text, messagebox, Canvas, filedialog, IntVar, simpledialog
from tkinter.ttk import Progressbar
import customtkinter

import os
import ntpath
import threading

###Conversion modules
import PyPDF2
import pyttsx3
from gtts import gTTS
# Google Text-to-Speech(gTTS) works online better quality but slower


import urllib.request



customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")

class TextToSpeech:
    bg_color = 'white'

    def __init__(self):
        # Speaker
        self.speaker_engine = pyttsx3.init()

        # /********ROOT**********/
        # self.root = tkinter.Tk()
        self.root = customtkinter.CTk()
        self.root.title("Text to speech")
        self.root.config(bg=TextToSpeech.bg_color)

        # /******VARIABLES*******/
        self.page_num = 0
        self.file_path = None
        self.file_name = ''
        self.audio_prefix = ''
        self.num_of_pages = 0
        self.page_to_read = IntVar()
        self.page_to_read.set(1)
        self.page_text = ""

        # /*****CANVAS***********/
        self.canvas = Canvas(self.root, bg=TextToSpeech.bg_color, highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=20, pady=20)

        # /****CANVAS ELEMENTS*****/
        # App Label
        self.main_label = Label(self.canvas, text='Text-Speecher', font=("Montserrat", 18, 'bold'),
                                bg=TextToSpeech.bg_color)
        self.main_label.grid(row=0, column=0, pady=20, columnspan=2)

        # Upload File Button
        self.upload_btn = customtkinter.CTkButton(self.canvas, text="Choose File to read", command=self._upload_file, )
        self.upload_btn.grid(row=1, column=0, columnspan=2)

        # Textbox1
        self.text_box = Text(self.canvas, height=5, bg="lightgrey", font=("Times", 10))
        self.text_box.grid(column=0, row=2, columnspan=2, pady=10)

        # Page To Read Section
        self.page_label = Label(self.canvas, text="Page to read:", bg=TextToSpeech.bg_color)
        self.page_label.grid(row=3, column=0, sticky="e", pady=10, padx=10)
        self.page_to_read_entry = Entry(self.canvas, width=10, bg="lightgrey", justify="center",
                                        textvariable=self.page_to_read)
        self.page_to_read_entry.grid(column=1, row=3, sticky='w')

        # Read Page Button
        self.read_btn = customtkinter.CTkButton(self.canvas, text="Read uploaded file",fg_color=("red"),
                               command=lambda: threading.Thread(target=self._read_file).start())
        self.read_btn.grid(row=4, column=0)
        self.save_btn = customtkinter.CTkButton(self.canvas, text="Create audio file",
                               command=self._create_audiobook)
        self.save_btn.grid(row=4, column=1)

        # Page Content Section
        self.text_in_page = Text(self.canvas, height=10, bg="lightgrey", font=("Times", 10))
        self.text_in_page.grid(column=0, row=5, sticky="we", columnspan=2, pady=10)

        # Initial functions and mainloop
        self._pdf_details_manager()
        self.root.mainloop()

    def _pdf_details_manager(self):
        """renders text for pdf info section"""
        self.file_path = 'Null' if self.file_path is None else self.file_path
        self.num_of_pages = self._num_Pages()
        pdf_details = f"File location : {self.file_path}\n\nNumber of pages : {self.num_of_pages}"
        self.text_box.delete(1.0, "end")
        self.text_box.insert(END, pdf_details)
        self.text_box.config(wrap=WORD)

    def _num_Pages(self):
        try:
            path = open(self.file_path, "rb")
            pdf_reader = PyPDF2.PdfFileReader(path)
            return pdf_reader.numPages
        except Exception:
            return 0

    def _upload_file(self):
        self.speaker_engine.stop()
        x = filedialog.askopenfile(mode="r", filetypes=[('pdf file', '*.pdf')])
        self.file_path = x.name

        # check if file path is correct and render it to textbox
        if self.file_path is not None:
            self.file_name = ntpath.basename(self.file_path).split(".pdf")[0]
            self._pdf_details_manager()

    def _create_audiobook(self):
        try:
            path = open(self.file_path, "rb")
            self._get_audio_name()
            # todo get location of where to save mp3 from user
            threading.Thread(target=self.generate_audio, args=(path,)).start()
        except Exception as e:
            TextToSpeech._no_file_error()

    def _get_audio_name(self):
        # modify audio prefix
        file_name = simpledialog.askstring(title="Audio title ",
                                           prompt="Input name of audiofile.\nPress Y to retain original name",
                                           parent=self.root)
        self.audio_prefix = file_name if file_name.lower() == "y" else self.file_name

    def generate_audio(self, path):
        # disable button while creating audiofile
        try:
            self.save_btn.config(state="disabled", text=f"Creating {self.audio_prefix}....")
            text = TextToSpeech.all_pages_text(path, self.num_of_pages)

            # GTTS is online but has better quality pyttsx3 is offline but quality is poor
            if TextToSpeech.check_connection():
                audio = gTTS(text=text, lang="en", slow=False)
                audio.save(f"{self.audio_prefix}.mp3")
            else:
                self.speaker_engine.save_to_file(text,
                                                 f"{self.audio_prefix}.mp3")  # todo filepath selection for new file

            messagebox.showinfo("Audio conversion complete ",
                                f"Audio file creation complete.\nFile name is {self.audio_prefix}.mp3")
            self.save_btn.config(state="normal", text="Create audio file")
        except Exception as e:
            self.save_btn.config(state="normal", text="Create audio file")

    def _reset_save_btn(self):
        self.save_btn.config(state="normal", text="Create audio file")

    def reset_read_btn(self):
        self.read_btn.config(state="normal", text="Read uploaded file")


    @staticmethod
    def _no_file_error():
        messagebox.showerror("No file selected", "Choose file to read first")

    @staticmethod
    def all_pages_text(path, total_pages):
        """returns all text from the document as a string"""
        page_text_list = []
        pdf_reader = PyPDF2.PdfFileReader(path)
        for page in range(total_pages):
            t = pdf_reader.getPage(page).extract_text()
            page_text_list.append(t)
        all_pages_text = "".join(page_text_list)
        return all_pages_text

    @staticmethod
    def check_connection():
        try:
            urllib.request.urlopen('http://google.com')  # Python 3.x
            return True
        except:
            return False

    def _render_page_text(self):
        """renders page content to bottom text box"""
        self.text_in_page.delete(1.0, "end")
        self.text_in_page.insert(END, self.page_text)
        self.text_in_page.config(wrap=WORD)
        self.root.update()

    def _check_page_to_read(self, pdf_reader):
        try:
            self.page_num = self.page_to_read.get() - 1
            if self.page_num > self.num_of_pages or self.page_num < 0:
                messagebox.showinfo("Not within page range", f'The file has {self.num_of_pages}')
                return
            self.page_text = pdf_reader.getPage(self.page_num).extract_text()

            # check if page content is blank or can be read
            if self.page_text == "":
                messagebox.showerror("Page Error",
                                     "Page could not be read. It could either be empty or not decipherable")
                return

            self._render_page_text()

            # read the text
            x = self.page_to_read.get()
            self.read_btn.config(state="disabled", text=f"Reading page {x}....")
            self.speaker_engine.say(self.page_text)
            self.speaker_engine.runAndWait()
            self.root.update()
            self.reset_read_btn()
            messagebox.showinfo("Reading complete ", f"End of page {x}")

        except Exception as e:
            messagebox.showerror("Invalid page number",
                                 f"Invalid page number \"{self.page_to_read_entry.get()}\".\nTry again")

    def _read_file(self):
        """the main read function"""
        try:
            path = open(self.file_path, "rb")
            pdf_reader = PyPDF2.PdfFileReader(path)
            self._check_page_to_read(pdf_reader)
        except Exception as e:
            TextToSpeech._no_file_error()

    def _stop_reading(self):
        """halts the speaker"""
        self.speaker_engine.stop()

# if __name__ == "__main__":
#     ws = TextToSpeech()
