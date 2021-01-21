import requests

token = ''

def test_login():
    global token
    # positive case
    resp = requests.post('http://127.0.0.1:5000/login', data=dict(username='User2',password='pass2'))
    assert resp.status_code == 200
    assert 'token' in resp.json()
    assert 'error_code' not in resp.json()
    token = resp.json()['token']
    # negative case
    resp = requests.post('http://127.0.0.1:5000/login', data=dict(username=' ', password=' '))
    assert resp.status_code == 200
    assert 'error_code' in resp.json()

def test_get_books():
    global token
    # positive case
    resp = requests.post(
        'http://127.0.0.1:5000/get_books/'+token,
        data=dict(filtername='Pride and Prejudice', start_page='1', page_size='3')
    )
    assert resp.status_code == 200
    assert 'error_code' not in resp.json()
    assert len(resp.json()) == 3
    resp = requests.post(
        'http://127.0.0.1:5000/get_books/' + token,
        data=dict(filtername='Pride and Prejudice', start_page='2', page_size='3')
    )
    assert resp.status_code == 200
    assert 'error_code' not in resp.json()
    assert len(resp.json()) == 2
    resp = requests.post(
        'http://127.0.0.1:5000/get_books/' + token,
        data=dict(filtername='ABCD', start_page='2', page_size='3')
    )
    assert resp.status_code == 200
    assert 'error_code' in resp.json()
    assert resp.json()['error_code'] == 'No Match'

def test_get_book():
    global token
    # positive test
    resp = requests.get(
        'http://127.0.0.1:5000/get_book/' + token + '?bookID=5'
    )
    assert resp.status_code == 200
    assert 'error_code' not in resp.json()
    assert resp.json()['title'] == "Harry Potter and the Prisoner of Azkaban (Harry Potter  #3)"
    # negative test
    resp = requests.get(
        'http://127.0.0.1:5000/get_book/' + token + '?bookID=6'
    )
    assert resp.status_code == 200
    assert 'error_code' in resp.json()
    assert  resp.json()['error_code'] == "Book not found"

def test_add_book():
    global token
    book = {
        'addtitle': 'dummyTitle',
        'addauthor': 'leAuthor',
        'addrating': '123',
        'addisbn': '12321312',
        'addlangcode': 'eng',
        'addratingcount': '123124',
        'addprice': '10'
    }
    resp = requests.post('http://127.0.0.1:5000/add_book/' + token,
        data=book)
    assert resp.status_code == 200
    assert 'error_code' not in resp.json()


def test_update_book():
    global token
    # fake book
    resp = requests.post('http://127.0.0.1:5000/update_book/' + token,
                         data=dict(updatebookID='6'))
    assert resp.status_code == 200
    assert 'error_code' in resp.json()
    assert resp.json()['error_code'] == 'Book not found'
    # update title
    resp = requests.post('http://127.0.0.1:5000/update_book/' + token,
                         data=dict(updatebookID='10', uptitle='', upauthor='', uprating='updated rating', upisbn='', uplangcode='', upratingcount='', upprice=''))
    assert resp.status_code == 200
    assert 'error_code' not in resp.json()


def test_add_fav_get_fav():
    global token
    # fake book id
    resp = requests.post('http://127.0.0.1:5000/add_favourite/' + token,
                         data=dict(favbookID='6'))
    assert resp.status_code == 200
    assert 'error_code' in resp.json()
    assert resp.json()['error_code'] == 'Book not found'
    # correct book
    resp = requests.post('http://127.0.0.1:5000/add_favourite/' + token,
                         data=dict(favbookID='5'))
    assert resp.status_code == 200
    assert 'error_code' not in resp.json()

    resp = requests.get('http://127.0.0.1:5000/get_favourite/' + token)
    assert resp.status_code == 200
    assert 'error_code' not in resp.json()
    assert len(resp.json()) == 1


def test_rem_fav_get_fav():
    global token
    # fake book id
    resp = requests.post('http://127.0.0.1:5000/remove_favourite/' + token,
                         data=dict(rembookID='6'))
    assert resp.status_code == 200
    assert 'error_code' in resp.json()
    assert resp.json()['error_code'] == 'Book Doesnt exist'

    # correct book
    resp = requests.post('http://127.0.0.1:5000/remove_favourite/' + token,
                         data=dict(rembookID='5'))
    assert resp.status_code == 200
    assert 'error_code' not in resp.json()

    resp = requests.get('http://127.0.0.1:5000/get_favourite/' + token)
    assert resp.status_code == 200
    assert 'error_code' not in resp.json()
    assert len(resp.json()) == 0


if __name__ == "__main__":
    test_login()
    test_get_books()
    test_get_book()
    test_add_book()
    test_update_book()
    test_add_fav_get_fav()
    test_rem_fav_get_fav()
    print(f'Token for test : {token}')
    print('Passed All Tests')