from django.shortcuts import render
#from myproject.myapp.forms import DocumentForm

def list(request):
    # Handle file upload
    
    # Render list page with the documents and the form
    return render(request,
        'buglocator/list.html',
        {}  )
