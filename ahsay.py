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
import urllib.request
import requests
import ssl

import csv

import time
import sys
from PyQt5.QtCore import QBasicTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QAction, qApp, QMenu, QTextEdit, QToolTip, QPushButton, QMessageBox, QDesktopWidget, QGridLayout, QLabel,  QProgressDialog, QLineEdit, QProgressBar)
from PyQt5.QtGui import QIcon

def main():

	back_up_user_information = None 
	#结构如下： {'LoginName': 'test0723', 'QuotaList': {'Enabled': True, 'Quota': 91200, 'DestinationName': 'AhsayCBS', 'DestinationKey': 'OBS'}, 'Owner': ''}

	selected_destination_dict = None
	#一个dict, key为destination, value为0,1，不过value是IntVar()要用get()来获得

	user_name_and_quota_from_xml = None
	#一个dict, key为destination, value为quota

	have_list = False
	have_check = False
	error_exist = False
	mismatch_exist = False
	mismatch_list = []


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


	def sendUpdateUser(**kargs):
		print(kargs)
		test_data = json.dumps(kargs)
		request_url = 'https://'+serverAd.get()+'/obs/api/json/2/UpdateUser.do'

		r = requests.post(request_url, data=test_data, verify=False)
		print(r.status_code)
		resp = json.loads(r.text, object_pairs_hook=my_obj_pairs_hook)
		return resp


	def sendListUsers():
		sysUser = usrName.get()
		sysPwd = usrPwd.get()
		d = dict(SysUser=sysUser, SysPwd=sysPwd)
		test_data = json.dumps(d)
		request_url = 'https://'+serverAd.get()+'/obs/api/json/2/ListUsers.do'

		try: 
			r = requests.post(request_url, data=d, verify=False)

		except OSError:
			print('life sucks')
			return -2 
			# return -2
		print(r.url)
		#print(r.text)		
		resp = json.loads(r.text, object_pairs_hook=my_obj_pairs_hook)
		print(resp['Status'])

		if resp['Status']=='OK':
			return resp
		else:
			print(resp)
			return -1	


##########################################################
####################listDest辅助方程######################
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
		print('\n\n\n\n\nlist dest')
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
				tkinter.messagebox.showinfo('Status','Wrong Username/Password')
			elif the_list == -2:
				tkinter.messagebox.showinfo('Status','Cannot connect to the backup server.')
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
				print(des_list)

				#建一个set并把里面的内容传递到createPage里面去

				createPage(*des_list)
				#得到的是一个value为IntVar()的dict
				nonlocal have_list
				have_list = True

		# actually it works with the info get from listusers locally
	def testFromServer():
		print('\n\n\n\n\ntest from server')
		nonlocal back_up_user_information
		nonlocal mismatch_list
		nonlocal have_list
		if have_list == True:
			try:
				time.sleep(0.5)
				output_path = os.getcwd()
				print(os.getcwd())
				tkinter.messagebox.showinfo('Path','The csv  file will be generated to '+os.getcwd())
				time.sleep(0.5)
				specific_output_path = output_path+ '/get_user.csv'
				with open(specific_output_path, 'w', newline='') as csvfile:
					filewriter = csv.writer(csvfile)
					filewriter.writerow(['User Name', 'Enabled', 'Quota', 'DestinationName', 'DestinationKey', 'Owner'])
				print(path.get())

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

				total_usr = 0
				for usr in back_up_user_information:
					total_usr = total_usr + 1

				cnt_usr = 0
				for usr in back_up_user_information:
					if selected_destination_dict[usr['QuotaList']['DestinationKey']].get() == 1:
						if usr['Owner'] == user_name_and_quota_from_xml[usr['LoginName']][1]:
							if usr['Owner']=='':
								usr['Owner']='None'
							usr['QuotaList']['Enabled'] = True
							usr['QuotaList']['Quota'] = user_name_and_quota_from_xml[usr['LoginName']][0]
							#print(usr)
							#基本正确了
							#写成csv即可
							with open(specific_output_path, 'a', newline='') as csvfile:
								filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
								filewriter.writerow([usr['LoginName'], usr['QuotaList']['Enabled'], usr['QuotaList']['Quota'], usr['QuotaList']['DestinationName'],usr['QuotaList']['DestinationKey'],usr['Owner']])
						else:
							if usr['Owner']=='':
								usr['Owner']='None'
							mismatch_list.append([usr['LoginName'], usr['Owner'], user_name_and_quota_from_xml[usr['LoginName']][1]])
					cnt_usr = cnt_usr + 1
					change_schedule(cnt_usr,total_usr)
				print(mismatch_list)

				tmp_list = []
				for i in mismatch_list:
					can_insert = True
					for j in tmp_list:
						if i[0]==j[0]:
							can_insert=False
							print('repeat info in line 264')
					if can_insert == True:
						tmp_list.append(i)

				mismatch_list = tmp_list
				
				
				print(mismatch_list)
				# for usr in mismatch_list:
				# 	with open(specific_output_path, 'a', newline='') as csvfile:
				# 		filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
				# 		filewriter.writerow([usr[0], usr[1], usr[2], usr[3],usr[4],usr[5]])


				have_list = False
				nonlocal have_check
				have_check = True
				tkinter.messagebox.showinfo('Status','Done.')
			except BaseException:
				tkinter.messagebox.showinfo('Status','Please choose the correct users.xml')
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
		print('\n\n\n\n\n submit to server')
		#将mismatch的信息最先放进去

		nonlocal mismatch_list
		print(mismatch_list)
		print('\n\n\n\n\n')

		nonlocal have_check
		if have_check == True:
			
			nonlocal error_exist

			outputpath = os.getcwd()
			specificOutputpath = outputpath+'/get_user.csv'
			error_csv_path = outputpath+'/error_accounts.csv'
			final_report_path = outputpath+'/final_report.csv'
			with open (final_report_path, 'w', newline='') as csv_file:
				filewriter = csv.writer(csv_file)
				filewriter.writerow(['User Name', 'Quota', 'Destination Name', 'Status'])
			
			with open (final_report_path, 'a', newline='') as csv_file:
				filewriter = csv.writer(csv_file)
				for i in mismatch_list:
					filewriter.writerow([i[0],'N/A','N/A','Owner Mismatch between CBS(Owner: %s) and Given users.xml(Owner: %s)'%(i[1],i[2])])

			if mismatch_list != []:
				print(mismatch_list)
				error_exist = True
				with open(error_csv_path, 'w', newline='') as csv_file:
					filewriter = csv.writer(csv_file)
					filewriter.writerow(['User', 'Error'])
					for i in mismatch_list:
						filewriter.writerow([i[0],'Owner Mismatch between CBS(Owner: %s) and Given users.xml(Owner: %s)'%(i[1],i[2])])

			#至此所有Mismatch的信息写完了，不用再管他了


			print('\n\n\n\n\n')
			#计算总共需要更新的个数
			total_usr = 0
			with open(specificOutputpath, 'r') as csv_file:
				reader = csv.reader(csv_file)
				for row in reader:
					if row[1]=='True' or row[1]=='False' or row[1]=='TRUE' or row[1]=='FALSE':
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
								with open(error_csv_path, 'w', newline='') as csv_file:
									filewriter = csv.writer(csv_file)
									filewriter.writerow(['User', 'Error'])
									filewriter.writerow([row[0], upStatus['Message']])
							else:
								with open(error_csv_path, 'a', newline='') as csv_file:
									filewriter = csv.writer(csv_file)
									filewriter.writerow([row[0], upStatus['Message']])
							with open(final_report_path, 'a', newline='') as csv_file:
								filewriter = csv.writer(csv_file)
								filewriter.writerow([row[0], row[3], row[4], upStatus['Message']])
						else:
							with open(final_report_path, 'a', newline='') as csv_file:
								filewriter = csv.writer(csv_file)
								filewriter.writerow([row[0], row[3], row[4], 'OK'])
							time.sleep(0.5)
						cnt_usr = cnt_usr + 1
						change_schedule(cnt_usr,total_usr)

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

	#缅怀这些新学的最后被pm无情干掉的页面

	# window = Tk()
	# window.title('Update User')
	# window.geometry('620x500')

	# Label(window, text='Note: Please follow the steps strictly').grid(row=0, columnspan=2, sticky=W)
	# Label(window, text='1.Please input the correct Server System\API UserName, Password, and ServerURL.').grid(row=1, columnspan=2, sticky=W)

	# usrName = StringVar()
	# SysUsertag = tk.Label(window, text='System User:', width=20, anchor=E)
	# SysUsertag.grid(row=2,column=0, sticky=W)
	# SysUser = tk.Entry(window, textvariable=usrName, width=30)
	# SysUser.grid(row=2,column=1)

	# usrPwd = StringVar()
	# SysPwdtag = tk.Label(window, text='System User Password:', width=20, anchor=E)
	# SysPwdtag.grid(row=3,column=0,sticky=W)
	# SysPwd = tk.Entry(window, textvariable=usrPwd, show='*', width=30)
	# SysPwd.grid(row=3,column=1)

	# serverAd = StringVar()
	# serverAdtag = tk.Label(window, text='Server IP Address:', width=20, anchor=E)
	# serverAdtag.grid(row=4,column=0,sticky=W)
	# serverAddress = tk.Entry(window, textvariable=serverAd, width=30)
	# serverAddress.grid(row=4,column=1)

	# Label(window, text='2.Please click List Dest, and click the Destinations need to be updated.').grid(row=5, columnspan=2, sticky=W)
	# list_dest = tk.Button(window, text='List Dest', width=50, height=2, command=listDest)
	# list_dest.grid(row=6, columnspan=2)

	# Label(window, text='3. Choose the right users.xml file and click check.\n    You can check the update informationin get_users.csv in the same path as this tool.', justify=LEFT).grid(row=7, columnspan=2, sticky=W)
	# path = StringVar()
	# chooseXml = tk.Button(window, text='Choose users.xml', width=25, height=2, command=inputXml)
	# chooseXml.grid(row=8, column=1, sticky=W)
	# xmlPath = tk.Entry(window, textvariable=path, width=30)
	# xmlPath.grid(row=8, column=0)

	# test = tk.Button(window, text='Check', width=50, height=2, command=testFromServer)
	# test.grid(row=9, columnspan=2)


	# Label(window, text='4. Click submit and wait until Success or Finish with Error.\n   You will get two csv files in the same path as this tool.\n   final_report for all updated users information\n   error_accounts if there exists error.', justify=LEFT).grid(row=10, columnspan=5, sticky=W)
	# submit = tk.Button(window, text='Submit', width=50, height=2, command=submitToServer)
	# submit.grid(row=13, columnspan=2)
	# submit_run_time = StringVar()


	# #做一个进度栏
	# x = StringVar()

	# canvas = Canvas(window, width=450, height=30, bg='white')
	# canvas.grid(row=14, columnspan=5)
	# out_rec = canvas.create_rectangle(0,0,450,30, outline='', width=0)
	# fill_rec = canvas.create_rectangle(0,0,0,30, outline='', width=0, fill='black')
	# Label(window, textvariable=x).grid(row=14, column=5, sticky=E)



	# window.mainloop()


	class main_window_class(QWidget):
		def __init__(self):
			super().__init__()
			self.initUI()

		def initUI(self):
			#self.statusBar().showMessage('Load completed')

			grid = QGridLayout()

			self.setLayout(grid)
		
			url_label = QLabel('CBS URL:')
			usr_label = QLabel('Username:')
			pwd_label = QLabel('Password:')
			xml_label = QLabel('users.xml:')
			pgb_label = QLabel('Current Operation Progress:')
			inf_label = QLabel('''Guide:
1) Enter CBS URL. If your CBS address is https://ahsaycbs.com:1000, enter ahsaycbs.com:1000.
2) Enter username and password for a system user or API user.
3) Click List Destination(s) and wait for a popup Window. Choose which Predefined 
Destination you want to push the old quota to and click “Confirm”. Though this tool allows
you to run it for multiple destinations at once, we would recommend you doing it for one
destination each time to avoid confusion.
4) Click “Select…” and locate the users.xml’s backup you saved before upgrading to 
v7.15.6.x. You can find it in CBS\conf\Backup\dr-*date*.zip\conf\\users.xml if you haven’t
kept it.
5) Click Analyse. This updater will generate a getUser.csv file to the directory where it 
resides in. It contains everything which will be pushed on to the server in the later 
stage. You can check or make amendments to it. The “Quota” will be pushed to the relative 
“User” for the “Destination” shown.
6) Click Update to start pushing quota updates to CBS. Final Report and Error Report will 
be outputted to the current directory.
				''')

			url_edit = QLineEdit()
			usr_edit = QLineEdit()
			pwd_edit = QLineEdit()
			pwd_edit.setEchoMode(QLineEdit.Password)
			xml_edit = QLineEdit()

			lis_but = QPushButton('List Destination')
			sel_but = QPushButton('Select')
			ana_but = QPushButton('Analyse')
			
			upd_but = QPushButton('Update')
			


			grid.addWidget(url_label, 1, 0)
			grid.addWidget(url_edit, 1, 1, 1, 4)

			grid.addWidget(usr_label, 2, 0)
			grid.addWidget(usr_edit, 2, 1)
			grid.addWidget(pwd_label, 2, 2)
			grid.addWidget(pwd_edit, 2, 3)
			grid.addWidget(lis_but, 2, 4)

			grid.addWidget(xml_label, 3, 0)
			grid.addWidget(xml_edit, 3, 1, 1, 3)
			grid.addWidget(sel_but, 3, 4)	

			grid.addWidget(ana_but, 4, 1)
			grid.addWidget(upd_but, 4, 3)

			upd_but.resize(upd_but.sizeHint())
			ana_but.resize(upd_but.sizeHint())


			# pb_label = QLabel('')
			# pb_bar = QProgressBar()
			self.pbar = QProgressBar()

			self.btn = QPushButton('Start')
			self.btn.clicked.connect(self.doAction)

			self.timer = QBasicTimer()
			self.step = 0	

			grid.addWidget(pgb_label, 5, 0, 1, 2)
			grid.addWidget(self.pbar, 6, 0, 1, 5)

			grid.addWidget(inf_label, 7, 0, 10, 5)







			grid.setSpacing(10)

			self.resize(600,600)
			self.center()
			self.setWindowTitle('Ahsay v7.15.6.x Quota Updater')
			self.show()

		def center(self):
			#用一个qr obj来存储self之后要放的位置
			qr = self.frameGeometry()
			cp = QDesktopWidget().availableGeometry().center()
			qr.moveCenter(cp)
			self.move(qr.topLeft())

		def timerEvent(self, e):
			if self.step >= 100:
				self.timer.stop()
				self.btn.setText('Finished')
				return
			self.step = self.step+1
			self.pbar.setValue(self.step)

		def doAction(self):
			if self.timer.isActive():
				self.timer.stop()
				self.btn.setText('Start')
			else:
				self.timer.start(100,self)
				self.btn.setText('Stop')

			
		

	app = QApplication(sys.argv)
	app.setWindowIcon(QIcon('/Users/yanbingong/Desktop/装乱七八糟东西的文件夹/tt1.png'))

	main_window = main_window_class()

	sys.exit(app.exec_())





##########################################################
#####################执行函数##############################
##########################################################


main()
