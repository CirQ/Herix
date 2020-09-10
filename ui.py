import re
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


class HerixApp(ttk.Notebook):
    def __init__(self, master=None):
        super().__init__(master)
        self.winfo_toplevel().title("Herix")
        # self.winfo_toplevel().geometry('800x600')
        self.winfo_toplevel().resizable(0, 0)
        self.create_components()
        self.pack(fill=tk.BOTH)
        # setting focus
        self.select(self.tab3)


    def create_components(self):
        # first function
        self.tab1 = self.create_github_issues()
        self.add(self.tab1, text='GitHub Issues')
        # second function
        self.tab2 = self.create_github_profile()
        self.add(self.tab2, text='GitHub Profile')
        # third function
        self.tab3 = self.create_dblp_bibtex()
        self.add(self.tab3, text='dblp bibtex')
        # next function
        self.tab4 = ttk.Frame(self)
        self.add(self.tab4, text='TBU')


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

            def _find_commits(tree):
                svg = tree.find('svg', class_='octicon-history')
                strong = svg.next_sibling
                while strong.find('strong') == -1:
                    strong = strong.next_sibling
                strong = strong.find('strong').text.strip()
                return int(strong.replace(',', ''))

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
                commit = _find_commits(b)
                return watch, star, fork, commit
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
                watch, star, fork, commit = _crawl_profile(content)
                _set_text(watch_text, str(watch))
                _set_text(star_text, str(star))
                _set_text(fork_text, str(fork))
                _set_text(commit_text, str(commit))
                dtstr = datetime.now().strftime('%c')
                date_label.config(text=f'Crawled on {dtstr}')
            except (ValueError, TypeError):
                _set_text(watch_text, 'Invalid URL!')
                _set_text(star_text, '')
                _set_text(fork_text, '')
                _set_text(commit_text, '')
                date_label.config(text='Crawled Date.')

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

        commit_panel = tk.Frame(right_panel)
        commit_panel.pack(anchor='e')
        commit_label = tk.Label(commit_panel, text='Commit Num.')
        commit_label.pack(side=tk.LEFT, padx=4, pady=8)
        commit_text = tk.Entry(commit_panel, width=32)
        commit_text.pack(padx=4, pady=8)
        commit_text.config(state=tk.DISABLED, disabledbackground='white')

        date_panel = tk.Frame(right_panel)
        date_panel.pack(anchor='w')
        date_label = tk.Label(date_panel, text='Crawled Date.')
        date_label.pack(side=tk.LEFT, padx=4, pady=8)

        return base


    def create_dblp_bibtex(self):

        perquery = 30

        def __ele2str(element):
            if isinstance(element, NavigableString):
                return str(element)
            elif isinstance(element, Tag):
                return element.text

        def _extract_from(html):
            papers = dict()
            b = BeautifulSoup(html, 'lxml')
            first = None
            for li in b.select('.publ-list .entry'):
                # meta
                id_ = li.attrs['id']
                class_ = li.attrs['class']
                class_.remove('entry')
                class_.remove('toc')
                assert len(class_) == 1

                # author
                ait = li.find_all('span', itemprop='author')
                authors = [it.text for it in ait]

                # title
                title_ele = li.find('span', class_='title')
                title_text = title_ele.text

                # venue
                eles = [__ele2str(it) for it in title_ele.next_siblings]
                venue = ''.join(eles)

                papers[id_] = (class_[0], authors, title_text, venue)
                if first is None:
                    first = class_[0]
            return papers, first

        # make this in a closure to preserve state
        paperdict = {
            'article': [],
            'inproceedings': [],
            'book': [],
            'editor': [],
            'informal': [],
        }
        allpapers = dict()
        last_title = None

        def _on_search_click(event=None):
            nonlocal paperdict, last_title, last_page
            content = title.get()
            if content == last_title:
                return
            last_title = content
            last_page = 0

            [v.clear() for v in paperdict.values()]

            url = f'https://dblp.uni-trier.de/search?q={content}'
            html = requests.get(url)
            papers, first = _extract_from(html.text)
            for id_, (class_, authors, title_txt, venue) in papers.items():
                for k, v in paperdict.items():
                    if k in class_:
                        v.append(id_)
                        break
                else:  # break does not happen
                    print('Unknown class:', class_)
            allpapers.update(papers)
            _update_paper_tabs(first, True)

        def _update_paper_tabs(first_class, renew_focus=False):
            tabs = {
                'article': (tab_journal, frame_journal),
                'inproceedings': (tab_conference, frame_conference),
                'book': (tab_book, frame_book),
                'editor': (tab_editor, frame_editor),
                'informal': (tab_informal, frame_informal),
            }

            [t[0].delete(0, tk.END) for t in tabs.values()]

            for class_, papers in paperdict.items():
                tab = tabs.get(class_)[0]
                for paperid in papers:
                    _, authors, title_txt, venue = allpapers[paperid]
                    # ic = frame'{" | ".join(authors)}\n{title_txt}\n{venue}'
                    title_item = tk.StringVar(tab, name=title_txt, value=paperid)
                    tab.insert('end', f' {title_item}')
            if renew_focus:
                nb.select(tabs[first_class][1])

        last_paper = None
        cached_bibtex = dict()

        def _on_paper_select(event, tab, class_):
            nonlocal last_paper
            try:
                idx = tab.curselection()[0]
                paper = paperdict[class_][idx]
                assert paper != last_paper
            except (IndexError, AssertionError):
                return
            last_paper = paper
            if paper not in cached_bibtex:
                url = f'https://dblp.uni-trier.de/rec/{paper}.html?view=bibtex'
                html = requests.get(url).text
                b = BeautifulSoup(html, 'lxml')
                verbatim = b.select_one('.verbatim')
                cached_bibtex[paper] = verbatim.text
            bibtex = cached_bibtex[paper]
            right_text.config(state=tk.NORMAL)
            right_text.delete(1.0, tk.END)
            right_text.insert(1.0, bibtex.strip())
            right_text.config(state=tk.DISABLED)

        def _create_paper_tab(master, class_):
            baseframe = tk.Frame(master)
            scrollx = tk.Scrollbar(baseframe, orient=tk.HORIZONTAL)
            scrolly = tk.Scrollbar(baseframe)
            tab = tk.Listbox(baseframe, xscrollcommand=scrollx.set, yscrollcommand=scrolly.set)
            scrollx.config(command=tab.xview)
            scrolly.config(command=tab.yview)
            scrollx.pack(fill=tk.X, side=tk.BOTTOM)
            scrolly.pack(fill=tk.Y, side=tk.RIGHT)
            tab.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
            tab.bind('<<ListboxSelect>>', lambda e: _on_paper_select(e, tab, class_))
            baseframe.pack()
            return tab, baseframe

        last_page = 0

        def _on_more_click(event=None):
            nonlocal paperdict, last_page
            content = title.get()
            if content == '' or content != last_title:
                return
            last_page += 1

            url = f'https://dblp.uni-trier.de/search/publ/inc?q={content}&h={perquery}&b={last_page}'
            html = requests.get(url)
            papers, _ = _extract_from(html.text)
            for id_, (class_, authors, title_txt, venue) in papers.items():
                for k, v in paperdict.items():
                    if k in class_:
                        v.append(id_)
                        break
                else:  # break does not happen
                    print('Unknown class:', class_)
            allpapers.update(papers)
            _update_paper_tabs(None)

        base = ttk.Frame(self)
        left_panel = tk.Frame(base)
        left_panel.pack(padx=4, side=tk.LEFT)

        lt = tk.Frame(left_panel)
        lt.pack(side=tk.TOP)
        title_label = tk.Label(lt, text='Paper Title:')
        title_label.pack(padx=10, anchor='w')
        title = tk.Entry(lt, width=60)
        title.bind('<Return>', _on_search_click)
        title.pack(padx=4, side=tk.LEFT)
        button = ttk.Button(lt, text='search', command=_on_search_click)
        button.pack(padx=4, side=tk.RIGHT)

        nb = ttk.Notebook(left_panel)
        nb.pack(expand=True, fill=tk.BOTH, padx=4, pady=8)
        tab_journal, frame_journal = _create_paper_tab(nb, 'article')
        nb.add(frame_journal, text='journal')
        tab_conference, frame_conference = _create_paper_tab(nb, 'inproceedings')
        nb.add(frame_conference, text='conference')
        tab_book, frame_book = _create_paper_tab(nb, 'book')
        nb.add(frame_book, text='book')
        tab_editor, frame_editor = _create_paper_tab(nb, 'editor')
        nb.add(frame_editor, text='editor')
        tab_informal, frame_informal = _create_paper_tab(nb, 'informal')
        nb.add(frame_informal, text='informal')

        more_btn = tk.Button(left_panel, text='more results', command=_on_more_click)
        more_btn.pack(pady=(10, 0), side=tk.BOTTOM)

        right_panel = tk.Frame(base)
        right_panel.pack(side=tk.RIGHT)
        scroll = tk.Scrollbar(right_panel, orient=tk.HORIZONTAL)
        scroll.pack(fill=tk.X, side=tk.BOTTOM)
        right_text = tk.Text(right_panel, wrap=tk.NONE, xscrollcommand=scroll.set)
        right_text.config(state=tk.DISABLED)
        scroll.config(command=right_text.xview)
        right_text.pack(padx=(0, 10), pady=4, side=tk.RIGHT)

        return base



def main():
    herix = HerixApp()
    herix.mainloop()


if __name__ == '__main__':
    main()
