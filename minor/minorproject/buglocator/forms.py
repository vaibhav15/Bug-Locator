from django import forms

class DocumentForm(forms.Form):
     name = forms.CharField(label='File name'	,max_length = 255)
     docfile = forms.FileField(label='Select a File')	


