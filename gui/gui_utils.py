import tkinter as tk


def clear_frame(frame):
    """Remove all widgets from a frame."""

    for widget in frame.winfo_children():
        widget.destroy()


def show_message(parent, title, message):
    """Display a simple information message."""

    from tkinter import messagebox

    messagebox.showinfo(
        title,
        message
    )


def show_error(parent, title, message):
    """Display a user-friendly error."""

    from tkinter import messagebox

    messagebox.showerror(
        title,
        message
    )