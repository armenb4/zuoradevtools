from tkinter import ttk


def get_style():
    style = ttk.Style()
    style.configure(
        "TButton",
        font=("calibri", 14, "bold"),
        foreground="#1ce7c5",
        background="#1ce7c5",
    )
    style.map(
        "TButton",
        foreground=[
            ("active", "!disabled", "white"),
            ("disabled", "grey"),
        ],
        # background=[("active", "!disabled", "#1ce7c5"), ("disabled", "#1ce7c5")], - for mac use tkmacosx
    )

    return style
