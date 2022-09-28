import os
import tkinter as tk
from tkinter import ttk
from modules.backend.db import DataBase
from modules.GUI.table import Table
from modules.GUI.app import App
from modules.GUI.add_sample import AddSampleTab
from modules.GUI.settings import Settings
from modules.backend.config import CFG, Fractions


def main():
    # Create Tk main window
    root_dir = os.getcwd()
    db = DataBase(root_dir)
    cfg = CFG(root_dir)
    fract = Fractions(root_dir)
    tk_window = tk.Tk()
    # Configure the root window
    tk_window.geometry('1000x620')
    tk_window.state(cfg.zoomed)
    tk_window.title('Sand granulometry')
    tk_window.iconphoto(True, tk.PhotoImage(file=os.path.join(root_dir, 'icon.png')))
    # Create tabs
    notebook = ttk.Notebook(tk_window)
    sample = AddSampleTab(notebook, db, fract, cfg)
    compare_samples = Table(notebook, db)
    settings = Settings(notebook, cfg, fract)
    app = App(notebook, sample, compare_samples, settings)
    app.start()
    tk_window.mainloop()


if __name__ == '__main__':
    main()
