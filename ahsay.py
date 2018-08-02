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
	error_exist = False


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
		Label(list_page,text='DestinationName',width=20, anchor=E).grid(row=0, column=0, columnspan=4, sticky=W)
		Label(list_page,text='DestinationKey',width=15, anchor=E).grid(row=0, column=5, columnspan=3, sticky=W)
		print(len(arg))
		row_num = 1
		for i in range(len(arg)):
			chosen[arg[i][1]]=IntVar()
			tmp_name = StringVar()
			tmp_key = StringVar()
			tmp_name.set(arg[i][0])
			tmp_key.set(arg[i][1]) 
			chk = Checkbutton(list_page, variable=chosen[arg[i][1]], width=5, anchor=W)
			chk.grid(row=row_num,column=0,sticky=W)
			Label(list_page, textvariable=tmp_name, width=15, anchor=E).grid(row=row_num,column=1, columnspan=3, sticky=W)
			Label(list_page, textvariable=tmp_key, width=20, anchor=E).grid(row=row_num,column=4, columnspan=4, sticky=W)
			row_num = row_num+1

		Button(list_page, text='confirm', width=40, height=2, command=list_page.destroy).grid(row=row_num, columnspan=10)
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
						d = dict(LoginName=usr['LoginName'], QuotaList=ql, Owner=usr['Owner'])
						info_list.append(d)

				nonlocal back_up_user_information
				back_up_user_information = info_list
				#print(info_list)
				#print('back_up_user_information已经变成info_list了')

				des_list = []
				for i in info_list:
					temp_list = [i['QuotaList']['DestinationName'],i['QuotaList']['DestinationKey']]
					if temp_list not in des_list:
						des_list.append(temp_list)
				des_list.sort()
				#print(des_list)

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
				filewriter.writerow(['User Name', 'Owner', 'Enabled', 'Quota', 'DestinationName', 'DestinationKey'])


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
						#d[usr_name] = Values.attrib['data']
						usr_quota = Values.attrib['data']
					#print(d[usr_name])
					if Values.attrib['name']=='owner':
						usr_owner = Values.attrib['data']
				d[usr_name] = [usr_quota, usr_owner]
				#print('\n\n\n\n\n\n\n\n\n\n\n')

			nonlocal user_name_and_quota_from_xml
			user_name_and_quota_from_xml = d

			#print(d)

			for usr in back_up_user_information:
				if selected_destination_dict[usr['QuotaList']['DestinationKey']].get() == 1:
					if usr['Owner'] == user_name_and_quota_from_xml[usr['LoginName']][1]:
						usr['QuotaList']['Enabled'] = True
						usr['QuotaList']['Quota'] = user_name_and_quota_from_xml[usr['LoginName']][0]
						#print(usr)
						#基本正确了
						#写成csv即可
						with open(specific_output_path, 'a') as csvfile:
							filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
							filewriter.writerow([usr['LoginName'], usr['Owner'], usr['QuotaList']['Enabled'], usr['QuotaList']['Quota'], usr['QuotaList']['DestinationName'],usr['QuotaList']['DestinationKey']])
					else:
						with open(specific_output_path, 'a') as csvfile:
							filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
							filewriter.writerow([usr['LoginName'], 'Mismatch', usr['QuotaList']['Enabled'], usr['QuotaList']['Quota'], usr['QuotaList']['DestinationName'],usr['QuotaList']['DestinationKey']])

			have_list = False
			nonlocal have_check
			have_check = True
			tkinter.messagebox.showinfo('Status','Done.')
		else:
			tkinter.messagebox.showinfo('Status','Please follow the step and List the Destination first.')

##########################################################
#############################写一个进度条###################
##########################################################
	def change_schedule(now_schedule, all_schedule):
		canvas.coords(fill_rec,(0,0,0+(now_schedule/all_schedule)*450,30))
		x.set(str(round(now_schedule/all_schedule*100,2))+'%')
		window.update()

#########################################################
##################全部重新改，直接返回ok, wrong就行了########
#########################################################

	def submitToServer():


		nonlocal have_check
		if have_check == True:
			#对于每一个账户的update要停1s，否则服务器接口端可能会崩溃
			nonlocal error_exist

			outputpath = os.getcwd()
			specificOutputpath = outputpath+'/get_user.csv'
			error_csv_path = outputpath+'/error_accounts.csv'
			final_report_path = outputpath+'/final_report.csv'
			with open (final_report_path, 'w') as csv_file:
				filewriter = csv.writer(csv_file)
				filewriter.writerow(['User Name', 'Quota', 'DestinationName', 'Status'])
			#计算总共需要更新的个数
			total_usr = 0
			with open(specificOutputpath, 'r') as csv_file:
				reader = csv.reader(csv_file)
				for row in reader:
					if row[2]=='True' or row[2]=='False' or row[2]=='TRUE' or row[2]=='FALSE':
						total_usr = total_usr+1
			
			cnt_usr = 0
			# with open(specificOutputpath, 'r') as csv_file:
			# 	reader = csv.reader(csv_file)
			# 	for row in reader:
			# 		print(row)
			with open(specificOutputpath, 'r') as csv_file:
				reader = csv.reader(csv_file)
				for row in reader:
					#如果是正确的，就建一个dict，可以收到
					if row == []:
						continue
					if row[2]=='True' or row[2]=='False' or row[2]=='TRUE' or row[2]=='FALSE':
						print(row)
						#d = dict()
						lgnm = row[0]
						if row[2]=='TRUE':
							row[2] = 'True'
						if row[2]=='FALSE':
							row[2] = 'False'
						on = row[1]
						tf = row[2]
						qt = row[3]
						dk = row[5]
						qld = dict(Enabled=tf, Quota=qt, DestinationKey=dk)
						qldl=[qld]
						su = usrName.get()
						sp = usrPwd.get()
						d = dict(SysUser=su, SysPwd=sp, LoginName=lgnm, QuotaList=qldl)

						if on=='Mismatch':
							if error_exist == False:
								error_exist = True
								with open(error_csv_path, 'w') as csv_file:
									filewriter = csv.writer(csv_file)
									filewriter.writerow(['User', 'Error'])
									filewriter.writerow([row[0], 'The owner information in the users.xml mismatchs the owner information get from server.'])
							else:
								with open(error_csv_path, 'a') as csv_file:
									filewriter = csv.writer(csv_file)
									filewriter.writerow([row[0], 'The owner information in the users.xml mismatchs the owner information get from server.'])
							with open(final_report_path, 'a') as csv_file:
								filewriter = csv.writer(csv_file)
								filewriter.writerow([row[0], row[3], row[4], 'The owner information in the users.xml mismatchs the owner information get from server.'])
							cnt_usr = cnt_usr + 1
						else:
							upStatus = sendUpdateUser(**d)
							print(upStatus)
							if upStatus['Status'] != 'OK':
								if error_exist == False:
									error_exist = True
									with open(error_csv_path, 'w') as csv_file:
										filewriter = csv.writer(csv_file)
										filewriter.writerow(['User', 'Error'])
										filewriter.writerow([row[0], upStatus['Message']])
								else:
									with open(error_csv_path, 'a') as csv_file:
										filewriter = csv.writer(csv_file)
										filewriter.writerow([row[0], upStatus['Message']])
								with open(final_report_path, 'a') as csv_file:
									filewriter = csv.writer(csv_file)
									filewriter.writerow([row[0], row[3], row[4], upStatus['Message']])
							else:
								with open(final_report_path, 'a') as csv_file:
									filewriter = csv.writer(csv_file)
									filewriter.writerow([row[0], row[3], row[4], 'OK'])
								time.sleep(0.5)
							cnt_usr = cnt_usr + 1
							change_schedule(cnt_usr,total_usr)

			time.sleep(2)
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
	window.geometry('600x450')

	Label(window, text='Note: Please follow the steps strictly').grid(row=0, columnspan=2, sticky=W)
	Label(window, text='1.Please input the correct Server System\API UserName, Password, and ServerURL.').grid(row=1, columnspan=2, sticky=W)

	usrName = StringVar()
	SysUsertag = tk.Label(window, text='System User:', width=20, anchor=E)
	SysUsertag.grid(row=2,column=0, sticky=W)
	SysUser = tk.Entry(window, textvariable=usrName, width=30)
	SysUser.grid(row=2,column=1)

	usrPwd = StringVar()
	SysPwdtag = tk.Label(window, text='System User Password:', width=20, anchor=E)
	SysPwdtag.grid(row=3,column=0,sticky=W)
	SysPwd = tk.Entry(window, textvariable=usrPwd, show='*', width=30)
	SysPwd.grid(row=3,column=1)

	serverAd = StringVar()
	serverAdtag = tk.Label(window, text='Server IP Address:', width=20, anchor=E)
	serverAdtag.grid(row=4,column=0,sticky=W)
	serverAddress = tk.Entry(window, textvariable=serverAd, width=30)
	serverAddress.grid(row=4,column=1)

	Label(window, text='2.Please click List Dest, and click the Destinations need to be updated.').grid(row=5, columnspan=2, sticky=W)
	list_dest = tk.Button(window, text='List Dest', width=50, height=2, command=listDest)
	list_dest.grid(row=6, columnspan=2)

	Label(window, text='3. Choose the right users.xml file and click check.\n    You can check the update informationin get_users.csv in the same path as this tool.', justify=LEFT).grid(row=7, columnspan=2, sticky=W)
	path = StringVar()
	chooseXml = tk.Button(window, text='choose users.xml', width=25, height=2, command=inputXml)
	chooseXml.grid(row=8, column=1, sticky=W)
	xmlPath = tk.Entry(window, textvariable=path, width=30)
	xmlPath.grid(row=8, column=0)

	test = tk.Button(window, text='Check', width=50, height=2, command=testFromServer)
	test.grid(row=9, columnspan=2)


	Label(window, text='4. Click submit and wait until Success or Finish with Error.\n   You will get two csv files in the same path as this tool.\n   final_report for all updated users information\n   error_accounts if there exists error.', justify=LEFT).grid(row=10, columnspan=5, sticky=W)
	submit = tk.Button(window, text='submit', width=50, height=2, command=submitToServer)
	submit.grid(row=13, columnspan=2)
	submit_run_time = StringVar()


	#做一个进度栏
	x = StringVar()

	canvas = Canvas(window, width=450, height=30, bg='white')
	canvas.grid(row=14, columnspan=5)
	out_rec = canvas.create_rectangle(0,0,450,30, outline='', width=0)
	fill_rec = canvas.create_rectangle(0,0,0,30, outline='', width=0, fill='black')
	Label(window, textvariable=x).grid(row=14, column=1, sticky=E)



	window.mainloop()



##########################################################
#####################执行函数##############################
##########################################################


main()
