from django.shortcuts import render
from django.http import HttpResponse

from rango.models import Category, Page

from rango.forms import CategoryForm, PageForm

from datetime import datetime
# Create your views here.
# def index(request):
#     context = {
#         'boldmessage': "Crunchy creamie blabla",
#     }
#     return render(request,'rango/index.html',context=context)


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request, response):
    visits = int(request.COOKIES.get('visits','1'))

    last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        response.set_cookie('last_visit',str(datetime.now()))
    else:
        response.set_cookie('last_visit', last_visit_cookie)
    response.set_cookie('visits',visits)

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context = {
        'categories': category_list,
        'pages': page_list,
    }

    # Cookie test
    # request.session.set_test_cookie()

    # cookie stuff
    response = render(request, 'rango/index.html', context)
    visitor_cookie_handler(request, response)

    return render(request, 'rango/index.html', context)

def about(request):
    # cookie test
    # if request.session.test_cookie_worked():
    #     print("TEST COOKIE WORKED!")
    #     request.session.delete_test_cookie()
    return render(request, 'rango/about.html', {})

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

    return render(request, 'rango/category.html', context)

def add_category(request, ):
    form = CategoryForm()
    if request.method=='POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
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

        
