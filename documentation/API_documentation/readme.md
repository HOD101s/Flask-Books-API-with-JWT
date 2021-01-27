# Flask API : ECS

| Endpoint                 | Method |
| :----------------------- | :----- |
| get_books/{token}        | POST   |
| get_book/{token}         | GET    |
| add_book/{token}         | POST   |
| update_book/{token}      | POST   |
| add_favourite/{token}    | POST   |
| remove_favourite/{token} | POST   |
| get_favourite/{token}    | GET    |
| login                    | POST   |
| add_user                    | GET   |

## Authentication

Done using **JWT** issued on logging in. This jwt is used to authenticate user for every request. The token expires every 15 minute which requires the user to login again. for this there is an extra endpoint. This is done by appending the token to every path.

### - /login : POST

#### params : [ username, password]

On successful auth issues a jwt token. Else returns Failed Auth.

## APIs

### - /get_books

Returns list of books entries with book title matching filtername passed

#### params : [filtername, start_page, page_size]

1. filtername : Name of book to search
2. start_page : indicates to skip mentioned number of pages in response. Ignores initial start_page-1 chunks of response
3. page_size : size of every individual split for response

### - /get_book

Returns books with matching bookID reference

#### params : [bookID]

1. bookID : the book user wants to get info on

### - /add_book

Adds book to 'data' table

#### params : [addtitle, addauthor, addrating, addisbn, addlangcode, addratingcount, addprice]

1. addtitle: Title of book
2. addauthor: Author of book 
3. addrating: average_rating of book
4. addisbn: isbn code of book
5. addlangcode: language_code of book
6. addratingcount: rating_count for book
7. addprice: price for book

### - /update_book

Updates attributes for book corresponding to updatebookID

#### params : [updatebookID, uptitle, upauthor, uprating, upisbn, uplangcode, upratingcount, upprice]

1. updatebookID: ID of book to update
2. uptitle: updated Title of book
3. upauthor: updated Author of book 
4. uprating: updated average_rating of book
5. upisbn: updated isbn code of book
6. uplangcode: updated language_code of book
7. upratingcount: updated rating_count for book
8. upprice: updated price for book

### - /add_favourite

Adds passed BookID to users favourite list in 'datausers' table. Note user here refers to the user who's valid token is passed in url with add_favourite

#### params : [favbookID]

1. favbookID : the book user wants to add to their favourite list

### - /remove_favourite

Removes passed BookID from users favourite list in 'datausers' table. Note user here refers to the user who's valid token is passed in url with remove_favourite

#### params : [favbookID]

1. rembookID : the book user wants to remove from their favourite list

### - /get_favourite

Returns information on every book in users favourite list.

### - /add_user

adds user to users table

#### params : [username, password]
```
http://127.0.0.1:5000/add_user?username=User3&password=pass3
```



