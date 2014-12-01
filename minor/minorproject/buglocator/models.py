from django.db import models
from django.contrib.auth.models import User
import datetime

class Document(models.Model):
     user = models.ForeignKey(User)
     name = models.CharField(max_length=255)
     file = models.FileField(upload_to='files')
 
class Bug(models.Model):
      user = models.ForeignKey(User)
      name = models.CharField(max_length=255)
      description = models.TextField(max_length=500)
      keyword = models.TextField(max_length=300)
      date = models.DateTimeField(editable=False)
     
      def save(self,*args,**kwargs):
          if not self.id :
              self.date = datetime.datetime.today()  
          return super(Bug,self).save(*args,**kwargs)	

class Function(models.Model):
      document = models.CharField(max_length=255)
      name = models.TextField(max_length=400)
      line_no = models.IntegerField()
           	
   
