import re
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from urllib.parse import urlparse


class HerixApp(ttk.Notebook):
    def __init__(self, master=None):
        super().__init__(master)
        self.winfo_toplevel().title("Herix")
        self.winfo_toplevel().geometry('800x600')
        self.winfo_toplevel().resizable(0, 0)
        self.create_components()
        self.pack(fill=tk.BOTH)


    def create_components(self):
        # first function
        self.tab1 = self.create_github_issues()
        self.add(self.tab1, text='GitHub Issues')
        # next function
        self.tab2 = ttk.Frame(self)
        self.add(self.tab2, text='TBU')


    def create_github_issues(self):
        PATH = re.compile(r'^/(.+?)/(.+?)/issues/(\d+)$')

        def _generate_bibtex(content):
            res = urlparse(content)
            if res.netloc != 'github.com':
                return 'invalid host: ' + res.netloc
            m = PATH.match(res.path)
            if m:
                user = m.group(1)
                repo = m.group(2)
                iid = int(m.group(3))
                today = datetime.now().strftime('%b. %e, %Y')
                return """
@online{{WEB:github/{repo:s}/{iid:d},
  title={{Issue \\#{iid:d} of project {repo:s}}},
  url={{https://github.com/{user:s}/{repo:s}/issues/{iid:d}}},
  note="(Accessed on {date:s})",
}}
                """.format(user=user, repo=repo, iid=iid, date=today)
            else:
                return 'invalid path: ' + res.path

        def _on_button_click():
            content = url.get()
            right_text.config(state=tk.NORMAL)
            bibtex = _generate_bibtex(content)
            right_text.delete(1.0, tk.END)
            right_text.insert(1.0, bibtex.strip())
            right_text.config(state=tk.DISABLED)

        base = tk.Frame(self)
        left_panel = tk.Frame(base)
        left_panel.pack(side=tk.LEFT)
        url_label = tk.Label(left_panel, text='GitHub Issue URL')
        url_label.pack(padx=10, anchor='w')
        url = tk.Entry(left_panel, width=64)

        url.insert(1, 'https://github.com/k9mail/k-9/issues/2110')

        url.pack(padx=10, pady=4)
        button = ttk.Button(left_panel, text='generate', command=_on_button_click)
        button.pack()
        right_text = tk.Text(base)
        right_text.config(state=tk.DISABLED)
        right_text.pack()
        return base


def main():
    herix = HerixApp()
    herix.mainloop()


if __name__ == '__main__':
    main()
