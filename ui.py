import tkinter as tk


class HerixApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.winfo_toplevel().title("Herix")
        self.winfo_toplevel().geometry('800x600')
        self.winfo_toplevel().resizable(0, 0)
        self.pack()


def main():
    herix = HerixApp()
    herix.mainloop()


if __name__ == '__main__':
    main()
