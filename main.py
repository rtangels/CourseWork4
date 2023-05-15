from src.classes import HeadHunter, JSONSaver

def main():
    keyword = 'Python'
    h = HeadHunter(keyword)
    vacancy = h.get_vacancies(1)
    json_saver = JSONSaver(keyword)
    json_saver.add_vacancy(vacancy)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


