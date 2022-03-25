import datetime 
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


import json

from .models import *



def loginPage(request):
    if request.method =='POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            try:
                user= User.objects.get(username=username)
            except:
                messages.error(request, 'User does not exist....')
            user = authenticate(request,username=username, password=password)

            if user is not None:
                login(request,user)
                return redirect('/')

            else:
                messages.error(request, 'Incorrect Username or Password ...')
    context={}
    return render(request,'store/login_page.html',context)

def logoutPage(request):
    logout(request)
    return redirect('/')

def registerUser(request):
    if request.method == 'POST' :
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'username taken.. try another one...!')
                return redirect('registration')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'email taken..try another ...!')
            else:
                user=User.objects.create_user(username=username,password=password1,email=email)
                user.save()
                print("user created")
                
                customer, created = Customer.objects.get_or_create(user=user, name=username, email=email)
                print(customer)
                return redirect('login')
        else:
            messages.info(request, 'password not matching .. re-enter password')
            return redirect('registraion')

        return redirect('login')

    else:
        
        context={}
        return render(request,'store/registration_page.html', context)





def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # Querying child objects by setting the parent value and then the child object with all lowercase values then 'underscore' set.all
        items = order.orderitem_set.all()

        cartItems = order.get_cart_items
    else:
        items=[]
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = order['get_cart_items']

    
    products = Product.objects.all()
    context={'products':products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # Querying child objects by setting the parent value and then the child object with all lowercase values then 'underscore' set.all
        items = order.orderitem_set.all()
        #to show the number of added items
        cartItems = order.get_cart_items
    else:
        # messages.info(request, "Please login first")
        return render(request,'store/loginrequired.html')  
        
       

    context={'items':items,'order':order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # Querying child objects by setting the parent value and then the child object with all lowercase values then 'underscore' set.all
        items = order.orderitem_set.all()

        cartItems = order.get_cart_items
    else:
        pass
        

    context={'items':items,'order':order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)
    
    

def updateItem(request):
    
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action', action)
    print('productId:',productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer,complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)


    if action == 'add':
        print('item added')
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity -1)
    
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('item was added',safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    print('transactionID:',transaction_id)
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        total = float(data['form']['total'])

        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],

        )


    else:
        print('user is not logged in ...')
        # return render(request,'store/loginrequired.html') 


    return JsonResponse('payment completed...',safe=False)



    


    

    

