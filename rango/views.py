from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime
from rango.bing_search import run_query, read_bing_key
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rango.models import UserProfile

# Create your views here.
# def index(request):
#     context = {
#         'boldmessage': "Crunchy creamie blabla",
#     }
#     return render(request,'rango/index.html',context=context)

@login_required
def register_profile(request):
    form = UserProfileForm()
    
    if request.method=='POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('index')
        else:
            print(form.errors)
    context = {
        'form': form,
    }
    return render(request, 'rango/profile_registration.html', context)

@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('index')
    
    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': userprofile.website, 'picture': userprofile.picture})
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('profile', user.username)
        else:
            print(form.errors)
    
    return render(request, 'rango/profile.html',
        {'userprofile': userprofile, 'selecteduser': user, 'form': form})

def goto_url2(request, page_id):
    obj = get_object_or_404(Page,id=page_id)
    url = obj.url
    return redirect(url)

def goto_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)


def search(request):
    result_list = []
    query = None
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits','1'))   # print('VISIT')
    # print(visits)

    last_visit_cookie = get_server_side_cookie(request,'last_visit',str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')

    # print('LAST VISIT TIME')
    # print(last_visit_time)

    # print('TIME NOW')
    # print (datetime.now())

    # print('DIFFERENCE')
    # print((datetime.now() - last_visit_time))
    if (datetime.now() - last_visit_time).seconds > 2:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context = {
        'categories': category_list,
        'pages': page_list,
        # 'visits': int(request.COOKIES.get('visits', '1')),
    }

    # cookie stuff
    visitor_cookie_handler(request)
    context['visits'] = request.session['visits']

    response = render(request, 'rango/index.html', context)
    return response

def about(request):
    visitor_cookie_handler(request)

    context = {
        'visits': request.session['visits'],
    }
    
    response = render(request, 'rango/about.html', context)
    return response

def show_category(request, category_name_url):
    context = {}
    try:
        category = Category.objects.get(slug=category_name_url)
        pages = Page.objects.filter(category=category)
        context['pages'] = pages
        context['category'] =  category
    except:
        context['category'] = None
        context['pages'] = None

    result_list = []
    query = None
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
        context['result_list'] = result_list

    return render(request, 'rango/category.html', context)

def add_category(request, ):
    form = CategoryForm()
    if request.method=='POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()

            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form':form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context = {
        'form': form,
        'category': category
    }
    return render(request, 'rango/add_page.html', context)

        
