import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from PIL import Image, ImageTk
import json
import urllib.request
import re
import html
from io import BytesIO
import os

# Preset font list (like Google Fonts)
available_fonts = ["Roboto", "Slabo 27px", "Delius", "Borel", "Chewy", "Parisienne", "Barriecito", "Bangers", "Caveat", "DM Serif Text"]

# Function to fetch painting information (returns list of (title, url))
def fetch_paintings():
    url = "https://www.pinotspalette.com/painting-library"
    print(f"Fetching HTML from: {url}")
    response = urllib.request.urlopen(url)
    html_content = response.read().decode('utf-8')

    painting_info = re.findall(
        r'<figure class="painting">.*?<img class="shadowed".*?data-src="(.*?)".*?alt="(.*?)"',
        html_content,
        re.DOTALL
    )

    print(f"Found {len(painting_info)} paintings")
    paintings = []
    for idx, (image_src, raw_title) in enumerate(painting_info):
        title = html.unescape(raw_title)
        url_clean = "tv".join(image_src.split('?')[0].rsplit("large", 1))
        paintings.append((title, url_clean))
        print(f"[{idx}] Title: {title}, URL: {url_clean}")

    return paintings

# Fetch paintings
paintings = fetch_paintings()

# Get list of subdirectories in the script's folder
script_dir = os.path.dirname(os.path.abspath(__file__))
local_dirs = [name for name in os.listdir(script_dir) if os.path.isdir(os.path.join(script_dir, name))]
if not local_dirs:
    local_dirs = ['.']

# Initialize default colors
title_color = "#FFFF00"
label_color = "#5555DD"
artist_color = "#0000FF"
bartender_color = "#00FF00"
background_color = "#e7e7ed"
panel_background = "#0094cc"

# Store color buttons here
color_buttons = {}

# Save configuration to JSON
def save_config():
    selected_title = painting_combobox.get()
    selected_url = next((url for title, url in paintings if title == selected_title), "")

    selected_dir = directory_combobox.get()
    save_path = os.path.join(selected_dir, "config.json")

    config = {
        "painting_name": selected_title,
        "artist_name": artist_name_entry.get(),
        "bartender_enabled": bartender_var.get(),
        "bartender_name": bartender_name_entry.get() if bartender_var.get() else "",
        "painting_source": selected_url,
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
            "panel_background": panel_background
        }
    }

    with open(save_path, "w") as json_file:
        json.dump(config, json_file, indent=4)

    messagebox.showinfo("Success", f"Configuration saved as {save_path}")

# Color picking
def pick_color(color_type):
    color = colorchooser.askcolor()[1]
    if color:
        globals()[color_type] = color
        btn = color_buttons.get(color_type)
        if btn:
            btn.config(bg=color, fg=invert_hex_color(color))

# Painting search update
def update_painting_list(*args):
    search_term = painting_search_var.get().lower()
    filtered_titles = [title for title, _ in paintings if search_term in title.lower()]
    painting_combobox['values'] = filtered_titles
    if filtered_titles:
        painting_combobox.set(filtered_titles[0])
    else:
        painting_combobox.set('')
    update_button_state(None)

# Painting preview window
def open_painting_window():
    painting_title = painting_combobox.get()
    painting_url = next((url for title, url in paintings if title == painting_title), "")
    response = urllib.request.urlopen(painting_url)
    image_data = response.read()
    image = Image.open(BytesIO(image_data))
    image.thumbnail((800, 800))
    photo = ImageTk.PhotoImage(image)

    painting_window = tk.Toplevel(root)
    painting_window.title(painting_title)
    tk.Label(painting_window, image=photo).pack(padx=20, pady=20)
    painting_window.image = photo  # keep reference
    tk.Label(painting_window, text=painting_title, font=("Arial", 14, "bold"), bg="#f1f1f1").pack(pady=10)

# Color utils
def invert_hex_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return '#{:02X}{:02X}{:02X}'.format(255 - r, 255 - g, 255 - b)

# Add color buttons once
def add_color_picker_buttons():
    color_fields = [
        ("Title Color", "title_color"),
        ("Label Color", "label_color"),
        ("Artist Color", "artist_color"),
        ("Bartender Color", "bartender_color"),
        ("Background Color", "background_color"),
        ("Panel Background", "panel_background")
    ]
    for label, var in color_fields:
        btn = tk.Button(
            advanced_options_frame,
            text=label,
            command=lambda v=var: pick_color(v),
            relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50",
            bg=eval(var),
            fg=invert_hex_color(eval(var))
        )
        btn.pack(anchor="w", pady=5)
        color_buttons[var] = btn

# Toggle advanced options
def toggle_advanced_options():
    if advanced_options_var.get():
        advanced_options_frame.pack(anchor="w")
        if not color_buttons:
            add_color_picker_buttons()
    else:
        advanced_options_frame.pack_forget()

# Toggle bartender field
def toggle_bartender_input():
    if bartender_var.get():
        bartender_name_entry.config(state="normal")
        bartender_font_combo.pack(side="left", padx=5)
    else:
        bartender_name_entry.config(state="disabled")
        bartender_font_combo.pack_forget()

# Enable/disable painting button
def update_button_state(event):
    open_painting_button.config(state="normal" if painting_combobox.get() else "disabled")

# UI start
root = tk.Tk()
root.title("Painting Configuration")
root.configure(bg="#f1f1f1")
root.option_add('*Font', 'Arial 12')

frame = tk.Frame(root, bg="#f1f1f1")
frame.pack(padx=20, pady=20, anchor="w", fill="both", expand=True)

# Font selection variables
artist_font_var = tk.StringVar(value=available_fonts[0])
bartender_font_var = tk.StringVar(value=available_fonts[0])
painting_font_var = tk.StringVar(value=available_fonts[0])

# Artist Name row
artist_row = tk.Frame(frame, bg="#f1f1f1")
artist_row.pack(anchor="w", pady=10, fill="x", expand=True)
tk.Label(artist_row, text="Artist Name:", bg="#f1f1f1").pack(side="left")
artist_name_entry = tk.Entry(artist_row, width=30, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50")
artist_name_entry.pack(side="left", fill="x", expand=True)
artist_font_combo = ttk.Combobox(artist_row, values=available_fonts, width=15, textvariable=artist_font_var, state="readonly")
artist_font_combo.pack(side="left", padx=5)

# Bartender Name row
bartender_var = tk.BooleanVar()
bartender_row = tk.Frame(frame, bg="#f1f1f1")
bartender_row.pack(anchor="w", pady=10, fill="x", expand=True)
bartender_checkbox = tk.Checkbutton(bartender_row, text="Bartender Name", variable=bartender_var, bg="#f1f1f1", relief="flat", command=toggle_bartender_input)
bartender_checkbox.pack(side="left")
bartender_name_entry = tk.Entry(bartender_row, width=30, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50")
bartender_name_entry.pack(side="left", fill="x", expand=True)
bartender_name_entry.config(state="disabled")
bartender_font_combo = ttk.Combobox(bartender_row, values=available_fonts, width=15, textvariable=bartender_font_var, state="readonly")

# Painting selection row
painting_search_row = tk.Frame(frame, bg="#f1f1f1")
painting_search_row.pack(anchor="w", pady=10, fill="x", expand=True)
tk.Label(painting_search_row, text="Search for a Painting:", bg="#f1f1f1").pack(anchor="w")
painting_search_var = tk.StringVar()
painting_search_var.trace_add("write", update_painting_list)
painting_search_entry = tk.Entry(painting_search_row, textvariable=painting_search_var, width=30, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50")
painting_search_entry.pack(anchor="w", fill="x", expand=True)
painting_combobox = ttk.Combobox(painting_search_row, width=30, state="readonly")
painting_combobox.pack(side="left", fill="x", expand=True)
painting_font_combo = ttk.Combobox(painting_search_row, values=available_fonts, width=15, textvariable=painting_font_var, state="readonly")
painting_font_combo.pack(side="left", padx=5)
painting_combobox.bind("<<ComboboxSelected>>", update_button_state)

# Open painting button
open_painting_button = tk.Button(
    painting_search_row, text="Open Painting", command=open_painting_window, state="disabled",
    relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50", bg="#4CAF50", fg="white"
)
open_painting_button.pack(side="right", padx=10)

# Advanced options
advanced_options_var = tk.BooleanVar()
tk.Checkbutton(frame, text="Show Advanced Options", variable=advanced_options_var, bg="#f1f1f1", command=toggle_advanced_options).pack(anchor="w", pady=10)
advanced_options_frame = tk.Frame(frame, bg="#f1f1f1")

# Save row
save_row = tk.Frame(frame, bg="#f1f1f1")
save_row.pack(anchor="w", pady=20, fill="x", expand=True)
tk.Button(save_row, text="Save Configuration", command=save_config, relief="flat", bd=2, highlightthickness=1, highlightcolor="#4CAF50", bg="#4CAF50", fg="white").pack(side="left", padx=(0,10))
directory_combobox = ttk.Combobox(save_row, values=local_dirs, width=40, state="readonly")
directory_combobox.pack(side="left", fill="x", expand=True)
directory_combobox.set(local_dirs[0])

root.mainloop()
