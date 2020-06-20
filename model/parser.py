import os
from time import sleep
from re import findall
import requests as req
from pickle import load
from random import random
from model.text_processing import article, list_article


def internet_connection(func):
    def wrapper(*arg, **keyword):
        try:
            func(*arg, **keyword)
        except Exception:
            return False
    return wrapper


def find_end_num(text):
    end_num_pattern = r'<a href="query_results\.asp\?pagenum=[\d]+">В&nbsp;конец</a>'
    st = findall(end_num_pattern, text)[0]
    i = st.find('<a href="query_results.asp?pagenum=')
    j = st.find('">В&nbsp;конец</a>', i)
    if i == -1:
        return 0
    return int(st[i + 35: j])


def find_id(text):
    id_pattern = r'<tr valign=middle bgcolor=#f5f5f5 id="a[\d]+">'
    all_id = findall(id_pattern, text)
    for i, val in enumerate(all_id):
        all_id[i] = val[39:-2]
    return all_id


class site_connection:
    state_code_decryption = {0: 'Ok',
                             -1: 'No_Internet_connection',
                             -2: 'No_Results_Found',
                             -3: 'Turing_Test',
                             -4: 'User_error',
                             -5: 'Server_Error',
                             -6: 'search_option_data is None',
                             -7: 'Site block program'}

    _issues_params_list = ['all', 'm1', 'm3', 'm6', 'm12']

    _order_by_params_list = ['rank', 'date', 'insdate', 'name', 'title', 'cited']

    search_option_data_blank = {'where_name': True,
                                'where_abstract': True,
                                'where_keywords': True,
                                'where_affiliation': False,
                                'where_references': False,
                                'where_fulltext': False,
                                'type_article': True,
                                'type_book': True,
                                'type_conf': True,
                                'type_preprint': False,
                                'type_disser': False,
                                'type_report': False,
                                'type_patent': False}
    _end_num = 0

    search_option_data = None

    state_code = 0

    articles = list_article()

    num_page = 1
    block_site = 'Из-за нарушения правил пользования сайтом eLIBRARY.RU'

    def __init__(self):
        # Иннициализация сессии
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'}

        self._session = req.Session()

        self._session.headers.update(headers)

        self._session.get('https://www.elibrary.ru/defaultx.asp')

    def login(self, login=None, password=None):
        # Вход в систему
        auth = None
        if login is not None and password is not None:
            auth = {'login': login,
                    'password': password}
        self._session.get('https://www.elibrary.ru/defaultx.asp', params=auth)

    def search_option(self, text, search_option_data=None, begin_year=0, end_year=0, issues="all", orderby="date",
                      order="rev"):
        # ввод параметров поиска
        if search_option_data is None:
            search_option_data = self.search_option_data_blank
        data = {'ftext': "",  # Текст для поиска
                'where_name': "on",  # Поиск в названии
                'where_abstract': "on",  # Поиск в аннотации
                'where_keywords': "on",  # Поиск в ключевых словах
                'where_affiliation': "on",  # Поиск в названии организации
                'where_references': "on",  # Поиск в литературе
                'where_fulltext': "on",  # Поиск в полном тексте
                'type_article': "on",  # Тип - статья
                'type_book': "on",  # Книга
                'type_conf': "on",  # Конфиренция
                'type_preprint': "on",  # Рукописи
                'type_disser': "on",  # Диссертация
                'type_report': "on",  # Отчёт
                'type_patent': "on",  # Патент
                'begin_year': "0",  # Год публикаций - от
                'end_year': "0",  # до
                'issues': "all",  # время поступления - всё время 'all', посл месяц 'm1', посл 3 месяца 'm3',
                # полгода 'm6', год 'm6'
                'orderby': "date",  # Упорядочивание статей - релевантность 'rank',  дата выпуска 'date',
                # дата поступления 'insdate', по названию статьи 'name', по названию журнала 'title',
                # по числу цитирования 'cited'
                'order': "rev",  # порядок - по убыванию 'rev', по возрастанию 'nrm'
                'authors_all': "",  # Список авторов
                'titles_all': "",  # Список журналы
                'rubrics_all': "",  # Список тематик
                'changed': "0",  # неизменяймые параметры
                'queryid': "112033467",
                'search_itemboxid': "",
                'queryboxid': "0",
                'save_queryboxid': "0"}

        for key in search_option_data:
            if not search_option_data[key]:
                data.pop(key)

        data['ftext'] = text.replace(' ', '+')

        data['begin_year'] = str(begin_year)

        data['end_year'] = str(end_year)

        data['issues'] = issues

        data['orderby'] = orderby

        data['order'] = order

        self.search_option_data = data

    @internet_connection
    def getting_these_articles(self, page_start=1, page_end=1000, clean_articles=False):
        # Получение
        if self.search_option_data is None:
            self.state_code = -6
            return False

        if clean_articles:
            self.articles = list_article()

        site = self._session.post("https://elibrary.ru/query_results.asp", params=self.search_option_data)

        self._check_block_site(site.text)

        if self.state_code:
            return False

        self._end_num = find_end_num(site.text)

        if not self._end_num:
            self.state_code = -2
            return False

        if page_end > 1000:
            page_end = 1000

        if self._end_num > page_end:
            self._end_num = page_end

        if page_start == 1:
            print('Номер страницы', 1)
            self.page_parser(site.text)
            if self.state_code:
                return False
            page_start += 1

        for i in range(page_start, self._end_num + 1):
            print('Номер страницы', i)
            site = self._session.post("https://elibrary.ru/query_results.asp", params={'pagenum': str(i)})
            self._check_block_site(site.text)
            self._session_status_code_check(site.status_code)
            if self.state_code:
                break
            sleep(random() * 3)
            self.page_parser(site.text)
            if self.state_code:
                return False
            self.num_page = i

    @internet_connection
    def page_parser(self, page_text):

        articles_address = find_id(page_text)

        all_address = self.articles.all_address()

        for address in articles_address:
            print(len(self.articles))
            if address in all_address:
                continue
            site = self._session.post('https://elibrary.ru/item.asp', params={'id': address})
            self._check_block_site(site.text)
            self._session_status_code_check(site.status_code)
            if self.state_code:
                break
            self.articles.append(article(site.text, address))
            sleep(random() * 3)
            if self.articles[-1].name == 'Тест Тьюринга':
                self.articles.pop()
                self.state_code = -3
                break

    def _session_status_code_check(self, code):
        if 400 <= code < 500:
            self.state_code = -4
        elif code >= 500:
            self.state_code = -5

    def _check_block_site(self, text_site):
        if self.block_site in text_site:
            self.state_code = -7
