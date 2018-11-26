import colorama
import sql_worker
import datetime
import time
import os

if 'PYCHARM_HOSTED' in os.environ:
    convert = False  # in PyCharm, we should disable convert
    strip = False
    print("Hi! You are using PyCharm")
else:
    convert = None
    strip = None

colorama.init(convert=convert, strip=strip)


def loop(request):
    def handle_this(hundeling_dict):
        commas = ("'", '"')
        for handle_this_id in hundeling_dict:
            if answer[handle_this_id][-1] not in commas:
                print(uncorrect_answer)
                continue
        data = {}
        for hndl_id in hundeling_dict:
            try:
                index_of_start = answer[hndl_id].index(hundeling_dict[hndl_id][0]) \
                                 + len(hundeling_dict[hndl_id][0])
            except Exception:
                try:
                    index_of_start = answer[hndl_id].index(hundeling_dict[hndl_id][1]) \
                                     + len(hundeling_dict[hndl_id][1])
                except Exception as e:
                    print(e)
                continue
            data[hundeling_dict[hndl_id][2]] = answer[hndl_id][index_of_start:-1]
        return data
    uncorrect_answer = colorama.Fore.RED + '\n\n\n\nВведите корректную команду!' + colorama.Fore.RESET
    answer = ''
    print('Здравствуйте, {}!'.format(request.user['login']))
    while " ".join(answer).lower() != 'exit':
        print(
            '\n\nСписок команд:\n\n'
            '"BOOK film=\'<title>\' place=\'<num_of_place>\' hall=\'<name>\'" - Забронировать место <num_of_place> на фильм <title> в кинозале <name>\n'
            '"SHOW CINEMAS" - Показать все кинотеатры\n'
            '"SHOW CINEMAS_HALLS" - Показать все кинозалы\n'
            '"SHOW FILMS" - Показать текущие фильмы\n'
            '"PRINT_FILM_HALL film=\'<title>\' hall=\'<name>\'" - Показать все места кинозала <name> фильма <title>\n'
            '"EXIT" - выйти из программы\n\n{}@localmachine:~$ '.format(request.user['login']),
            end=''
        )
        answer = input().split()
        print()
        print()
        print()

        if len(answer) < 1:
            print(uncorrect_answer)
            continue
        elif answer[0] == 'BOOK':
            data = handle_this({1: ('film=\'', 'film="', 'film'), 2: ('place=\'', 'place="', 'place'), 3: ('hall=\'', 'hall="', 'hall')})
            hall_from_bd = request.cursor.execute('SELECT * FROM cinemas_halls WHERE name="{}"'.format(data['hall']))[0]
            film = request.cursor.execute('SELECT * FROM films WHERE title="{}" and halls LIKE "%{}%"'.format(data['film'], data['hall']))[0]
            print('Фильм: {}'.format(film[1]))
            print('Забронировать место: {}'.format(data['place']))
            halls = film[2].split()
            places = ''
            for hall in halls:
                if hall[:len(data['hall'])] == data['hall']:
                    places = hall[len(data['hall']) + 1:-1].split('|')[1:]
                    break
            flag = True
            for place_id in range(len(places)):
                place = places[place_id].split('-')
                if place_id == int(data['place']):
                    if place[1] == '1':
                        flag = False
                        print('Данное место уже занято!')
                        break
                    else:
                        places[place_id] = places[place_id][:-1] + '1' + '-' + request.user['login']
                        break
            if not flag:
                continue
            halls_for_bd = ''
            for hall in range(len(halls)):
                if halls[hall][:len(data['hall'])] == data['hall']:
                    halls_for_bd += data['hall'] + '[|' + "|".join(places) + '] '
                else:
                    halls_for_bd += halls[hall] + ' '
            request.cursor.execute('UPDATE films SET halls="{}" WHERE title="{}"'.format(halls_for_bd, film[1]))
            print('Успешно!')
        elif answer[0] == 'SHOW':
            if len(answer) != 2:
                print(uncorrect_answer)
                continue
            elif answer[1] == 'CINEMAS':
                cinemas = request.cursor.execute('SELECT * FROM cinemas')
                if len(cinemas) > 0:
                    print('№) <name> - <address>')
                else:
                    print(colorama.Fore.RED + 'Не найдено ни одного кинотеатра' + colorama.Fore.RESET)
                for cinema in cinemas:
                    print('{}) {} - {}'.format(cinema[0], cinema[1], cinema[2]))
            elif answer[1] == 'CINEMAS_HALLS':
                cinemas_halls = request.cursor.execute('SELECT * FROM cinemas_halls')
                if len(cinemas_halls) > 0:
                    print('№) <name> - <cinema_name>')
                else:
                    print(colorama.Fore.RED + 'Не найдено ни одного кинозала' + colorama.Fore.RESET)
                for hall in cinemas_halls:
                    print('{}) {} - {}'.format(
                        hall[0],
                        hall[1],
                        request.cursor.execute('SELECT name FROM cinemas WHERE id="{}"'.format(hall[4]))[0][0]
                    ))
                    places = hall[2].split('|')[1:]

                    len_of_place = len(str(len(places) - 1))
                    num_cols = int(hall[3])
                    num_spaces_in_row = num_cols - 1
                    len_of_row = len_of_place * num_cols + num_spaces_in_row

                    print()
                    print(colorama.Fore.YELLOW + 'Экран'.rjust(len_of_row // 2 + 5 - 3, '-').ljust(len_of_row,
                                                                                                   '-') + colorama.Fore.RESET)
                    for place_id in range(len(places)):
                        place = places[place_id].split('-')
                        if place[1] == '1':
                            print(colorama.Fore.RED + place[0].rjust(len(str(len(places) - 1)),
                                                                     '0') + colorama.Fore.RESET, end=' ')
                        if place[1] == '0':
                            print(colorama.Fore.GREEN + place[0].rjust(len(str(len(places) - 1)),
                                                                       '0') + colorama.Fore.RESET, end=' ')
                        if (place_id + 1) % int(hall[3]) == 0:
                            print()
                    print()
            elif answer[1] == 'FILMS':
                print('№) <title> - <halls>')
                now = datetime.datetime.now().timestamp()
                films = request.cursor.execute('SELECT * FROM films WHERE actual_to > {}'.format(now))
                for film in films:
                    print('{}) {} - {}'.format(film[0], film[1],
                                               ", ".join([hall.split('[')[0] for hall in film[2].split()])))
            else:
                print(uncorrect_answer)
                continue
        elif answer[0] == 'PRINT_FILM_HALL' and len(answer) == 3:
            data = handle_this({1: ('film=\'', 'film="', 'film'), 2: ('hall=\'', 'hall="', 'hall')})
            film = request.cursor.execute('SELECT * FROM films WHERE title="{}" and halls LIKE "%{}%"'.format(data['film'], data['hall']))[0]
            hall_from_bd = request.cursor.execute('SELECT * FROM cinemas_halls WHERE name="{}"'.format(data['hall']))[0]
            print('Фильм: {}'.format(film[1]))
            halls = film[2].split()
            places = ''
            for hall in halls:
                if hall[:len(data['hall'])] == data['hall']:
                    places = hall[len(data['hall'])+1:-1].split('|')[1:]
                    break

            len_of_place = len(str(len(places) - 1))
            num_cols = int(hall_from_bd[3])
            num_spaces_in_row = num_cols - 1
            len_of_row = len_of_place * num_cols + num_spaces_in_row

            print()
            print(colorama.Fore.YELLOW + 'Экран'.rjust(len_of_row // 2 + 5 - 3, '-').ljust(len_of_row,
                                                                                           '-') + colorama.Fore.RESET)
            for place_id in range(len(places)):
                place = places[place_id].split('-')
                if place[1] == '1':
                    print(colorama.Fore.RED + place[0].rjust(len(str(len(places) - 1)), '0') + colorama.Fore.RESET,
                          end=' ')
                if place[1] == '0':
                    print(colorama.Fore.GREEN + place[0].rjust(len(str(len(places) - 1)), '0') + colorama.Fore.RESET,
                          end=' ')
                if (place_id + 1) % int(hall_from_bd[3]) == 0:
                    print()
            print()
        elif answer[0] == 'EXIT' and len(answer) == 1:
            return None
        else:
            print(uncorrect_answer)
            continue


if __name__ == '__main__':
    request = sql_worker.Request()
    print('Здравствуйте! Вас приветствует система контроля кинотеатров.')
    print('Чтобы зарегистрироваться, введите "r"')
    print('Чтобы войти в свой аккаунт, введите "l"')
    choise = input('{}@localmachine:~$ '.format(request.user['login']))
    while choise.lower() not in ('r', 'l'):
        print(colorama.Fore.RED + 'Некорректный символ!' + colorama.Fore.RESET)
        choise = input('{}@localmachine:~$ '.format(request.user['login']))
    if choise == 'r':
        print()
        print('Регистрация в CCS (Cinema Control System)')
        login = input('Введите логин: ')
        while len(login) < 4:
            print('Логин должен быть длиннее 5 символов')
            login = input('Введите логин: ')
        users_with_this_login = request.cursor.execute('SELECT * FROM auth WHERE login="{}"'.format(login))
        while len(users_with_this_login) > 0:
            print(colorama.Fore.RED + 'Аккаунт с таким логином существует!' + colorama.Fore.RESET)
            login = input('Введите логин: ')
            users_with_this_login = request.cursor.execute('SELECT * FROM auth WHERE login="{}"'.format(login))
        password = input('Введите пароль: ')
        while len(password) < 6:
            print('Пароль должен быть длиннее 6 символов')
            password = input('Введите пароль: ')
        request.cursor.execute('INSERT INTO auth (login, password, is_admin) VALUES ("{}", "{}", "0")'.format(login, password))
        print('Успешно!')
        request_answer = request.auth(login, password)
        loop(request)
    elif choise == 'l':
        print()
        print('Авторизация в CCS (Cinema Control System)')
        login = input('Введите логин: ')
        password = input('Введите пароль: ')
        request_answer = request.auth(login, password)
        request_answer = request_answer.get('success', request_answer.get('error', None))
        if request_answer is not None:
            print(request_answer)
        if request.user['login'] != 'Anonym':
            loop(request)
    else:
        print('Хакер что-ли? -_-')
    input('Нажмите ENTER, чтобы завершить программу')
    request.kill()

