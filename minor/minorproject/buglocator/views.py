from django.shortcuts import render
from forms import DocumentForm
from models import Document
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse


def list(request):
    # Handle file upload
    if request.method=='POST':
       form=DocumentForm(request.POST,request.FILES)
       if form.is_valid():
          newfile = Document(name=request.POST['name'],file=request.FILES['docfile'])
          newfile.save()
   
          return HttpResponseRedirect(reverse('buglocator.views.list'))
          
    else : 
       form = DocumentForm() 
       documents = Document.objects.all()
       # Render list page with the documents and the form
       return render(request,'buglocator/list.html',{'form':form,'documents':documents}  )

def registration(request):
    if request.method=='POST':
       try:
           user = User.objects.get(email = request.DATA["email"])
       except:
          post_values = request.DATA.copy()
          password = post_values["password"]
          post_values["password"]= make_password(password)
          user = User(username=request.DATA["username"],email=request.DATA["email"],password=post_values["password"])   
          user.save()
          return HttpResponse("Registration successfull")
       return HttpResponse("Registration unsuccessfull")
                                                   
def login(request):
    if request.method=="POST":
       try :
           user=User.objects.get(email=request.DATA["email"])
       except:
           return HttpResponse("User not found")
    
       if make_password(request.DATA["password"],user.password):
          return HttpResponse("Login successfull")
       return HttpResponse("Login unsuccessfull") 

       

             

