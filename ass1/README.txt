Student ID: z5129432
Name: Yiqun Jiang

## Installation Guide

- unzip service.zip to an empty folder
- using pyCharm to open this folder
- pyCharm -> File -> Settings -> Project:service -> Project Interpreter
    - make sure the Project Interpreter should be service/venv/bin/python
- run controller.py in pyCharm

## Test Case

### Case 1

1.Cashier creates an order

```
{
    "order": 100,
    "cost": 5.15,
    "coffee": "mocha"
}
```
2.Cashier amends the order by adding an addition

```
{
    "order": 100,
    "cost": 5.15,
    "coffee": "mocha",
    "additions": "extra ice"
}
```

3.Cashier creates a Payment for the order

```
{
    "type": "card",
    "amount": 5.15,
    "cardNumber": "5217200044449876",
    "name": "Yiqun Jiang",
    "expireDate": "2020/3/19"
}
```
4.Barista gets the list of all Open Orders (only one order is available)

headers: key = releaseStatus; value = open

5.Barista changes the status of the Order to being prepared

```
{
    "paymentStatus": "hasPayed",
    "releaseStatus": "open",
    "drinkStatus": "prepared"
}
```

6.Barista checks if the order is paid

just GET http://127.0.0.1:5000/order/100

7.Barista releases the order 

```
{
    "paymentStatus": "hasPayed",
    "releaseStatus": "released",
    "drinkStatus": "prepared"
}
```

8.Barista gets the list of all Open Orders (No order is availabl

headers: key = releaseStatus; value = open

### Case 2

1.Cashier creates an order  

```
{
    "order": 100,
    "cost": 5.15,
    "coffee": "mocha"
}
```

2.Cashier creates a Payment for the order 

```
{
    "type": "card",
    "amount": 5.15,
    "cardNumber": "5217200044449876",
    "name": "Yiqun Jiang",
    "expireDate": "2020/3/19"
}
```

3.Cashier amends the order by adding an addition, but it is refused

```
{
    "order": 100,
    "cost": 5.15,
    "coffee": "mocha",
    "additions": "extra ice"
}
```
 
4.Cashier tries to cancel the order, but it is refuse

just DELETE the order

### Case 3

1.Cashier creates an order (order 1) 

```
{
    "order": 100,
    "cost": 5.15,
    "coffee": "mocha"
}
```

2.Cashier creates an order (order 2) 

```
{
    "order": 101,
    "cost": 6.15,
    "coffee": "latte"
}
```

3.Cashier creates an order (order 3) 

```
{
    "order": 102,
    "cost": 4.15,
    "coffee": "black coffee"
}
```

4.Cashier amends the Order‐2 by adding an addition 

```
{
    "order": 101,
    "cost": 6.15,
    "coffee": "latte",
    "additions": "extra ice"
}
```
5.Cashier creates a Payment for the order‐1 

```
{
    "type": "card",
    "amount": 5.15,
    "cardNumber": "5217200044449876",
    "name": "Yiqun Jiang",
    "expireDate": "2020/3/19"
}
```

6.Cashier creates a Payment for the order‐2 

```
{
    "type": "cash", 
    "amount": 6.15
}
```

7.Barista gets the list of all Open Orders (three orders are avai
lable)  

headers: key = releaseStatus; value = open