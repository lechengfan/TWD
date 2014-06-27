from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
	context = RequestContext(request)

	category_list = Category.objects.order_by('-likes')[:5] #only want the top 5
	context_dict = {'categories': category_list}

	for category in category_list :
		category.url = category.name.replace(' ', '_')

	page_list = Page.objects.order_by('-views')[:5] #top 5 pages
	context_dict['page_list'] = page_list

	visits = int(request.COOKIES.get('visits', '0'))
	
	if request.session.get('last_visit'):
		last_visit_time = request.session.get('last_visit')

		visits = request.session.get('visits', 0)
		if (datetime.now()-datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).seconds > 5:
			request.session['visits'] = visits+1
			request.session['last_visit'] = str(datetime.now())
	else:
		request.session['visits'] = 1
		request.session['last_visit'] = str(datetime.now())

	return render_to_response('rango/index.html', context_dict, context)

def about(request):
	
	context = RequestContext(request)
	visits = int(request.COOKIES.get('visits', '0'))

	return render_to_response('rango/about.html', {'visits':visits}, context)

def category(request, category_name_url):
	context = RequestContext(request)

	category_name = category_name_url.replace('_', ' ')

	context_dict = {'category_name':category_name}

	try:
		category = Category.objects.get(name = category_name)

		pages = Page.objects.filter(category=category)

		context_dict['pages'] = pages

		context_dict['category'] = category

		context_dict['category_name_url'] = category_name_url

	except Category.DoesNotExist: 
		pass

	return render_to_response('rango/category.html', context_dict, context)

def add_category(request):
	context = RequestContext(request)

	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)

			return index(request)
		else:
			print form.errors
	else:
		form = CategoryForm()

	return render_to_response('rango/add_category.html', {'form':form}, context)

def add_page(request, category_name_url):
	context = RequestContext(request)

	category_name = decode_url(category_name_url)
	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			page=form.save(commit=False)

			try:
				cat= Category.objects.get(name=category_name)
				page.category = cat
			except Category.DoesNotExist:
				return render_to_response('rango/add_category.html', {}, context)

			page.views=0

			page.save()

			return category(request, category_name_url)
		else:
			print form.errors
	else:
		form = PageForm()

	return render_to_response( 'rango/add_page.html',
		{'category_name_url':category_name_url,
		'category_name': category_name, 'form': form},
		context)

def decode_url(url):
	return url.replace('_', ' ')

def register(request):
    if request.session.test_cookie_worked():
        print ">>>> TEST COOKIE WORKED"
        request.session.delete_test_cookie()

    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Print form errors to the terminal.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
	context = RequestContext(request)

	if request.method== 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username, password=password)

		if user:

			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponse('Your Rango account has been disabled.')
		else:
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details provided.")

	else:
		return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(request):
	return HttpResponse("Since you are logged in, you can see this text")

@login_required
def user_logout(request):
	logout(request)

	return HttpResponseRedirect('/rango/')