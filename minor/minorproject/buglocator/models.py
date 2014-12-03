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
      keywords = models.TextField(max_length=300)
      date = models.DateTimeField(editable=False)
     
      def save(self,*args,**kwargs):
          if not self.id :
              self.date = datetime.datetime.today()  
          return super(Bug,self).save(*args,**kwargs)	

class Function(models.Model):
      document = models.CharField(max_length=255)
      name = models.TextField(max_length=400)
      line_no = models.IntegerField()
           	
class BugLocation(models.Model):
      bug = models.ForeignKey(Bug)
      file_path = models.CharField(max_length=255)
      keyword = models.CharField(max_length=255)
      line_no = models.TextField(max_length=2000)
      inFunction = models.TextField(max_length=1000) 
    
