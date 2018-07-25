#--*-- coding: utf-8 --*--

__author__ = 'Mike.GONG'


from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
import tkinter as tk

import os
import xml.etree.ElementTree as ET

import json
import urllib
import http.client, urllib.parse

import csv

def main():

##########################################################
#######################解析函数############################
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

	def outputPath():
		path_ = askdirectory()
		return path_

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

	def sendUpdateUser(**kargs):
		print(kargs)
		test_data = json.dumps(kargs)
		request_url = 'http://'+serverAd.get()+'/obs/api/json/2/UpdateUser.do'
		header = {"content-type":"text/plain; charset=UTF-8"}
		conn.request(method="POST", url=request_url, headers=header, body=test_data)
		response = conn.getresponse()
		print(response.status)
		print(response.reason)
		res = response.read()
		#print(res)
		resp = json.loads(res, object_pairs_hook=my_obj_pairs_hook)
		#print(resp)
		return resp


##########################################################
#####################按键触发功能###########################
##########################################################

	def testFromServer():
		outputpath = outputPath()
		#这里考虑要不要让用户自定义名字
		specificOutputpath = outputpath+'/getUser.csv'
		#print(specificOutputpath)
		#print('************this 79************')
		#创造或写入csv,记录所有user
		# csv肯定不能满足这个功能
		# with open(specificOutputpath, 'w') as csvfile:
		# 	filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		# 	filewriter.writerow(['User Name','Quota','Destination Name'])
		#写个玩意让user确定自己的路径是正确的
		#print(path.get())
		#记录用户输入的账号密码
		name = usrName.get()
		pwd = usrPwd.get()

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


			with open(specificOutputpath, 'w') as csvfile:
				filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
				filewriter.writerow(['User Name'])
				filewriter.writerow(d['LoginName'])

			#用send func
			needWrite = sendGetUser(**d)
			#print(isinstance(needWrite['Data'], dict))
			print(d['LoginName'])
			print(needWrite['Data']['QuotaList'])
			print('\n\n\n\n\n\n')
			#对每一个用户进行写入即可
			with open(specificOutputpath, 'w') as csvfile:
				filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
				filewriter.writerow(['Quota', 'Destination Key'])


			#得到单个用户所有信息，写就行了，
			with open(specificOutputpath, 'w') as csvfile:
				filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
				for i in needWrite['Data']['QuotaList']:
					filewriter.writerow([i['Quota'], i['DestinationKey']])


	def submitToServer():

		outputpath = outputPath()
		specificOutputpath = outputpath+'/UpdateResult.csv'
		print(specificOutputpath)
		print('************this 127************')
		#创造或写入csv

		#写个玩意让user确定自己的路径是正确的
		print(path.get())
		#记录用户输入的账号密码
		name = usrName.get()
		pwd = usrPwd.get()

		tree = ET.parse(path.get())
		root = tree.getroot()
		print(root.tag)
		print(root.attrib)
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

			print(d)
			print('************** line 163 ****************')














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

	usrDes = StringVar()
	SysDestag = tk.Label(window, text='Destination Key:')
	SysDestag.pack()
	SysDes = tk.Entry(window, textvariable=usrDes)
	SysDes.pack()

	path = StringVar()
	chooseXml = tk.Button(window, text='choose users.xml', width=15, height=2, command=inputXml)
	chooseXml.pack()
	xmlPath = tk.Entry(window, textvariable=path)
	xmlPath.pack()

	test = tk.Button(window, text='test', width=15, height=2, command=testFromServer)
	test.pack()

	submit = tk.Button(window, text='submit', width=15, height=2, command=submitToServer)
	submit.pack()



	window.mainloop()


##########################################################
#####################执行函数##############################
##########################################################


main()
