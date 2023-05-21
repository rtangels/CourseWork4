import os

import requests

import json



from abc import ABC, abstractmethod


class ParsingError (Exception):
    """Пользовательский класс ошикок"""

    def __str__(self):
        """Возвращает текст ошибки"""
        return 'Ошибка получения данных'

class apiRecruiter(ABC):
    """Абстракный класс для работы

         с рекрутинговыми API"""

    @abstractmethod
    def get_vacancies (self):
        pass

    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def format_vacancies(self):
        pass

class HeadHunter(apiRecruiter):
  def __init__(self, keyword):
      """конструктора класса для API hh.ru"""
      self.__header = {'User-Agent': 'Mozilla/5.0 (platform; rv:gekoversion)  Gecko/geckotrail YaBrowser/23.3.3.719'}
      self.__params = {
          'text': keyword,
          'page': 0,
          'per_page' : 20
          
          ,
      }
      self.__vacancies = []

  @staticmethod
  def get_salary(salary):
      """Приводит зарпалату к зарплате в одной валюте"""
      formated_salary = [None,None]
      if salary and salary['from'] and salary['from'] !=0:
          if salary['currency'].lower() == 'rur':
            formated_salary[0]=salary['from']
          elif salary['currency'].lower() == 'eur':
            formated_salary[0] = salary['from'] * 84
          else:
            formated_salary[0] = salary['from'] * 78

      if salary and salary['to'] and salary['to'] !=0:
          if salary['currency'].lower() == 'rur':
            formated_salary[1]=salary['to']
          elif salary['currency'].lower() == 'eur':
            formated_salary[1] = salary['to'] * 84
          else:
            formated_salary[1] = salary['to'] * 78
      return formated_salary

  def get_request(self):
      """Получение ответа на запрос по вакансиям"""

      response =  requests.get('https://api.hh.ru/vacancies',
                               headers=self.__header,
                               params=self.__params
                               )
      if response.status_code != 200:
          raise ParsingError
      return response.json()['items']


  def get_vacancies(self, page_count=1):
      """Получает вакансии head hunter"""
      while self.__params['page'] < page_count:
          print(f"Cбор сведений hh, страница{self.__params['page']+1}", end=": ")
          try:
              values = self.get_request()
          except  ParsingError:
              print ('Ошибка получения данных!')
              break
          print (f"Найдено ({len(values)}) вакансий \n")
          self.__vacancies.extend(values)
          self.__params['page'] += 1


  def format_vacancies(self):
      """Возвращает вакансии в едином формате
      для hh и superjob"""
      vacancies = []
      if self.__vacancies:
          for row in self.__vacancies:
              salary_from, salary_to = self.get_salary(row['salary'])
              temp_dict = {
                           'title' : row['name'],
                           'salary_from' : salary_from,
                           'salary_to' : salary_to,
                           'discription' : row['snippet']['responsibility'],
                           'company_name' : row['employer']['name'],
                           'link' : row['alternate_url']
                           }
              vacancies.append(temp_dict)
      return vacancies

class SuperJob(apiRecruiter):
    """Класса для superjob"""

    def __init__(self, keyword):
        self.__header = {
            "X-Api-App-Id": os.getenv('SJ_API_KEY')
        }
        self.__params = {
            "keyword" : keyword,
            "page" : 0,
            "count" : 100
        }
        self.__vacancies = []


    def get_request(self):
        """Получение ответа на запрос по вакансиям"""
        response =  requests.get('https://api.superjob.ru/2.0/vacancies',
                               headers=self.__header,
                               params=self.__params
                               )
        if response.status_code != 200:
            raise ParsingError
        return response.json()['objects']


    def get_vacancies(self, page_count=1):
        """Получает вакансии Superjob"""
        while self.__params['page'] < page_count:
            print(f"Cбор сведений superjob, страница{self.__params['page']+1}", end=": ")
            try:
                values = self.get_request()
            except  ParsingError:
                print ('Ошибка получения данных!')
                break
            print (f"Найдено ({len(values)}) вакансий \n")
            self.__vacancies.extend(values)
            self.__params['page'] += 1

    @staticmethod
    def get_salary(data):
        """Приводит зарпалату к зарплате в одной валюте"""
        formated_salary = [None, None]
        if data and data['payment_from'] and data['payment_from'] != 0:
            if data['currency'].lower() == 'rub':
                formated_salary[0] = data['payment_from']
            elif data['currency'].lower() == 'eur':
                formated_salary[0] = data['payment_from'] * 84
            else:
                formated_salary[0] = data['payment_from'] * 78

        if data and data['payment_to']and data['payment_to'] != 0:
            if data['currency'].lower() == 'rub':
                formated_salary[1] = data['payment_to']
            elif data['currency'].lower() == 'eur':
                formated_salary[1] = data['payment_to'] * 84
            else:
                formated_salary[1] = data['payment_to'] * 78
        return formated_salary

    def format_vacancies(self):
        """Возвращает вакансии в едином формате
        для hh и superjob"""
        vacancies = []
        if self.__vacancies:
            for row in self.__vacancies:
                salary_from, salary_to = self.get_salary(row)
                temp_dict = {
                    'title': row['profession'],
                    'salary_from': salary_from,
                    'salary_to': salary_to,
                    'discription': row['vacancyRichText'],
                    'company_name': row['firm_name'],
                    'link': row['link']
                     }
                vacancies.append(temp_dict)
        return vacancies


class Vacancy:
    """Каласс работы с вакансиями"""
    __slots__ = ('__title','__salary_from', '__salary_to', '__discription', '__company_name','__link')

    def __init__ (self, title, salary_from, salary_to, discription, company_name, link):
        """Конструктор класса вакансий"""
        self.__title = title
        self.__salary_from = salary_from
        self.__salary_to = salary_to
        self.__discription = discription
        self.__company_name = company_name
        self.__link = link

    def __str__(self):
        """Выводит иноформацию о вакансии для пользователя"""
        salary_min = f" ОТ {self.__salary_from}" if self.__salary_from else ""
        salary_max = f"ДО {self.__salary_to}" if self.__salary_to else ""
        if self.__salary_from is None and self.__salary_to is None:
            salary_max = "Зарплата не указана"
        return f"""Вакансия: {self.__title} от компании {self.__company_name}
 зарплата {salary_min} {salary_max}\n"""

    @property
    def salary_from(self):
        """Возвращает зарплату ОТ"""
        return self.__salary_from

    @property
    def salary_to(self):
        """Возвращает зарплату До"""
        return self.__salary_to

    def __lt__(self, other):
        """Метод сравнения вакансий"""
        if not self.salary_from and not self.salary_to:
            return True
        elif not self.salary_from:
            if not other.salary_from and not other.salary_to:
                return False
            elif not other.salary_to:
                return self.salary_to <= other.salary_from
            elif not other.salary_from:
                return  self.salary_to <= other.salary_to
            else:
                if self.salary_to > other.salary_from:
                    return  (self.salary_to < other.salary_to)
        elif self.salary_from and not self.salary_to:
            if  not other.salary_from and not other.salary_to:
                return  False
            elif not other.salary_to:
                return  self.salary_from <= other.salary_from
            elif not other.salary_from:
                return self.salary_from < other.salary_to
            else:
                return (self.salary_from <= other.salary_from) and (self.salary_from < other.salary_to)
        else:
            if  not other.salary_from and not other.salary_to:
                return False
            elif not other.salary_to:
                return (self.salary_from <= other.salary_from) and (self.salary_to <= other.salary_from)
            elif not other.salary_from:
                return (self.salary_from <= other.salary_to) and (self.salary_to <= other.salary_to)
            else:
                return (self.salary_from <= other.salary_from) and (self.salary_to < other.salary_to)








class FileSaver(ABC):
    """Абстрактный класс для сохранения в файлы"""
    @abstractmethod
    def add_vacancies(self):
        pass


class JSONSaver(FileSaver):
    """Класс для сохранения файла"""
    def __init__(self, keyword):
        """Конструктор класса JSONSaver"""
        self.__filename = f'{keyword.title()}.json'

    @property
    def filename(self):
        """Возвращает имя файла"""
        return self.__filename

    def add_vacancies(self, information):
        """Добавляет вакансию в файл"""
        with open(self.__filename, 'w', encoding='utf-8') as file:
            json.dump(information,file,indent=4,ensure_ascii=False)

    def  select (self):
        """Чтение вакансий из файла"""
        with open (self.__filename, 'r', encoding= 'utf-8') as file:
             data = json.load(file)
             vacancies = []
             for d_dict in data:
                 v = Vacancy(d_dict['title'], d_dict['salary_from'], d_dict['salary_to'], d_dict['discription'], d_dict['company_name'], d_dict['link'])
                 vacancies.append(v)
        return vacancies

    def sorted_vacancies(self):
        """Производит сортировку данных их файла
         с вакансиями  по возрастанию зарплат"""
        vacancies = self.select()
        vacancies = sorted(vacancies)
        return vacancies

    def get_top_vacancies(self,data,num_top=1):
        """Возвращает num_top количество
        вакансий"""
        print(f"\n Топ {num_top} вакансий\n")
        vacancies = [data[-i] for i in range(1,num_top+1)]
        return vacancies

    def vacancies_by_salary_range(self,salary_range):
        """Выводит зарплаты в заданном диапазоне"""
        data = self.select()
        if isinstance(salary_range, str) and '-' in salary_range:
            salary_min_str, salary_max_str = salary_range.split('-')
            salary_min = int(salary_min_str)
            salary_max = int(salary_max_str)
        else:
            print("Неверный формат диапазона")

        if salary_min > salary_max:
            t = salary_max
            salary_maх = salary_min
            salary_min = t
        elif salary_min == salary_max:
            print("Не указан диапазон")



        vacancies = []


        for vacancy in data:
            salary_from = vacancy.salary_from if vacancy.salary_from else 0
            salary_to = vacancy.salary_to if vacancy.salary_to else 0
            if salary_min <= salary_from < salary_max or salary_min < salary_to <= salary_max:
                vacancies.append(vacancy)

        return vacancies











