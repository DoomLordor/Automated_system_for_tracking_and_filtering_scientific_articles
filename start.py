from model.parser import site_connection
from pickle import load, dump
morph_dict_path = r'setting\morph.rol'
print('initialization_start')
parser = site_connection()
parser.search_option('Интеллектуальный анализ данных')
print('initialization_end')
print('parser_start')
parser.getting_these_articles()
print('parser_end')
articles = parser.articles
with open('Doc_and_test\\test.txt', 'w') as f:
    for i, article in enumerate(articles):
        f.write('{}\t{}\n'.format(i + 1, article.name))
with open('Doc_and_test\\articles.rol', 'wb') as f:
    dump(articles, f)

# with open('index.html', 'w', encoding='utf-8') as f:
#     f.write(site.text)




