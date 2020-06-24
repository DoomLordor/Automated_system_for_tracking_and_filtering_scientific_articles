import os
from pickle import load, dump
from pymorphy2 import MorphAnalyzer
import model.text_analis as ta

morph_dict_path = 'setting\\morph.md'

stop_word_path = 'setting\\stop_word.sd'

stop_word_text_file_path = 'setting\\stop_word.txt'


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

    def all_word_bag(self):
        if self.__len__() == 0:
            return []
        else:
            return [val.word_bag for val in self]

    def all_journal(self):
        if self.__len__() == 0:
            return []
        else:
            return [val.journal[1] for val in self]

    def append(self, val):
        if type(val) is not article:
            raise TypeError('must be article, not {}'.format(type(val).__name__))
        super().append(val)

    def __setitem__(self, key, value):
        if type(value) is not article:
            raise TypeError('must be article, not {}'.format(type(value).__name__))
        super().__setitem__(key, value)


class article:
    _journal_type = ['статья в журнале - научная статья', 'статья в журнале - материалы конференции',
                     'статья в журнале - обзорная статья', 'статья в журнале - редакторская заметка',
                     'статья в журнале - краткое сообщение']
    _conf_type = ['статья в сборнике трудов конференции', 'сборник трудов конференции', 'тезисы доклада на конференции',
                  'статья в сборнике статей', 'сборник тезисов конференции']

    def __init__(self, text_publication=None, address=None):
        self._text = None
        self.address = None
        self.name = None
        self.keywords = None
        self.annotation = None
        self.authors = None
        self.article_type = None
        self.journal = None
        self.word_bag = None
        if text_publication is not None and address is not None:
            self.search_on_page(text_publication, address)

    def search_on_page(self, text_publication, address):
        self.address = address
        self._text = text_publication
        self._find_name()
        self._find_keywords()
        self._find_annotation()
        self._find_authors()
        self._find_article_type()
        if self.article_type in self._journal_type:
            self._find_journal()
        elif self.article_type in self._conf_type:
            self._find_conf()
        del self._text
        self.word_bag_create()

    def word_bag_create(self, morph_analyzer=None, list_stop_words=None):
        annotation_dict = lemmatization_text(self.annotation)
        keywords_dict = lemmatization_text(self.keywords)
        name_dict = lemmatization_text(self.name)
        self.word_bag = ta.sum_dict(annotation_dict, keywords_dict, name_dict)

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
        if 'АННОТАЦИЯ' in self._text:
            i = self._text.find(
                '<div id="abstract1" style="width:504px; border:0;'
                + ' margin:0; padding:0; text-align:left;"><p align=justify>')
            j = self._text.find('</div>', i)
            self.annotation = self._text[i + 106: j]
        else:
            self.annotation = ''

    def _find_authors(self):
        all_author = {}
        i = self._text.find('<a href=\'author_items.asp?authorid=')
        text = self._text
        while i > 0:
            text = text[i:]
            k = text.find("' title='Список публикаций этого автора'>")
            j = text.find('</a>', k)
            if all_author.get(text[35:k]) is None:
                name = text[k + 41: j]
                name = name.replace('<b>', '')
                name = name.replace('</b>', '')
                all_author[text[35:k]] = name
            i = text.find('<a href=\'author_items.asp?authorid=', j)
        self.authors = all_author

    def _find_article_type(self):
        i = self._text.find('Тип:&nbsp;<font color=#00008f>')
        j = self._text.find('</font>', i)
        self.article_type = self._text[i + 30: j]

    def _find_journal(self):
        i = self._text.find('\n<a href="contents.asp?id=')
        k = self._text.find('" title="Оглавления выпусков этого журнала">', i)
        j = self._text.find('</a>', k)
        name = self._text[k + 44: j]
        name = name.replace('\n', '').replace('\r', '')
        self.journal = [self._text[i + 26: k], name]

    def _find_conf(self):
        if 'ИСТОЧНИК:' in self._text:
            i = self._text.find('<a href="item.asp?id=')
            k = self._text.find('">', i)
            j = self._text.find('</a>', k)
            self.journal = [self._text[i + 21: k], self._text[k + 2: j]]
        else:
            self.journal = ['', '']


class morph:
    _morph_dict = {}
    _analyzer = MorphAnalyzer()

    def __init__(self, path=morph_dict_path):
        self.load_morph_dict(path)

    def load_morph_dict(self, path=morph_dict_path):
        if os.path.exists(path) and path.endswith('.md'):
            if os.path.getsize(path):
                with open(path, 'rb') as f:
                    self._morph_dict = load(f)

    def dump_morph_dict(self, path=morph_dict_path):
        if not path.endswith('.md'):
            path = path + '.md'
        with open(path, 'wb') as f:
            dump(self._morph_dict, f)

    def normal_form(self, word):
        if self._morph_dict.get(word) is None:
            self._morph_dict[word] = self._analyzer.parse(word)[0].normal_form.upper()
        return self._morph_dict[word]


class stop_words:
    def __init__(self, path=stop_word_path):
        self.stop_words = []
        self.load_dict_stop_word(path)

    def load_dict_stop_word(self, path=stop_word_path):
        if os.path.exists(path) and path.endswith('.sd'):
            with open(path, 'rb') as f:
                self.stop_words = load(f)

    def load_dict_stop_word_text_file(self, path=stop_word_text_file_path):
        if os.path.exists(path) and path.endswith('.txt'):
            with open(path) as f:
                self.stop_words = f.read().upper().split('\n')
            with open(path, 'wb') as f:
                dump(self.stop_words, f)


def lemmatization_text(text, morph_analyzer=None, list_stop_words=None):
    if morph_analyzer is None:
        morph_analyzer = morph()
    if list_stop_words is None:
        list_stop_words = stop_words()
    text = ta.removing_special_characters(text)[0]
    word_dict = {}
    for word in text.split():
        lemm = morph_analyzer.normal_form(word)
        if word_dict.get(lemm) is None:
            word_dict[lemm] = 1
        else:
            word_dict[lemm] += 1
    if word_dict.get('') is not None:
        word_dict.pop('')
    word_dict = ta.delete_stop_word(word_dict, list_stop_words.stop_words)
    word_dict = ta.delete_english_word(word_dict)
    word_dict = ta.delete_numbers(word_dict)
    morph_analyzer.dump_morph_dict(morph_dict_path)
    return word_dict
