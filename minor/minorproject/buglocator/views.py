from __future__ import print_function
from django.shortcuts import render
from forms import DocumentForm
from models import Document,Bug,Function,BugLocation
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
        if 'def ' in line :
           position=line.find('def')
           print(line_number,line[position+4:])           
           function = Function(document=file,name=line[position+4:],line_no=line_number)
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
       bug = Bug(user=user,name=request.POST["name"],description=request.POST["message"],keywords=request.POST["keyword_message"])
       bug.save()
       locate_bug(bug,user)
       return render(request,'buglocator/report.html',{'username':request.session.get('name',False)})
    return render(request,'buglocator/report.html',{'username':request.session.get('name',False)})

def locate_bug(bug,user):
    hints=bug.keywords
    keywords=hints.split(',')
    files = Document.objects.filter(user=user)
    for file in files:
        if file :
           lines = file.file.readlines()
           for keyword in keywords :
               found=[]  
               found_functions=find_function(keyword,file)
               print(keyword)
               line_number = 0
               for line in lines :
                   line_number += 1
                   if keyword.lower() in line.lower() :
                      print(keyword,line_number)
                      found.append(line_number)
               buglocation=BugLocation(bug=bug,file_path=file.file,keyword=keyword,line_no=found,function=found_functions)
               buglocation.save()

def find_function(keyword,file):
    #for file in files:
    string=""
    functions = Function.objects.filter(document=file.file)
    for function in functions:
        if keyword.lower() in function.name.lower() :
           if string=="" :
              string=(str(function.name)).strip() 
           else :
              string+=","+(str(function.name)).strip() 
        else :
           print("Not found") 
    return string    

def locatebug(request):
 
    user = User.objects.get(username=request.session.get('name',False))
    bugs = Bug.objects.filter(user = user)      
    return render(request,'buglocator/locate.html',{'bugs':bugs,'username':request.session.get('name',False)})

def showbug(request,bug_id):
    bugs = BugLocation.objects.filter(bug=bug_id)
    list=[]
    add_files=[]
    for bug in bugs:
        if bug.function:
           funcs=(str(bug.function)).split(',')
           print(funcs)
           for func in funcs :
               response_data={}
               print(func)
               try:
                  function=Function.objects.get(name__contains=func)
               except:
                  print("Not Found")
               response_data['location_lines']=get_lines(function.line_no,bug.file_path)
               response_data['filename']=bug.file_path
               if response_data :
                  list.append(response_data)
                  print(list)
    return render(request,'buglocator/viewbug.html',{'username':request.session.get('name',False),'lists':list})

def get_lines(line_no,file):
    f=open(file,'r')    
    lines = f.readlines()
    return lines[line_no-4:line_no+4]
