from flask import Flask, jsonify
from flask_restful import reqparse, request
import json, copy
from model import *

app = Flask(__name__)


# basic order CRUD functions
@app.route("/order", methods=['POST'])
def create_order():
    # get the input
    order_input = json.loads(request.data)
    # check the input
    if not set(("order", "cost", "coffee")).issubset(order_input.keys()):
        return jsonify({"error": "missing attributes"}), 400
    if not isValidOrder(order_input["order"]):
        return jsonify({"error": "order ID must be an non-negative integer"}), 400
    if not isValidMoney(order_input["cost"]):
        return jsonify({"error": "cost must be an non-negative float"}), 400
    if existOrderID(order_input["order"]):
        return jsonify({"error": "order already exists"}), 409
    # write into database
    key = int(order_input["order"])
    value = copy.deepcopy(template)
    value["order"] = key
    value["cost"] = float(order_input["cost"])
    if existAttribute("additions", order_input):
        value["additions"] = order_input["additions"]
    value["coffee"] = order_input["coffee"]
    database[key] = value
    # form return format
    order_detail = formOrderDetail(key)
    return jsonify(order_detail), 201


@app.route("/order/<order>", methods=['GET'])
def read_order(order):
    order = int(order)
    if not existOrderID(order):
        return jsonify({"error": "order does not exists"}), 404
    order_detail = formOrderDetail(order)
    return jsonify(order_detail), 200


@app.route("/order/<order>", methods=['PUT'])
def update_order(order):
    # get the input
    order_input = json.loads(request.data)
    order = int(order)
    # check the input
    if not existOrderID(order):
        return jsonify({"error": "order does not exists"}), 404
    if not set(("order", "cost", "coffee")).issubset(order_input.keys()):
        return jsonify({"error": "missing attributes"}), 400
    if not isValidOrder(order_input["order"]):
        return jsonify({"error": "order ID must be an non-negative integer"}), 400
    if not isValidMoney(order_input["cost"]):
        return jsonify({"error": "cost must be an non-negative float"}), 400
    if (int(order_input["order"]) != order):
        return jsonify({"error": "input order is inconsistent with URL"}), 400
    # check the logic
    if (database[order]["status"]["paymentStatus"] == "hasPayed"):
        return jsonify({"error": "rejected! can not amend an payed order"}), 400
    if (database[order]["status"]["drinkStatus"] == "prepared"):
        return jsonify({"error": "rejected! can not amend an prepared order"}), 400
    # write into database
    key = int(order_input["order"])
    value = copy.deepcopy(template)
    value["order"] = key
    value["cost"] = float(order_input["cost"])
    if existAttribute("additions", order_input):
        value["additions"] = order_input["additions"]
    value["coffee"] = order_input["coffee"]
    database[key] = value
    # form return format
    order_detail = formOrderDetail(key)
    return jsonify(order_detail), 200


@app.route("/order/<order>", methods=['DELETE'])
def delete_order(order):
    order = int(order)
    if not existOrderID(order):
        return jsonify({"error": "order does not exists"}), 404
    if (database[order]["status"]["paymentStatus"] == "hasPayed"):
        return jsonify({"error": "rejected! can not cancel an payed order"}), 400
    order_detail = formOrderDetail(order)
    del database[order]
    return jsonify(order_detail), 200


# other order functions
@app.route("/order", methods=['GET'])
def list_order():
    pattern_keys = set(request.headers.keys())
    # initialize order list
    order_list = {}
    for key in database.keys():
        order_list[key] = copy.deepcopy(database[key]["status"])
    # remove unmatched item from order list
    for key in database.keys():
        if 'paymentStatus'.title() in pattern_keys:
            if (request.headers["paymentStatus"] 
                    != order_list[key]["paymentStatus"]):
                del order_list[key]
                continue
        if 'releaseStatus'.title() in pattern_keys:
            if (request.headers["releaseStatus"] 
                    != order_list[key]["releaseStatus"]):
                del order_list[key]
                continue
        if 'drinkStatus'.title() in pattern_keys:
            if (request.headers["drinkStatus"] 
                    != order_list[key]["drinkStatus"]):
                del order_list[key]
                continue
    return jsonify(order_list), 200


@app.route("/order/<order>", methods=['PATCH'])
def change_status(order):
    # get the input
    status_input = json.loads(request.data)
    order = int(order)
    # check the input
    if not existOrderID(order):
        return jsonify({"error": "order does not exists"}), 404
    if not set(("paymentStatus", "releaseStatus", \
            "drinkStatus")).issubset(status_input.keys()):
        return jsonify({"error": "missing attributes"}), 400
    if not(status_input["paymentStatus"] in ("notPayed", "hasPayed")):
        return  jsonify({"error": "bad paymentStatus value"}), 400
    if not(status_input["releaseStatus"] in ("open", "released")):
        return  jsonify({"error": "bad releaseStatus value"}), 400
    if not(status_input["drinkStatus"] in ("pending", "prepared")):
        return  jsonify({"error": "bad drinkStatus value"}), 400
    if (status_input["releaseStatus"] == "released"):
        if (status_input["paymentStatus"] == "notPayed"):
            return  jsonify({"error": "reject! can not release before payment"}), 409
        if (status_input["drinkStatus"] == "pending"):
            return  jsonify({"error": "reject! can not release before prepared"}), 409
    # write into database
    database[order]["status"]["paymentStatus"] = status_input["paymentStatus"]
    database[order]["status"]["releaseStatus"] = status_input["releaseStatus"]
    database[order]["status"]["drinkStatus"] = status_input["drinkStatus"]
    # form return format
    order_detail = formOrderDetail(order)
    return jsonify(order_detail), 200


# payment functions
@app.route("/payment/<order>", methods=['POST'])
def create_payment(order):
    # get the input
    payment_input = json.loads(request.data)
    order = int(order)
    # check the input
    if not existOrderID(order):
        return jsonify({"error": "order does not exists"}), 404
    if not set(("type", "amount")).issubset(payment_input.keys()):
        return jsonify({"error": "missing attributes"}), 400
    if (payment_input["type"] == "cash"):
        pass
    elif (payment_input["type"] == "card"):
        if not set(("cardNumber", "name", \
                "expireDate")).issubset(payment_input.keys()):
            return jsonify({"error": "missing attributes"}), 400 
    else:
        return jsonify({"error": "bad payment type"}), 400
    if not isValidMoney(payment_input["amount"]):
        return jsonify({"error": "cash must be an non-negative float"}), 400
    # check the logic
    if (database[order]["status"]["paymentStatus"] == "hasPayed"):
        return jsonify({"error": "rejected, payment alread exists"}), 409
    # write into database
    database[order]["payment"]["type"] = payment_input["type"]
    database[order]["payment"]["amount"] = float(payment_input["amount"])
    if (payment_input["type"] == "card"):
        database[order]["payment"]["cardNumber"] = payment_input["cardNumber"]
        database[order]["payment"]["name"] = payment_input["name"]
        database[order]["payment"]["expireDate"] = payment_input["expireDate"]
    database[order]["status"]["paymentStatus"] = "hasPayed"
    return jsonify(database[order]), 201

# payment functions
@app.route("/payment/<order>", methods=['GET'])
def read_payment(order):
    order = int(order)
    if not existOrderID(order):
        return jsonify({"error": "order does not exists"}), 404
    return jsonify(database[order]), 200


# helper functions
def formOrderDetail(order):
    order_detail = copy.deepcopy(database[order])
    order_detail["links"] = [{
        "rel": "self",
        "href": "http://127.0.0.1:5000/order/" + str(order)
        }, {
        "rel": "payment",
        "href": "http://127.0.0.1:5000/payment/" + str(order)
        }]
    del order_detail["payment"]
    return order_detail


# debug functions
@app.route("/debug/read_database", methods=['GET'])
def read_database():
    print(database)
    return jsonify(database), 200


@app.route("/debug/update_database", methods=['PUT'])
def update_database():
    order_input = json.loads(request.data)
    for key in order_input.keys():
        database[int(key)] = order_input[key]
    return jsonify(database), 200


if __name__ == "__main__":
    app.run()
