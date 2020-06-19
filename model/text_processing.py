import os
from pickle import load, dump
from pymorphy2 import MorphAnalyzer
from model.text_analis import removing_special_characters, delete_english_word, delete_stop_word, sum_dict

with open('setting\\stop_word.stopdict', 'rb') as f:
    dictionary_of_stop_words = load(f)


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
        annotation_dict = lemmatization_text(self.annotation)
        keywords_dict = lemmatization_text(self.keywords)
        name_dict = lemmatization_text(self.name)
        self.word_bag = sum_dict(annotation_dict, keywords_dict, name_dict)

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
        self.journal = [self._text[i + 26: k], self._text[k + 44: j]]

    def _find_conf(self):
        i = self._text.find('<a href="item.asp?id=')
        k = self._text.find('">', i)
        j = self._text.find('</a>', k)
        self.journal = [self._text[i + 21: k], self._text[k + 2: j]]


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
    text = removing_special_characters(text)[0]
    morph_analyzer = morph()
    word_dict = {}
    for word in text.split():
        lemm = morph_analyzer.normal_form(word)
        if word_dict.get(lemm) is None:
            word_dict[lemm] = 1
        else:
            word_dict[lemm] += 1
    if word_dict.get('') is not None:
        word_dict.pop('')
    word_dict = delete_stop_word(word_dict, dictionary_of_stop_words)
    word_dict = delete_english_word(word_dict)
    return word_dict

