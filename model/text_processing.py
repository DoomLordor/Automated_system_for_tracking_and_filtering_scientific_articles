import os
from pickle import load, dump
from pymorphy2 import MorphAnalyzer


class list_article(list):
    def __init__(self, iterable=None):
        if iterable is None:
            iterable = []
        for val in iterable:
            if type(val) is not article:
                raise TypeError('must be article, not {}'.format(type(val).__name__))

        super().__init__(iterable)

    def all_address(self):
        if self.__len__() == 0:
            return []
        else:
            return [val.address for val in self]


class article:
    def __init__(self, text_publication=None, address=None):
        if text_publication is not None and address is not None:
            self.search_on_page(text_publication, address)
        else:
            self._text = None
            self.address = None
            self.name = None
            self.keywords = None
            self.annotation = None
            self.authors = None
            self.article_type = None
            self.journal = None
            self.word_bag = None

    def search_on_page(self, text_publication, address):
        self.address = address
        self._text = text_publication
        self._find_name()
        self._find_keywords()
        self._find_annotation()
        self._find_authors()
        self._find_article_type()
        if self.article_type == 'статья в журнале - научная статья':
            self._find_journal()
        elif self.article_type == 'статья в сборнике трудов конференции':
            self._find_conf()
        del self._text
        self.word_bag_create()

    def word_bag_create(self):
        pass

    def _find_name(self):
        i = self._text.find('<title>')
        j = self._text.find('</title>', i)
        self.name = self._text[i + 7: j]

    def _find_keywords(self):
        all_keywords = []
        i = self._text.find('<a href=\"keyword_items.asp?id=')
        text = self._text
        while i > 0:
            text = text[i:]
            k = text.find('">')
            j = text.find('</a>', k)
            all_keywords.append(text[k + 2: j])
            i = text.find('<a href=\"keyword_items.asp?id=', j)
        self.keywords = ' '.join(all_keywords)

    def _find_annotation(self):
        i = self._text.find(
            '<div id="abstract1" style="width:504px; border:0; margin:0; padding:0; text-align:left;"><p align=justify>')
        j = self._text.find('</div>', i)
        self.annotation = self._text[i + 106: j]

    def _find_authors(self):
        all_author = {}
        i = self._text.find('<a href=\'author_items.asp?authorid=')
        text = self._text
        while i > 0:
            text = text[i:]
            k = text.find("' title='Список публикаций этого автора'>")
            j = text.find('</b></a>', k)
            if all_author.get(text[35:k]) is None:
                all_author[text[35:k]] = text[k + 44: j]
            i = text.find('<a href=\'author_items.asp?authorid=', j)
        self.authors = all_author

    def _find_article_type(self):
        i = self._text.find('???:&nbsp;<font color=#00008f>')
        j = self._text.find('</font>', i)
        self.article_type = self._text[i + 30: j]

    def _find_journal(self):
        i = self._text.find('\n<a href="contents.asp?id=')
        k = self._text.find('" title="Оглавления выпусков этого журнала?">', i)
        j = self._text.find('</a>', k)
        self.journal = {self._text[i + 26: k]: self._text[k + 44: j]}

    def _find_conf(self):
        i = self._text.find('<a href="item.asp?id=')
        k = self._text.find('">', i)
        j = self._text.find('</a>', k)
        self.journal = {self._text[i + 21: k]: self._text[k + 2: j]}


class morph:
    _morph_dict = {}
    _analyzer = MorphAnalyzer()

    def load_morph_dict(self, path):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self._morph_dict = load(f)

    def dump_morph_dict(self, path):
        with open(path, 'wb') as f:
            dump(self._morph_dict, f)

    def normal_form(self, word):
        if self._morph_dict.get(word) is None:
            self._morph_dict[word] = self._analyzer.parse(word)[0].normal_form.upper()
        return self._morph_dict[word]


def lemmatization_text(text):
    pass


def removing_special_characters(input_text):
    special_characters = '–«»;()"-.,:\t•—\n'
    for char in special_characters:
        for i, word in enumerate(input_text):
            if char in word:
                input_text[i] = word.replace(char, ' ')
    return input_text


# даление спец символов

with open("setting\\stop_word.txt") as f:
    dictionary_of_stop_words = f.read().upper().split('\n')