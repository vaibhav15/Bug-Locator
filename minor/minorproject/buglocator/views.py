from django.shortcuts import render
from forms import DocumentForm
from models import Document
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

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
