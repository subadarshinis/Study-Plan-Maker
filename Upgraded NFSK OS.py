import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import webbrowser
import os
import json
import time
from PIL import ImageGrab

APP_DATA_FILE = "installed_apps.json"
HTML_APP_FOLDER = "html_apps"
USERS_FILE = "users.json"
USER_DATA_FOLDER = "user_data"

HTML_APPS = {
    "File Type Detector": "File type detector_Ethical coding.html",
    "HTML Viewer": "HTML.HTML",
    "ChatBot": "chatbot.html",
    "Quiz 1": "quiz 1.html",
    "Quiz 2": "quiz 2.html",
    "Study Plan Maker": "study plan maker.html"
}

class NFSKMiniOS:
    def __init__(self, root):
        self.root = root
        self.root.title("NFSK Mini OS")
        self.root.geometry("1000x700")
        self.username = ""
        self.wallpaper_path = None

        self.all_apps = {
            "App Store": self.open_app_store,
            "Notepad": self.launch_notepad,
            "MS Word": self.launch_ms_word,
            "MS Excel": self.launch_ms_excel,
            "Paint": self.launch_paint,
            "Chrome": self.launch_chrome,
            "File Explorer": self.open_file_explorer,
            "Clock": self.launch_clock_app,
        }

        self.installed_apps = dict(self.all_apps)
        self.icon_positions = {}
        self.custom_names = {}

        os.makedirs(HTML_APP_FOLDER, exist_ok=True)
        self.show_login_page()

    def show_login_page(self):
        self.users = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                self.users = json.load(f)

        login_frame = tk.Frame(self.root)
        login_frame.pack(expand=True)

        tk.Label(login_frame, text="NFSK Mini OS", font=("Arial", 16)).pack(pady=10)
        tk.Label(login_frame, text="Username:").pack()
        username_entry = tk.Entry(login_frame)
        username_entry.pack()

        tk.Label(login_frame, text="Password:").pack()
        password_entry = tk.Entry(login_frame, show="*")
        password_entry.pack()

        def login():
            username = username_entry.get()
            password = password_entry.get()
            if username in self.users and self.users[username] == password:
                self.username = username
                messagebox.showinfo("Welcome", f"Hello, {self.username}!")
                login_frame.destroy()
                self.load_os_ui()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")

        def register():
            username = username_entry.get()
            password = password_entry.get()
            if username and password:
                self.users[username] = password
                with open(USERS_FILE, "w") as f:
                    json.dump(self.users, f)
                messagebox.showinfo("Registered", "User registered successfully!")

        tk.Button(login_frame, text="Login", command=login).pack(pady=5)
        tk.Button(login_frame, text="Register", command=register).pack()

    def load_os_ui(self):
        self.desktop = tk.Canvas(self.root, bg="#cfd8dc")
        self.desktop.pack(fill='both', expand=True)

        self.taskbar = tk.Frame(self.root, bg='#0078d7', height=30)
        self.taskbar.pack(side='bottom', fill='x')

        tk.Button(self.taskbar, text='Start', bg='#005fa3', fg='white', command=self.show_start_menu).pack(side='left', padx=5)
        tk.Button(self.taskbar, text='Shutdown', bg='#a30000', fg='white', command=self.shutdown).pack(side='left', padx=5)
        self.clock_label = tk.Label(self.taskbar, fg='white', bg='#0078d7', font=("Arial", 10))
        self.clock_label.pack(side='right', padx=10)
        self.update_clock()

        self.load_user_data()
        self.create_desktop_icons()

        # Autosave on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def update_clock(self):
        self.clock_label.config(text=time.strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def create_icon(self, app_name, command, x=None, y=None):
        display_name = self.custom_names.get(app_name, app_name)
        font_size = 10 if len(display_name) <= 12 else 8 if len(display_name) <= 18 else 7
        btn = tk.Button(self.desktop, text=display_name, width=12, height=3, font=("Arial", font_size))
        btn.bind("<Button-1>", lambda e: self.icon_click_menu(app_name, command, btn))
        btn.bind("<B1-Motion>", lambda e, b=btn, a=app_name: self.drag_icon(e, b, a))
        if not x or not y:
            x, y = self.icon_positions.get(app_name, (20 + len(self.icon_positions) * 100, 20))
        self.icon_positions[app_name] = (x, y)
        self.desktop.create_window(x, y, anchor='nw', window=btn)

    def create_desktop_icons(self):
        self.desktop.delete("all")
        for app, cmd in self.installed_apps.items():
            pos = self.icon_positions.get(app, None)
            self.create_icon(app, cmd, *(pos if pos else (None, None)))

    def drag_icon(self, event, widget, app_name):
        x, y = event.x_root - self.root.winfo_rootx(), event.y_root - self.root.winfo_rooty()
        self.icon_positions[app_name] = (x, y)
        self.create_desktop_icons()
        self.save_user_data()

    def icon_click_menu(self, name, command, widget):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Open", command=command)
        if name not in self.all_apps:
            menu.add_command(label="Rename", command=lambda: self.rename_app(name))
            menu.add_command(label="Delete", command=lambda: self.delete_app(name))
        menu.tk_popup(widget.winfo_rootx(), widget.winfo_rooty())

    def rename_app(self, app_name):
        new_name = simpledialog.askstring("Rename", f"Enter new name for '{app_name}':")
        if new_name:
            self.custom_names[app_name] = new_name
            self.create_desktop_icons()
            self.save_user_data()

    def show_start_menu(self):
        win = tk.Toplevel(self.root)
        win.title("Start Menu")
        win.geometry("300x400")
        tk.Label(win, text=f"Installed Apps ({self.username})", font=('Arial', 12, 'bold')).pack(pady=10)
        for app in self.installed_apps:
            tk.Button(win, text=self.custom_names.get(app, app), command=self.installed_apps[app]).pack(pady=2)

    def open_app_store(self):
        win = tk.Toplevel(self.root)
        win.title("App Store")
        win.geometry("400x500")
        tk.Label(win, text="Install Apps", font=('Arial', 14)).pack(pady=10)
        for app, filename in HTML_APPS.items():
            if app not in self.installed_apps:
                frame = tk.Frame(win)
                frame.pack(fill='x', pady=2, padx=5)
                tk.Label(frame, text=app, width=20, anchor='w').pack(side='left')
                tk.Button(frame, text="Install", command=lambda a=app, f=filename: self.install_html_app(a, f)).pack(side='left')

    def install_html_app(self, app_name, filename):
        self.installed_apps[app_name] = self.make_html_launcher(filename)
        self.create_desktop_icons()
        self.save_user_data()
        messagebox.showinfo("Installed", f"{app_name} installed successfully.")

    def delete_app(self, app_name):
        if app_name in self.installed_apps:
            del self.installed_apps[app_name]
            if app_name in self.icon_positions:
                del self.icon_positions[app_name]
            if app_name in self.custom_names:
                del self.custom_names[app_name]
            self.create_desktop_icons()
            self.save_user_data()
            messagebox.showinfo("Deleted", f"{app_name} was removed.")

    def launch_notepad(self):
        win = tk.Toplevel(self.root)
        win.title("Notepad")
        win.geometry("500x400")
        text_area = tk.Text(win)
        text_area.pack(expand=True, fill='both')
        tk.Button(win, text="Save", command=lambda: self.save_text(text_area)).pack(side='left')
        tk.Button(win, text="Open", command=lambda: self.load_text(text_area)).pack(side='right')

    def launch_ms_word(self):
        win = tk.Toplevel(self.root)
        win.title("MS Word")
        win.geometry("600x400")
        text_area = tk.Text(win, font=("Times New Roman", 14))
        text_area.pack(expand=True, fill='both')
        tk.Button(win, text="Save", command=lambda: self.save_text(text_area, ".doc")).pack(side='left')
        tk.Button(win, text="Open", command=lambda: self.load_text(text_area)).pack(side='right')

    def launch_ms_excel(self):
        win = tk.Toplevel(self.root)
        win.title("MS Excel")
        win.geometry("600x400")
        entries = [[tk.Entry(win, width=12) for _ in range(5)] for _ in range(10)]
        for i, row in enumerate(entries):
            for j, e in enumerate(row):
                e.grid(row=i, column=j)

    def launch_paint(self):
        win = tk.Toplevel(self.root)
        win.title("Paint")
        win.geometry("500x400")
        canvas = tk.Canvas(win, bg='white')
        canvas.pack(fill='both', expand=True)
        canvas.bind('<B1-Motion>', lambda e: canvas.create_oval(e.x, e.y, e.x+2, e.y+2, fill='black'))

    def launch_chrome(self):
        try:
            chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
            if os.path.exists(chrome_path):
                os.startfile(chrome_path)
            else:
                webbrowser.open("https://www.google.com")
        except Exception as e:
            messagebox.showerror("Chrome Error", str(e))

    def make_html_launcher(self, filename):
        def launch():
            file_path = os.path.join(HTML_APP_FOLDER, filename)
            if os.path.exists(file_path):
                webbrowser.open(f"file://{os.path.abspath(file_path)}")
            else:
                messagebox.showerror("Missing", f"{filename} not found in '{HTML_APP_FOLDER}' folder.")
        return launch

    def launch_clock_app(self):
        win = tk.Toplevel(self.root)
        win.title("Clock")
        win.geometry("200x100")
        clock_label = tk.Label(win, font=("Arial", 24))
        clock_label.pack(expand=True)
        def update():
            clock_label.config(text=time.strftime("%H:%M:%S"))
            win.after(1000, update)
        update()

    def save_text(self, widget, ext=".txt"):
        path = filedialog.asksaveasfilename(defaultextension=ext)
        if path:
            with open(path, 'w') as f:
                f.write(widget.get("1.0", tk.END))

    def load_text(self, widget):
        path = filedialog.askopenfilename()
        if path:
            with open(path, 'r') as f:
                widget.delete("1.0", tk.END)
                widget.insert(tk.END, f.read())

    def open_file_explorer(self):
        path = filedialog.askopenfilename()
        if path:
            if os.name == 'nt':
                os.startfile(path)
            else:
                webbrowser.open(path)

    # --- Saving & Loading User Data ---
    def get_user_data_file(self):
        os.makedirs(USER_DATA_FOLDER, exist_ok=True)
        return os.path.join(USER_DATA_FOLDER, f"{self.username}_data.json")

    def save_user_data(self):
        data = {
            "apps": {name: f"html::{HTML_APPS.get(name, '')}" for name in self.installed_apps if name not in self.all_apps},
            "positions": self.icon_positions,
            "custom_names": self.custom_names
        }
        with open(self.get_user_data_file(), "w") as f:
            json.dump(data, f)

    def load_user_data(self):
        self.installed_apps = dict(self.all_apps)
        path = self.get_user_data_file()
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                for name, ref in data.get("apps", {}).items():
                    if ref.startswith("html::"):
                        filename = ref.split("::", 1)[1]
                        self.installed_apps[name] = self.make_html_launcher(filename)
                self.icon_positions = data.get("positions", {})
                self.custom_names = data.get("custom_names", {})

    def shutdown(self):
        if messagebox.askyesno("Shutdown", "Are you sure you want to shutdown?"):
            self.save_user_data()
            self.root.destroy()

    def on_exit(self):
        self.save_user_data()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = NFSKMiniOS(root)
    root.mainloop()
