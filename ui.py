import re
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class HerixApp(ttk.Notebook):
    def __init__(self, master=None):
        super().__init__(master)
        self.winfo_toplevel().title("Herix")
        # self.winfo_toplevel().geometry('800x600')
        self.winfo_toplevel().resizable(0, 0)
        self.create_components()
        self.pack(fill=tk.BOTH)


    def create_components(self):
        # first function
        self.tab1 = self.create_github_issues()
        self.add(self.tab1, text='GitHub Issues')
        # second function
        self.tab2 = self.create_github_profile()
        self.add(self.tab2, text='GitHub Profile')
        # next function
        self.tab3 = ttk.Frame(self)
        self.add(self.tab3, text='TBU')


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
                return 'invalid issue path: ' + res.path

        def _on_button_click(event=None):
            content = url.get()
            bibtex = _generate_bibtex(content)
            right_text.config(state=tk.NORMAL)
            right_text.delete(1.0, tk.END)
            right_text.insert(1.0, bibtex.strip())
            right_text.config(state=tk.DISABLED)

        base = tk.Frame(self)
        left_panel = tk.Frame(base)
        left_panel.pack(side=tk.LEFT)
        url_label = tk.Label(left_panel, text='GitHub Issue URL:')
        url_label.pack(padx=10, anchor='w')
        url = tk.Entry(left_panel, width=48)
        url.bind('<Return>', _on_button_click)
        url.pack(padx=10, pady=4)
        button = ttk.Button(left_panel, text='generate', command=_on_button_click)
        button.pack()
        right_text = tk.Text(base)
        right_text.config(state=tk.DISABLED)
        right_text.pack(padx=4, pady=4)
        return base


    def create_github_profile(self):
        PATH = re.compile(r'^/(.+?)/(.+?)$')
        WATCH = re.compile(r'/watchers$')
        STAR = re.compile(r'/stargazers$')
        FORK = re.compile(r'/members$')

        def _crawl_profile(content):
            res = urlparse(content)
            if res.netloc != 'github.com':
                raise ValueError('Invalid')
            m = PATH.match(res.path)
            if m:
                link = res.scheme + '://' + res.netloc + m.group(0)
                resp = requests.get(link)
                b = BeautifulSoup(resp.text, 'lxml')
                watch = int(b.find('a', {'href':WATCH})['aria-label'].split()[0])
                star = int(b.find('a', {'href':STAR})['aria-label'].split()[0])
                fork = int(b.find('a', {'href':FORK})['aria-label'].split()[0])
                return watch, star, fork
            else:
                raise ValueError('Invalid')

        def _set_text(text_widget, the_text):
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(0, tk.END)
            text_widget.insert(0, the_text)
            text_widget.config(state=tk.DISABLED, disabledbackground='white')

        def _on_button_click(event=None):
            content = url.get()
            try:
                watch, star, fork = _crawl_profile(content)
                _set_text(watch_text, str(watch))
                _set_text(star_text, str(star))
                _set_text(fork_text, str(fork))
            except (ValueError, TypeError):
                _set_text(watch_text, 'Invalid URL!')
                _set_text(star_text, '')
                _set_text(fork_text, '')

        base = ttk.Frame(self)
        left_panel = tk.Frame(base)
        left_panel.pack(side=tk.LEFT)
        url_label = tk.Label(left_panel, text='GitHub URL:')
        url_label.pack(padx=10, anchor='w')
        url = tk.Entry(left_panel, width=48)
        url.bind('<Return>', _on_button_click)
        url.pack(padx=10, pady=4)
        button = ttk.Button(left_panel, text='crawl', command=_on_button_click)
        button.pack()
        right_panel = tk.Frame(base)
        right_panel.pack(padx=64, pady=16, anchor='w')

        watch_panel = tk.Frame(right_panel)
        watch_panel.pack(anchor='e')
        watch_label = tk.Label(watch_panel, text='Watch Num.')
        watch_label.pack(side=tk.LEFT, padx=4, pady=8)
        watch_text = tk.Entry(watch_panel, width=32)
        watch_text.pack(padx=4, pady=8)
        watch_text.config(state=tk.DISABLED, disabledbackground='white')

        star_panel = tk.Frame(right_panel)
        star_panel.pack(anchor='e')
        star_label = tk.Label(star_panel, text='Star Num.')
        star_label.pack(side=tk.LEFT, padx=4, pady=8)
        star_text = tk.Entry(star_panel, width=32)
        star_text.pack(padx=4, pady=8)
        star_text.config(state=tk.DISABLED, disabledbackground='white')

        fork_panel = tk.Frame(right_panel)
        fork_panel.pack(anchor='e')
        fork_label = tk.Label(fork_panel, text='Fork Num.')
        fork_label.pack(side=tk.LEFT, padx=4, pady=8)
        fork_text = tk.Entry(fork_panel, width=32)
        fork_text.pack(padx=4, pady=8)
        fork_text.config(state=tk.DISABLED, disabledbackground='white')

        return base



def main():
    herix = HerixApp()
    herix.mainloop()


if __name__ == '__main__':
    main()
