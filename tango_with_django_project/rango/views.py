from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):
	#return HttpResponse("HELLO WORLD! <a href='/rango/about/'> About</a>")
	context = RequestContext(request)

	context_dict = {'boldmessage': "I'm the bolded text"}

	return render_to_response('rango/index.html', context_dict, context)

def about(request):
	
	context = RequestContext(request)

	return render_to_response('rango/about.html', context)