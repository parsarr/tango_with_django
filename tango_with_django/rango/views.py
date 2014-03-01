from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm

def index(request):
	context = RequestContext(request)
	category_list = Category.objects.order_by('-likes')[:100]
	page_list = Page.objects.order_by('-views')[:100]
	#context_dict = {'boldmessage': "I am bold font from the context"}
	context_dict = {'categories': category_list, 'pages': page_list}
	#context_dict = {'pages': page_list}
	for category in category_list:
		category.url = category.name.replace(' ', '_')
	return render_to_response('rango/index.html', context_dict, context)

	
#	return HttpResponse("Rango says Hi Ya!!! <a href='/rango/about'>About</a>")

def about(request):
	context = RequestContext(request)
	context_dict = {'boldmessage': "I am bold font from the context"}
	return render_to_response('rango/about.html', context_dict, context)
	#return HttpResponse("Rango Says: Here is the about page <a href='/rango'>Main Page</a>")
	
'''def static(request):
	return HttpResponse(STATIC_PATH)
	'''
	
def category(request, category_name_url):
	context = RequestContext(request)
	category_name = category_name_url.replace('_',' ')
	context_dict = {'category_name': category_name, 'category_name_url': category_name_url}
	
	try:
		category = Category.objects.get(name=category_name)
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category
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
		
	return render_to_response('rango/add_category.html', {'form': form}, context)

def decode_url(category_name_url):
	return category_name_url.replace('_', ' ')
	
def add_page(request, category_name_url):
	context = RequestContext(request)
	
	category_name = decode_url(category_name_url)
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			page = form.save(commit=False)
			try:
				cat = Category.objects.get(name=category_name)
				page.category = cat
			except Category.DoesNotExist:
				return render_to_response('rango/add_page.html', {}, context)
			page.views = 0
			page.save()
			return category(request, category_name_url)
		else:
			print form.errors
	else:
		form = PageForm()
	
	return render_to_response('rango/add_page.html', {'category_name_url': category_name_url, 'category_name': category_name, 'form': form}, context)

def register(request):
    context = RequestContext(request)

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
        'rango/register.html',
        {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
        context)

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied")

    else:
        return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango')