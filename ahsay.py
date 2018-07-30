#--*-- coding: utf-8 --*--

__author__ = 'Mike.GONG'


from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
import tkinter as tk
import tkinter
import tkinter.messagebox

import os
import xml.etree.ElementTree as ET

import json
import urllib
import http.client, urllib.parse

import csv

import time

def main():

##########################################################
#######################解析函数############################
#####################返回一个数组list######################
##########################################################

	def my_obj_pairs_hook(lst):
		result={}
		count={}
		for key,val in lst:
			if key in count: count[key] = 1+count[key]
			else: count[key] = 1
			if key in result:
				if count[key]>2:
					result[key].append(val)
				else:
					result[key]=[result[key],val]
			else:
				result[key]=val
		return result



##########################################################
####################通过窗口获得路径########################
##########################################################

#	def outputPath():
#		path_ = askdirectory()
#		return path_

	def inputXml():
		path_ = askopenfilename()
		path.set(path_)


##########################################################
###################发送API功能（POST）######################
##########################################################

	def sendGetUser(**kargs):
		#print(kargs)
		test_data = json.dumps(kargs)
		#test_data_url_encode = urllib.parse.urlencode(test_data)
		request_url = 'http://'+serverAd.get()+'/obs/api/json/2/GetUser.do'
		conn = http.client.HTTPConnection(serverAd.get())
		header = {"content-type": "text/plain;charset=UTF-8"}
		conn.request(method="POST", url=request_url, headers=header, body=test_data)
		response = conn.getresponse()
		#print(response.status)
		#print(response.reason)
		res = response.read()
		#print(res)
		resp = json.loads(res, object_pairs_hook=my_obj_pairs_hook)
		#print(resp)
		return resp





##########################################################
#####################按键触发功能###########################
##########################################################

	def testFromServer():
		#为了减少出错率，将output的路径设为这个tool的路径
		#outputpath = outputPath()
		outputpath = os.getcwd()
		print(os.getcwd())
		#这里考虑要不要让用户自定义名字
		#到时候的csv文件写到这个位置
		specificOutputpath = outputpath+'/getUser.csv'
		#print(specificOutputpath)
		#print('************this 79************')
		#创造或写入csv,记录所有user
		# csv肯定不能满足这个功能
		with open(specificOutputpath, 'w') as csvfile:
			filewriter = csv.writer(csvfile)
			filewriter.writerow(['User Name', 'Enabled', 'Quota', 'DestinationName', 'DestinationKey'])
		#写个玩意让user确定自己的路径是正确的
		#print(path.get())
		#记录用户输入的账号密码
		name = usrName.get()
		pwd = usrPwd.get()


		#打开的xml的路径
		tree = ET.parse(path.get())
		root = tree.getroot()
		#print(root.tag)
		#print(root.attrib)
		for users in root:
			#print(users.tag, users.attrib)
			#确认进入了对的用户层了
			d = dict(SysUser=usrName.get(),SysPwd=usrPwd.get())
			for Values in users:
				#print(Values.tag, Values.attrib)
				#确认进入了Value，只用在 name='name'和name='owner'和name='quota'找到data就好了
				if Values.attrib['name']=='name':
					d['LoginName'] = Values.attrib['data']
				if Values.attrib['name']=='quota':
					d['quota'] = Values.attrib['data']
				if Values.attrib['name']=='owner':
					d['owner'] = Values.attrib['data']


			# with open(specificOutputpath, 'w') as csvfile:
			# 	filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			# 	filewriter.writerow(['User Name'])
			# 	filewriter.writerow(d['LoginName'])

			#用send func
			needWrite = sendGetUser(**d)
			#print(isinstance(needWrite['Data'], dict))



			#用一个filter来决定打印出来玩的user有哪些

			#if not usrDes, print all

			#if usrDes is not empty
			#if regex can find the usrDes
			#then print
			if usrDes.get() =='':
				print(len(needWrite['Data']['QuotaList']))
				print(d['LoginName'])
				print(needWrite['Data']['QuotaList'])
				for i in range(len(needWrite['Data']['QuotaList'])):
					with open(specificOutputpath, 'a') as csvfile:
						filewriter = csv.writer(csvfile)
						filewriter.writerow([d['LoginName'],needWrite['Data']['QuotaList'][i]['Enabled'], needWrite['Data']['QuotaList'][i]['Quota'], needWrite['Data']['QuotaList'][i]['DestinationName'], needWrite['Data']['QuotaList'][i]['DestinationKey']])

				with open(specificOutputpath, 'a') as csvfile:
					filewriter = csv.writer(csvfile)
					filewriter.writerow('')
					filewriter.writerow('')
					filewriter.writerow('')


				print('\n\n\n\n\n\n')				
			else:
				hasDesKey = False
				desKey = usrDes.get()
				#needWrite['Data']['QuotaList'] is a list type structure
				for qtls in needWrite['Data']['QuotaList']:
					if desKey == qtls['DestinationKey']:
						hasDesKey = True
						break

				if hasDesKey:
					#根据长度来打表
					print(len(needWrite['Data']['QuotaList']))
					print(d['LoginName'])
					print(needWrite['Data']['QuotaList'])
					for one in needWrite['Data']['QuotaList']:
						if one['DestinationKey'] == desKey:
							#改变这个里面的数据
							one['Enabled'] = True
							one['Quota'] = d['quota']
							print(one['Enabled'])
							print(one['Quota'])

					print(needWrite['Data']['QuotaList'])
					for i in range(len(needWrite['Data']['QuotaList'])):
						if needWrite['Data']['QuotaList'][i]['DestinationKey'] == desKey:
							with open(specificOutputpath, 'a') as csvfile:
								filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
								filewriter.writerow([d['LoginName'], True, d['quota'], needWrite['Data']['QuotaList'][i]['DestinationName'], needWrite['Data']['QuotaList'][i]['DestinationKey']])
						else:
							with open(specificOutputpath, 'a') as csvfile:
								filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
								filewriter.writerow([d['LoginName'],needWrite['Data']['QuotaList'][i]['Enabled'], needWrite['Data']['QuotaList'][i]['Quota'], needWrite['Data']['QuotaList'][i]['DestinationName'], needWrite['Data']['QuotaList'][i]['DestinationKey']])

					with open(specificOutputpath, 'a') as csvfile:
						filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
						filewriter.writerow('')
						filewriter.writerow('')
						filewriter.writerow('')


					print('\n\n\n\n\n\n')						


			#把得到的玩意写到csv里
			#就是print的部分
			#加一行空行
			#搞定






#########################################################
##################全部重新改，直接返回ok, wrong就行了########
#########################################################
	def sendUpdateUser(**kargs):
		print(kargs)
		test_data = json.dumps(kargs)
		request_url = 'http://'+serverAd.get()+'/obs/api/json/2/UpdateUser.do'
		conn = http.client.HTTPConnection(serverAd.get())
		header = {"content-type":"text/plain; charset=UTF-8"}
		conn.request(method="POST", url=request_url, headers=header, body=test_data)
		response = conn.getresponse()
		print(response.status)
		print(response.reason)
		res = response.read()
		#print(res)
		resp = json.loads(res, object_pairs_hook=my_obj_pairs_hook)
		#print(resp)
		#该值就是 一个简单的status
		return resp




	def submitToServer():

		#对于每一个账户的update要停1s，否则服务器接口端可能会崩溃
		outputpath = os.getcwd()
		specificOutputpath = outputpath+'/getUser.csv'
		with open(specificOutputpath, 'r') as csv_file:
			reader = csv.reader(csv_file)
			for row in reader:
				#如果是正确的，就建一个dict，可以收到
				if row == []:
					continue
				if row[1] == 'True' or row[1] =='False':
					print(row)
					#d = dict()
					lgnm = row[0]
					tf = row[1]
					qt = row[2]
					dk = row[4]
					qld = dict(Enabled=tf, Quota=qt, DestinationKey=dk)
					qldl = [qld]
					su = usrName.get()
					sp = usrPwd.get()
					d = dict(SysUser=su, SysPwd=sp, LoginName=lgnm, QuotaList=qldl)
					upStatus = sendUpdateUser(**d)
					print(upStatus)
					if upStatus['Status'] != 'OK':
						tkinter.messagebox.showerror('Error',upStatus['Message'])
						print(upStatus)
					else:
						time.sleep(1)
		tkinter.messagebox.showinfo('Status','Success')

			# for line in csv_file:
			# 	print(line)
				#读取正确，只要交上去就行了，耶
			#if is json info， add SysUser, SysPwd, then it works


		# outputpath = os.getcwd()
		# specificOutputpath = outputpath+'/getUser.csv'
		# d = 打开从这个路径得到的文件，还在纠结做成什么类型什么格式
		#假设可以弄成刚刚得到的这种格式
		#[{'Enabled': True, 'Quota': 52428800, 'DestinationName': 'GoogleDrive-1', 'DestinationKey': '-1532572601525'}, {'Enabled': True, 'Quota': 53687091200, 'DestinationName': 'AhsayCBS', 'DestinationKey': 'OBS'}, {'Enabled': False, 'Quota': 0, 'DestinationName': 'Local-1', 'DestinationKey': '-1532572537100'}]



		# #打开用户刚刚得到的csv文件
		# # the file is like: usr_name,owner(get from users.xml), QuotaList1, QuotaList2, Quotalist3...
		# # 
		# theSubmitDict
		# specificOutputpath = outputpath+'/GetUser.do.csv'
		# #应该是对上一个getUser的反向操作
		# #应该是对上一个getUser的反向操作
		# #应该是对上一个getUser的反向操作
		# usrList = []
		# #用一个list存所有usr的信息，每一个都是一个dict
		# d = dict()

		# with open(specificOutputpath, 'r') as csv_file:
		# 	#csv_reader = csv.reader(csv_file)
		# 	#最上面一行是field name
		# 	csv_reader = csv.DictReader(csv_file)
		# 	#或者 fieldnames = []
		# 	# csv_writer = csv.DictWriter(newfile, filednames=fieldnames, delimiter = ',')
		# 	#这样就可以写出按需求的csv 
		# 	for line in csv_reader:
		# 		# 找到合适的行，存进来
		# 		#做成dict

		# #把原来csv读出来的str list 转化为json 
		# #不用转化，转化的步骤是在上传的时候完成的
		# #所以直接上传d就行了



		# ##获取到正确的json结构后上传上去
		# ##获取到正确的json结构后上传上去
		# ##获取到正确的json结构后上传上去

		# # print(specificOutputpath)
		# # print('************this 227************')
		# #创造或写入csv

		# # #写个玩意确定自己的路径是正确的
		# # print(path.get())
		# # #记录用户输入的账号密码
		# # name = usrName.get()
		# # pwd = usrPwd.get()
		# # #ownr = 
		# # tree = ET.parse(path.get())
		# # root = tree.getroot()
		# # print(root.tag)
		# # print(root.attrib)
		# # for users in root:
		# # 	#print(users.tag, users.attrib)
		# # 	#确认进入了对的用户层了
		# # 	d = dict(SysUser=usrName.get(),SysPwd=usrPwd.get())
		# # 	for Values in users:

		# # 		#print(Values.tag, Values.attrib)
		# # 		#确认进入了Value，只用在 name='name'和name='owner'和name='quota'找到data就好了
		# # 		if Values.attrib['name']=='name':
		# # 			d['LoginName'] = Values.attrib['data']
		# # 		if Values.attrib['name']=='quota':
		# # 			d['quota'] = Values.attrib['data']
		# # 		if Values.attrib['name']=='owner':
		# # 			d['owner'] = Values.attrib['data']

		# # 	print(d)
		# # 	print('************** line 163 ****************')

		# get_result = sendUpdateUser(**d)
		# #如果成功，打印OK。
		# #如果失败，打印重复之前的getUser的操作
		# print (get_result)
		# #直接判断status就行了
		# # {"Status":"OK"}
		# if get_result['Status'] == 'OK':








##########################################################
##############按键界面的组成以及各个object###################
##########################################################



	window = Tk()
	window.title('Update User')
	window.geometry('400x400')

	usrName = StringVar()
	SysUsertag = tk.Label(window, text='System User:')
	SysUsertag.pack()
	SysUser = tk.Entry(window, textvariable=usrName)
	SysUser.pack()

	usrPwd = StringVar()
	SysPwdtag = tk.Label(window, text='System User Password:')
	SysPwdtag.pack()
	SysPwd = tk.Entry(window, textvariable=usrPwd, show='*')
	SysPwd.pack()

	serverAd = StringVar()
	serverAdtag = tk.Label(window, text='Server IP Address:')
	serverAdtag.pack()
	serverAddress = tk.Entry(window, textvariable=serverAd)
	serverAddress.pack()


	#这个同时可以作为一个filter，只打印出相关的user的信息 
	usrDes = StringVar()
	#设置一个空值初始化它
	usrDes.set('')
	SysDestag = tk.Label(window, text='Destination Key:')
	SysDestag.pack()
	SysDes = tk.Entry(window, textvariable=usrDes)
	SysDes.pack()

	path = StringVar()
	chooseXml = tk.Button(window, text='choose users.xml', width=15, height=2, command=inputXml)
	chooseXml.pack()
	xmlPath = tk.Entry(window, textvariable=path)
	xmlPath.pack()

	test = tk.Button(window, text='Configuration', width=15, height=2, command=testFromServer)
	test.pack()

	submit = tk.Button(window, text='submit', width=15, height=2, command=submitToServer)
	submit.pack()



	window.mainloop()


##########################################################
#####################执行函数##############################
##########################################################


main()
