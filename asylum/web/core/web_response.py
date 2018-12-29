from flask import jsonify, make_response, redirect, url_for


def database_error():
    return make_response(jsonify(
        {
            'status': 'error',
            'message': 'Błąd bazy danych!'
        }
    ), 500)


def redirect_to(function_name):
    return redirect(url_for(function_name), code=302)


def bad_request():
    return make_response(jsonify(
        {
            'status': 'error',
            'message': 'Błędne zapytanie!'
        }
    ), 400)


def blind_task_added():
    return make_response(jsonify(
        {
            'status': 'success',
            'message': 'Dodano nowe zadanie!'
        }
    ), 201)


def blinds_schedule_added():
    return make_response(jsonify(
        {
            'status': 'success',
            'message': 'Dodanio nowy harmonogram!'
         }
    ), 201)


def blinds_task_deleted():
    return make_response(jsonify(
        {
            'status': 'success',
            'message': 'Usunięto zadanie!'
        }
    ), 200)


def blinds_schedule_deleted():
    return make_response(jsonify(
        {
            'status': 'success',
            'message': 'Usunięto harmonogram!'
        }
    ), 200)


def blinds_action_executed():
    return make_response(jsonify(
        {
            'status': 'success',
            'message': 'Akcja została wykonana!'
        }
    ), 200)


def user_added():
    return make_response(jsonify(
        {
            'status': 'success',
            'message': 'Poprawnie utworzono użytkownika!'
         }
    ), 201)


def user_already_exist():
    return make_response(jsonify(
        {
            'status': 'error',
            'message': 'Użytkownik o podanym loginie już istnieje!'
        }
    ), 400)


def login_failed():
    return make_response(jsonify(
        {
            'status': 'error',
            'message': 'Niepoprawny login lub hasło!'
        }
    ), 400)


def login_success(cookie):
    res = make_response(jsonify(
        {
            'status': 'success',
            'message': 'Zalogowano!'
        }
    ), 200)
    res.set_cookie(*cookie, secure=False, httponly=True, samesite='strict')
    return res


def logout():
    res = make_response(redirect(url_for('login'), code=302))
    res.set_cookie('Authorization', '', expires=0, secure=False, httponly=True, samesite='strict')
    return res
