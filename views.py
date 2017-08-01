# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response

import json
import time

from django.core import serializers

from web3 import Web3, KeepAliveRPCProvider, IPCProvider
web3 = Web3(KeepAliveRPCProvider(host='localhost', port='8545'))

# database
from ethereum.models import Order, Room

# terminal color
color_front = '\x1b[7;30;42m'
color_end = '\x1b[0m'
def print_color(text):
	print(color_front + text + color_end)

def get(request,title):

	if title == 'peers':	
		ouptput = json.dumps(web3.admin.peers, sort_keys=True, indent=4)
		return HttpResponse(ouptput, content_type="application/json")

	if title == 'nodeinfo':	
		output = json.dumps(web3.admin.nodeInfo, sort_keys=True, indent=4)
		return HttpResponse(output, content_type="application/json")	

	if title == 'node':	
		output = json.dumps(web3.version.node, sort_keys=True, indent=4)
		return HttpResponse(output, content_type="application/json")		

	if title == 'network':	
		output = json.dumps(web3.version.network, sort_keys=True, indent=4)
		return HttpResponse(output, content_type="application/json")		

	if title == 'accounts':	
		output = json.dumps(web3.personal.listAccounts, sort_keys=True, indent=4)
		return HttpResponse(output, content_type="application/json")

	if title == 'block':
		number = int(request.GET['number'])
		output = json.dumps(web3.eth.getBlock(int(number)), sort_keys=True, indent=4)
		return HttpResponse(output, content_type="application/json")					

def booking_contract(request,function):
	abi = [ { "constant": "false", "inputs": [ { "name": "key", "type": "bytes" }, { "name": "user_id", "type": "bytes" }, { "name": "date", "type": "bytes" }, { "name": "room_type", "type": "uint256" }, { "name": "order_id", "type": "bytes" } ], "name": "new_order", "outputs": [], "payable": "false", "type": "function" }, { "constant": "true", "inputs": [], "name": "owner_2", "outputs": [ { "name": "", "type": "address" } ], "payable": "false", "type": "function" }, { "constant": "false", "inputs": [ { "name": "old_key", "type": "bytes" }, { "name": "new_key", "type": "bytes" }, { "name": "user_id", "type": "bytes" }, { "name": "date", "type": "bytes" }, { "name": "room_type", "type": "uint256" }, { "name": "order_id", "type": "bytes" } ], "name": "update_order", "outputs": [], "payable": "false", "type": "function" }, { "constant": "false", "inputs": [ { "name": "key", "type": "bytes" } ], "name": "room_detail", "outputs": [ { "name": "", "type": "bytes" }, { "name": "", "type": "uint256" }, { "name": "", "type": "uint256" } ], "payable": "false", "type": "function" }, { "constant": "false", "inputs": [ { "name": "key", "type": "bytes" }, { "name": "total", "type": "uint256" } ], "name": "new_room", "outputs": [], "payable": "false", "type": "function" }, { "constant": "false", "inputs": [ { "name": "key", "type": "bytes" } ], "name": "delete_room", "outputs": [], "payable": "false", "type": "function" }, { "constant": "false", "inputs": [ { "name": "order_id", "type": "bytes" }, { "name": "key", "type": "bytes" } ], "name": "delete_order", "outputs": [], "payable": "false", "type": "function" }, { "constant": "true", "inputs": [], "name": "owner", "outputs": [ { "name": "", "type": "address" } ], "payable": "false", "type": "function" }, { "constant": "false", "inputs": [ { "name": "key", "type": "bytes" } ], "name": "check", "outputs": [ { "name": "", "type": "bool" } ], "payable": "false", "type": "function" }, { "constant": "false", "inputs": [ { "name": "key", "type": "bytes" }, { "name": "total", "type": "uint256" }, { "name": "soldout", "type": "uint256" } ], "name": "edit_room", "outputs": [], "payable": "false", "type": "function" }, { "constant": "false", "inputs": [ { "name": "order_id", "type": "bytes" } ], "name": "order_detail", "outputs": [ { "name": "", "type": "bytes" }, { "name": "", "type": "bytes" }, { "name": "", "type": "bytes" }, { "name": "", "type": "uint256" } ], "payable": "false", "type": "function" }, { "constant": "false", "inputs": [ { "name": "newOwner", "type": "address" } ], "name": "transferOwnership", "outputs": [], "payable": "false", "type": "function" }, { "constant": "false", "inputs": [ { "name": "newOwner", "type": "address" } ], "name": "addOwnership", "outputs": [], "payable": "false", "type": "function" }, { "inputs": [], "payable": "false", "type": "constructor" }, { "anonymous": "false", "inputs": [ { "indexed": "false", "name": "key", "type": "bytes" }, { "indexed": "false", "name": "user_id", "type": "bytes" }, { "indexed": "false", "name": "order_id", "type": "bytes" }, { "indexed": "false", "name": "check", "type": "bool" } ], "name": "new_order_event", "type": "event" }, { "anonymous": "false", "inputs": [ { "indexed": "false", "name": "new_key", "type": "bytes" }, { "indexed": "false", "name": "user_id", "type": "bytes" }, { "indexed": "false", "name": "order_id", "type": "bytes" }, { "indexed": "false", "name": "check", "type": "bool" } ], "name": "update_order_event", "type": "event" } ]
	address = '0xAE97B88aa2188bC37ED01DF2e61BC7AE73526038'
	myContract = web3.eth.contract(abi=abi,address=address)

	if function == 'new_order':
		user_id = request.POST['user_id']
		date = request.POST['date']
		room_type = int(request.POST['room_type'])
		
		key = date + '_' + str(room_type)
		print_color('key: ' + key)
		order_id = key + '_' + user_id + '_' + time.strftime("%H:%M:%S")
		print_color('order_id: ' + order_id)

		if myContract.call().check(key) == True: #check回傳true表示可以預約 post可以執行
			web3.personal.unlockAccount(web3.eth.coinbase, 'internintern')

			# 訂單寫入區塊鏈
			output = myContract.transact({'from': web3.eth.coinbase}).new_order(key, user_id, date, room_type, order_id)
			print_color(output)

			# 訂單寫入ＤＢ
			order = Order.objects.create(key=key, user_id=user_id, date=date, room_type=room_type, order_id=order_id)
			print_color('Order: ' + order_id + ' is NEWED!')
			room = Room.objects.get(key=key)
			room.soldout += 1
			room.save()
			print_color('Room: ' + key + ' soldout +1!')

			result = json.dumps({'transaction': output}, sort_keys=True, indent=4)
			return HttpResponse(result, content_type="application/json")
		else:	#check如果回傳false代表已經exist有人預約了 不行
			result = json.dumps({'transaction': 'unavailable'}, sort_keys=True, indent=4)
			return HttpResponse(result, content_type="application/json")


	if function == 'update_order':
		order_id = request.POST['order_id']
		old_key = order_id.split('_')[0] + '_' + order_id.split('_')[1]	#長字串.split('分割的方式')[第幾組]

		user_id = request.POST['user_id']
		date = request.POST['date']
		room_type = int(request.POST['room_type'])
		
		new_key = date + '_' + str(room_type)

		if myContract.call().check(new_key) == True: 
			web3.personal.unlockAccount(web3.eth.coinbase, 'internintern')

			# 訂單寫入區塊鏈
			output = myContract.transact({'from': web3.eth.coinbase}).update_order(old_key, new_key, user_id, date, room_type, order_id)
			print_color(output)

			# 訂單寫入ＤＢ
			order = Order.objects.get(order_id=order_id)
			order.key = new_key
			order.user_id = user_id
			order.date = date
			order.room_type = room_type
			print_color('user_id: ' + user_id + '   new key: ' + new_key)
			order.save()
			print_color('Order: ' + order_id + ' is UPDATED!')

			room_old = Room.objects.get(key=old_key)
			room_old.soldout -= 1
			room_old.save()

			room_new = Room.objects.get(key=new_key)
			room_new.soldout += 1
			room_new.save()
			print_color('SOLDOUT: old room ' + old_key + ' -1   new room ' + new_key + ' +1')

			result = json.dumps({'transaction': output}, sort_keys=True, indent=4)
			return HttpResponse(result, content_type="application/json")
		else:
			result = json.dumps({'transaction': 'unavailable'}, sort_keys=True, indent=4)
			return HttpResponse(result, content_type="application/json")


	if function == 'delete_order':
		order_id = request.POST['order_id']
		key = request.POST['key']

		if Order.objects.filter(order_id=order_id).exists():
			web3.personal.unlockAccount(web3.eth.coinbase, 'internintern')

			# 訂單寫入區塊鏈
			output = myContract.transact({'from': web3.eth.coinbase}).delete_order(order_id, key)
			print_color(output)

			# ＤＢ
			Order.objects.filter(order_id=order_id).delete()
			print_color(order_id + ' is deleted!')

			room = Room.objects.get(key=key)
			room.soldout -= 1
			room.save()
			print_color('Room: ' + key + ' soldout -1!')

			result = json.dumps({'transaction': output}, sort_keys=True, indent=4)
			return HttpResponse(result, content_type="application/json")

		else:
			result = json.dumps({'transaction': 'order do not exist'}, sort_keys=True, indent=4)
			return HttpResponse(result, content_type="application/json")


	if function == 'order_detail':
		result = serializers.serialize('json', Order.objects.all())
		print_color('return all objects of Order')
		return HttpResponse(result, content_type="application/json")

	if function == 'room_detail':
		result = serializers.serialize('json', Room.objects.all())
		print_color('return all objects of Room')
		return HttpResponse(result, content_type="application/json")

	if function == 'new_room':
		key = request.POST['key']
		total = int(request.POST['total'])
		print_color('total: ' + str(total) + '   soldout: 0')

		web3.personal.unlockAccount(web3.eth.coinbase, 'internintern')

		# 訂單寫入區塊鏈
		output = myContract.transact({'from': web3.eth.coinbase}).new_room(key, total)
		print_color(output)

		# 訂單寫入ＤＢ
		order = Room.objects.create(key=key, total=total, soldout=0)
		print_color('Room ' + key + ' is NEWED!')

		result = json.dumps({'transaction': output}, sort_keys=True, indent=4)
		return HttpResponse(result, content_type="application/json")

	if function == 'edit_room':
		key = request.POST['key']
		total = int(request.POST['total'])
		soldout = int(request.POST['soldout'])
		print_color('total: ' + str(total)+ '   soldout: ' + str(soldout))

		web3.personal.unlockAccount(web3.eth.coinbase, 'internintern')

		# 訂單寫入區塊鏈
		output = myContract.transact({'from': web3.eth.coinbase}).edit_room(key, total, soldout)
		print_color(output)

		# 訂單寫入ＤＢ
		order = Room.objects.get(key=key)
		order.total = total
		order.soldout = soldout
		order.save()
		print_color('Room ' + key + ' is UPDATED!')

		result = json.dumps({'transaction': output}, sort_keys=True, indent=4)
		return HttpResponse(result, content_type="application/json")

	if function == 'delete_room':
		key = request.POST['key']

		if Room.objects.filter(key=key).exists():
			web3.personal.unlockAccount(web3.eth.coinbase, 'internintern')

			# 訂單寫入區塊鏈
			output = myContract.transact({'from': web3.eth.coinbase}).delete_room(key)
			print_color(output)

			# ＤＢ
			Room.objects.filter(key=key).delete()
			print_color('Room ' + key + ' is DELETED!')

			result = json.dumps({'transaction': output}, sort_keys=True, indent=4)
			return HttpResponse(result, content_type="application/json")

		else:
			result = json.dumps({'transaction': 'key do not exist'}, sort_keys=True, indent=4)
			return HttpResponse(result, content_type="application/json")
		

	# if function == 'order_id':
	# 	#總共有幾筆資料
	# 	size = myContract.call().order_id_table_size()
	# 	print("size" + str(size))

	# 	for i in range(0,size):
	# 		output = myContract.call().order_id_table(i)
	# 		print(i)
	# 		if 'orders' in locals(): #如果不是第一筆 可以直接append
	# 			orders.append(output)
	# 		else:	#如果是第一筆
	# 			orders = []
	# 			orders.append(output)

	# 	result = json.dumps(orders, sort_keys=True, indent=4)
	# 	print(result) 
	# 	return HttpResponse(result, content_type="application/json")



