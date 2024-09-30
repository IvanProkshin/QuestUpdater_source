import multiprocessing
import os
import subprocess
from threading import Thread
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askyesno, showerror, showwarning, showinfo
import requests
import wget
from bs4 import BeautifulSoup


class CustomOutput(Text):
    def write(self, prompt):
        self.insert(END, f"{prompt}\n")

    def flush(self):
        pass

    def fileno(self):
        return 1


def progress_update(*args):
    global progress
    progress["value"] = (args[0] / args[1] * 100)
    percent["text"] = str(int(args[0] / args[1] * 100)) + "%"
    root.update()
    if args[0] == args[1]:
       showinfo("Прошивка скачана.", "Прошивка скачана.")


def select_adb():
    global file
    file = askopenfilename(filetypes=[('Executable files', '*.exe',)])
    if file:
        button_check["state"] = "normal"
        label_path["text"] = file
    else:
        showwarning("Драйвер не выбран!", "Сначала выберете драйвер!")


def check_connect_func():
    with subprocess.Popen(f"{file} devices", stdout=subprocess.PIPE, text=True) as connected_to_adb:
        if connected_to_adb.communicate()[0] != "List of devices attached\n\n":
            button_run["state"] = "normal"
        else:
           showerror("Шлем не обнаружен!", "Шлем не обнаружен!")


def run_update(file):
    text_out.insert(END, file)
    text_out.insert(END, f"{file} sideload firmware.zip")
    with subprocess.Popen(f"{file} sideload firmware.zip", stdout=subprocess.PIPE, text=True, universal_newlines=True) as updater:
        for line in updater.stdout:
            text_out.insert(END, line.encode("windows-1251").decode("cp866"))


adb_pth: str
file = "./files/adb.exe"

root = Tk()
root.title("Quest updater")
root.iconbitmap("./files/favicon.ico")
root.geometry("500x500+710+290")

button_select = ttk.Button(root, text="Путь к adb драйверу", command=select_adb)
button_check = ttk.Button(root, text="Проверить подключение по adb", command=check_connect_func, state="normal")
button_run = ttk.Button(root, text="Запустить прошивку", command=Thread(target=lambda: run_update(file)).start,
                        state="disabled")
label_path = ttk.Label(root)
progress = ttk.Progressbar(orient="horizontal", length=430)
percent = ttk.Label(root, text="100%" if "firmware.zip" in os.listdir("./") else "0%")
text_out = CustomOutput(root, width=59, height=20, background="black", foreground="green")

button_select.place(x=10, y=10)
button_check.place(x=10, y=40)
button_run.place(x=10, y=70)
text_out.place(x=10, y=100)
label_path.place(x=135, y=11)
progress.place(x=10, y=440)
percent.place(x=450, y=442)

label_path["text"] = file

if "firmware.zip" not in os.listdir("./"):
    if askyesno("Прошивка не найдена", "Прошивка не найдена. Загрузить сейчас?"):
        text_out.insert(END, "making request...\n")
        bs = BeautifulSoup(requests.get("https://cocaine.trade/Quest_2_firmware").text, "lxml")
        text_out.insert(END, "parsing...\n")
        res = bs.find_all('a', 'fw-link')[-1].get("href")
        text_out.insert(END, "downloading...\n")
        downloaded_file = wget.detect_filename(res)
        multiprocessing.Process(target=wget.download(res, out="./firmware.zip", bar=progress_update),
                                daemon=True).start()
        text_out.insert(END, "downloaded\n")

if __name__ == "__main__":
    root.mainloop()
