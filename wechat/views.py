#encoding:utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.core.exceptions import *

# I Defined
from wechat.config import *
from wechat.functions import *
from wechat.models import *

import datetime
import time
import hashlib
import json
import sys

try:
    from django.http import JsonResponse
except ImportError:
    from .tool import JsonResponse

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

# Create your views here.
@csrf_exempt
def index(request):
	"微信接入参考 http://mp.weixin.qq.com/wiki/17/2d4265491f12608cd170a95559800f2d.html"
	if request.method == "GET":
		signature	= request.GET.get("signature")
		timestamp	= request.GET.get("timestamp")
		nonce		= request.GET.get("nonce")
		echostr		= request.GET.get("echostr")
		# 放到数组中按字典序排序
		token		= WEIXIN_TOKEN
		tmp_list 	= [token, timestamp, nonce]
		tmp_list.sort()
		# 把三个字符串拼接在一起进行sha1加密
		tmp_str 	= "%s%s%s" % tuple(tmp_list)
		tmp_str		= hashlib.sha1(tmp_str).hexdigest()
		# 判断与传递进来的 signature 是否一致
		if tmp_str == signature:
			return HttpResponse(echostr)
		else:
			return HttpResponse('')
	elif request.method == "POST":
		raw_xml = request.body.decode(u'UTF-8')
		dict_str = parse_Xml2Dict(raw_xml)
		try:
			MsgType = dict_str['MsgType']
		except:
			MsgType = ''
		try:
			Event = dict_str['Event']
		except:
			Event = ''
		if MsgType == 'text':#当接收到用户发来的文本信息时
			res_dict = {}
			res_dict['ToUserName'] = dict_str['FromUserName']
			res_dict['FromUserName'] = dict_str['ToUserName']
			res_dict['CreateTime'] = int(time.time())
			res_dict['MsgType'] = 'text'
			res_dict['Content'] = dict_str['Content']
			echostr = parse_Dict2Xml('xml', res_dict)
			return HttpResponse(echostr)
		elif MsgType == 'image':
			send_text(dict_str['FromUserName'], "收到你发送的图片")
			return HttpResponse('')
		elif MsgType == 'voice':
			dict_user_info = get_user_info(dict_str['FromUserName'])
			print '------------------------------'
			print '发送语音的用户信息如下'
			print dict_user_info
			print dict_user_info['nickname'].encode('utf-8')
			print '------------------------------'
			return HttpResponse('')
		elif Event == 'subscribe':# 关注公众号事件
			if dict_str['EventKey'] and dict_str['Ticket']:# 通过扫描二维码进行关注
				qrcode_num = dict_str['EventKey'].split('_')[1]
				send_text(dict_str['FromUserName'], "感谢您关注公众号！qrcode is " + str(qrcode_num))
			else:
				send_text(dict_str['FromUserName'], "感谢您关注公众号！")
			return HttpResponse('')
		elif Event == 'SCAN':
			send_text(dict_str['FromUserName'], "qrcode is " + str(dict_str['EventKey']))
			return HttpResponse('')
		elif MsgType == 'location':
			send_text(dict_str['FromUserName'], "你现在在:\n" + dict_str['Label'])
			return HttpResponse('')
		else:
			return HttpResponse('')
		
def create_menu(request):
	"在微信公共号中创建菜单，这个请求是要我们主动发起的"
	menu_data = {}
	button1 = {}
	button1['name'] = '我的历程'
	button1['type'] = 'view'
	button1['url'] = HOME_URL

	menu_data['button'] = [button1]
	
	post_url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + get_access_token()	
	post_data = parse_Dict2Json(menu_data)
	resp, content = my_post(post_url, post_data)
	response = parse_Json2Dict(content)
	
	if response['errcode'] == 0:
		return HttpResponse('create menu OK.')
	else:
		return HttpResponse(WEIXIN_ACCESS_TOKEN + ' create menu err:' + response['errmsg'])


def user_info(request):
	"获取用户 openid 判定 ID 是否是认证用户来跳转不同的页面"
	# http://www.cnblogs.com/txw1958/p/weixin71-oauth20.html
	code	= request.GET.get("code", "")
	state	= request.GET.get("state", "")
	
	if code == '':
		return HttpResponse('非法访问...')
	
	# 构造请求 openid 的 url，使用 get 方式请求该 url，将得到的数据转为字典
	url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=' + WEIXIN_APPID + '&secret=' + WEIXIN_APPSECRET + '&code=' + code + '&grant_type=authorization_code'
	resp, content = my_get(url)
	user_dict = parse_Json2Dict(content)
	
	# 临时变量，用来显示用户是否已经申请成为认证用户
	showUrl = ""
	showText = ""
	
	user = authenticate(username=user_dict['unionid'], password=user_dict['openid'])
	if user is not None:
		# 用户存在，判断用户是否是认证用户
		if user.is_active:
			# 登录用户，其他任何途径都无法登录用户，后面使用装饰器验证用户是否登录来防止一些页面被用户直接访问
			login(request, user)
		
			# 取用户信息
			profile = UserProfile.objects.get(fromUser = user)
		
			# 获取用户的个人信息
			userInfo = {}
			# 用户的 id 以 django 提供的 auth_user 表为准
			userInfo["userId"]	 = profile.fromUser.id
			userInfo["imageUrl"] = profile.photoAddr
			userInfo["userName"] = profile.nickName
			userInfo["inClass"]	 = profile.inClass
			return render(request, 'authorized.html', userInfo)
		else:
			# 修改前台用来显示的文字
			showUrl = HOME_URL
			showText = "审核中，请等待..."
	else:
		# 构造申请成为认证用户的地址
		callback = 'http://www.itcastcpp.cn/register/'
		showUrl = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + WEIXIN_APPID + '&redirect_uri=' + callback + '&response_type=code&scope=snsapi_userinfo&state=snsapi_userinfo#wechat_redirect'
		showText = "申请成为认证学员"

	# 检索学院列表信息
	registerDict = {}
	academyInfoList = AcademyInfo.objects.all()
	registerDict['AcademyInfoList'] = academyInfoList
	registerDict['showUrl'] = showUrl
	registerDict['showText'] = showText

	# 返回
	return render(request, 'index.html', registerDict)
	
def register(request):
	"成为认证学员，构造register页面"
	code	= request.GET.get("code", "")
	state	= request.GET.get("state", "")
	
	if code == '':
		return HttpResponse('非法访问...')
	
	# 构造请求 openid 的 url，使用 get 方式请求该 url，将得到的数据转为字典
	url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=' + WEIXIN_APPID + '&secret=' + WEIXIN_APPSECRET + '&code=' + code + '&grant_type=authorization_code'
	resp, content = my_get(url)
	user_dict = parse_Json2Dict(content)
	
	# 获取用户详细信息，储存到 user_info 字典中
	info = 'https://api.weixin.qq.com/sns/userinfo?access_token=' + user_dict['access_token'] + '&openid=' + user_dict['openid'] + '&lang=zh_CN'
	resp, content = my_get(info)
	user_info = parse_Json2Dict(content)
	
	# 返回的 json 数据格式 http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
	# 修改字典的 headimgurl 属性，把头像修改成 96*96 的
	user_info['headimgurl'] = user_info['headimgurl'][:-1]
	user_info['headimgurl'] += '96'
	
	# 取学院的列表
	academyInfoList = AcademyInfo.objects.all()
	user_info['academyInfoList'] = academyInfoList
	
	# 时间过滤 http://www.cnblogs.com/linjiqin/p/3821914.html
	# https://docs.djangoproject.com/en/1.8/ref/models/querysets/#exclude
	# 只取近 60 天内开的班
	begDate = datetime.datetime.now() + datetime.timedelta(days = -60)
	user_info['classInfo'] = ClassInfo.objects.filter(academyID = academyInfoList[0], classBegDate__gt = begDate)
	user_info['homePage'] = HOME_URL
	
	print user_info
	
	return render(request, 'register.html', user_info)
	
def academyInfo(request, academyinfo_name_slug):
	"点学院分类跳转到的函数，category_name_slug 是跳转的参数"
	context_dict = {}
	try:
		academyInfo = AcademyInfo.objects.get(slug = academyinfo_name_slug)
		context_dict['academyInfo'] = academyInfo
	except AcademyInfo.DoesNotExist:
		pass
	
	return render(request, 'academyInfo.html', context_dict)

def baseTest(request, academyinfo_name_slug):
	"入学前基础测试"
	academyInfo = AcademyInfo.objects.get(slug = academyinfo_name_slug)
	topic = SyllabusInfo.objects.filter(academyID = academyInfo)	#通过学院academy获取所在学院课程信息
	syllName = topic[0]
	topic_base = topic[0].id	#!!!!假设基础测试阶段存储在SyllabusInfo开始位置，获取课程名称
	return render(request, "topicTest.html",{'topicId':topic_base,'syllName':syllName})


@csrf_exempt
def userPost(request):
	"接收用户申请成为认证学员的数据"
	if request.method == "POST":
		# 使用 Django 用户认证系统创建用户
		# 注意，此处获取 unionid 必须要绑定公共平台帐号，参见 http://www.cnblogs.com/txw1958/p/weixin98-get-user-UnionID.html
		user = User.objects.create_user(username=request.POST.get("unionid"), password=request.POST.get("openid"))
		# 默认未激活状态，用来判断是否是已经通过认证的学员
		user.is_active = False
		user.save()
		
		profile = UserProfile(
			fromUser = user,
			nickName = request.POST.get("nickname"),					# 用户昵称，由微信接口获取
			stuSex = request.POST.get("sex"),							# 用户性别，由微信接口获取
			stuName = request.POST.get("username"),						# 用户名称，由用户自己输入
			country = request.POST.get("country"),						# 用户国家，由微信接口获取
			province = request.POST.get("province"),					# 用户身份，由微信接口获取
			city = request.POST.get("city"),							# 用户城市，由微信接口获取
			inClass = ClassInfo(id = request.POST.get("classInfo")),	# 所属班级，由用户自己选择
			tel = request.POST.get("usertel"),							# 用户电话，由用户自己输入
			photoAddr = request.POST.get("headimgurl"),					# 用户头像，由微信接口获取
			createTime = datetime.datetime.now(),						# 创建时间
			lastTime = datetime.datetime.now()							# 修改时间，以后修改资料可能会用到
		)
		profile.save()
		
		return HttpResponse(HOME_URL)
	else:
		return HttpResponse(HOME_URL)

@login_required
def student(request, student_name_slug):
	"根据班级信息获取班级里面所有学生"	
	context_dict = {}
	
	# a.is_active = 1 是判定该用户是否是认证用户
	cursor = connection.cursor()
	cursor.execute("select s.nickName, s.stuSex, s.photoAddr, s.country, s.province, s.city, s.createTime, SUM(g.grade) as allCount " 
				"from (select a.id, u.stuName, u.nickName, u.stuSex, u.photoAddr, u.country, u.province, u.city, u.createTime from "
				"wechat_userprofile u right join auth_user a on u.fromUser_id = a.id where a.is_active = 1 and u.inClass_id = " + student_name_slug + ") s "
				"left join wechat_gradeinfo g "
				"on s.id = g.stuID_id "
				"group by stuName, nickName, stuSex, photoAddr, country, province, city, createTime "
				"order by allCount desc")
	# 将 execute 执行返回的列表转为字典
	context_dict["stuList"] = dictfetchall(cursor)

	return render(request, "student.html", context_dict)

@login_required
def courseList(request, course_name_slug):
	"构造用户每个阶段的课程和测试信息"
	stuId = request.GET.get("userId")
	context_dict = {}
	
	# 获取用户所在班级的开班时间
	fromUserInfo = User.objects.get(id = stuId);
	print "--------" + stuId
	begTime = UserProfile.objects.get(fromUser = fromUserInfo).inClass.classBegDate
	print "========"
	dateRet = datetime.date.today() - begTime
	classTime = dateRet.days

	# 写个自定义sql，django貌似实现不了这个嵌套查询 + left join
	# 参考资料 http://python.usyiyi.cn/django/topics/db/sql.html
	cursor = connection.cursor()
	cursor.execute("select s.id, "
				"g.stuID_id, "
				"s.lessonName, "
				"DATE_ADD('" + str(begTime) + "', INTERVAL s.timeOut DAY) as endTime, "
				"s.timeOut, "
				"g.grade "
				"from wechat_syllabusinfo s left outer join "
				"(select * from wechat_gradeinfo where stuID_id = " + stuId + ") g "
				"on s.id = g.syllaID_id")
				
	# 将 execute 执行返回的列表转为字典
	context_dict["courseList"] = dictfetchall(cursor)
	context_dict["classTime"] = classTime
	
	return render(request, "courseList.html", context_dict)

def topic(request):
	context_dict = {}
	syllId = request.GET.get("topicId")
	try:
		# 根据传递进来的阶段ID，查询阶段中里面的课程信息
		course = SyllabusInfo.objects.get(pk = syllId)
	except SyllabusInfo.DoesNotExist:
		pass
	else:
		context_dict["topicInfo"] = course
	
	return render(request, "courseInfo.html", context_dict)

def topicTest(request):
	"从数据库拉取测试题目以及答案信息"
	retGet = request.GET.get("topicId")	#获取题目ID
	syllName = SyllabusInfo.objects.get(id = retGet)	
	return render(request, "topicTest.html",{'topicId':retGet,'syllName':syllName})

def quiz_choice(request):
	"从数据库拉取测试题目以及答案信息"
	retGet = request.GET['topicId']
	# 检索 retGet 阶段所对应的测试题目
	questionDict = TestInfo.objects.filter(syllaID = retGet)
	questList = []
	for question in questionDict:
		context_dict = {}
		# 题目
		context_dict["question"] = str(question)
		option = TestAnsInfo.objects.filter(testInfoId = question)
		optionList = []
		for opt in option:
			optionList.append(str(opt))
		context_dict["answers"] = optionList
		
		# 题目的编号;这里返回的是TestInfo中默认生成的id。
		context_dict["questionNumber"] = question.id
		questList.append(context_dict)
		
	question = {'questions' :questList}
	return JsonResponse(question)

def get_answer(request):
	an = request.GET['an']
	answers = json.loads(an)
	correctAnswers = []
	myAnswers = []
	for ans in answers:
		correctAnswer=[]
		testId = long(ans[u'questionNumber'])
		correctAnswer.append(testId)
		correctAnswer.append(int(ans[u'userAnswer']))
		myAnswers.append(correctAnswer)
		Tid = TestInfo.objects.get(id = testId)
		answerInfo = TestAnsInfo.objects.filter(testInfoId = Tid)		
		firstId = answerInfo[0].id
		for info in answerInfo:
			if (info.rightOption):
				rightNumber = info.id-firstId+1
				correctAnswers.append(rightNumber)
				break
		
	return HttpResponse(json.dumps(correctAnswers), content_type='application/json')

def ajaxGetClassInfo(request):
	"根据get传递过来的数据请求学科下面的班级信息，返回 json 数据"
	context_dict = {}
	academyId = request.GET.get("academyId")
	classList = ClassInfo.objects.filter(academyID = academyId)
	
	for list in classList:
		context_dict[list.id] = list.className
	
	return HttpResponse(json.dumps(context_dict), content_type = 'application/json')
	
def help(request):
	context_dict = {}
	return render(request, "courseList.html", context_dict)
	
def about(request):
	context_dict = {}
	return render(request, "courseList.html", context_dict)
	
def ajaxTest(request):
	appid	= request.GET.get("appid")
	return HttpResponse('ajax ok...')
