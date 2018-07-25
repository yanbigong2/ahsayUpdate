from tkinter import *
from tkinter.filedialog import askopenfilename
import tkinter as tk

import os
import xml.etree.ElementTree as ET

import json
import urllib
import http.client, urllib.parse

def main():


	def inputXml():
		path_ = askopenfilename()
		path.set(path_)

	def sendGetUser(**kargs):
		print(kargs)
		test_data = json.dumps(kargs)
		#test_data_url_encode = urllib.parse.urlencode(test_data)
		request_url = 'http://'+serverAd.get()+'/obs/api/json/2/GetUser.do'
		conn = http.client.HTTPConnection(serverAd.get())
		header = {"content-type": "text/plain;charset=UTF-8"}
		conn.request(method="POST", url=request_url, headers=header, body=test_data)
		response = conn.getresponse()
		print(response.status)
		print(response.reason)
		res = response.read()
		#print(res)
		resp = json.loads(res)
		print(resp)



	def sendUpdateUser(**kargs):
		pass

	def testFromServer():
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
					print(Values.attrib['data'])
					d['LoginName'] = Values.attrib['data']
				if Values.attrib['name']=='quota':
					print(Values.attrib['data'])
					d['quota'] = Values.attrib['data']
				if Values.attrib['name']=='owner':
					print(Values.attrib['data'])
					d['owner'] = Values.attrib['data']



			print(d)
			print('************** line 69 ****************')


			#用send func
			sendGetUser(**d)




	def submitToServer():
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
			d = dict()
			for Values in users:

				
				#print(Values.tag, Values.attrib)
				#确认进入了Value，只用在 name='name'和name='owner'和name='quota'找到data就好了
				if Values.attrib['name']=='name':
					print(Values.attrib['data'])
					d['LoginName'] = Values.attrib['data']
				if Values.attrib['name']=='quota':
					print(Values.attrib['data'])
					d['quota'] = Values.attrib['data']
				if Values.attrib['name']=='owner':
					print(Values.attrib['data'])
					d['owner'] = Values.attrib['data']

				#转化成json然后传过去
			jsonObj = json.dumps(d)

				#用send func
			sendUpdateUser(jsonObj)
		


















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



main()


