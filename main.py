from src.classes import HeadHunter, JSONSaver, SuperJob

from pprint import pprint

def main():
    """Основная функция взаимодействия с пользователем"""
    keyword = input('ВВедите ключевое слово\n')

    hh = HeadHunter(keyword)
    sj = SuperJob(keyword)
    for recruter in hh, sj:
        recruter.get_vacancies(page_count=10)
        vacancies = recruter.format_vacancies()
        json_saver = JSONSaver(keyword)
        json_saver.add_vacancies(vacancies)

    while True:
        command = input(f"""\nВведите обозначение команды:
1: Сортировать вакансии по возрастанию зарплаты и вывести их на экран
2: Вывести на экран топ  N вакансий
3: Вывсти на экран вакансии с зарплатой в диапазоне
exit: Выйти из программы\n""")
        if command == '1':
            data = json_saver.sorted_vacancies()
            for v in data:
                print(v)
        elif command == '2':
            number_vacancies = input('Введите количество входящих в ТОП вакансий\n')
            data = json_saver.sorted_vacancies()
            for r in json_saver.get_top_vacancies(data, int(number_vacancies)):
                print(r)
        elif command == '3':
            range = input ('Введите диапозон зарплат через дефис, например 10000-30000 \n')
            for v in json_saver.vacancies_by_salary_range(range):
                print(v)
        elif command.lower() == 'exit':
            break
        else:
            print('Неверная команда')





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


