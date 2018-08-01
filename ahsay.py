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

	back_up_user_information = None 
	#结构如下： {'LoginName': 'test0723', 'QuotaList': {'Enabled': True, 'Quota': 91200, 'DestinationName': 'AhsayCBS', 'DestinationKey': 'OBS'}}

	selected_destination_dict = None
	#一个dict, key为destination, value为0,1，不过value是IntVar()要用get()来获得

	user_name_and_quota_from_xml = None
	#一个dict, key为destination, value为quota

	have_list = False
	have_check = False


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

	def sendListUsers():
		sysUser = usrName.get()
		sysPwd = usrPwd.get()
		d = dict(SysUser=sysUser, SysPwd=sysPwd)
		test_data = json.dumps(d)
		request_url = 'http://'+serverAd.get()+'/obs/api/json/2/ListUsers.do'
		conn = http.client.HTTPConnection(serverAd.get())
		header = {'content-type':'text/plain;charset=UTF-8'}
		conn.request(method='POST', url=request_url, headers=header, body=test_data)
		response = conn.getresponse()
		res = response.read()
		resp = json.loads(res, object_pairs_hook=my_obj_pairs_hook)
		if resp['Status']=='OK':
			return resp
		else:
			return -1


##########################################################
####################listDest 辅助方程######################
##########################################################

	def createPage(*arg):
		chosen = dict() #记录被选中的有哪些
		list_page = Toplevel(window)
		Label(list_page,text='Holy').pack()
		print(len(arg))
		for i in range(len(arg)):
			chosen[arg[i][1]]=IntVar()
			tmp_var = StringVar()
			tmp_str = arg[i][0].ljust(20)+arg[i][1].ljust(20)
			tmp_var.set(tmp_str)
			print(tmp_var.get())
			chk = Checkbutton(list_page, textvariable=tmp_var, variable=chosen[arg[i][1]], width=60)
			chk.pack()

		Button(list_page, text='confirm', width=15, height=2, command=list_page.destroy).pack()
		list_page.wait_window()
		nonlocal selected_destination_dict
		selected_destination_dict = chosen




##########################################################
#####################按键触发功能###########################
##########################################################

	def listDest():
		#将文件只存在内存中，而不打印出来
		name = usrName.get()
		pwd = usrPwd.get()
		ad = serverAd.get()
		if (name=='' or pwd=='' or ad==''):
			tkinter.messagebox.showinfo('Status','Please fill the UserName, Password and ServerURL')
		#在else中操作
		else:
			the_list = sendListUsers()

			#print(the_list)
			if the_list == -1:
				tkinter.messagebox.showinfo('Status','Please correct the UserName, Password and ServerURL')
			else:
				#先清理出来
				info_list = list()
				for usr in the_list['User']:
					for ql in usr['QuotaList']:
						d = dict(LoginName=usr['LoginName'], QuotaList=ql)
						info_list.append(d)

				nonlocal back_up_user_information
				back_up_user_information = info_list
				#print('back_up_user_information已经变成info_list了')

				des_list = []
				for i in info_list:
					temp_list = [i['QuotaList']['DestinationName'],i['QuotaList']['DestinationKey']]
					if temp_list not in des_list:
						des_list.append(temp_list)
				des_list.sort()
				print(des_list)

				#建一个set并把里面的内容传递到createPage里面去

				createPage(*des_list)
				#得到的是一个value为IntVar()的dict
				nonlocal have_list
				have_list = True

	def testFromServer():
		nonlocal have_list
		if have_list == True:
			output_path = os.getcwd()
			print(os.getcwd())
			specific_output_path = output_path+ '/get_user.csv'
			with open(specific_output_path, 'w') as csvfile:
				filewriter = csv.writer(csvfile)
				filewriter.writerow(['User Name', 'Enabled', 'Quota', 'DestinationName', 'DestinationKey'])


			#打开的xml的路径
			tree = ET.parse(path.get())
			root = tree.getroot()
			#print(root.tag)
			#print(root.attrib)
			d = dict()
			for users in root:
				#print(users.tag, users.attrib)
				#确认进入了对的用户层了
				for Values in users:
					#print(Values.tag, Values.attrib)
					#确认进入了Value，只用在 name='name'和name='owner'和name='quota'找到data就好了
					if Values.attrib['name']=='name':
						usr_name = Values.attrib['data']
					#print(usr_name)
					if Values.attrib['name']=='quota':
						d[usr_name] = Values.attrib['data']
					#print(d[usr_name])

				#print('\n\n\n\n\n\n\n\n\n\n\n')

			nonlocal user_name_and_quota_from_xml
			user_name_and_quota_from_xml = d


			for usr in back_up_user_information:
				#print('进入258')
				if selected_destination_dict[usr['QuotaList']['DestinationKey']].get() == 1:
					usr['QuotaList']['Enabled'] = True
					usr['QuotaList']['Quota'] = user_name_and_quota_from_xml[usr['LoginName']]
					print(usr)
					#基本正确了
					#写成csv即可
					with open(specific_output_path, 'a') as csvfile:
						filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
						filewriter.writerow([usr['LoginName'], usr['QuotaList']['Enabled'], usr['QuotaList']['Quota'], usr['QuotaList']['DestinationName'],usr['QuotaList']['DestinationKey']])
			have_list = False
			nonlocal have_check
			have_check = True
		else:
			tkinter.messagebox.showinfo('Status','Please follow the step and List the Destination first.')


#########################################################
##################全部重新改，直接返回ok, wrong就行了########
#########################################################

	def submitToServer():
		nonlocal have_check
		if have_check == True:
			#对于每一个账户的update要停1s，否则服务器接口端可能会崩溃
			error_exist = False
			outputpath = os.getcwd()
			specificOutputpath = outputpath+'/get_user.csv'
			error_csv_path = outputpath+'/error_accounts.csv'
			with open(specificOutputpath, 'r') as csv_file:
				reader = csv.reader(csv_file)
				for row in reader:
					#如果是正确的，就建一个dict，可以收到
					if row == []:
						continue
					if row[1]=='True' or row[1]=='False' or row[1]=='TRUE' or row[1]=='FALSE':
						print(row)
						#d = dict()
						lgnm = row[0]
						if row[1]=='TRUE':
							row[1] = 'True'
						if row[1]=='FALSE':
							row[1] = 'False'
						tf = row[1]
						qt = row[2]
						dk = row[4]
						qld = dict(Enabled=tf, Quota=qt, DestinationKey=dk)
						qldl=[qld]
						su = usrName.get()
						sp = usrPwd.get()
						d = dict(SysUser=su, SysPwd=sp, LoginName=lgnm, QuotaList=qldl)
						upStatus = sendUpdateUser(**d)
						print(upStatus)
						if upStatus['Status'] != 'OK':
							if error_exist == False:
								error_exist = True
								with open(error_csv_path, 'w') as csv_file:
									filewriter = csv.writer(csv_file)
									filewriter.writerow(['Error'])
									filewriter.writerow([upStatus['Message']])
							else:
								with open(error_csv_path, 'a') as csv_file:
									filewriter = csv.writer(csv_file)
									filewriter.writerow([upStatus['Message']])
						else:
							time.sleep(1)
			if error_exist == False:
				tkinter.messagebox.showinfo('Status','Success')
			else:
				tkinter.messagebox.showinfo('Status','Finish with Error')
			have_check = False
		else:
			tkinter.messagebox.showinfo('Status','Please follow the step and do the check first.')



##########################################################
##############按键界面的组成以及各个object###################
##########################################################



	window = Tk()
	window.title('Update User')
	window.geometry('400x400')

	Label(window, text='Note: Please follow the steps strictly').pack()
	Label(window, text='1.Please input the correct Server System UserName, Password, and ServerURL.').pack()

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

	Label(window, text='2.Please click List Dest, and click the Destinations need to be updated.').pack()
	list_dest = tk.Button(window, text='List Dest', width=15, height=2, command=listDest)
	list_dest.pack()

	Label(window, text='3. Choose the right users.xml file and click check. You can check the update information in the same path as this tool.').pack()
	path = StringVar()
	chooseXml = tk.Button(window, text='choose users.xml', width=15, height=2, command=inputXml)
	chooseXml.pack()
	xmlPath = tk.Entry(window, textvariable=path)
	xmlPath.pack()

	# varClick = IntVar()
	# Radiobutton(window,text='Click to show all Destination Information', variable=varClick,value=1).pack(anchor=W)
	# Radiobutton(window,text='Click to show only selected Destination(Key) Information', variable=varClick,value=2).pack(anchor=W)


	test = tk.Button(window, text='Check', width=15, height=2, command=testFromServer)
	test.pack()
	Label(window, text='4. Click submit and wait until Success or Finish with Error. Error message is in the same path as this tool.').pack()
	submit = tk.Button(window, text='submit', width=15, height=2, command=submitToServer)
	submit.pack()



	window.mainloop()


##########################################################
#####################执行函数##############################
##########################################################


main()
