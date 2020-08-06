import os
from pickle import load, dump
from pymorphy2 import MorphAnalyzer
import model.text_analis as ta

morph_dict_path = 'setting\\morph.md'

stop_word_path = 'setting\\stop_word.sd'

stop_word_text_file_path = 'setting\\stop_word.txt'

journal_type = ['статья в журнале - научная статья', 'статья в журнале - материалы конференции',
                 'статья в журнале - обзорная статья', 'статья в журнале - редакторская заметка',
                 'статья в журнале - краткое сообщение']
conf_type = ['статья в сборнике трудов конференции', 'сборник трудов конференции', 'тезисы доклада на конференции',
              'статья в сборнике статей', 'сборник тезисов конференции']


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

    def __init__(self, text_publication=None, address=None, site_tupe=None):
        self.address = address
        self.name = None
        self.keywords = None
        self.annotation = None
        self.authors = None
        self.article_type = None
        self.journal = None
        self.year = None
        self.word_bag = None
        self.site_type = site_tupe
        if text_publication is not None and address is not None:
            if site_tupe == 'elibrary':
                self.search_on_elibrary_page(text_publication)

    def search_on_elibrary_page(self, text_publication):
        res = elibrary_find_text(text_publication)
        self.name = res[0]
        self.keywords = res[1]
        self.annotation = res[2]
        self.authors = res[3]
        self.article_type = res[4]
        self.journal = res[5]
        self.year = res[6]
        self.word_bag_create()

    def word_bag_create(self, morph_analyzer=None, list_stop_words=None):
        annotation_dict = lemmatization_text(self.annotation)
        keywords_dict = lemmatization_text(self.keywords)
        name_dict = lemmatization_text(self.name)
        self.word_bag = ta.sum_dict(annotation_dict, keywords_dict, name_dict)


def elibrary_find_text(text):
    res = []
    # Название статьи
    i = text.find('<title>')
    j = text.find('</title>', i)
    res.append(text[i + 7: j])
    # ключевые слова
    all_keywords = []
    i = text.find('<a href=\"keyword_items.asp?id=')
    temp_text = text
    while i > 0:
        temp_text = temp_text[i:]
        k = temp_text.find('">')
        j = temp_text.find('</a>', k)
        all_keywords.append(temp_text[k + 2: j])
        i = temp_text.find('<a href=\"keyword_items.asp?id=', j)
    res.append(' '.join(all_keywords))
    # аннотация
    if 'АННОТАЦИЯ' in text:
        i = text.find(
            '<div id="abstract1" style="width:504px; border:0;'
            + ' margin:0; padding:0; text-align:left;"><p align=justify>')
        j = text.find('</div>', i)
        res.append(text[i + 106: j])
    else:
        res.append('')
    # поиск авторов
    all_author = {}
    i = text.find("<a href='author_items.asp?authorid=")
    temp_text = text
    while i > 0:
        temp_text = temp_text[i:]
        k = temp_text.find("' title='Список публикаций этого автора'>")
        j = temp_text.find('</a>', k)
        if all_author.get(temp_text[35:k]) is None:
            name = temp_text[k + 41: j]
            name = name.replace('<b>', '')
            name = name.replace('</b>', '')
            all_author[temp_text[35:k]] = name
        i = temp_text.find('<a href=\'author_items.asp?authorid=', j)
    res.append(all_author)
    # тип статьи
    i = text.find('Тип:&nbsp;<font color=#00008f>')
    j = text.find('</font>', i)
    res.append(text[i + 30: j])

    if res[-1] in journal_type:
        i = text.find('\n<a href="contents.asp?id=')
        k = text.find('" title="Оглавления выпусков этого журнала">', i)
        j = text.find('</a>', k)
        name = text[k + 44: j]
        name = name.replace('\n', '').replace('\r', '')
        res.append([text[i + 26: k], name])
    elif res[-1] in conf_type:
        if 'ИСТОЧНИК:' in text:
            start = text.find('ИСТОЧНИК:')
            i = text.find('<a href="item.asp?id=', start)
            k = text.find('">', i)
            j = text.find('</a>', k)
            res.append([text[i + 21: k], text[k + 2: j]])
        else:
            res.append(['', ''])
    else:
        res.append(['', ''])
    # поиск года
    i = text.find('Год')
    j = text.find('</font>', i)
    res.append(text[j - 4:j])
    return res


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


Morph = morph()
Stop_Words = stop_words()


def lemmatization_text(text, morph_analyzer=Morph, list_stop_words=Stop_Words):
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
