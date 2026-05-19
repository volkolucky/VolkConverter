import os
import sys
import subprocess
import glob
import threading
import time
import re
import ctypes
import json
import shutil
import csv
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pygame
import windnd

def get_short_path_name(long_name):
    try:
        if not os.path.exists(long_name): return long_name
        buffer = ctypes.create_unicode_buffer(260)
        ctypes.windll.kernel32.GetShortPathNameW(long_name, buffer, 260)
        return buffer.value if buffer.value else long_name
    except: return long_name

LANG_DATA = {
    "RU": {
        "header": "WEM-BNK-PCK Audio Converter",
        "btn_start": "НАЧАТЬ КОНВЕРТАЦИЮ",
        "btn_stop": "ОСТАНОВИТЬ КОНВЕРТАЦИЮ",
        "btn_dict": "Загрузить словарь (JSON/CSV)",
        "btn_play": "▶",
        "btn_stop_play": "■",
        "btn_open_dir": "📁 Открыть результат",
        "btn_export_json": "Экспорт JSON",
        "btn_compare": "Сравнить билды",
        "btn_manual_sig": "Скан по сигнатуре",
        "log_succ": "КОНВЕРТАЦИЯ ЗАВЕРШЕНА.",
        "err_engine": "КРИТИЧЕСКАЯ ОШИБКА: Движки не найдены!",
        "path_src": "ПУТЬ ИСТОЧНИКА (Файл/Папка):",
        "path_dst": "ПУТЬ КОНВЕРТАЦИИ:",
        "src_lbl": "ИСТОЧНИКИ",
        "fmt_lbl": "ФОРМАТ",
        "filter_lbl": "ФИЛЬТРЫ И QoL",
        "struct_lbl": "СТРУКТУРА",
        "smart_lbl": "СМАРТ МОДУЛИ",
        "watch_mode": "Watchdog (Автоскан)",
        "radio_same": "В ту же папку",
        "radio_diff": "В другую папку"
    },
    "EN": {
        "header": "VOLK CONVERTER",
        "btn_start": "START CONVERSION",
        "btn_stop": "STOP CONVERSION",
        "btn_dict": "Load Dictionary (JSON/CSV)",
        "btn_play": "▶",
        "btn_stop_play": "■",
        "btn_open_dir": "📁 Open Output",
        "btn_export_json": "Export JSON",
        "btn_compare": "Compare Builds",
        "btn_manual_sig": "Manual Sig Scan",
        "log_succ": "CONVERSION COMPLETED.",
        "err_engine": "CRITICAL ERROR: Engines not found!",
        "path_src": "SOURCE PATH (File/Dir):",
        "path_dst": "CONVERSION PATH:",
        "src_lbl": "SOURCES",
        "fmt_lbl": "FORMAT",
        "filter_lbl": "FILTERS & QoL",
        "struct_lbl": "STRUCTURE",
        "smart_lbl": "SMART MODULES",
        "watch_mode": "Watchdog (Autoscan)",
        "radio_same": "Same folder",
        "radio_diff": "Different folder"
    }
}

def get_banner_text(lang="RU"):
    dog_art = r"""
 ┈┈┏╮┏╮┈┈┈┈┈┈┈┈╭╮ 
 ┈╭┛┗┛┗┳━━━━━━╮┃┃ 
 ┈┃▅┃▅┈┃╰╰╰╰╰╰┣╯┃ 
 ▇┻━╯┈┈┃╰╰╰╰╰╰┣━╯ 
 ┣━━━╯┈╰╰╰╰╰╰╰┃┈┈ 
 ╰━━┳┳━┓┏━┳┳┓┏╯┈┈ 
 ┈┈┈┃┃┈┃┃┈┃┃┃┃┈┈┈ 
"""
    logo_art = r"""
 __      __  ____   _        ____  _  _   ____   _  __  ________  ______  _     __  __ 
 \ \    / / / __ \ | |     / ___|| | | | / __ \ | |/ / |__    __||  ____|/ \    |  \/  |
  \ \  / / | |  | || |    | |    | |_| || |  | || ' /     |  |   | |__  / ^ \   | \  / |
   \ \/ /  | |  | || |    | |    |  _  || |  | ||  <      |  |   |  __|/ ___ \  | |\/| |
    \  /   | |__| || |____| |___ | | | || |__| || . \     |  |   | |__/ /   \ \ | |  | |
     \/     \____/ |______|____| |_| |_| \____/ |_|\_\    |__    |___/_/     \_\|_|  |_|

                     * V  O  L  C  H  O  K  * T  E  A  M  *
"""
    return dog_art + logo_art + f"\n SYSTEM: {LANG_DATA[lang]['header']}\n BUILD: 1005 \n"

class VolkConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VolkConverter v1005")
        self.geometry("1300x950")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#121212")
        
        self.lang = "RU"
        pygame.mixer.init()
        self.hash_dict = {}
        self.metadata_log = []
        self.watchdog_active = False
        self.is_converting = False
        self.cancel_flag = False
        self.last_files = []
        
        self.engine_dir = self.get_engine_path()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkScrollableFrame(self, width=320, corner_radius=0, fg_color="#1A1A1A", border_width=1, border_color="#333333")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="VolkConverter", font=("Courier New", 22, "bold"), text_color="#E0E0E0").pack(pady=10)
        
        self.lang_btn = ctk.CTkButton(self.sidebar, text="RU / EN", height=28, fg_color="#333333", hover_color="#444444", command=self.toggle_lang)
        self.lang_btn.pack(pady=10, padx=20)

        self.src_lbl = self.create_side_label(LANG_DATA[self.lang]["src_lbl"])
        self.wem_var, self.bnk_var, self.pck_var = ctk.BooleanVar(value=True), ctk.BooleanVar(value=True), ctk.BooleanVar(value=True)
        self.fsb_var, self.usm_var, self.hca_var = ctk.BooleanVar(value=True), ctk.BooleanVar(value=True), ctk.BooleanVar(value=True)
        self.create_check(self.sidebar, ".WEM", self.wem_var)
        self.create_check(self.sidebar, ".BNK", self.bnk_var)
        self.create_check(self.sidebar, ".PCK", self.pck_var)
        self.create_check(self.sidebar, ".FSB", self.fsb_var)
        self.create_check(self.sidebar, ".USM", self.usm_var)
        self.create_check(self.sidebar, ".HCA", self.hca_var)

        self.fmt_lbl = self.create_side_label(LANG_DATA[self.lang]["fmt_lbl"])
        self.out_fmt_var = ctk.StringVar(value="wav")
        ctk.CTkOptionMenu(self.sidebar, values=["wav", "mp3", "ogg", "flac"], variable=self.out_fmt_var, fg_color="#2C2C2C", button_color="#333333").pack(pady=5, padx=20)

        self.filter_lbl = self.create_side_label(LANG_DATA[self.lang]["filter_lbl"])
        self.norm_var, self.downmix_var, self.trim_var = ctk.BooleanVar(value=True), ctk.BooleanVar(), ctk.BooleanVar()
        self.sound_var = ctk.BooleanVar(value=True)
        self.create_check(self.sidebar, "EBU R128 Norm", self.norm_var)
        self.create_check(self.sidebar, "5.1 -> Stereo", self.downmix_var)
        self.create_check(self.sidebar, "Trim Silence", self.trim_var)
        self.create_check(self.sidebar, "Sound Notification", self.sound_var)

        self.struct_lbl = self.create_side_label(LANG_DATA[self.lang]["struct_lbl"])
        self.keep_struct_var, self.sort_var = ctk.BooleanVar(value=True), ctk.BooleanVar(value=True)
        self.tag_var, self.del_var, self.sub_var = ctk.BooleanVar(value=True), ctk.BooleanVar(), ctk.BooleanVar(value=True)
        self.create_check(self.sidebar, "Keep Dir Structure", self.keep_struct_var)
        self.create_check(self.sidebar, "Dict Auto-Sort", self.sort_var)
        self.create_check(self.sidebar, "Write Tags", self.tag_var)
        self.create_check(self.sidebar, "Delete Originals", self.del_var)
        self.create_check(self.sidebar, "Recursive Scan", self.sub_var)

        self.smart_lbl = self.create_side_label(LANG_DATA[self.lang]["smart_lbl"])
        self.watchdog_var = ctk.BooleanVar()
        self.watch_chk = self.create_check(self.sidebar, LANG_DATA[self.lang]["watch_mode"], self.watchdog_var)
        
        self.dict_btn = ctk.CTkButton(self.sidebar, text=LANG_DATA[self.lang]["btn_dict"], fg_color="#4A4A4A", hover_color="#5A5A5A", command=self.load_dict)
        self.dict_btn.pack(pady=10, padx=20, fill="x")
        
        self.compare_btn = ctk.CTkButton(self.sidebar, text=LANG_DATA[self.lang]["btn_compare"], fg_color="#4A4A4A", hover_color="#5A5A5A", command=self.open_compare)
        self.compare_btn.pack(pady=5, padx=20, fill="x")

        self.manual_btn = ctk.CTkButton(self.sidebar, text=LANG_DATA[self.lang]["btn_manual_sig"], fg_color="#4A4A4A", hover_color="#5A5A5A", command=self.open_manual_sig)
        self.manual_btn.pack(pady=5, padx=20, fill="x")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=30, pady=20, sticky="nsew")

        self.header_lbl = ctk.CTkLabel(self.main_frame, text=LANG_DATA[self.lang]["header"], font=("Courier New", 22, "bold"), text_color="#E0E0E0")
        self.header_lbl.pack(pady=10)

        self.path_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.path_container.pack(fill="x", pady=5)

        self.src_path_lbl = ctk.CTkLabel(self.path_container, text=LANG_DATA[self.lang]["path_src"], anchor="w", text_color="#AAAAAA")
        self.src_path_lbl.pack(fill="x")
        self.tar_row = self.create_path_row(self.path_container, self.browse_tar)
        self.tar_entry = self.tar_row.winfo_children()[0]

        self.exp_frame = ctk.CTkFrame(self.path_container, fg_color="transparent")
        self.dst_path_lbl = ctk.CTkLabel(self.exp_frame, text=LANG_DATA[self.lang]["path_dst"], anchor="w", text_color="#AAAAAA")
        self.dst_path_lbl.pack(fill="x")
        self.exp_row = self.create_path_row(self.exp_frame, self.browse_exp)
        self.exp_entry = self.exp_row.winfo_children()[0]

        self.exp_mode = ctk.IntVar(value=0)
        self.radio_s = ctk.CTkRadioButton(self.main_frame, text=LANG_DATA[self.lang]["radio_same"], variable=self.exp_mode, value=0, fg_color="#555555", command=self.update_exp_visibility)
        self.radio_s.pack(anchor="w", pady=2)
        self.radio_d = ctk.CTkRadioButton(self.main_frame, text=LANG_DATA[self.lang]["radio_diff"], variable=self.exp_mode, value=1, fg_color="#555555", command=self.update_exp_visibility)
        self.radio_d.pack(anchor="w", pady=2)

        self.progress = ctk.CTkProgressBar(self.main_frame, height=12, progress_color="#666666", fg_color="#222222")
        self.progress.pack(fill="x", pady=15); self.progress.set(0)
        
        self.stats_lbl = ctk.CTkLabel(self.main_frame, text="", font=("Consolas", 12), text_color="#AAAAAA")
        self.stats_lbl.pack(pady=5)

        self.start_btn = ctk.CTkButton(self.main_frame, text=LANG_DATA[self.lang]["btn_start"], height=55, font=("Courier New", 18, "bold"), fg_color="#333333", hover_color="#444444", command=self.toggle_conversion)
        self.start_btn.pack(fill="x", pady=10)

        self.util_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.util_frame.pack(fill="x", pady=5)
        self.open_dir_btn = ctk.CTkButton(self.util_frame, text=LANG_DATA[self.lang]["btn_open_dir"], width=150, fg_color="#2C2C2C", hover_color="#3A3A3A", command=self.open_out_dir)
        self.open_dir_btn.pack(side="left", padx=5)
        self.json_btn = ctk.CTkButton(self.util_frame, text=LANG_DATA[self.lang]["btn_export_json"], width=150, fg_color="#2C2C2C", hover_color="#3A3A3A", command=self.export_json)
        self.json_btn.pack(side="right", padx=5)

        self.player_frame = ctk.CTkFrame(self.main_frame, fg_color="#1A1A1A", border_width=1, border_color="#333333")
        self.player_frame.pack(fill="x", pady=15)
        self.play_box = ctk.CTkComboBox(self.player_frame, values=["Empty"], width=500, fg_color="#1A1A1A", border_color="#333333", button_color="#333333")
        self.play_box.pack(side="left", padx=10, pady=10)
        self.btn_p = ctk.CTkButton(self.player_frame, text=LANG_DATA[self.lang]["btn_play"], width=50, fg_color="#2C2C2C", command=self.play_audio)
        self.btn_p.pack(side="left", padx=5)
        self.btn_s = ctk.CTkButton(self.player_frame, text=LANG_DATA[self.lang]["btn_stop_play"], width=50, fg_color="#2C2C2C", command=self.stop_audio)
        self.btn_s.pack(side="left", padx=5)

        self.console = ctk.CTkTextbox(self.main_frame, height=450, font=("Consolas", 12), fg_color="#0A0A0A", text_color="#00FF00", border_width=1, border_color="#333333")
        self.console.pack(fill="x", expand=True)

        self.log(get_banner_text(self.lang))
        
        try:
            windnd.hook_dropfiles(self, func=self.handle_drop)
        except: pass

    def get_engine_path(self):
        """Определяет путь к папке с движками"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def handle_drop(self, files):
        if files:
            try:
                p = files[0].decode('gbk') if sys.platform == 'win32' else files[0].decode('utf-8')
            except:
                p = str(files[0])
            self.tar_entry.delete(0, 'end')
            self.tar_entry.insert(0, os.path.normpath(p))

    def toggle_lang(self):
        self.lang = "EN" if self.lang == "RU" else "RU"
        self.update_ui_text()

    def update_ui_text(self):
        d = LANG_DATA[self.lang]
        self.src_lbl.configure(text=d["src_lbl"])
        self.fmt_lbl.configure(text=d["fmt_lbl"])
        self.filter_lbl.configure(text=d["filter_lbl"])
        self.struct_lbl.configure(text=d["struct_lbl"])
        self.smart_lbl.configure(text=d["smart_lbl"])
        self.watch_chk.configure(text=d["watch_mode"])
        self.dict_btn.configure(text=d["btn_dict"])
        self.compare_btn.configure(text=d["btn_compare"])
        self.manual_btn.configure(text=d["btn_manual_sig"])
        self.header_lbl.configure(text=d["header"])
        self.src_path_lbl.configure(text=d["path_src"])
        self.dst_path_lbl.configure(text=d["path_dst"])
        self.radio_s.configure(text=d["radio_same"])
        self.radio_d.configure(text=d["radio_diff"])
        self.btn_p.configure(text=d["btn_play"])
        self.btn_s.configure(text=d["btn_stop_play"])
        self.open_dir_btn.configure(text=d["btn_open_dir"])
        self.json_btn.configure(text=d["btn_export_json"])
        if not self.is_converting: 
            self.start_btn.configure(text=d["btn_start"])

    def create_side_label(self, txt):
        lbl = ctk.CTkLabel(self.sidebar, text=txt, font=("Arial", 11, "bold"), text_color="#666666")
        lbl.pack(pady=(15,2), anchor="w", padx=20)
        return lbl

    def create_check(self, parent, txt, var):
        chk = ctk.CTkCheckBox(parent, text=txt, variable=var, fg_color="#555555", hover_color="#777777", text_color="#E0E0E0", font=("Arial", 11))
        chk.pack(anchor="w", padx=20, pady=3)
        return chk

    def create_path_row(self, parent, cmd):
        f = ctk.CTkFrame(parent, fg_color="transparent"); f.pack(fill="x", pady=(2, 10))
        e = ctk.CTkEntry(f, fg_color="#1A1A1A", border_color="#333333", text_color="#E0E0E0")
        e.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(f, text="...", width=50, fg_color="#2C2C2C", command=cmd).pack(side="right")
        return f

    def log(self, t): 
        self.console.insert("end", f"{t}\n")
        self.console.see("end")

    def log_history(self, t):
        try:
            with open(os.path.join(self.engine_dir, "history.log"), "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {t}\n")
        except: pass

    def update_exp_visibility(self):
        if self.exp_mode.get() == 1: 
            self.exp_frame.pack(fill="x", after=self.tar_row)
        else: 
            self.exp_frame.pack_forget()

    def browse_tar(self): 
        p = filedialog.askdirectory()
        if not p:
            p = filedialog.askopenfilename()
        if p:
            self.tar_entry.delete(0, 'end')
            self.tar_entry.insert(0, p)
            
    def browse_exp(self): 
        d = filedialog.askdirectory()
        if d:
            self.exp_entry.delete(0, 'end')
            self.exp_entry.insert(0, d)

    def load_dict(self):
        p = filedialog.askopenfilename(filetypes=[("Dict", "*.json *.csv *.txt")])
        if not p: return
        try:
            if p.endswith('.json'):
                with open(p, "r", encoding="utf-8") as f: self.hash_dict = json.load(f)
            elif p.endswith('.csv'):
                with open(p, "r", encoding="utf-8") as f:
                    r = csv.reader(f)
                    for row in r:
                        if len(row)>=2: self.hash_dict[row[0].strip()] = row[1].strip()
            else:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line: 
                            k, v = line.strip().split("=", 1)
                            self.hash_dict[k] = v
            self.log(f"[DICT] Loaded: {len(self.hash_dict)} entries")
        except Exception as e: self.log(f"[DICT] Error: {e}")

    def play_audio(self):
        f = self.play_box.get()
        if os.path.exists(f) and f.lower().endswith(('.wav', '.mp3', '.ogg')):
            try:
                pygame.mixer.music.load(f)
                pygame.mixer.music.play()
            except Exception as e:
                self.log(f"[PLAYER] Error: {e}")
            
    def stop_audio(self): 
        pygame.mixer.music.stop()

    def open_out_dir(self):
        d = self.exp_entry.get() if self.exp_mode.get() == 1 else self.tar_entry.get()
        if os.path.isdir(d): 
            os.startfile(d)
        elif os.path.isfile(d): 
            os.startfile(os.path.dirname(d))

    def export_json(self):
        if not self.metadata_log: 
            self.log("[JSON] No data to export")
            return
        p = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if p:
            with open(p, "w", encoding="utf-8") as f: 
                json.dump(self.metadata_log, f, indent=4, ensure_ascii=False)
            self.log(f"[JSON] Exported to {p}")

    def open_compare(self):
        w = ctk.CTkToplevel(self)
        w.title("Build Comparer")
        w.geometry("600x400")
        w.grab_set() 
        
        ctk.CTkLabel(w, text="Dir A (Old):").pack(pady=2)
        da = ctk.CTkEntry(w, width=400)
        da.pack(pady=2)
        
        ctk.CTkLabel(w, text="Dir B (New):").pack(pady=2)
        db = ctk.CTkEntry(w, width=400)
        db.pack(pady=2)
        
        res = ctk.CTkTextbox(w, width=550, height=200)
        res.pack(pady=10)
        
        def browse_a():
            d = filedialog.askdirectory()
            if d: da.delete(0, 'end'); da.insert(0, d)
            
        def browse_b():
            d = filedialog.askdirectory()
            if d: db.delete(0, 'end'); db.insert(0, d)
            
        ctk.CTkButton(w, text="Browse A", command=browse_a, width=100).pack(pady=2)
        ctk.CTkButton(w, text="Browse B", command=browse_b, width=100).pack(pady=2)
        
        def run_cmp():
            d1, d2 = da.get(), db.get()
            if not os.path.exists(d1) or not os.path.exists(d2):
                res.insert("end", "Invalid paths!\n")
                return
            f1 = {os.path.relpath(os.path.join(r, f), d1): os.path.getsize(os.path.join(r, f)) 
                  for r, d, fs in os.walk(d1) for f in fs}
            f2 = {os.path.relpath(os.path.join(r, f), d2): os.path.getsize(os.path.join(r, f)) 
                  for r, d, fs in os.walk(d2) for f in fs}
            s1, s2 = set(f1.keys()), set(f2.keys())
            added, removed = s2 - s1, s1 - s2
            changed = [f for f in s1.intersection(s2) if f1[f] != f2[f]]
            res.delete("1.0", "end")
            res.insert("end", f"ADDED: {len(added)}\n" + "\n".join(list(added)[:15]) + ("...\n" if len(added)>15 else "\n"))
            res.insert("end", f"\nREMOVED: {len(removed)}\n" + "\n".join(list(removed)[:15]) + ("...\n" if len(removed)>15 else "\n"))
            res.insert("end", f"\nCHANGED: {len(changed)}\n" + "\n".join(changed[:15]) + ("...\n" if len(changed)>15 else "\n"))
            
        ctk.CTkButton(w, text="COMPARE", command=run_cmp, fg_color="#555555").pack(pady=10)

    def open_manual_sig(self):
        w = ctk.CTkToplevel(self)
        w.title("Manual Signature Scanner")
        w.geometry("500x300")
        w.grab_set()
        
        ctk.CTkLabel(w, text="Target File:").pack(pady=5)
        tf = ctk.CTkEntry(w, width=350)
        tf.pack(pady=5)
        
        def browse_file():
            f = filedialog.askopenfilename()
            if f: tf.delete(0, 'end'); tf.insert(0, f)
            
        ctk.CTkButton(w, text="Browse", command=browse_file, width=100).pack(pady=2)
        
        ctk.CTkLabel(w, text="Signature (hex or text):").pack(pady=5)
        sig = ctk.CTkEntry(w, width=350)
        sig.pack(pady=5)
        
        ctk.CTkLabel(w, text="Offset (optional):").pack(pady=5)
        offset = ctk.CTkEntry(w, width=350, placeholder_text="0")
        offset.pack(pady=5)
        
        result_text = ctk.CTkTextbox(w, width=450, height=100)
        result_text.pack(pady=10)
        
        def scan():
            p, s = tf.get(), sig.get()
            if not os.path.exists(p) or not s:
                result_text.insert("end", "Invalid file or signature!\n")
                return
            try:
                if s.startswith("0x") or all(c in "0123456789ABCDEFabcdef " for c in s.replace(" ", "")):
                    hex_str = s.replace("0x", "").replace(" ", "")
                    pattern = bytes.fromhex(hex_str)
                else:
                    pattern = s.encode()
                
                off = int(offset.get()) if offset.get().isdigit() else 0
                
                with open(p, "rb") as f:
                    f.seek(off)
                    data = f.read()
                
                indices = [m.start() for m in re.finditer(re.escape(pattern), data)]
                out_dir = os.path.dirname(p)
                out_subdir = os.path.join(out_dir, "sig_dumps")
                os.makedirs(out_subdir, exist_ok=True)
                
                for i, start in enumerate(indices):
                    end = indices[i+1] if i+1 < len(indices) else len(data)
                    chunk = data[start:end]
                    out_file = os.path.join(out_subdir, f"sig_{i}_{start}.bin")
                    with open(out_file, "wb") as wf:
                        wf.write(chunk)
                
                result_text.delete("1.0", "end")
                result_text.insert("end", f"Found {len(indices)} blocks\nDumped to: {out_subdir}")
                self.log(f"[SIG] Found {len(indices)} blocks of {s}")
            except Exception as e:
                result_text.delete("1.0", "end")
                result_text.insert("end", f"Error: {str(e)}")
                
        ctk.CTkButton(w, text="SCAN & DUMP", command=scan, fg_color="#555555").pack(pady=10)

    def find_exe(self, name):
        """Поиск EXE файлов в папке с программой и в системных путях"""
        local_path = os.path.join(self.engine_dir, name)
        if os.path.exists(local_path):
            return local_path
        
        for root, dirs, files in os.walk(self.engine_dir):
            if name in files:
                return os.path.join(root, name)
        
        import shutil
        sys_path = shutil.which(name)
        if sys_path:
            return sys_path
            
        return ""

    def rip_pck(self, pck_path):
        base = os.path.splitext(os.path.basename(pck_path))[0]
        ext_files = []
        try:
            with open(pck_path, "rb") as f:
                data = f.read()
            indices = [m.start() for m in re.finditer(b'RIFF', data)]
            for i, start in enumerate(indices):
                if self.cancel_flag:
                    break
                end = indices[i+1] if i+1 < len(indices) else len(data)
                chunk = data[start:end]
                if b'WAVEfmt' in chunk:
                    tmp = os.path.join(os.path.dirname(pck_path), f"rip_{base}_{i}.wem")
                    with open(tmp, "wb") as wf:
                        wf.write(chunk)
                    ext_files.append((tmp, base))
            self.log(f"[PCK] Ripped {len(ext_files)} streams from {os.path.basename(pck_path)}")
        except Exception as e:
            self.log(f"[PCK] Error ripping {pck_path}: {e}")
        return ext_files

    def get_duration(self, ffp, f_path):
        try:
            cmd = f'"{ffp}" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{f_path}"'
            result = subprocess.check_output(cmd, shell=True, text=True, creationflags=0x08000000, timeout=10)
            return float(result.strip())
        except:
            return 0.0

    def process_file(self, f_path, cli, ff, ffp, base_out_dir, out_fmt, root_target):
        if self.cancel_flag:
            return False, 0
            
        f_path = os.path.abspath(f_path)
        is_pck = f_path.lower().endswith(".pck")
        
        if is_pck:
            items = self.rip_pck(f_path)
        else:
            items = [(f_path, "Standalone")]
            
        if not items:
            return False, 0
        
        cli_s, ff_s = get_short_path_name(cli), get_short_path_name(ff)
        succ = 0
        
        for p, parent_arch in items:
            if self.cancel_flag:
                break
                
            if not os.path.exists(p):
                continue
                
            orig_base = os.path.splitext(os.path.basename(p))[0]
            mapped_name = self.hash_dict.get(orig_base, orig_base)
            mapped_name = re.sub(r'[<>:"/\\|?*]', '_', mapped_name)
            
            work_out_dir = base_out_dir
            if self.keep_struct_var.get() and os.path.isdir(root_target):
                rel = os.path.relpath(os.path.dirname(f_path), root_target)
                if rel != "." and rel != "..":
                    work_out_dir = os.path.join(base_out_dir, rel)
            
            if is_pck:
                work_out_dir = os.path.join(work_out_dir, parent_arch)
                
            os.makedirs(work_out_dir, exist_ok=True)
            
            tmp_wav = os.path.join(work_out_dir, f"{mapped_name}_tmp.wav")
            p_s, tw_s = get_short_path_name(p), get_short_path_name(tmp_wav)
            
            vgm_cmd = f'"{cli_s}" -o "{tw_s}" "{p_s}"'
            try:
                subprocess.run(vgm_cmd, shell=True, capture_output=True, creationflags=0x08000000, timeout=60)
            except subprocess.TimeoutExpired:
                self.log(f"[ERROR] Timeout converting {orig_base}")
                continue
            
            if os.path.exists(tmp_wav) and os.path.getsize(tmp_wav) > 44:  
                cat_dir = work_out_dir
                dur = self.get_duration(ffp, tmp_wav) if ffp else 0.0
                
                if self.sort_var.get():
                    ln = mapped_name.lower()
                    if ln.startswith("bgm_") or dur > 35.0:
                        cat_dir = os.path.join(work_out_dir, "MUSIC")
                    elif ln.startswith("vo_") or "skill" in ln or "voice" in ln:
                        cat_dir = os.path.join(work_out_dir, "VOICE")
                    elif 0 < dur < 4.0:
                        cat_dir = os.path.join(work_out_dir, "SFX")
                
                os.makedirs(cat_dir, exist_ok=True)
                final_out = os.path.join(cat_dir, f"{mapped_name}.{out_fmt}")
                
                ff_cmd = f'"{ff_s}" -y -i "{tw_s}"'
                
                filters = []
                if self.norm_var.get():
                    filters.append("loudnorm")
                if self.trim_var.get():
                    filters.append("silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-50dB")
                if filters:
                    ff_cmd += f' -af "{",".join(filters)}"'
                if self.downmix_var.get():
                    ff_cmd += ' -ac 2'
                if self.tag_var.get():
                    ff_cmd += f' -metadata album="{parent_arch}" -metadata comment="VolchokData"'
                
                if out_fmt == "mp3":
                    ff_cmd += ' -b:a 192k'
                elif out_fmt == "ogg":
                    ff_cmd += ' -c:a libvorbis -q:a 5'
                elif out_fmt == "flac":
                    ff_cmd += ' -compression_level 5'
                    
                ff_cmd += f' "{final_out}"'
                
                try:
                    subprocess.run(ff_cmd, shell=True, capture_output=True, creationflags=0x08000000, timeout=60)
                except subprocess.TimeoutExpired:
                    self.log(f"[ERROR] FFmpeg timeout for {mapped_name}")
                    
                if os.path.exists(tmp_wav):
                    try:
                        os.remove(tmp_wav)
                    except:
                        pass
                
                if os.path.exists(final_out) and os.path.getsize(final_out) > 0:
                    succ += 1
                    self.last_files.append(final_out)
                    self.metadata_log.append({
                        "file": os.path.basename(final_out),
                        "path": final_out,
                        "src": f_path,
                        "duration": dur,
                        "format": out_fmt,
                        "original_name": orig_base
                    })
                    self.log(f"  [OK] {mapped_name}.{out_fmt} ({dur:.1f}s)")
            else:
                self.log(f"  [FAIL] {orig_base} - conversion failed")
            
            if is_pck and os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass
            
        if self.del_var.get() and succ > 0 and os.path.exists(f_path) and not is_pck:
            try:
                os.remove(f_path)
            except:
                pass
                
        return succ > 0, succ

    def process(self, specific_files=None, is_watchdog_call=False):
        cli = self.find_exe("vgmstream-cli.exe")
        ff = self.find_exe("ffmpeg.exe")
        ffp = self.find_exe("ffprobe.exe")
        
        if not cli or not ff:
            self.log("[ERROR] " + LANG_DATA[self.lang]["err_engine"])
            messagebox.showerror("CRITICAL ERROR", LANG_DATA[self.lang]["err_engine"])
            self.reset_ui()
            return
            
        target = os.path.normpath(self.tar_entry.get())
        if not os.path.exists(target):
            self.log("[ERROR] Source path does not exist!")
            self.reset_ui()
            return
        
        if self.exp_mode.get() == 1:
            out_dir = os.path.normpath(self.exp_entry.get())
            if not out_dir:
                self.log("[ERROR] Output directory not specified!")
                self.reset_ui()
                return
        else:
            if os.path.isfile(target):
                out_dir = os.path.dirname(target)
            else:
                out_dir = target
        
        os.makedirs(out_dir, exist_ok=True)
        
        files = specific_files
        if not files:
            if os.path.isfile(target):
                ext = os.path.splitext(target)[1].lower()
                ext_map = {
                    '.wem': self.wem_var.get(), '.bnk': self.bnk_var.get(),
                    '.pck': self.pck_var.get(), '.fsb': self.fsb_var.get(),
                    '.usm': self.usm_var.get(), '.hca': self.hca_var.get()
                }
                if ext_map.get(ext, False):
                    files = [target]
                else:
                    self.log(f"[WARN] Extension {ext} not enabled for conversion")
                    self.reset_ui()
                    return
            else:
                exts = []
                if self.wem_var.get(): exts.append((".wem", ".WEM"))
                if self.bnk_var.get(): exts.append((".bnk", ".BNK"))
                if self.pck_var.get(): exts.append((".pck", ".PCK"))
                if self.fsb_var.get(): exts.append((".fsb", ".FSB"))
                if self.usm_var.get(): exts.append((".usm", ".USM"))
                if self.hca_var.get(): exts.append((".hca", ".HCA"))
                
                files = []
                for ext_low, ext_up in exts:
                    pattern = f"*{ext_low}"
                    found = glob.glob(os.path.join(target, "**" if self.sub_var.get() else "", pattern), recursive=self.sub_var.get())
                    files.extend(found)
                    pattern_up = f"*{ext_up}"
                    found_up = glob.glob(os.path.join(target, "**" if self.sub_var.get() else "", pattern_up), recursive=self.sub_var.get())
                    files.extend(found_up)
                
                files = list(set(files)) 
                
        if files:
            self.log(f"\n[START] Processing {len(files)} files...")
            t0 = time.time()
            completed = 0
            total_succ = 0
            total_err = 0
            
            with ThreadPoolExecutor(max_workers=min(os.cpu_count(), 8)) as ex:
                futures = {}
                for f in files:
                    if self.cancel_flag:
                        break
                    future = ex.submit(self.process_file, f, cli, ff, ffp, out_dir, self.out_fmt_var.get(), target)
                    futures[future] = f
                
                for future in as_completed(futures):
                    if self.cancel_flag:
                        break
                    res, s_cnt = future.result()
                    completed += 1
                    if res:
                        total_succ += s_cnt
                    else:
                        total_err += 1
                    self.progress.set(completed / len(files))
                    self.log(f" [{completed}/{len(files)}] {os.path.basename(futures[future])}")
            
            if self.last_files:
                display_files = self.last_files[-30:]
                self.play_box.configure(values=display_files)
                self.play_box.set(display_files[-1] if display_files else "Empty")
            
            tt = round(time.time() - t0, 1)
            stat_msg = f"Success: {total_succ} | Errors: {total_err} | Time: {tt}s"
            self.stats_lbl.configure(text=stat_msg)
            self.log_history(f"Target: {target} | {stat_msg}")
            
            if self.sound_var.get() and not self.cancel_flag:
                try:
                    ctypes.windll.user32.MessageBeep(0)
                except:
                    pass
                
            if not self.cancel_flag:
                self.log(f"\n[FINISH] {LANG_DATA[self.lang]['log_succ']}")
                self.log(stat_msg)
        else:
            self.log("[!] No matching files found.")
        
        if not is_watchdog_call:
            self.reset_ui()

    def watchdog_loop(self):
        self.log("[WATCHDOG] Active - scanning every 5 seconds...")
        cache = set()
        
        while self.watchdog_active and not self.cancel_flag:
            target = os.path.normpath(self.tar_entry.get())
            if os.path.exists(target):
                current_files = set()
                exts = ['.wem', '.bnk', '.pck', '.fsb', '.usm', '.hca']
                for ext in exts:
                    pattern = os.path.join(target, "**", f"*{ext}")
                    found = glob.glob(pattern, recursive=True)
                    pattern_up = os.path.join(target, "**", f"*{ext.upper()}")
                    found_up = glob.glob(pattern_up, recursive=True)
                    current_files.update(found)
                    current_files.update(found_up)
                
                new_files = [f for f in current_files if f not in cache]
                if new_files:
                    self.log(f"[WATCHDOG] Detected {len(new_files)} new files")
                    self.process(specific_files=new_files, is_watchdog_call=True)
                    cache.update(current_files)
            time.sleep(5)
        self.log("[WATCHDOG] Stopped")

    def toggle_conversion(self):
        if self.is_converting:
            self.cancel_flag = True
            self.start_btn.configure(text="STOPPING...", state="disabled")
        else:
            self.is_converting = True
            self.cancel_flag = False
            self.watchdog_active = False
            self.start_btn.configure(text=LANG_DATA[self.lang]["btn_stop"], fg_color="#8B0000")
            if self.watchdog_var.get():
                self.watchdog_active = True
                threading.Thread(target=self.watchdog_loop, daemon=True).start()
            else:
                threading.Thread(target=self.process, daemon=True).start()

    def reset_ui(self):
        self.is_converting = False
        self.cancel_flag = False
        self.watchdog_active = False
        self.start_btn.configure(state="normal", text=LANG_DATA[self.lang]["btn_start"], fg_color="#333333")
        self.progress.set(0)

if __name__ == "__main__":
    app = VolkConverter()
    app.mainloop()