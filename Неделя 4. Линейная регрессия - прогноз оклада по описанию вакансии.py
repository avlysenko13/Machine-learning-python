# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 11:06:10 2017
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import DictVectorizer
from scipy.sparse import hstack
from sklearn.linear_model import Ridge

#==============================================================================
# Загрузите данные об описаниях вакансий и соответствующих годовых зарплатах из файла salary-train.csv
# (либо его заархивированную версию salary-train.zip).
#==============================================================================
data_train=pd.read_csv('salary-train.csv')
data_test=pd.read_csv('salary-test-mini.csv')


#==============================================================================
# Проведите предобработку:
# Приведите тексты к нижнему регистру (text.lower()).
# Замените все, кроме букв и цифр, на пробелы — это облегчит дальнейшее разделение текста на слова.
# Для такой замены в строке text подходит следующий вызов: re.sub('[^a-zA-Z0-9]', ' ', text).
# Также можно воспользоваться методом replace у DataFrame, чтобы сразу преобразовать все тексты:
#==============================================================================
data_train['FullDescription'].replace('[^a-zA-Z0-9]', ' ', regex = True,inplace=True)
data_test['FullDescription'].replace('[^a-zA-Z0-9]', ' ', regex = True,inplace=True)

#==============================================================================
# Примените TfidfVectorizer для преобразования текстов в векторы признаков.
# Оставьте только те слова, которые встречаются хотя бы в 5 объектах (параметр min_df у TfidfVectorizer).
#==============================================================================
vectorizer = TfidfVectorizer(min_df=5)
fullDescription_train=vectorizer.fit_transform(data_train['FullDescription'])#сбор статистики и трансформация характетистик в числа
fullDescription_test=vectorizer.transform(data_test['FullDescription'])#трансформация на основе ранее собранной статистики

#==============================================================================
# Замените пропуски в столбцах LocationNormalized и ContractTime на специальную строку 'nan'.
#==============================================================================
data_train['LocationNormalized'].fillna('nan', inplace=True)
data_train['ContractTime'].fillna('nan', inplace=True)

#==============================================================================
# Примените DictVectorizer для получения one-hot-кодирования признаков LocationNormalized и ContractTime.
#==============================================================================
#сливаем две колонки из датасета панды в словарь
enc = DictVectorizer()
X_train_categ = enc.fit_transform(data_train[['LocationNormalized', 'ContractTime']].to_dict('records'))#.toarray()
X_test_categ = enc.transform(data_test[['LocationNormalized', 'ContractTime']].to_dict('records'))#.toarray()
#==============================================================================
# Объедините все полученные признаки в одну матрицу "объекты-признаки".
# Обратите внимание, что матрицы для текстов и категориальных признаков являются разреженными.
# Для объединения их столбцов нужно воспользоваться функцией scipy.sparse.hstack.
#==============================================================================
joinedMatrix_train=hstack([fullDescription_train,X_train_categ])#соединяем признаки

#==============================================================================
# Обучите гребневую регрессию с параметрами alpha=1 и random_state=241. Целевая переменная записана в столбце SalaryNormalized.
#==============================================================================
clf = Ridge(alpha=1.0,random_state=241)
clf.fit(joinedMatrix_train, data_train['SalaryNormalized'])

#==============================================================================
# Постройте прогнозы для двух примеров из файла salary-test-mini.csv.
# Значения полученных прогнозов являются ответом на задание. Укажите их через пробел.
#==============================================================================
joinedMatrix_test=hstack([fullDescription_test,X_test_categ])#соединяем признаки
predict=clf.predict(joinedMatrix_test)

print('Прогноз по зарплате')
print (' '.join(map(lambda x: str(round(x,2)), predict)))
