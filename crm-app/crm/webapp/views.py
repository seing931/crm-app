from django.shortcuts import render, redirect, get_object_or_404
import csv
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm,AddClientForm,NewProductForm
from .models import Client
from django.db.models import Q

def home(request):
    clients = Client.objects.all()

    # check the logged in user
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome to Home page')
            # then we have to redirect to a page
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('home')
    else:
        return render(request, 'home.html', {'clients': clients})

#def login_view(request):
    #pass

def logout_view(request):
    logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'You are successfully registered !')
            return redirect('home')
    else:
        form = RegistrationForm()
        
    # This must be unindented so it runs for GET requests AND invalid POST forms
    return render(request, 'register.html', {'form': form})

def client(request, pk):
    if request.user.is_authenticated:
        # Look up the specific client data
        client_record = Client.objects.get(id=pk)
        return render(request, 'client.html', {'client_record': client_record})
    else:
        messages.success(request, 'You have to login...')
        return redirect('home')

def client_delete(request, pk):
    if request.user.is_authenticated:
        delete_record = Client.objects.get(id=pk)
        delete_record.delete()
        messages.success(request, 'You have successfully deleted...')
        return redirect('home')
    else:
        messages.success(request, 'You have to login first...')
        return redirect('home')

def add_client(request):
    form = AddClientForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                add_client = form.save()
                messages.success(request, "New Client added ...")
                return redirect('home')
        return render(request, 'add_client.html', {'form': form})
    else:
        messages.success(request, "You have to Login to add new record...")
        return redirect('home')

def client_update(request, pk):
        if request.user.is_authenticated:
            current_record = Client.objects.get(id=pk)
            form = AddClientForm(request.POST or None, instance=current_record)
            if request.method == "POST":
                if form.is_valid():
                    update_client = form.save()
                    messages.success(request, 'Client info updated...')
                    return redirect('home')
            return render(request, 'client_update.html', {'form': form})
        else:
            messages.success(request, "You have to login...")
            return redirect('home')

#For Product
def product(request, client_pk):
    if request.user.is_authenticated:
        client = get_object_or_404(Client, id=client_pk)
        products = client.product.all()
        return render(request, 'product.html', {'client':client, 'products':products})
    else:
        messages.success(request, "You have to login first.")
        return redirect('home')

# For product purchase record add
def new_product(request, client_pk):
    if request.user.is_authenticated:
        client = get_object_or_404(Client, id=client_pk)
        products = client.product.all()
        if request.method == 'POST':
            form = NewProductForm(request.POST, client=client)
            if form.is_valid():
                product = form.save(commit=False)
                product.client = client
                product.save()
                messages.success(request, "Product added successfully...")
                return render(request, 'product.html', {'client':client, 'products':products})
            else:
                messages.success(request, "Product not added")
                form = NewProductForm(client=client)
        else:
            form = NewProductForm(client=client)
        return render(request, 'new_product.html', {'form':form})
    else:
        messages.success(request, "You are not allow to access this page")
        return redirect('home')

def export_csv(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content_Disposition'] = 'attachment; filename="clients.csv"'

    # create a csv writer
    writer = csv.writer(response)

    # for csv header
    writer.writerow(['full_name', 'email', 'phone', 'city'])

    # Fetch client data
    client_data = Client.objects.all()
    for client in client_data:
        writer.writerow([client.full_name, client.email, client.phone, client.city])
    return response

# Search feature
def search_client(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Client.objects.filter(Q(name__contains=query) | Q(city__contains=query))

    return render(request, "search_client.html", {'results':results, 'query':query})