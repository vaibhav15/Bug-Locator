from django.shortcuts import render

from forms import DocumentForm
from models import Document
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password,check_password
import logging

def list(request):
    # Handle file upload
    if request.method=='POST':
       form=DocumentForm(request.POST,request.FILES)
       if form.is_valid():
          newfile = Document(name=request.POST['name'],file=request.FILES['docfile'])
          newfile.save()
          extract_file() 
                      
          return HttpResponseRedirect(reverse('buglocator.views.list'))
       return HttpResponse("Please try again")
   
    else : 
       form = DocumentForm() 
       documents = Document.objects.all()
       # Render list page with the documents and the form
       return render(request,'buglocator/list.html',{'form':form,'documents':documents}  )

def extract_file():
    logging.debug("File extract")
    

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
           return HttpResponse("Sorry! User not found")
    
       if check_password(request.POST["password"],user.password):
          return render(request,'buglocator/user.html',{'user':user.username})
       return HttpResponse("The password you entered is incorrect. Please try again") 

def homepage(request):
    
    return render(request,'buglocator/index.html',{})       

def reportbug(request):
    
    return render(request,'buglocator/report.html',{})
