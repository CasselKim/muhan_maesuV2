from django.shortcuts import render, redirect
from django.http import HttpResponse

def index(request) : 
    print(request.user)
    if request.user.is_authenticated : 
        context = {'hello' : 'My friends'}
        return render(request, 'polls/manage.html', context)
    else : 
        return redirect('common/login')


# Create your views here.
