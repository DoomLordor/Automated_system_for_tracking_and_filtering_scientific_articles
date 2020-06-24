import re
import pymorphy2
from random import choice, seed, random
import numpy as np
from math import sqrt, log


def set_keywords(self, keywords):
    for i, keyword in enumerate(keywords):
        self[i][4] = keyword
    return self


def reception_keywords(self):
    return list(map(lambda x: x[4], self))


def reception_teachers_data(self):
    return list(map(lambda x: '{} {} {}'.format(x[0], x[1], x[2]), self))


def partition(input_text):
    keywords = {}
    morph = pymorphy2.MorphAnalyzer()
    for word in input_text:
        for words in (word.split('\t')[0]).split(' '):
            lemma = morph.parse(words)[0].normal_form.upper()
            if keywords.get(lemma) is None:
                keywords[lemma] = int(word.split('\t')[1])
            else:
                keywords[lemma] += int(word.split('\t')[1])
    if keywords.get('') is not None:
        del keywords['']
    return keywords


def partition2(input_text, not_common=False):
    morph = pymorphy2.MorphAnalyzer()
    morph_dict = {}
    keywords = []
    for string in input_text:
        keyword = {}
        for words in string.split():
            if morph_dict.get(words) is None:
                lemma = morph.parse(words)[0].normal_form.upper()
                morph_dict[words] = lemma
            else:
                lemma = morph_dict[words]
            if keyword.get(lemma) is None:
                keyword[lemma] = 1
            else:
                keyword[lemma] += 1
        if keyword.get('') is not None:
            del keyword['']
        keywords.append(keyword.copy())
    if not_common:
        return keywords
    else:
        return sum_dict(keywords)


# разделение списка на ключевые слова

def removing_special_characters(input_text):
    if type(input_text) is str:
        input_text = [input_text]
    for i, word in enumerate(input_text):
        sp = set(re.findall(r'\W', word))
        if ' ' in sp:
            sp.remove(' ')
        for char in sp:
            word = word.replace(char, ' ')
            input_text[i] = word
    return input_text


# даление спец символов


def delete_english_word(keywords):
    copy_dictionary = keywords.copy()
    pattern = r"[A-Za-z]"
    for word in copy_dictionary.keys():
        if re.search(pattern, word):
            del keywords[word]
    return keywords


# удаление английских слов из словаря


def delete_numbers(keywords):
    res_keywords = keywords.copy()
    for word in keywords:
        if word.isdigit():
            del res_keywords[word]
    return res_keywords


# удаление чисел из словаря


def delete_stop_word(keywords, dictionary_of_stop_words):
    res_keywords = {}
    for word in keywords.keys():
        if not (word in dictionary_of_stop_words):
            res_keywords[word] = keywords[word]
    return res_keywords


# удаление стоп слов из словаря


def delete_one_frequency_keyword(keywords):
    res_keyword = {}
    for keyword in keywords:
        if 1 < keywords[keyword]:
            res_keyword[keyword] = keywords[keyword]
    return res_keyword


def delete_frequency_keyword(keywords, threshold_percentage=5, in_percents=True):
    res_keyword = {}
    if in_percents:
        threshold = max(keywords.values()) * threshold_percentage / 100
    else:
        threshold = threshold_percentage
    for keyword in keywords:
        if threshold < keywords[keyword]:
            res_keyword[keyword] = keywords[keyword]
    return res_keyword


# удаление одначастотных слов


def keyword_teachers(input_text):
    pos = 0
    keyword = []
    for i in range(1, len(input_text) - 1):
        if input_text[i][-1] > input_text[i - 1][-1]:
            keyword.append(partition(input_text[pos:i]))
            pos = i
    keyword.append(partition(input_text[pos:-1]))
    return keyword


# получение ключевых слов из общего списка


def sum_dict(*keywords):
    keywords = list(keywords)
    if len(keywords) == 1:
        keywords = keywords[0]
    res_dict = keywords[0].copy()
    for keyword in keywords[1:]:
        for word in keyword:
            if res_dict.get(word) is not None:
                res_dict[word] += keyword[word]
            else:
                res_dict[word] = keyword[word]
    return res_dict


# сумма нескольких словарей


def profile(keywords, list_keywords):
    for pos, teacher in enumerate(list_keywords):
        mat_profile = {}
        for keyword in keywords:
            mat_profile[keyword] = teacher.get(keyword, 0)
        list_keywords[pos] = mat_profile
    return list_keywords


# сопоставление общих сключевых слов с кл словами преподавателя


def vec_cos(vector1, vector2):
    vector1 = list(vector1)
    vector2 = list(vector2)
    if vector2 == vector1:
        return 1
    else:
        sum1 = sum(np.array(vector1) * np.array(vector2))
        sum2 = sqrt(sum(np.array(vector1) ** 2))
        sum3 = sqrt(sum(np.array(vector2) ** 2))
    return sum1 / (sum2 * sum3)


# косинус вектора


def sum_values(*dictionaries):
    dictionaries = list(dictionaries)
    if len(dictionaries) == 1 and type(dictionaries[0]) is not dict:
        dictionaries = dictionaries[0]
    res = dictionaries[0].copy()
    for dictionary in dictionaries[1:]:
        for key in dictionary:
            res[key] += dictionary[key]
    return res


# сумма значений одинаковых словарей


def total_square_deviation(keywords, *means):
    means = list(means)
    if len(means) == 1:
        means = means[0]
    qd = []  # квадратичное отклонение
    for keyword in keywords:
        num = belonging_of_cluster(keyword, means)
        qd.append(squared_error(list(keyword.values()), list(means[num].values())))
    return sum(np.array(qd))


# суммарный квадрат ошибки


def length_vector(vector1, vector2=None):
    if vector2 is None:
        return sqrt(sum(np.array(list(vector1)) ** 2))
    return sqrt(sum((np.array(list(vector1)) - np.array(list(vector2))) ** 2))


# длинна вектора


def squared_error(vector1, vector2=None):
    if vector2 is None:
        return sum(np.array(list(vector1)) ** 2)
    return sum((np.array(list(vector1)) - np.array(list(vector2))) ** 2)


# квадрат ошибки


def belonging_of_cluster(keyword, *means):
    means = list(means)
    if len(means) == 1:
        means = means[0]
    val = [length_vector(keyword.values(), mn.values()) for mn in means]
    return val.index(min(val))


# принадлежность векторов к клатерам

def arithmetic_mean_dictionary(*keywords):
    keywords = list(keywords)
    if len(keywords) == 1:
        keywords = keywords[0]
    return {k: v / len(keywords) for k, v in sum_values(keywords).items()}


# среднее арифмитическое словарей (ценнтр масс)


def cluster_distribution(keywords, means):
    keywords_in_cluster = []
    for i in range(len(means)):
        keywords_in_cluster.append([k for k in keywords if belonging_of_cluster(k, means) == i])
    return keywords_in_cluster


def k_means(keywords, *means, error_start=False, error_end=False):
    means = list(means)
    if len(means) == 1:
        means = means[0]
    keywords_in_cluster = cluster_distribution(keywords, means)
    val_1 = total_square_deviation(keywords, means)
    errors = [float(val_1)]

    for i in range(len(means)):
        means[i] = arithmetic_mean_dictionary(keywords_in_cluster[i])
    val_2 = total_square_deviation(keywords, means)

    while val_1 != val_2:
        for i in range(len(means)):
            means[i] = arithmetic_mean_dictionary(keywords_in_cluster[i])
        val_1 = val_2
        val_2 = total_square_deviation(keywords, means)
        keywords_in_cluster = cluster_distribution(keywords, means)
    if error_start:
        return errors, means
    elif error_start and error_end:
        errors.append(float(val_2))
        return errors, means
    elif error_end:
        return float(val_2), means
    else:
        return means


# метод к-средних


def tfidf(list_keywords):
    idf = {}
    idf = idf.fromkeys(list_keywords[0].keys(), 0)
    for word in idf:
        for teacher in list_keywords:
            if teacher[word] > 0:
                idf[word] += 1
        idf[word] = log(len(list_keywords) / idf[word])

    for teacher in list_keywords:
        sum_val = sum(teacher.values())
        for word in teacher:
            teacher[word] *= idf[word] / sum_val
    return list_keywords


def tf(list_keywords):
    for teacher in list_keywords:
        sum_val = sum(teacher.values())
        for word in teacher:
            teacher[word] /= sum_val
    return list_keywords


def sort_val(sort_dict):
    return dict(sorted(sort_dict.items(), key=lambda x: (-x[1], x[0])))


def list_items(input_list, val):
    if val in input_list:
        pos_now = 0
        pos = []
        while True:
            pos.append(pos_now + input_list[pos_now:].index(val))
            pos_now = pos[-1] + 1
            if val not in input_list[pos_now:]:
                break
        return pos
    else:
        return []


def k_means_plus_plus(number_of_clusters, keywords, seed_now=0):
    if seed_now is not None:
        seed(seed_now)
    means = [choice(keywords)]
    for i in range(number_of_clusters - 1):
        length_all = []
        for keyword in keywords:
            length = squared_error(keyword.values(), means[0].values())
            for m in means[1:]:
                length_now = squared_error(keyword.values(), m.values())
                if length_now < length:
                    length = length_now
            length_all.append(length)
        probability = random() * sum(length_all)
        i = 0
        sum_length = length_all[0]
        while sum_length < probability:
            i += 1
            sum_length += length_all[i]
        means.append(keywords[i])
    return means


# Поиск начальных центройдов методом k-means++


def kwords_annotation(input_text, kwords=False, annotation=False):
    if not (kwords and annotation):
        for i, doc in enumerate(input_text):
            text = doc.split('\n')
            if not kwords and not annotation:
                input_text[i] = text[0]
            elif not kwords and annotation:
                input_text[i] = text[0] + '\n' + text[5] + '\n'
            elif kwords and not annotation:
                input_text[i] = text[0] + '\n' + text[2] + '\n'
    return input_text


# Удаление ключевых слов, аннотаций из текста


def delete_elements_certain_length(keywords, name_document, n):
    del_list = []

    for keyword in keywords:
        if len(delete_frequency_keyword(keyword, 0)) < n:
            del_list.append(keyword)

    for val in del_list:
        pos = keywords.index(val)
        del keywords[pos], name_document[pos]

    return keywords, name_document

# Удаление из списка элемеентов меньше n
