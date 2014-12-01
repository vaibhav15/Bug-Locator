from __future__ import print_function
from django.shortcuts import render
from forms import DocumentForm
from models import Document,Bug,Function
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password,check_password
import logging
import os

def list(request):
    # Handle file upload
    if request.method=='POST':
       user = User.objects.get(username = request.session.get('name',False))
       newfile = Document(user=user,name=request.POST['name'],file=request.FILES['docfile'])
       newfile.save()
       extract_file(newfile.file) 
                      
       return render(request,'buglocator/user.html',{'username':request.session.get('name',False)})
   
    else : 
       return render(request,'buglocator/user.html',{'username':request.session.get('name',False)} )

def extract_file(file):
    lines = file.readlines()
    line_number = 0
    for line in lines :     
        line_number += 1 
        if 'def' in line :
            print(line_number,line[4:])           
            function = Function(document=file,name=line[4:],line_no=line_number)
            function.save()
 
def registration(request):
    if request.method=='POST':
       try:
           user = User.objects.get(username = request.POST["email"])
       except:
          password = request.POST["password"]
          password = make_password(password)
          user = User(first_name=request.POST["first_name"],last_name=request.POST["last_name"],\
                      username=request.POST["email"],email=request.POST["email"],password=password)   
          user.save()
          return HttpResponse("Registration successfull")
       return HttpResponse("Registration unsuccessfull Username already exists!")
                                                   
def login(request):
    if request.method=="POST":
       try :
           user=User.objects.get(email=request.POST["email"])
       except:
           return render(request,'buglocator/index.html',{})
    
       if check_password(request.POST["password"],user.password):
          request.session['name']=user.username
          return render(request,'buglocator/user.html',{'username':user.username})

       return render(request,'buglocator/index.html',{}) 
    
    elif request.session.get('name',False):
            return render(request,'buglocator/user.html',{'username':request.session.get('name',False)} )
    else :
            return render(request,'buglocator/index.html',{})
    
def homepage(request):
    request.session.flush()    
    return render(request,'buglocator/index.html',{})       

def reportbug(request):
    
    if request.method=="POST" :
       user = User.objects.get(username=request.session.get('name',False))
       bug = Bug(user=user,name=request.POST["name"],description=request.POST["message"],keyword=request.POST["keyword_message"])
       bug.save()
       return render(request,'buglocator/report.html',{'username':request.session.get('name',False)})
    return render(request,'buglocator/report.html',{'username':request.session.get('name',False)})

def locatebug(request):
 
    user = User.objects.get(username=request.session.get('name',False))
    bugs = Bug.objects.filter(user = user)      
    return render(request,'buglocator/locate.html',{'bugs':bugs,'username':request.session.get('name',False)})
