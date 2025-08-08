import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
from PIL import Image, ImageTk
import json
import urllib.request
import re
import html
from io import BytesIO
import os
import shutil

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
    print("tkinterdnd2 found!")
except ImportError:
    DND_AVAILABLE = False
    print("tkinterdnd2 NOT found.")

available_fonts = ["Roboto", "Slabo 27px", "Delius", "Borel", "Chewy", "Parisienne", "Barriecito", "Bangers", "Caveat", "DM Serif Text"]

def fetch_paintings():
    url = "https://www.pinotspalette.com/painting-library"
    print(f"Fetching HTML from: {url}")
    response = urllib.request.urlopen(url)
    html_content = response.read().decode('utf-8')
    painting_info = re.findall(
        r'<figure class="painting">.*?<img class="shadowed".*?data-src="(.*?)".*?alt="(.*?)"',
        html_content, re.DOTALL
    )
    print(f"Found {len(painting_info)} paintings")
    paintings = []
    for img_src, raw_title in painting_info:
        title = html.unescape(raw_title)
        url_clean = "tv".join(img_src.split('?')[0].rsplit("large", 1))
        paintings.append((title, url_clean))
        print(f"Title: {title}, URL: {url_clean}")
    return paintings

paintings = fetch_paintings()

script_dir = os.path.dirname(os.path.abspath(__file__))
local_dirs = [
    name for name in os.listdir(script_dir)
    if os.path.isdir(os.path.join(script_dir, name)) and
       os.path.isfile(os.path.join(script_dir, name, "room.txt"))
]

if not local_dirs:
    local_dirs = ['.']

#title_color = "#FFFF00"
#label_color = "#5555DD"
#artist_color = "#0000FF"
#bartender_color = "#00FF00"
#background_color = "#e7e7ed"
#panel_background = "#0094cc"

title_color = "#FFFF00"
label_color = "#5555DD"
artist_color = "#0000FF"
bartender_color = "#00FF00"
background_color = "#000000"
panel_background = "#000000"
footer_background = "#FF0080"

color_buttons = {}

if DND_AVAILABLE:
    root = TkinterDnD.Tk()
else:
    root = tk.Tk()
root.title("Painting Configuration")
root.configure(bg="#f1f1f1")
root.option_add('*Font', 'Arial 12')

artist_font_var = tk.StringVar(value=available_fonts[0])
bartender_font_var = tk.StringVar(value=available_fonts[0])
painting_font_var = tk.StringVar(value=available_fonts[0])
painting_override_title = tk.StringVar()
painting_override_file = tk.StringVar()

def save_config():
    override_title = painting_override_title_entry.get().strip()
    if painting_override_title_entry.is_placeholder_active() or not override_title:
        override_title = None

    selected_title = painting_combobox.get()  # Always use selected painting from combobox

    selected_dir = directory_combobox.get()
    save_path = os.path.join(selected_dir, "config.json")

    if painting_override_file.get():
        images_dir = os.path.join(selected_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        source_path = painting_override_file.get()
        filename = os.path.basename(source_path)
        dest_path = os.path.join(images_dir, filename)

        try:
            shutil.copy2(source_path, dest_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy image override:\n{e}")
            return

        painting_source = os.path.join("images", filename).replace("\\", "/")
    else:
        print(selected_title)
        painting_source = next((url for title, url in paintings if title == selected_title), "")
        print(painting_source)

    config = {
        "painting_name": override_title if override_title else selected_title,
        "artist_name": artist_name_entry.get(),
        "bartender_enabled": bartender_var.get(),
        "bartender_name": bartender_name_entry.get() if bartender_var.get() else "",
        "painting_source": painting_source,
        "fonts": {
            "artist_font": artist_font_var.get(),
            "bartender_font": bartender_font_var.get(),
            "painting_font": painting_font_var.get()
        },
        "colors": {
            "title_color": title_color,
            "label_color": label_color,
            "artist_color": artist_color,
            "bartender_color": bartender_color,
            "background_color": background_color,
            "panel_background": panel_background,
            "footer_background": footer_background
        }
    }

    with open(save_path, "w") as json_file:
        json.dump(config, json_file, indent=4)

    messagebox.showinfo("Success", f"Configuration saved as {save_path}")

def invert_hex_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0,2,4))
    return '#{:02X}{:02X}{:02X}'.format(255 - r, 255 - g, 255 - b)

def pick_color(var):
    color = colorchooser.askcolor()[1]
    if color:
        globals()[var] = color
        btn = color_buttons.get(var)
        if btn:
            btn.config(bg=color, fg=invert_hex_color(color))

def toggle_bartender_input():
    if bartender_var.get():
        bartender_name_entry.config(state="normal")
        bartender_font_combo.pack(side="left", padx=5)
    else:
        bartender_name_entry.config(state="disabled")
        bartender_font_combo.pack_forget()

def update_painting_list(*_):
    term = painting_search_var.get().lower()
    filtered = [t for t,_ in paintings if term in t.lower()]
    painting_combobox['values'] = filtered
    painting_combobox.set(filtered[0] if filtered else '')
    update_button_state(None)

def update_button_state(_):
    open_painting_button.config(state="normal" if painting_combobox.get() else "disabled")

def open_painting_window():
    title = painting_combobox.get()
    url = next((u for t,u in paintings if t==title), "")
    img = Image.open(BytesIO(urllib.request.urlopen(url).read()))
    img.thumbnail((800,800))
    photo = ImageTk.PhotoImage(img)
    win = tk.Toplevel(root); win.title(title)
    tk.Label(win, image=photo).pack(padx=10, pady=10); win.image=photo
    tk.Label(win, text=title, font=("Arial", 14, "bold"), bg="#f1f1f1").pack(pady=5)

def add_color_picker_buttons():
    for label, var in [("Title Color", "title_color"), ("Label Color", "label_color"), ("Artist Color", "artist_color"), ("Bartender Color", "bartender_color"), ("Background Color", "background_color"), ("Panel Background", "panel_background"), ("Footer Background", "footer_background")]:
        btn = tk.Button(advanced_options_colors_frame, text=label, command=lambda v=var: pick_color(v), relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50", bg=eval(var), fg=invert_hex_color(eval(var)))
        btn.pack(anchor="w", pady=2, fill="x")
        color_buttons[var]=btn

def toggle_advanced_options():
    if advanced_options_var.get():
        advanced_options_frame.pack(anchor="w", fill="x", padx=10)
        if not color_buttons: add_color_picker_buttons()
    else:
        advanced_options_frame.pack_forget()

def clear_overrides():
    painting_override_title_entry.delete(0, tk.END)
    painting_override_title_entry._add_placeholder()
    painting_override_title_entry.focus_set()
    root.focus()
    
    painting_override_file.set("")
    open_image_btn.config(state="disabled", bg="#cccccc", fg="black")

def browse_image():
    f = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")])
    if f:
        painting_override_file.set(f)
        open_image_btn.config(state="normal", bg="#4CAF50", fg="white")

def open_selected_image():
    path = painting_override_file.get()
    if os.path.exists(path):
        os.startfile(path)

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", color='grey', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()

    def _clear_placeholder(self, e=None):
        if self['fg'] == self.placeholder_color:
            self.delete(0, "end")
            self['fg'] = self.default_fg_color

    def _add_placeholder(self, e=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color

    def is_placeholder_active(self):
        return self['fg'] == self.placeholder_color

frame = tk.Frame(root,bg="#f1f1f1")
frame.pack(padx=20, pady=20, anchor="w", fill="both", expand=True)

artist_row = tk.Frame(frame, bg="#f1f1f1")
artist_row.pack(anchor="w", pady=5, fill="x")
tk.Label(artist_row, text="Artist Name:", bg="#f1f1f1").pack(side="left")
artist_name_entry = tk.Entry(artist_row, width=30, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50")
artist_name_entry.pack(side="left", fill="x", expand=True)
artist_font_combo = ttk.Combobox(artist_row, values=available_fonts, width=15, textvariable=artist_font_var, state="readonly")
artist_font_combo.pack(side="left", padx=5)

bartender_var = tk.BooleanVar()
bartender_row = tk.Frame(frame,bg="#f1f1f1"); bartender_row.pack(anchor="w", pady=5, fill="x")
tk.Checkbutton(bartender_row, text="Bartender Name", variable=bartender_var, bg="#f1f1f1", command=toggle_bartender_input).pack(side="left")
bartender_name_entry = tk.Entry(bartender_row, width=30, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50", state="disabled")
bartender_name_entry.pack(side="left", fill="x", expand=True)
bartender_font_combo = ttk.Combobox(bartender_row, values=available_fonts, width=15, textvariable=bartender_font_var, state="readonly")

painting_search_row = tk.Frame(frame, bg="#f1f1f1"); painting_search_row.pack(anchor="w", pady=5, fill="x")
painting_search_var = tk.StringVar()
painting_search_entry = PlaceholderEntry(painting_search_row, textvariable=painting_search_var, placeholder="Search for painting...", width=30, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50")
painting_search_entry.pack(side="left", fill="x", expand=True)
painting_combobox = ttk.Combobox(painting_search_row, width=30, state="readonly"); painting_combobox.pack(side="left", fill="x", expand=True)
painting_font_combo = ttk.Combobox(painting_search_row, values=available_fonts, width=15, textvariable=painting_font_var, state="readonly")
painting_font_combo.pack(side="left", padx=5)
painting_search_var.trace_add("write", update_painting_list)
painting_combobox.bind("<<ComboboxSelected>>", update_button_state)
open_painting_button = tk.Button(painting_search_row, text="Open Painting", command=open_painting_window, state="disabled", relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50", bg="#4CAF50", fg="white")
open_painting_button.pack(side="right", padx=5)

advanced_options_var = tk.BooleanVar()
tk.Checkbutton(frame, text="Show Advanced Options", variable=advanced_options_var, bg="#f1f1f1", command=toggle_advanced_options).pack(anchor="w", pady=5)
advanced_options_frame = tk.Frame(frame, bg="#f1f1f1")

advanced_options_colors_frame = tk.Frame(advanced_options_frame, bg="#f1f1f1")
advanced_options_colors_frame.pack(side="left", fill="y", padx=(0, 20), pady=5)

advanced_options_override_frame = tk.Frame(advanced_options_frame, bg="#f1f1f1")
advanced_options_override_frame.pack(side="left", fill="both", expand=True, pady=5)

painting_override_row = tk.Frame(advanced_options_override_frame, bg="#f1f1f1")
painting_override_row.pack(anchor="w", pady=5, fill="x")

painting_override_title_entry = PlaceholderEntry(painting_override_row, textvariable=painting_override_title, placeholder="Override painting title...", width=30, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50")
painting_override_title_entry.pack(side="left", fill="x", expand=True)

image_override_box = tk.Frame(painting_override_row, bg="#ddd", width=200, height=40, relief="ridge")
image_override_box.pack(side="left", padx=10)
image_override_box.pack_propagate(0)

open_image_btn = tk.Button(image_override_box, text="Open Image", state="disabled", relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50", bg="#cccccc")
open_image_btn.pack(side="left", padx=2, pady=2)
open_image_btn.config(command=lambda: open_selected_image())

browse_btn = tk.Button(image_override_box, text="Browse", command=browse_image, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50", bg="#cccccc")
browse_btn.pack(side="left", padx=(2, 0), pady=2)

if DND_AVAILABLE:
    def drop(event):
        path = event.data
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
        painting_override_file.set(path)
        open_image_btn.config(state="normal", bg="#4CAF50", fg="white")
    image_override_box.drop_target_register(DND_FILES)
    image_override_box.dnd_bind('<<Drop>>', drop)

clear_btn = tk.Button(advanced_options_override_frame, text="Clear Overrides", command=clear_overrides, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50", bg="#cccccc")
clear_btn.pack(anchor="w", pady=10)

save_row = tk.Frame(frame,bg="#f1f1f1")
save_row.pack(anchor="w", pady=10, fill="x")
tk.Button(save_row, text="Save Configuration", command=save_config, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50", bg="#4CAF50", fg="white").pack(side="left", padx=5)
directory_combobox = ttk.Combobox(save_row, values=local_dirs, width=40, state="readonly")
directory_combobox.pack(side="left", fill="x", expand=True)
directory_combobox.set(local_dirs[0])

root.mainloop()