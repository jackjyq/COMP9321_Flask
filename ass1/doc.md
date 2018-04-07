# API documentation

## Yiqun Jiang
[z5129432@student.unsw.edu.au](mailto:5129432@student.unsw.edu.au)

## Overview

This documentation covers API of COMP9321 Assignment 1.

## URLs and Operations

Operation     | URL             | Method | Returns                         | Inputs
--------------|-----------------|--------|---------------------------------|------------------------------------------
ListOrder     | /order          | GET    | [listreturn](#listreturn)       | [listinput](#listinput)
CreateOrder   | /order          | POST   | [orderDetail](#orderdetail)     | [order](#order), [cost](#cost), [coffee](#coffee), [additons](#additions)
ReadOrder     | /order/{order}  | GET    | [orderDetail](#orderdetail)     | Null
UpdateOrder   | /order/{order}  | PUT    | [orderDetail](#orderdetail)     | [order](#order), [cost](#cost), [coffee](#coffee), [additons](#additions)
DeleteOrder   | /order/{order}  | DELETE | [orderDetail](#orderdetail)     | Null
ChangeStatus  | /order/{order}  | PATCH  | [orderDetail](#orderdetail)     | [status](#status)
CreatePayment | /payment/{order}| POST   | [paymentDetail](#paymentdetail) | [payment](#payment)
ReadPayment   | /payment/{order}| GET    | [paymentDetail](#paymentdetail) | Null

## Inputs and Returns

### listinput

use the key and value in header to query, for example:

function                    | key             | value
----------------------------|-----------------|------------
List all the open order     | "releaseStatus" | "open"
List all the notPayed order | "paymentStatus" | "notPayed"
List every order            | Null            | Null

### listreturn

```json
{
    100 : {
        "paymentStatus": "notPayed",
        "releaseStatus": "open",
        "drinkStatus": "pending"
    },
    101 : {
        "paymentStatus": "hasPayed",
        "releaseStatus": "open",
        "drinkStatus": "pending"
    },
    102 : {
        "paymentStatus": "notPayed",
        "releaseStatus": "open",
        "drinkStatus": "ready"
    }
}
```

### paymentdetail

for example:

```json
{
    "order": 100,
    "cost": 5.15,
    "coffee": "mocha",
    "additions": "extro ice",
    "status": {
        "paymentStatus": "notPayed",
        "releaseStatus": "open",
        "drinkStatus": "pending"
    },
    "payment": {
        "type": "card",
        "amount": 5.15,
        "cardNumber": "12345678901",
        "name": "Jack",
        "expireDate": "2020/03/20"
    }
}
```

### orderdetail

orderDetail is paymentDetail without payment attribute, but with extra links information. For example:

```json
{
    "order": 100,
    "cost": 5.15,
    "coffee": "mocha",
    "additions": "extro ice",
    "status": {
        "paymentStatus": "notPayed",
        "releaseStatus": "open",
        "drinkStatus": "pending"
    },
    "links":[{
        "rel": "self",
        "href": "http://127.0.0.1:5000/order/100"
    },
    {
        "rel": "payment",
        "href": "http://127.0.0.1:5000/payment/100"
    }]
}
```

## Data type

### order

use an positive integer to indicate the order ID, e.g. 100

### cost

use an positive float to indicate the cost, e.g. 6.15

### coffee

use a string to indicate the type of coffee.

### additions

use a string to indicate the additons, e.g. "extro ice".

### status

the status of an order, only the following key and value are allowed.

- paymentStatus
    - "notPayed"
    - "hasPayed"
- releaseStatus
    - "open"
    - "released"
- drinkStatus
    - "pending"
    - "prepared"

for example:

```json
{
    "paymentStatus": "notPayed",
    "releaseStatus": "open",
    "drinkStatus": "pending"
}
```

### payment

the detail of a payment

```json
{
    "type": "cash" / "card",
    "amount": float,
    "cardNumber": "string",
    "name": "string",
    "expireDate": "string"
}
```