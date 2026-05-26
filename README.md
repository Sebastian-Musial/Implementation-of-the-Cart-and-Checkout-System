

- Ograniczenia i założenia biznesowe
    - Stan magazynowy nie może spaść poniżej 0
    - Cena produktu nie może być ujemna
    - Ilosc produktow w koszyku musi byc wieksza od 0
    - Jeden klient może mieć tylko jeden koszyk
    - Koszyk nie może mieć dwóch pozycji z tym samym produkcem, w przypadku dobrania produktu zwiekszamy ilosc produk w pozycji koszyka
    - Zamówienie musi posiadac przynajmniej 1 produkt w ilości jednej sztuki
    - W przypadku gdy 2 klientow naraz chce kupić ten sam produkt w momencie kiedy mamy ostatnią sztukę produktu, kierujemy się zasadą "Kto pierwszy ten lepszy"



- Model danych

Klient {
    - ID klienta
    - Imie
    - Nazwisko
    - Numer tel
}


Koszyk zakupowy {
    - ID koszyka // Wydaje mi się że samo ID koszyka mogę traktować jako sesje
    - ID klienta
    [Zawartość koszyka _ Nowa tabela] {
        Pozycja koszyka 1 [Nowa tabela] { //Produkt 1 w koszyku
            - ID koszyka
            - ID pozycji koszyka
            - ID produktu
            - Ilość
        }
        Pozycja koszyka 2 { //Produkt 2 w koszyku
            - ID koszyka
            - ID pozycji koszyka
            - ID produktu
            - Ilość
        }
        Pozycja koszyka 3 { //Produkt 3 w koszyku
            - ID koszyka
            - ID pozycji koszyka
            - ID produktu
            - Ilość
        }
    }
    - Status koszyka //Aktualny plan użycia statusu będzie tylko do kodu aby móc sprawdzać czy koszyk jest: Otwarty, w trakcie zamówienia, zakończony
}


Zamówienie {
    - ID zamówienia
    - ID klienta
    - Data zamówienia
    - Pozycje zamówienia {
        //Tutaj przenosimy zawartość koszyka w takiej samej formie poniżej przykład:
        Pozycja zamówienia 1 [Nowa tabela] { //Produkt 1 z koszyka
            - ID zamówienia
            - ID pozycji zamówienia
            - ID produktu
            - Nazwa
            - Ilość
            - Cena jednostkowa
        }
    }
    - Status zamówienia //Aktualny plan użycia statustu będzie do kodu aby móc spradzać czy zamówienie jest: W trakcie realizacji, anulowane, ukończone
    - Cena całego zamówienia suma
}


Produkt {
    - ID produktu
    - Nazwa
    - Cena jednostkowa
    - Stan magazynowy
}



- Projekt tabel

Clients:
    Kolumny:
        - ID [Id; Not Null]
        - Name [string; Not Null]
        - Surname [string; Not Null]
        - Phone_number [string; Not Null]
    Klucz główny:
        - ID
    Klusze obce:
        - Brak
    Ograniczenia:
        - Brak ponieważ zakładamy że telefon może być współdzielony przez kilka osób



Carts:
    Kolumny:
        - ID [Id; Not Null]
        - ID_client [Id; Not Null; UNIQUE]
        - Status [enum; Not Null]
    Klucz główny:
        - ID
    Klusze obce:
        - ID_client
    Ograniczenia:
        - Jeden klient ma tylko jeden koszyk, ID_client UNIQUE



Cart_items:
    Kolumny:
        - ID [Id, Not Null]
        - ID_cart [Id, Not Null]
        - ID_product [Id, Not Null]
        - Amount [int; Not Null]
    Klucz główny:
        - ID
    Klusze obce:
        - ID_cart
        - ID_product
    Ograniczenia:
        - Amount > 0 
        - Para: ID_cart + ID_product musi być UNIQUE



Orders:
    Kolumny:
        - ID [Id, Not Null]
        - ID_client [Id, Not Null]
        - Created_at [datetime; Not Null]
        - Status [enum; Not Null]
        - Total_order_price [decimal; Not Null]
    Klucz główny:
        - ID
    Klusze obce:
        - ID_client
    Ograniczenia:
        - Total_order_price > 0



Order_items:
    Kolumny:
        - ID [Id, Not Null]
        - ID_order [Id, Not Null]
        - ID_product [Id, Not Null]
        - Product_name [string; Not Null]
        - Product_amount [int; Not Null]
        - Unit_price [decimal; Not Null]
    Klucz główny:
        - ID
    Klusze obce:
        - ID_order
        - ID_product
    Ograniczenia:
        - Product_amount > 0
        - Unit_price > 0



Products:
    Kolumny:
        - ID [Id, Not Null]
        - Name [string; Not Null]
        - Unit_price [decimal; Not Null]
        - Amount_in_stock [int; Not Null]
    Klucz główny:
        - ID
    Klusze obce:
        - Brak
    Ograniczenia:
        - Unit_price > 0
        - Amount_in_stock >= 0



- Algorytm checkoutu koszyka zakupowego. Cały checkout musi dokonać się w formie jednej transakcji bazodanowej
    1. Pobranie koszyka zakupowego
    2. Sprawdzenie czy koszyk nie jest pusty (Walidacja czy jest produktu i czy jest poprawna ilosc)
    3. Sprawdzenie stanów magazynowych dla wybranych produktów
        - Brak produktu w magazynie = poinformowanie klienta o chwilowym braku produktu
        - Produkt w magazynie przechodzimy dalej
    4. Blokada odpowiedniej ilości produktu w magazynie na realizacje tego zamówienia
    5. Zrealizowanie zamówienia zapisanie na stałe takich danych jak [nazwa produktu w momencie zakupu] [cena jednostkowa produktu w momencie zakupu]
    6. Wyczyszczenie koszyka zakupowego
    7. Poinformowanie klienta o udanych zakupach 



- REST API - Endpoint

    - Koszyk: [Wyświetlenei koszyka] [Dodanie produktu do koszyka] [Usunięcie produktu z koszyka] [Zmiana ilości produktu w koszyku] [Checkout]

        1. Wyświetlenie koszyka zakupowego

            Metoda HTTP: GET /carts/{cart_id} HTTP/1.1
            Ścieżka: localhost:8000
            
            Path params:
            - cart_id: int, required, musi istnieć w tabeli carts

            Dane wejściowe przykład: 
                {}

            Response  model:
            - client_id: int, musi istnieć w tabeli clients
            - cart_id: int, musi istnieć w tabeli carts
            - items: lista CartItemsResponse

            CartItemsResponse:
            - product_id: int, musi istnieć w tabeli products
            - product_name: string
            - amount: int

            Sukces przykład:
                HTTP/1.1 200 OK
                Content-Type: application/json
                Cache-Control: no-cache
                {
                    "client_id": 1,
                    "cart_id": 1,
                    "items": [
                        {
                            "product_id": 1,
                            "product_name": "Produkt 1",
                            "amount": 4
                        }
                        .
                        .
                        .
                        {
                            "product_id": X,
                            "product_name": "Produkt X",
                            "amount": 2
                        }
                    ]
                }

            Możliwe błędy:
                400 Bad Request - Błąd w parametrach
                404 Not Found - Zasób nie znaleziony


        2. Dodanie produktu do koszyka lub w przypadku gdy produkt już jest zmieniamy ilość
            
            Metoda HTTP: POST /carts/{cart_id}/items HTTP/1.1
            Ścieżka: localhost:8000

            Path params:
            - cart_id: int, required, musi istnieć w tabeli carts
            
            Request model:
            - product_id: int, required, musi istnieć w tabeli products
            - amount: int, required, większy od 0 

            Dane wejściowe przykład:
                {
                    "product_id": 2,
                    "amount": 4
                }

            Sukces przykład:
                HTTP/1.1 201 Created    //201 Created - kiedy dodamy nowy produkt do koszyka, 200 ok jeśli produkt już był i aktualizujemy ilość
                Content-Type: application/json
                Cache-Control: no-cache
                {}

            Możliwe błędy:
                400 Bad Request - Błąd w parametrach, w treści JSON
                422 Unprocessable Content - Walidacja danych np. Czy ilość jest większa od 0


        3. Usunięcie produktu z koszyka

            Metoda HTTP: DELETE /carts/{cart_id}/items/{product_id} HTTP/1.1
            Ścieżka: localhost:8000

            Path params:
            - cart_id: int, required, musi istnieć w tabeli carts
            - product_id: int, required, musi istnieć w tabeli products

            Dane wejściowe przykład:
                {}

            Sukces przykład:
                HTTP/1.1 204 No Content
                
            Możliwe błędy:
                404 Not Found - Zasób nie znaleziony
                
        4. Zmiana ilości dla danego produktu w koszyku

            Metoda HTTP: PATCH /carts/{cart_id}/items/{product_id} HTTP/1.1
            Ścieżka: localhost:8000

            Path params:
            - cart_id: int, required, musi istnieć w tabeli carts
            - product_id: int, required, musi istnieć w tabeli products

            Request model:
            - amount: int, required, większy od 0 

            Dane wejściowe:
                {
                    "amount": 4
                }

            Sukces:
                HTTP/1.1 200 OK
                Content-Type: application/json
                Cache-Control: no-cache
                {}

            Możliwe błędy:
                400 Bad Request - Błąd w parametrach, w treści JSON
                404 Not Found - Zasób nie znaleziony
                422 Unprocessable Content - Walidacja danych np. Czy ilość nie jest mniejsza od 0 

        5. Checkout koszyka czyli realizacja zamówienia

            Metoda HTTP: POST /carts/{cart_id}/checkout HTTP/1.1
            Ścieżka: localhost:8000

            Path params:
            - cart_id: int, required, musi istnieć w tabeli carts

            Dane wejściowe:
                {}

            Sukces:
                HTTP/1.1 201 Created
                Content-Type: application/json
                Cache-Control: no-cache
                {}

            Możliwe błędy:
                400 Bad Request - Błąd w parametrach
                409 Conflict - Bład, ilość danego produktu w koszyku przekracza stan w magazynie


    - Zamówienia [Wyświetl zamówienie]

        1. Wyświetlenie konkretnego zamówienia

            Metoda HTTP: GET /orders/{order_id} HTTP/1.1
            Ścieżka: localhost:8000

            Path params:
            - order_id: int, required, musi istnieć w tabeli orders

            Dane wejściowe przykład: 
                {}

            Response model:
            - client_id: int, musi istnieć w tabeli clients
            - order_id: int, musi istnieć w tabeli orders
            - items: lista OrderItemResponse
            - total_order_price: decimal

            OrderItemResponse:
            - product_id: int, musi istnieć w tabeli products
            - product_name: string
            - amount: int
            - unit_price: decimal

            Sukces przykład:
                HTTP/1.1 200 OK
                Content-Type: application/json
                Cache-Control: no-cache
                {
                    "client_id": 1,
                    "order_id": 1,
                    "items": [
                        {
                            "product_id": 1,
                            "product_name": "Produkt 1",
                            "amount": 4,
                            "unit_price": 1.50
                        },
                        .
                        .
                        .
                        {
                            "product_id": x,
                            "product_name": "Produkt X",
                            "amount": 2,
                            "unit_price": 1.50
                        }
                    ],
                    "total_order_price": 125.95
                }

            Możliwe błędy:
                400 Bad Request - Błąd w parametrach
                404 Not Found - Zasób nie znaleziony


    - Klienci [Wyświetl klienta] [Dodaj klienta] [Usun klienta]

        1. Wyświetlenie konkretnego klienta

            Metoda HTTP: GET /clients/{client_id} HTTP/1.1
            Ścieżka: localhost:8000

            Path params:
            - client_id: int, required, musi istnieć w tabeli clients

            Dane wejściowe przykład: 
                {}

            Response model:
            - client_id: int, musi istnieć w tabeli clients
            - name: string
            - surname: string
            - phone_number: string

            Sukces przykład:
                HTTP/1.1 200 OK
                Content-Type: application/json
                Cache-Control: no-cache
                {
                    "client_id": 1,
                    "name": "Adam",
                    "surname": "Biegała",
                    "phone_number": "999111222"
                }

            Możliwe błędy:
                400 Bad Request - Błąd w parametrach
                404 Not Found - Zasób nie znaleziony


        2. Dodanie klienta
            
            Metoda HTTP: POST /clients HTTP/1.1
            Ścieżka: localhost:8000

            Request model:
            - name: string, required
            - surname: string, required
            - phone_number: string, required

            Dane wejściowe przykład:
                {
                    "name": "Adam",
                    "surname": "Biegała",
                    "phone_number": "999111222"
                }

            Sukces przykład:
                HTTP/1.1 201 Created
                Content-Type: application/json
                Cache-Control: no-cache
                {}

            Możliwe błędy:
                400 Bad Request - Błąd w parametrach, w treści JSON


        3. Usunięcie klienta

            Metoda HTTP: DELETE /clients/{client_id} HTTP/1.1
            Ścieżka: localhost:8000

            Path params:
            - client_id: int, required, musi istnieć w tabeli clients

            Dane wejściowe przykład:
                {}

            Sukces przykład:
                HTTP/1.1 204 No Content
                
            Możliwe błędy:
                404 Not Found - Zasób nie znaleziony



    - Produkty [Wyświetl produkt] [Dodaj produkt] [Usuń produkt]

        1. Wyświetlenie konkretnego produktu

            Metoda HTTP: GET /products/{product_id} HTTP/1.1
            Ścieżka: localhost:8000

            Path params:
            - product_id: int, required, musi istnieć w tabeli products

            Dane wejściowe przykład: 
                {}

            Response model:
            - product_id: int, musi istnieć w tabeli products
            - name: string
            - unit_price: decimal
            - amount_in_stock: int

            Sukces przykład:
                HTTP/1.1 200 OK
                Content-Type: application/json
                Cache-Control: no-cache
                {
                    "product_id": 1,
                    "name": "Produkt 1",
                    "unit_price": 2.50 ,
                    "amount_in_stock": 30
                }

            Możliwe błędy:
                400 Bad Request - Błąd w parametrach
                404 Not Found - Zasób nie znaleziony


        2. Dodanie produktu
            
            Metoda HTTP: POST /products HTTP/1.1
            Ścieżka: localhost:8000

            Request model:
            - name: string, required
            - unit_price: decimal, required, większa od 0
            - amount_in_stock: int, required, większe lub równe 0

            Dane wejściowe przykład:
                {
                    "name": "Produkt 1",
                    "unit_price": 2.50 ,
                    "amount_in_stock": 30
                }

            Sukces przykład:
                HTTP/1.1 201 Created
                Content-Type: application/json
                Cache-Control: no-cache
                {}

            Możliwe błędy:
                400 Bad Request - Błąd w parametrach, w treści JSON
                422 Unprocessable Content - Walidacja danych np. Czy ilość nie jest mniejsza od 0 albo czy cena większa od 0


        3. Usunięcie produktu

            Metoda HTTP: DELETE /products/{product_id} HTTP/1.1
            Ścieżka: localhost:8000

            Path params:
            - product_id: int, required, musi istnieć w tabeli products

            Dane wejściowe przykład:
                {}

            Sukces przykład:
                HTTP/1.1 204 No Content
                
            Możliwe błędy:
                404 Not Found - Zasób nie znaleziony

        4. Zmiana ilości na magazynie dla danego produktu

            Metoda HTTP: PATCH /products/{product_id} HTTP/1.1
            Ścieżka: localhost:8000

            Path params:
            - product_id: int, required, musi istnieć w tabeli products

            Request model:
            - amount_in_stock: int, required, większe lub równe 0

            Dane wejściowe:
                {
                    "amount_in_stock": 4
                }

            Sukces:
                HTTP/1.1 200 OK
                Content-Type: application/json
                Cache-Control: no-cache
                {}

            Możliwe błędy:
                400 Bad Request - Błąd w parametrach, w treści JSON
                404 Not Found - Zasób nie znaleziony
                422 Unprocessable Content - Walidacja danych np. Czy ilość jest większa lub równa 0









