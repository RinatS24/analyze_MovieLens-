import re
from collections import OrderedDict, defaultdict, Counter
import requests
from bs4 import BeautifulSoup
import datetime
import csv
import statistics
import pytest
######################### Tags - helenwav #########################

class Tags:
    """
    Анализ данных из tags.csv
    """

    def __init__(self, path_to_the_file):
        """
        Укажите здесь любые поля, которые, по вашему мнению, могут понадобиться.
        """
        self.file_path = path_to_the_file
        self.user_ids, self.move_ids, self.tags, self.timestamps = self.file_pars()

    def file_pars(self):
        """
        Парсинг файла на 4 списка: userID, movieID, tags, timestamps
        """
        user_ids = []
        move_ids = []
        tags = []
        timestamps = []

        with open(self.file_path, "r") as data_file:

            pattern = r"(\d+),(\d+),([^,]+),(\d+)"

            for line in data_file:
                line = line.strip()
                match = re.match(pattern, line)

                if match:
                    user_ids.append(match.group(1))
                    move_ids.append(match.group(2))
                    tags.append(match.group(3))
                    timestamps.append(match.group(4))

        return user_ids, move_ids, tags, timestamps

    def most_words(self, n):
        """
        Метод возвращает топ-n тегов с наибольшим количеством слов внутри.
        Это словарь, где ключами являются теги, а значениями — количество слов в теге.
        Удалите дубликаты. Отсортируйте по количеству в порядке убывания.
        """
        unique_tags = set(self.tags)
        big_tags = {tag: len(tag.split()) for tag in unique_tags}
        sorted_big_tags = dict(
            sorted(big_tags.items(), key=lambda item: item[1], reverse=True)
        )
        big_tags = dict(list(sorted_big_tags.items())[:n])

        return big_tags

    def longest(self, n):
        """
        Метод возвращает топ-n самых длинных тегов по количеству символов.
        Это список тегов. Удалите дубликаты. Отсортируйте по количеству в порядке убывания.
        """
        unique_tags = set(self.tags)
        sorted_tags = sorted(unique_tags, key=len, reverse=True)
        big_tags = sorted_tags[:n]

        return big_tags

    def most_words_and_longest(self, n):
        """
        Метод возвращает пересечение между топ-n тегами с наибольшим количеством слов
        и топ-n самыми длинными тегами по количеству символов.
        Удалите дубликаты. Это список тегов.
        """
        set_longest_tags = set(self.longest(n))
        words_tags = self.most_words(n)
        set_words_tags = set(words_tags.keys())

        big_tags = set_longest_tags.intersection(set_words_tags)

        return big_tags

    def most_popular(self, n):
        """
        Метод возвращает самые популярные теги.
        Это словарь, где ключами являются теги, а значениями — количество.
        Удалите дубликаты. Отсортируйте по количеству в порядке убывания.
        """
        popular_tags = Counter(self.tags)
        popular_tags = dict(popular_tags.most_common(n))

        return popular_tags

    def tags_with(self, word):
        """
        Метод возвращает все уникальные теги, которые содержат слово, переданное в качестве аргумента.
        Удалите дубликаты. Это список тегов. Отсортируйте по названиям тегов в алфавитном порядке.
        """
        tags_with_word = list(set(tag for tag in self.tags if word in tag))
        tags_with_word.sort()

        if not tags_with_word:
            tags_with_word.append(f"tags_with: No tags with {word}")

        return tags_with_word

    def merge_links(self):

        pattern = r"(\d+),(\d+),(\d+)"
        links_dict = OrderedDict()

        with open('links.csv', 'r') as links_file:
            for line in links_file:
                line = line.strip()
                match = re.match(pattern, line)
                
                if match:
                    movie_id = match.group(1)
                    imdb_id = match.group(2)
                    links_dict[movie_id] = imdb_id 
                    
        imdb_ids = [links_dict[movie_id] for movie_id in self.move_ids if movie_id in links_dict]
                    
        return imdb_ids
            

    def movies_with_tag(self, word):
        """
        Метод возвращает список названий фильмов, в тэге которого содержится слово,
        переданное в качестве аргумента. Сортировка списка по алфавиту.
        """
        movies_titles = set()
        imdb_ids = self.merge_links() 
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110"
        }
        
        for index, tag in enumerate(self.tags):
            if word.lower() in tag.lower():
                imdb_id = imdb_ids[index]
                url = f"https://www.imdb.com/title/tt{imdb_id}/"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200: 
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_element = soup.find('div', class_='sc-ec65ba05-1 fUCCIx') 
                    
                    if title_element:
                        movie_title = title_element.get_text(strip=True)
                        movie_title = movie_title.replace("Original title: ", "").strip()
                        movies_titles.add(movie_title)
                    
        movies_titles = sorted(movies_titles)

        if not movies_titles:
            movies_titles.append(f"movies_with_tag: Movie ID not found for {word}.")
        
            
        return movies_titles

    def tags_of_movie(self, num_id):
        """
        Метод возвращает тэги фильма по id, переданного в качестве аргумента.
        Это список тэгов, отсортированный в алфавитном порядке, без дубликатов.
        """
        tags_movie = list(
            set(
                self.tags[index]
                for index, movie_id in enumerate(self.move_ids)
                if int(movie_id) == num_id
            )
        )
        tags_movie.sort()

        if not tags_movie:
            tags_movie.append(f"tags_of_movie: tags for {num_id} not found.")

        return tags_movie

######################### Movies - helenwav #########################

class Movies:
    """
    Анализ данных из movies.csv
    """

    def __init__(self, path_to_the_file):
        """
        Укажите здесь любые поля, которые, по вашему мнению, могут понадобиться.
        """
        self.file_path = path_to_the_file
        self.movies_id, self.movies_titles, self.movies_genres = self.file_pars()

    def file_pars(self):
        """
        Парсинг файла на 3 списка: movieID, titles, genres
        """
        movie_ids = []
        titles = []
        genres = []
        with open(self.file_path, "r") as data_file:

            pattern = r'(\d+),\s*"(.*?)",\s*(.+)|(\d+),\s*([^,]+),\s*(.+)'  # группы это скобки

            for line in data_file:
                line = line.strip()
                match = re.match(pattern, line)

                if match:
                    if match.group(1):
                        movie_ids.append(match.group(1))
                        titles.append(match.group(2))
                        genres.append(match.group(3))
                    else:
                        movie_ids.append(match.group(4))
                        titles.append(match.group(5))
                        genres.append(match.group(6))

        return movie_ids, titles, genres

    def dist_by_release(self):
        """
        Метод возвращает словарь или OrderedDict, где ключами являются годы(years),
        а значениями — количество фильмов(counts).
        Необходимо извлечь годы из названий(years from the titles).
        Отсортируйте по количеству в порядке убывания.
        """
        release_years = defaultdict(int)

        for title in self.movies_titles:
            match = re.search(r"\((\d{4})\)", title)
            if match:
                year = int(match.group(1))
                release_years[year] += 1

        release_years = OrderedDict(
            sorted(release_years.items(), key=lambda item: item[1], reverse=True)
        )

        return release_years

    def dist_by_genres(self):
        """
        Метод возвращает словарь, где ключами являются жанры(genres),
        а значениями — количество фильмов(counts).
        Отсортируйте по количеству в порядке убывания.
        """
        genres = defaultdict(int)

        for genres_movie in self.movies_genres:
            split_genres_movie = genres_movie.split("|")
            for genre in split_genres_movie:
                genres[genre] += 1

        genres = dict(sorted(genres.items(), key=lambda item: item[1], reverse=True))

        return genres

    def most_genres(self, n):
        """
        Метод возвращает словарь с топ-n фильмов, где ключами являются названия фильмов(movie titles), а
        значениями — количество жанров фильма. Отсортируйте по количеству в порядке убывания.
        """
        movies = dict()

        for index, title_movie in enumerate(self.movies_titles):

            title_movie = re.sub(r"\s*\((\d{4})\)\s*", "", title_movie)
            genres_movie = self.movies_genres[index]
            split_genres_movie = genres_movie.split("|")

            if split_genres_movie[0] != "(no genres listed)":
                movies[title_movie] = len(split_genres_movie)
            else:
                movies[title_movie] = 0

        movies = dict(sorted(movies.items(), key=lambda item: item[1], reverse=True))
        movies = dict(list(movies.items())[:n])

        return movies

    def movies_of_genre(self, words):
        """
        Метод возвращает список названий фильмов с жанрами,
        переданным в качестве аргумента в виде списка. Список отсортирован по алфавиту.
        """
        if not isinstance(words, list):
            words = [words]

        movies = [
            re.sub(r"\s*\((\d{4})\)\s*", "", self.movies_titles[index])
            for index, genre in enumerate(self.movies_genres)
            if all(word.strip() in genre.split("|") for word in words)
        ]
        
        movies.sort()
        
        if not movies:
            movies.append(f"movies_of_genre: Movies for {', '.join(words)} not found")
            
        return movies
    
    def genres_of_movie(self, word):
        """
        Метод возвращает список жанров фильма переданного в качестве аргумента.
        Список остортирован по алфавиту.
        """
        year_pattern = r"\s*\((\d{4})\)\s*"
        
        genres = next(
        (self.movies_genres[index].split("|") for index, title in enumerate(self.movies_titles)
         if re.sub(year_pattern, "", title).strip() == word),
        []
        )
        
        genres.sort()
        
        if not genres:
            genres.append(f"Movie '{word}' not found")
                              
        return genres
    
######################### Links - aleenjer #########################

class Links:
    """
    Analyzing data from links.csv
    """
    def __init__(self, path_to_the_file):
        self.file_path = path_to_the_file
        self.movie_data = {}
        self.directors = {}
        self.budgets = {}
        self.profits = {}
        self.runtimes = {}
        self.costs = {}
        self.data = []
    
    def file_reader(self):
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                if not lines:
                    raise ValueError("The file is empty.")
                data = []
                for line in lines:
                    value = line.strip().split(',')
                    data.append(value)
                self.data = data
                return data
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File '{self.filepath}' not found.")

    def time_to_minutes(self, time):
        time = time.replace('hours', 'hour').replace('minutes', 'minute')
        parts = time.split('hour')
        if len(parts) == 2:
            hours = int(parts[0].strip())
            minutes = int(parts[1].strip().split('minute')[0].strip())
            return hours * 60 + minutes
        else:
            minutes = int(parts[0].strip().split('minute')[0].strip())
            return minutes
    
    def get_imdb(self,list_of_movies, list_of_fields):
        imdb_info = []
        connect_timeout = 15
        read_timeout = 30
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        imdb_info.append(list_of_movies[0]+list_of_fields)
        for movie in list_of_movies[1:]:
            url = f'http://www.imdb.com/title/tt{movie[1]}/'
            response = requests.get(url, headers=headers, timeout=(connect_timeout, read_timeout))
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item')
            directors = []
            for link in links:
                href = link.get('href', '')
                if 'dr' in href.split('ref_')[-1]: 
                    directors.append(link.text)
            movie.append(directors[0] if directors else None)
            gross = soup.find_all(attrs={"data-testid":"title-boxoffice-cumulativeworldwidegross"})
            if gross:
                values = gross[0].find('span', class_='ipc-metadata-list-item__list-content-item') 
                if values:
                    revenue_str = values.text.strip().replace('$','').replace(',','')
                    try:
                        movie.append(int(revenue_str))
                    except ValueError:
                        movie.append(None)
                else:
                    movie.append(None)
            else:
                values = None
                movie.append(values)
            time = soup.find_all(attrs={"data-testid":"title-techspec_runtime"})
            values_time = time[0].find("div", class_='ipc-metadata-list-item__content-container')
            movie.append(self.time_to_minutes(values_time.text))
            budjet = soup.find_all(attrs={"data-testid":"title-boxoffice-budget"})
            if budjet:
                values_budjet = budjet[0].find("span", class_='ipc-metadata-list-item__list-content-item')
                budget_str = values_budjet.text.strip()
                budget_str = budget_str.replace('$','').replace(',','').replace('(estimated)','').strip()
                try:
                    movie.append(int(budget_str))
                except ValueError:
                    movie.append(None)
            else:
                movie.append(None)
            imdb_info.append(movie)

        imdb_info.sort(key=lambda x: x[0], reverse=True)
        """
        The method returns a list of lists [movieId, field1, field2, field3, ...] for the list of movies given as the argument (movieId).
        For example, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        The values should be parsed from the IMDB webpages of the movies.
     Sort it by movieId descendingly.
        """
        return imdb_info
        
    def valid_list_without_header(self):
        if not self.data:
            self.file_reader()
        return self.data[1:]
    
    def top_directors(self, n):
        """
        Returns dict with top-n directors and their movie counts
        """
        data = self.valid_list_without_header()

        directors_count = {}
        for row in data:
            if len(row) > 3:  
                director = row[3]
                if director:  
                    directors_count[director] = directors_count.get(director, 0) + 1
                
        sorted_directors = sorted(directors_count.items(), key=lambda x: x[1], reverse=True)[:n]
        return dict(sorted_directors)

    
    def most_expensive(self, n):
        """
        Returns dict with top-n movies by budget
        """
        data = self.valid_list_without_header() 
        
        valid_movies = []
        for row in data:
            try:
                if len(row) > 6 and row[6] is not None:
                    movie_id = row[0]
                    budget = int(row[6])
                    valid_movies.append((movie_id, budget))
            except (IndexError, ValueError):
                continue
                
        valid_movies.sort(key=lambda x: x[1], reverse=True)
        top_n = valid_movies[:n]
        
        return {m[0]: m[1] for m in top_n}
        
    def most_profitable(self, n):
        """
        Returns dict with top-n movies by profit (gross - budget)
        """
        data = self.valid_list_without_header() 
        profits_list = []
        
        for row in data:
            try:
                if len(row) > 6: 
                    if row[4] is not None and row[6] is not None:
                        movie_id = row[0]
                        gross = int(row[4]) if isinstance(row[4], (int, str)) else 0
                        budget = int(row[6]) if isinstance(row[6], (int, str)) else 0
                        profit = gross - budget
                        profits_list.append((movie_id, profit))
            except (IndexError, ValueError):
                continue
                
        profits_list.sort(key=lambda x: x[1], reverse=True)
        top_n = profits_list[:n]
        
        return {m[0]: m[1] for m in top_n}

    def longest(self, n):
        """
        Returns dict with top-n movies by runtime
        """
        data = self.valid_list_without_header()
        valid_movies = []
        
        for row in data:
            try:
                if len(row) > 5:
                    movie_id = row[0]
                    runtime = row[5]
                    if runtime is not None:
                        runtime = int(runtime) if isinstance(runtime, (int, str)) else 0
                        valid_movies.append((movie_id, runtime))
            except (IndexError, ValueError):
                continue
                
        valid_movies.sort(key=lambda x: x[1], reverse=True)
        top_n = valid_movies[:n]
        
        return {m[0]: m[1] for m in top_n}
        
    def top_cost_per_minute(self, n):
        """
        Returns dict with top-n movies by cost per minute
        """
        data = self.valid_list_without_header() 
        costs_list = []
        
        for row in data:
            try:
                if len(row) > 6:
                    movie_id = row[0]
                    runtime = row[5]
                    budget = row[6]
                    if runtime and budget and int(runtime) > 0:
                        cost_per_min = round(int(budget) / int(runtime), 2)
                        costs_list.append((movie_id, cost_per_min))
            except (IndexError, ValueError, TypeError, ZeroDivisionError):
                continue
                
        costs_list.sort(key=lambda x: x[1], reverse=True)
        top_n = costs_list[:n]
        
        return {m[0]: m[1] for m in top_n}
    
######################### Ratings - woolsbub #########################

class Ratings:
    def __init__(self, path_to_the_file):
        self.path_to_the_file = path_to_the_file
    
    class Movies:    
        def dist_by_year(self):
            """
            Метод возвращает dict, где ключами являются годы, а значениями - количество. 
            Отсортируйте его по возрастанию лет. Вам нужно извлечь годы из временных меток.
            """

            ratings_by_year={}
            with open(self.path_to_the_file,"r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    year = datetime.datetime.fromtimestamp(int(row["timestamp"])).year
                    if year in ratings_by_year.keys():
                        ratings_by_year[year] += 1
                    else:
                        ratings_by_year[year] = 1
            return dict(sorted(ratings_by_year.items()))
        
        def dist_by_rating(self):
            """
            Метод возвращает dict, в котором ключами являются оценки, а значениями - количество.
            Отсортируйте его по возрастанию оценок.
            """

            ratings_distribution={}
            with open(self.path_to_the_file,"r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    mark = float(row["rating"])
                    if mark in ratings_distribution.keys():
                        ratings_distribution[mark] += 1
                    else:
                        ratings_distribution[mark] = 1

            return dict(sorted(ratings_distribution.items()))
        
        def top_by_num_of_ratings(self, n=5):
            """
            Метод возвращает n лучших фильмов по количеству оценок. 
            Это dict, в котором ключами являются названия фильмов, а значениями - числа.
            Отсортируйте его по убыванию чисел.
            """
            top_rating = {}
            with open(self.path_to_the_file,"r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    moveid = int(row["movieId"])
                    if moveid in top_rating.keys():
                        top_rating[moveid] += 1
                    else:
                        top_rating[moveid] = 1

            top_rating = dict(sorted(top_rating.items(),reverse=True, key=lambda x: x[1]))
            top_rating_key = list(top_rating.keys())[:n]
            top_rating_values = list(top_rating.values())[:n]
            
            title = []
            movieId_title = []
            with open("movies.csv","r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    title.append(row["title"])
                    movieId_title.append(int(row["movieId"]))

            top_movies = [title[movieId_title.index(index_r)] for index_r in top_rating_key]
            
            return dict((top_movies[i],top_rating_values[i]) for i in range(n)) 

        def top_by_ratings(self, n=5, metric="average"):
            """
            Метод возвращает n лучших фильмов по среднему показателю или медиане оценок.
            Это справочник, в котором ключами являются названия фильмов, а значениями - значения показателей.
            Отсортируйте его по убыванию показателей.
            Значения должны быть округлены до 2 знаков после запятой.
            """
            movieId_rating = {}
            with open(self.path_to_the_file,"r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    movieId = int(row["movieId"])
                    if movieId in movieId_rating.keys():
                        movieId_rating[movieId].append(float(row["rating"]))
                    else:
                        movieId_rating[movieId] = [float(row["rating"])]       
                
                for key in movieId_rating.keys():
                    if metric == "average":
                        movieId_rating[key] = round(statistics.mean(movieId_rating[key]),2)
                    elif metric == "median":
                        movieId_rating[key] = statistics.median(movieId_rating[key])
                movieId_rating = dict(sorted(movieId_rating.items(),reverse=True, key=lambda x: x[1])[:n])    
                
            title = {}
            with open("movies.csv","r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    title[int(row["movieId"])] = row["title"]
            
            top_movies = {}
            for key, value in movieId_rating.items():
                top_movies[title[key]] = value

            return top_movies
        
        def top_controversial(self, n=5):
            """
            Метод возвращает n лучших фильмов по разнице рейтингов.
            Это справочник, в котором ключами являются названия фильмов, а значениями - различия.
            Отсортируйте его по убыванию различий.
            Значения следует округлить до 2 знаков после запятой.
            """
            
            movieId_rating = {}
            with open(self.path_to_the_file,"r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    movieId = int(row["movieId"])
                    if movieId in movieId_rating.keys():
                        movieId_rating[movieId].append(float(row["rating"]))
                    else:
                        movieId_rating[movieId] = [float(row["rating"])]       
                
                for key in movieId_rating.keys():
                    movieId_rating[key] = max(movieId_rating[key]) - min(movieId_rating[key])
                movieId_rating = dict(sorted(movieId_rating.items(),reverse=True, key=lambda x: x[1])[:n])    
                
            title = {}
            with open("movies.csv","r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    title[int(row["movieId"])] = row["title"]
            
            top_movies = {}
            for key, value in movieId_rating.items():
                top_movies[title[key]] = value

            return top_movies

    class Users(Movies):
        """
        В этом классе должны работать три метода. 
        Первый возвращает распределение пользователей по количеству выставленных ими оценок.
        Второй возвращает распределение пользователей по средним или медианным оценкам, выставленным ими.
        Третий возвращает список из n лучших пользователей с наибольшей разницей в их рейтингах.
        Наследуется от класса Movies. Несколько методов аналогичны методам из него.
        """
        def top_by_person_of_ratings(self,n=5):
            ratings_by_person={}
            with open(self.path_to_the_file,"r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    userId = int(row["userId"])
                    if userId in ratings_by_person.keys():
                        ratings_by_person[userId] += 1
                    else:
                        ratings_by_person[userId] = 1
            return dict(sorted(ratings_by_person.items(),key= lambda x: x[1],reverse=True)[:n])

        def top_by_ratings(self, n=5, metric="average"):
            movieId_rating = {}
            with open(self.path_to_the_file,"r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    movieId = int(row["userId"])
                    if movieId in movieId_rating.keys():
                        movieId_rating[movieId].append(float(row["rating"]))
                    else:
                        movieId_rating[movieId] = [float(row["rating"])]       
                
                for key in movieId_rating.keys():
                    if metric == "average":
                        movieId_rating[key] = round(statistics.mean(movieId_rating[key]),2)
                    elif metric == "median":
                        movieId_rating[key] = statistics.median(movieId_rating[key])
                top_movies = dict(sorted(movieId_rating.items(),reverse=True, key=lambda x: x[1])[:n])    
                
            return top_movies

        def top_controversial(self, n=5):
            movieId_rating = {}
            with open(self.path_to_the_file,"r") as file:
                columns = csv.DictReader(file)
                for row in columns:
                    movieId = int(row["userId"])
                    if movieId in movieId_rating.keys():
                        movieId_rating[movieId].append(float(row["rating"]))
                    else:
                        movieId_rating[movieId] = [float(row["rating"])]       
                
                for key in movieId_rating.keys():
                    movieId_rating[key] = max(movieId_rating[key]) - min(movieId_rating[key])
                top_movies = dict(sorted(movieId_rating.items(),reverse=True, key=lambda x: x[1])[:n])    
                
            return top_movies
        
######################### TEST :( #########################

class Tests:
    """--------------------------Tests for class Tags------------------------------"""

    @pytest.fixture
    def tags_instance(self):
        return Tags("tags.csv")

    def test_file_pars_tags(self, tags_instance):
        assert isinstance(tags_instance.user_ids, list)
        assert isinstance(tags_instance.move_ids, list)
        assert isinstance(tags_instance.tags, list)
        assert isinstance(tags_instance.timestamps, list)
        assert all(isinstance(i, str) for i in tags_instance.user_ids)
        assert all(isinstance(i, str) for i in tags_instance.move_ids)
        assert all(isinstance(i, str) for i in tags_instance.tags)
        assert all(isinstance(i, str) for i in tags_instance.timestamps)

    def test_most_words(self, tags_instance):
        result = tags_instance.most_words(5)
        assert isinstance(result, dict)
        assert all(
            isinstance(key, str) and isinstance(value, int)
            for key, value in result.items()
        )
        assert len(result) <= 5
        assert sorted(result.values(), reverse=True) == list(result.values())

    def test_longest(self, tags_instance):
        result = tags_instance.longest(5)
        assert isinstance(result, list)
        assert all(isinstance(tag, str) for tag in result)
        assert len(result) <= 5
        assert result == sorted(result, key=len, reverse=True)

    def test_most_words_and_longest(self, tags_instance):
        result = tags_instance.most_words_and_longest(5)
        assert isinstance(result, set)
        assert all(isinstance(tag, str) for tag in result)

    def test_most_popular(self, tags_instance):
        result = tags_instance.most_popular(5)
        assert isinstance(result, dict)
        assert all(
            isinstance(key, str) and isinstance(value, int)
            for key, value in result.items()
        )
        assert len(result) <= 5
        assert sorted(result.values(), reverse=True) == list(result.values())

    def test_tags_with(self, tags_instance):
        result = tags_instance.tags_with("funny")
        assert isinstance(result, list)
        assert all(isinstance(tag, str) for tag in result)
        assert result == sorted(result)

    def test_movies_with_tag(self, tags_instance):
        result = tags_instance.movies_with_tag("funny")
        assert isinstance(result, list)
        assert all(isinstance(movie_title, str) for movie_title in result)
        assert result == sorted(result)

    def test_tags_of_movie(self, tags_instance):
        result = tags_instance.tags_of_movie(1)
        assert isinstance(result, list)
        assert all(isinstance(tag, str) for tag in result)
        assert result == sorted(result)

    def test_tags_with_no_results(self, tags_instance):
        result = tags_instance.tags_with("nonexistent_tag")
        assert isinstance(result, list)
        assert result == ["tags_with: No tags with nonexistent_tag"]

    def test_movies_with_tag_no_results(self, tags_instance):
        result = tags_instance.movies_with_tag("nonexistent_tag")
        assert isinstance(result, list)
        assert result == ["movies_with_tag: Movie ID not found for nonexistent_tag."]

    def test_tags_of_movie_no_results(self, tags_instance):
        result = tags_instance.tags_of_movie(999880999)
        assert isinstance(result, list)
        assert result == ["tags_of_movie: tags for 999880999 not found."]

    """--------------------------Tests for class Movies------------------------------"""

    @pytest.fixture
    def movie_data(self):
        return Movies("movies.csv")

    def test_file_pars_movies(self, movie_data):
        assert isinstance(movie_data.movies_id, list)
        assert isinstance(movie_data.movies_titles, list)
        assert isinstance(movie_data.movies_genres, list)
        assert all(isinstance(i, str) for i in movie_data.movies_id)
        assert all(isinstance(i, str) for i in movie_data.movies_titles)
        assert all(isinstance(i, str) for i in movie_data.movies_genres)

    def test_dist_by_release(self, movie_data):
        release = movie_data.dist_by_release()
        assert isinstance(release, dict)
        assert all(isinstance(k, int) for k in release.keys())
        assert all(isinstance(v, int) for v in release.values())
        assert sorted(release.items(), key=lambda item: item[1], reverse=True) == list(
            release.items()
        )

    def test_dist_by_genres(self, movie_data):
        genres = movie_data.dist_by_genres()
        assert isinstance(genres, dict)
        assert all(isinstance(k, str) for k in genres.keys())
        assert all(isinstance(v, int) for v in genres.values())
        assert sorted(genres.items(), key=lambda item: item[1], reverse=True) == list(
            genres.items()
        )

    def test_most_genres(self, movie_data):
        most_genres = movie_data.most_genres(3)
        assert isinstance(most_genres, dict)
        assert len(most_genres) == 3
        assert all(isinstance(k, str) for k in most_genres.keys())
        assert all(isinstance(v, int) for v in most_genres.values())
        assert sorted(
            most_genres.items(), key=lambda item: item[1], reverse=True
        ) == list(most_genres.items())

    def test_movies_of_genre(self, movie_data):
        movies = movie_data.movies_of_genre(
            ["Adventure", "Animation", "Children", "Comedy", "Fantasy"]
        )
        assert isinstance(movies, list)
        assert all(isinstance(i, str) for i in movies)
        assert movies == [
            "Adventures of Rocky and Bullwinkle, The",
            "Ant Bully, The",
            "Antz",
            "Asterix and the Vikings (Astérix et les Vikings)",
            "Emperor's New Groove, The",
            "Enchanted",
            "Gnomeo & Juliet",
            "Home",
            "Inside Out",
            "Moana",
            "Monsters, Inc.",
            "Puss in Boots (Nagagutsu o haita neko)",
            "Robots",
            "Shrek",
            "Shrek Forever After (a.k.a. Shrek: The Final Chapter)",
            "Shrek the Third",
            "Space Jam",
            "TMNT (Teenage Mutant Ninja Turtles)",
            "Tale of Despereaux, The",
            "The Good Dinosaur",
            "The Lego Movie",
            "Toy Story",
            "Toy Story 2",
            "Toy Story 3",
            "Turbo",
            "Twelve Tasks of Asterix, The (Les douze travaux d'Astérix)",
            "Valiant",
            "Who Framed Roger Rabbit?",
            "Wild, The",
        ]
        
    def test_genres_of_movie(self, movie_data):
        genres = movie_data.genres_of_movie('Toy Story')
        assert isinstance(genres, list)
        assert all(isinstance(i, str) for i in genres)
        assert genres == ['Adventure', 'Animation', 'Children', 'Comedy', 'Fantasy']
    
    """--------------------------Tests for class Links------------------------------"""

    @pytest.fixture
    def links_instance(self):
        return Links('links.csv')

    def test_file_reader(self, links_instance):
        data = links_instance.file_reader()
        assert isinstance(data, list)
        if data:
            first_row = data[0]
            assert isinstance(first_row, list)
            assert len(first_row) == 3  # movieId, imdbId, tmdbId

    def test_time_to_minutes(self, links_instance):
        minutes = links_instance.time_to_minutes("2 hours 30 minutes")
        assert isinstance(minutes, int)
        assert minutes == 150

        minutes = links_instance.time_to_minutes("45 minutes")
        assert isinstance(minutes, int)
        assert minutes == 45

    def test_get_imdb(self, links_instance):
        movies = links_instance.file_reader()[:5]  # Test with first 5 movies
        fields = ['Director', 'Cumulative Worldwide Gross', 'Runtime', 'Budget']
        result = links_instance.get_imdb(movies, fields)
        assert isinstance(result, list)
        for row in result:
            assert isinstance(row, list)

    def test_valid_list_without_header(self, links_instance):
        data = links_instance.valid_list_without_header()
        assert isinstance(data, list)
        if data:
            first_row = data[0]
            assert isinstance(first_row, list)
            assert len(first_row) == 3  # movieId, imdbId, tmdbId

    def test_top_directors(self, links_instance):
        links_instance.file_reader()
        result = links_instance.top_directors(5)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, int)

    def test_most_expensive(self, links_instance):
        links_instance.file_reader()
        result = links_instance.most_expensive(5)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, int)

    def test_most_profitable(self, links_instance):
        links_instance.file_reader()
        result = links_instance.most_profitable(5)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, int)

    def test_longest(self, links_instance):
        links_instance.file_reader()
        result = links_instance.longest(5)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, int)

    def test_top_cost_per_minute(self, links_instance):
        links_instance.file_reader()
        result = links_instance.top_cost_per_minute(5)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, float)
    
    """--------------------------Tests for class Ratings------------------------------"""

    @pytest.fixture
    def rating_instance(self):
        return Ratings("ratings.csv")

    def test_dist_by_year(self,rating_instance):
        ratings = rating_instance
        result = ratings.Movies.dist_by_year(ratings)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, int)
            assert isinstance(value, int)
        assert list(result.items()) == sorted(result.items())


    def test_dist_by_rating(self,rating_instance):
        ratings = rating_instance
        result = ratings.Movies.dist_by_rating(ratings)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, float)
            assert isinstance(value, int)
        assert list(result.items()) == sorted(result.items())


    def test_top_by_num_of_ratings(self,rating_instance):
        ratings = rating_instance
        result = ratings.Movies.top_by_num_of_ratings(ratings,5)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, int)
        assert list(result.items()) == sorted(result.items(),reverse=True,key = lambda x : x[1])


    def test_top_by_ratings_median(self,rating_instance):
        ratings = rating_instance
        result = ratings.Movies.top_by_ratings(ratings,5,"median")
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, float)
        assert list(result.items()) == sorted(result.items(),reverse=True,key = lambda x : x[1])


    def test_top_by_ratings_average(self,rating_instance):
        ratings = rating_instance
        result = ratings.Movies.top_by_ratings(ratings,5,"average")
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, float)
        assert list(result.items()) == sorted(result.items(),reverse=True,key = lambda x : x[1])


    def test_top_controversial(self,rating_instance):
        ratings = rating_instance
        result = ratings.Movies.top_controversial(ratings,5)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, float)
        assert list(result.items()) == sorted(result.items(),reverse=True,key = lambda x : x[1])

    def test_top_by_person_of_ratings(self,rating_instance):
        ratings = rating_instance
        result = ratings.Users.top_by_person_of_ratings(ratings)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, int)
            assert isinstance(value, int)
        assert list(result.items()) == sorted(result.items(),reverse=True,key = lambda x : x[1])
    
    def test_top_by_ratings_user_average(self,rating_instance):
        ratings = rating_instance
        result = ratings.Users.top_by_ratings(ratings,5,"average")
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, int)
            assert isinstance(value, float)
        assert list(result.items()) == sorted(result.items(),reverse=True,key = lambda x : x[1])
    
    def test_top_by_ratings_user_median(self,rating_instance):
        ratings = rating_instance
        result = ratings.Users.top_by_ratings(ratings,5,"median")
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, int)
            assert isinstance(value, float)
        assert list(result.items()) == sorted(result.items(),reverse=True,key = lambda x : x[1])

    def test_top_controversial_user(self,rating_instance):
        ratings = rating_instance
        result = ratings.Users.top_controversial(ratings,5)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, int)
            assert isinstance(value, float)
        assert list(result.items()) == sorted(result.items(),reverse=True,key = lambda x : x[1])