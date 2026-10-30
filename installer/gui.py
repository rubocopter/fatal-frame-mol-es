"""Small Spanish Windows installer: choose folder, verify, install or restore."""

import argparse
import json
import os
from pathlib import Path
import queue
import re
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from installer import core


def payload_folder():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)/"payload"
    return Path(__file__).resolve().parents[1]/"work/installer_payload"


def detect_game():
    libraries = []
    if os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                libraries.append(Path(winreg.QueryValueEx(key, "SteamPath")[0]))
        except OSError:
            pass
    libraries.append(Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))/"Steam")
    for library in list(libraries):
        config = library/"steamapps/libraryfolders.vdf"
        if config.is_file():
            for value in re.findall(r'"path"\s+"([^"\n]+)"', config.read_text(encoding="utf-8", errors="replace")):
                libraries.append(Path(value.replace("\\\\", "\\")))
    for library in libraries:
        common = library/"steamapps/common"
        if common.is_dir():
            for candidate in common.iterdir():
                if (candidate/"FATAL_FRAME_MOL.exe").is_file():
                    return str(candidate)
    return ""


class App:
    def __init__(self, root, game=""):
        self.root = root
        self.bundle = payload_folder()
        self.events = queue.Queue()
        self.busy = False
        self.path = tk.StringVar(value=game or detect_game())
        self.message = tk.StringVar(value="Elige la carpeta del juego y pulsa Comprobar.")
        self.detail = tk.StringVar(value="La carpeta debe contener FATAL_FRAME_MOL.exe.")
        root.title("FATAL FRAME · Traducción al castellano")
        root.geometry("840x590")
        root.minsize(780, 570)
        root.configure(bg="#11191f")
        root.protocol("WM_DELETE_WINDOW", self.close)
        icon = self.bundle/"luna.ico"
        if icon.is_file():
            root.iconbitmap(str(icon))
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#11191f")
        style.configure("TLabel", background="#11191f", foreground="#e7e3d7", font=("Segoe UI", 10))
        style.configure("Sub.TLabel", foreground="#a6b8c2", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=(16, 10), background="#25343e", foreground="#eee9db", borderwidth=0)
        style.map("TButton", background=[("active", "#354955"), ("disabled", "#1b2730")], foreground=[("disabled", "#697b85")])
        style.configure("Gold.TButton", background="#b9a474", foreground="#11191f", font=("Segoe UI", 10, "bold"))
        style.map("Gold.TButton", background=[("active", "#d0bc8b"), ("disabled", "#394248")])
        style.configure("Horizontal.TProgressbar", troughcolor="#25333c", background="#c0aa77", borderwidth=0, thickness=5)
        body = ttk.Frame(root, padding=28)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        header = tk.Canvas(body, height=122, bg="#11191f", highlightthickness=0)
        header.grid(row=0, column=0, sticky="ew")
        header.create_oval(2, 12, 66, 76, fill="#c4b488", outline="")
        header.create_oval(20, 4, 76, 65, fill="#11191f", outline="")
        header.create_text(96, 22, text="PROJECT ZERO", anchor="nw", fill="#eae4d7", font=("Times New Roman", 26))
        header.create_text(98, 62, text="MASK OF THE LUNAR ECLIPSE", anchor="nw", fill="#a5b6c0", font=("Segoe UI", 10))
        header.create_text(98, 91, text="TRADUCCIÓN AL CASTELLANO  ·  v0.1.0", anchor="nw", fill="#c4b488", font=("Segoe UI", 10))
        ttk.Label(body, text="Carpeta del juego", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", pady=(10, 9))
        folder = ttk.Frame(body)
        folder.grid(row=2, column=0, sticky="ew")
        folder.columnconfigure(0, weight=1)
        self.entry = ttk.Entry(folder, textvariable=self.path, font=("Segoe UI", 11))
        self.entry.grid(row=0, column=0, sticky="ew", ipady=9, padx=(0, 10))
        self.browse = ttk.Button(folder, text="Examinar…", command=self.choose)
        self.browse.grid(row=0, column=1)
        ttk.Label(body, text="Se sustituirán los recursos de la traducción, aunque tengas otros mods de texturas.",
                  style="Sub.TLabel", wraplength=740).grid(row=3, column=0, sticky="w", pady=(15, 5))
        ttk.Label(body, text="Se guardará una copia exacta de tus archivos anteriores. No necesitas instalar un pack HD.",
                  style="Sub.TLabel", wraplength=740).grid(row=4, column=0, sticky="w")
        ttk.Separator(body).grid(row=5, column=0, sticky="ew", pady=22)
        ttk.Label(body, textvariable=self.message, wraplength=740, font=("Segoe UI", 11, "bold")).grid(row=6, column=0, sticky="w")
        ttk.Label(body, textvariable=self.detail, wraplength=740, style="Sub.TLabel").grid(row=7, column=0, sticky="w", pady=(7, 14))
        self.bar = ttk.Progressbar(body, mode="determinate", maximum=100)
        self.bar.grid(row=8, column=0, sticky="ew", pady=(0, 18))
        buttons = ttk.Frame(body)
        buttons.grid(row=9, column=0, sticky="ew")
        buttons.columnconfigure(3, weight=1)
        self.check = ttk.Button(buttons, text="Comprobar", command=lambda: self.start("check"))
        self.check.grid(row=0, column=0, padx=(0, 9))
        self.apply = ttk.Button(buttons, text="Instalar / actualizar", style="Gold.TButton", command=lambda: self.start("install"))
        self.apply.grid(row=0, column=1, padx=(0, 9))
        self.undo = ttk.Button(buttons, text="Restaurar copia", command=lambda: self.start("restore"))
        self.undo.grid(row=0, column=2)
        ttk.Label(body, text="Versión de prueba · Windows x64 · onitaku / rubocopter", style="Sub.TLabel").grid(row=10, column=0, sticky="w", pady=(26, 0))
        self.controls = [self.entry, self.browse, self.check, self.apply, self.undo]
        root.after(100, self.poll)

    def choose(self):
        folder = filedialog.askdirectory(parent=self.root, title="Selecciona la carpeta de FATAL FRAME", mustexist=True)
        if folder:
            self.path.set(folder)
            self.message.set("Carpeta seleccionada. Puedes comprobarla o instalar.")
            self.detail.set("Solo se modifican los recursos de la traducción; las partidas se conservan.")

    def start(self, action):
        if self.busy:
            return
        game = self.path.get().strip().strip('"')
        if not game:
            messagebox.showinfo("Carpeta del juego", "Elige primero la carpeta donde está instalado el juego.", parent=self.root)
            return
        self.busy = True
        for control in self.controls:
            control.configure(state="disabled")
        self.message.set("Comprobando…" if action == "check" else "Preparando la operación…")
        self.detail.set("Espera a que termine antes de abrir el juego.")
        self.bar["value"] = 0
        threading.Thread(target=self.worker, args=(action, game), daemon=True).start()

    def worker(self, action, game):
        try:
            def progress(text, current, total):
                self.events.put(("progress", text, current*100/max(1,total)))
            if action == "check":
                result = core.inspect(game, self.bundle).message
            elif action == "install":
                result = core.install(game, self.bundle, progress)
            else:
                result = core.restore(game, self.bundle, progress)
            self.events.put(("done", result, action))
        except PermissionError:
            self.events.put(("error", "No se puede escribir en esa carpeta. Comprueba sus permisos o ejecuta el instalador como administrador."))
        except Exception as error:
            self.events.put(("error", str(error)))

    def poll(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "progress":
                    self.message.set(event[1])
                    self.bar["value"] = event[2]
                else:
                    self.busy = False
                    for control in self.controls:
                        control.configure(state="normal")
                    self.message.set("Comprobación terminada" if event[0] == "done" and event[2] == "check" else
                                     "Operación terminada" if event[0] == "done" else "No se ha podido completar")
                    self.detail.set(event[1])
                    if event[0] == "done":
                        self.bar["value"] = 100
                    else:
                        messagebox.showerror("Traducción al castellano", event[1], parent=self.root)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo("Operación en curso", "Espera a que termine para conservar la verificación y la copia de seguridad.", parent=self.root)
        else:
            self.root.destroy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-dir", default="")
    parser.add_argument("--action", choices=("check", "install", "restore"))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.action:
        try:
            if not args.game_dir or not args.report:
                raise ValueError("La prueba requiere --game-dir y --report.")
            result = (core.inspect(args.game_dir, payload_folder()).message if args.action == "check" else
                      getattr(core, args.action)(args.game_dir, payload_folder()))
            report = {"ok": True, "message": result}
        except Exception as error:
            report = {"ok": False, "message": str(error)}
        if args.report:
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0 if report["ok"] else 1
    root = tk.Tk()
    App(root, args.game_dir)
    root.mainloop()
    return 0
