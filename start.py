from model.parser import site_connection
from model.text_processing import list_article
from pickle import load, dump
# from wordcloud import WordCloud

if __name__ == "__main__":
    morph_dict_path = r'setting\morph.rol'
    print('initialization_start')
    parser = site_connection()
    parser.search_option('Интеллектуальный анализ данных')
    print('initialization_end')
    # with open('Doc_and_test\\articles.rol', 'wb') as f:
    #     parser.articles = load(f)
    print('parser_start')
    parser.getting_these_articles(page_start=1, page_end=1)
    print('parser_end')
    articles = parser.articles
    print(parser.state_code)
    print(parser.num_page)

    with open('Doc_and_test\\articles.rol', 'wb') as f:
        dump(articles, f)






