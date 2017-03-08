from django.test import TestCase
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from wechat.models import *
import json

# I Defined
from wechat.config import *
from wechat.functions import *
from wechat.models import *

# Create your tests here.
def ajaxTest(request):
	academyId = request.GET.get("academyId")
	name_dict = {'saywhat': 'I love python and Django', 'school': 'Itcastcpp'}
	classList = ClassInfo.objects.filter(academyID = academyId)
	
	context_dict = {}
	
	for list in classList:
		context_dict[list.id] = list.className
	
	print context_dict
	return HttpResponse(json.dumps(context_dict), content_type = 'application/json')
	