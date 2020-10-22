import re
import pandas as pd


class Corpus():
    def __init__(self, data):
        self.data = data
    
    
    def simple_search(self, pattern, ntop=10, complex_s=False):
        """
        search by exact wordforms / patterns
        """
 
        pattern = pattern.strip('"')
        
        answers = []
        indeces = []
 
        for sent_ind, sent in data.iterrows():
            if pattern in sent['sentence'].split():
                word_ind = sent['sentence'].split().index(pattern)
                changed_sent = re.sub(r'(\b|^)' + pattern + r'(\b|$)',
                                       '\033[0;34;47m' + pattern + '\033[0m',
                                       sent['sentence'])
                indeces.append((sent_ind, word_ind, sent['sentence'], False))
                answers.append((pattern,
                                sent['source'],
                                sent['title'],
                                changed_sent))
        if complex_s == True:
            return indeces
        else:
            return answers
        
    
    def morph_search(self, pattern, ntop=10, complex_s=False):
        """
        input: pattern ('word+POS')
        
        output: должна вернуть спискок кортежей (pattern, source, title, sentence)
        найденный паттерн выделяется цветом
        в конце печать ответов через self.print_answer(pattern, answers, ntop)
        """
        answers = []
        indeces = []
 
        lemma, pos_tag = pattern.split('+')
        for sent_ind, sent in self.data.iterrows():
            if lemma in sent['lemmatized']: # есть ли в предложении
                lemmas = sent['lemmatized'].split() 
                pos = sent['pos'].split()
                for word_ind, one in enumerate(lemmas): # идем по номерам лемм
                    if lemma in one.split('|') and pos_tag in pos[word_ind].split('|'):
                        token = sent['tokenized'].split()[word_ind]
                        changed_sent = re.sub(r'(\b|^)' + token + r'(\b|$)', 
                                       '\033[0;34;47m' + token + '\033[0m', 
                                       sent['sentence'])
                        indeces.append((sent_ind, word_ind, sent['sentence'], False))
                        answers.append((pattern, 
                                        sent['source'], 
                                        sent['title'], 
                                        changed_sent))
        if complex_s == True:
            return indeces
        else:
            return answers    
    
    
    def form_search(self, pattern, ntop=10, complex_s=False):
        """
        input: pattern ('word')
        
        output: должна вернуть спискок кортежей (pattern, source, title, sentence)
        найденный паттерн выделяется цветом
        в конце печать ответов через self.print_answer(pattern, answers, ntop)
        """
        answers = []
        indeces = []
 
        for sent_ind, sent in self.data.iterrows():
            if pattern in sent['lemmatized']:
                for word_ind in range(len(sent['lemmatized'].split())):
                    if pattern in sent['lemmatized'].split()[word_ind].split('|'):
                        changed_sent = re.sub(r'(\b|^)' + sent['tokenized'].split()[word_ind] + r'(\b|$)', 
                                       '\033[0;34;47m' + sent['tokenized'].split()[word_ind] + '\033[0m', 
                                       sent['sentence'])
                        indeces.append((sent_ind, word_ind, sent['sentence'], False))
                        answers.append((pattern, 
                                sent['source'], 
                                sent['title'], 
                                changed_sent))
                    
        if complex_s == True:
            return indeces
        else:
            return answers
    
    
    def pos_search(self, pattern, ntop=10, complex_s=False):
        """
        input: pattern ('POS')
        
        output: должна вернуть спискок кортежей (pattern, source, title, sentence)
        найденный паттерн выделяется цветом
        в конце печать ответов через self.print_answer(pattern, answers, ntop)
        """
        
        answers = []
        indeces = []
 
        for sent_ind, sent in self.data.iterrows():
            if pattern in sent['pos']:
                for word_ind in range(len(sent['pos'].split())):
                    if pattern in sent['pos'].split()[word_ind].split('|'):
                        changed_sent = re.sub(r'(\b|^)' + sent['tokenized'].split()[word_ind] + r'(\b|$)', 
                                       '\033[0;34;47m' + sent['tokenized'].split()[word_ind] + '\033[0m', 
                                       sent['sentence'])
                        indeces.append((sent_ind, word_ind, sent['sentence'], False))
                        answers.append((pattern, 
                                sent['source'], 
                                sent['title'], 
                                changed_sent))
        if complex_s == True:
            return indeces
        else:
            return answers

    def analyze(self, pattern, column, indeces):
        """
        pattern(str) - паттерн поиска (например, NOUN  или "поиска")
        column(str) - название нужного столбца в датафрейме
        indeces(list) - список кортежей (индекс предложения, индекс слова)

        Функция проверяет, соответствует ли слово, 
        следующее за уже найденным паттерну запроса
        """
        
        new_indeces = []
        answers = []
        
        for sent_id, first_word_id, sentence, changed in indeces: # индекс предложения, индекс слова в предложении
            
            answer = self.data[column][sent_id].split() # строка, по которой ведется поиск
            word_id = first_word_id + 1
            if word_id < len(answer) and answer[word_id] == '—':
                word_id += 1  # индекс слова, которое мы ищем
            if word_id < len(answer) and answer[word_id] == pattern: # соответсвует ли слово паттерну

                if not changed:
                    sentence = sentence.split()
                    sentence[first_word_id] = '\033[0;34;47m' + sentence[first_word_id] + '\033[0m'  # делаем выделение первого слова паттерна
                    sentence = ' '.join(sentence)

                changed_sent = sentence.split()
                changed_sent[word_id] = '\033[0;34;47m' + changed_sent[word_id] + '\033[0m'  # делаем выделение последующего слова
                changed_sent = ' '.join(changed_sent)
              
                new_indeces.append((sent_id, word_id, changed_sent, True)) # добавляет индекс предложения и индекс слова, которое нашли
                answers.append((pattern, # паттерн
                                data['source'][sent_id], # источник
                                data['title'][sent_id], # название статьи
                                changed_sent)) # форматирование выдачи (когда в индексах будут предложения, ЗАМЕНИТ)Ь
        return new_indeces, answers
 
 
 
    def check_next_word(self, pattern, indeces, is_last=False):
        """
        pattern(str) - паттерн поиска (например, NOUN  или "поиска")
        index(list) - список кортежей (индекс предложения, индекс слова)
        is_last(bool) - True, если последнее слово в запросе, 
                      False - в остальных случаях
        """
        answers = [] 
        new_indeces = []
        
        continue_simple_search = False # проверяет, продолжается ли поиск по токенам
     
        if '+' in pattern: # поиск знать+NOUN, поиск одновременно по леммам и частям речи, поэтому не вызывает analyze()
            for sent_id, old_id, sentence, changed in indeces:
                word, pos_tag = pattern.split('+')
                answer = self.data['lemmatized'][sent_id].split()
                pos = self.data['pos'][sent_id].split()
                word_id = old_id + 1
                if word_id < len(answer) and answer[word_id] == 'UNK':
                    word_id += 1
                if word_id < len(answer) and word in answer[word_id].split('|') and pos_tag in pos[word_id].split('|'):
                  
                    if not changed:
                        sentence = sentence.split()
                        sentence[old_id] = '\033[0;34;47m' + sentence[old_id] + '\033[0m'  # делаем выделение первого слова паттерна
                        sentence = ' '.join(sentence)
                  
                    changed_sent = sentence.split()
                    changed_sent[word_id] = '\033[0;34;47m' + changed_sent[word_id] + '\033[0m'  # делаем выделение последующего слова
                    changed_sent = ' '.join(changed_sent)

                    new_indeces.append((sent_id, word_id, changed_sent, True))
                    answers.append((pattern,
                                     data['source'][sent_id], 
                                     data['title'][sent_id],
                                     changed_sent))
                                 
        elif '"' in pattern: # поиск по токену
            if not pattern.endswith('"'):
                continue_simple_search = True # продолжает поиск, если слово не заканчивается кавычкой
            pattern = pattern.strip('"')
            new_indeces, answers = self.analyze(pattern, 'tokenized', indeces)
                    
        elif pattern.isupper(): # поиск по части речи
            new_indeces, answers = self.analyze(pattern, 'pos', indeces)

        else: # поиск по лемме
            new_indeces, answers = self.analyze(pattern, 'lemmatized', indeces)
 
        if is_last == False: # если не последнее слово, то возвращает индексы предложений и слов
            return new_indeces, continue_simple_search
        else: # если последнее, то возвращает ответы в заданном формате
            return answers
    
    
    def search(self, pattern, ntop=10):
        """
        input: pattern ('POS word POS') и любые вариации 
        + мб можно добавить и возможность смешанного поиска: чтобы можно было найти
        что-то типа 'POS word+POS word', но немного сложновато кажется
        
        output: должна вернуть спискок кортежей (pattern, source, title, sentence)
        найденный паттерн выделяется цветом
        в конце печать ответов через self.print_answer(pattern, answers, ntop)
        """
 
        print(f'Поиск по запросу: {pattern}\n')
 
        pattern = pattern.split()
        if len(pattern) == 1:
            complex_s = False
        else:
            complex_s = True
        
        # поиск предложения с первым словом в запросе
        if '"' in pattern[0]:
            answers = self.simple_search(pattern[0], ntop, complex_s)
            if not pattern[0].endswith('"'):
                pattern[1] = '"' + pattern[1]
        elif '+' in pattern[0]:
            answers = self.morph_search(pattern[0], ntop, complex_s)           
        elif pattern[0].isupper():
            answers = self.pos_search(pattern[0], ntop, complex_s)
        else:
            answers = self.form_search(pattern[0], ntop, complex_s)
            
  
        for i in range(1, len(pattern)):
            if i != len(pattern) - 1:
                answers, continue_simple_search = self.check_next_word(pattern[i], answers, is_last=False)
                if continue_simple_search == True:
                    pattern[i+1] = '"' + pattern[i+1]
            else:
                answers = self.check_next_word(pattern[i], answers, is_last=True)
        
        self.print_answer(pattern, answers, ntop)
      
    def write_file(self, pattern, answers):
        """
        writes file with search results
        """
        
        i = 1
        PATH = 'search_results_{}.csv'.format(i)
        while os.path.exists(PATH):
            i += 1
            PATH = 'search_results_{}.csv'.format(i)
        else:
            df = pd.DataFrame(answers, columns=['pattern', 'source', 'title', 'sentence'])
            df.to_csv(PATH, sep='\t')
            
    
    def print_answer(self, pattern, answers, ntop):
        """
        print the answer
        if the output is too big, asks the user to write a file
        with seacrh results
        """
        
        if ntop > len(answers):
            ntop = len(answers)
            
        print(f'\nРЕЗУЛЬТАТЫ ({ntop}/{len(answers)}):\n')
        
        for sent in answers[:ntop]:
            print(f'Источник: {sent[2]} ({sent[1]})')  # sent[2] это название статьи,  sent[1] - ссылка на нее
            print(sent[3]+'\n')  # sent[3] - это само предложение
        
        if len(answers) > 10:
            more = input('Показать больше примеров? (y/n) ')
        
            if more == 'y':
                n = answers[ntop:]
                if len(n) >= 10:
                    more = input('Примеров слишком много для вывода. Записать примеры в файл? (y/n) ')
                    if more == 'y':
                        self.write_file(pattern, answers)
                        print('Файл удачно записан.')
                else:
                    for sent in answers[ntop:]:
                        print(f'\nИсточник: {sent[2]} ({sent[1]})')
                        print(sent[3]+'\n')
