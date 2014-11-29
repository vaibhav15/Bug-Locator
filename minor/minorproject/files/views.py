from django.shortcuts import render
from django.contrib.auth.models import User
from Api.models import tempUser,Profile,PredictionDetail,Team,LeagueType,Prediction,CompletedText,League,PurchasedPrediction,PurchasedCredit,UserCredit,Unit
from Api.serializer import tempUserSerializer,ProfileSerializer,PredictionSerializer,PredictionDSerializer,UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes	
from rest_framework import status
import random,string
from rest_framework.renderers import JSONRenderer 
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password,check_password	
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
import base64,json
from django.utils import simplejson
from push_notifications.models import APNSDevice, GCMDevice
from django.db.models import Sum

URL = "178.21.172.107"
@api_view(['POST'])
def registration(request):
    if request.method=='POST':
       content = ("Hello Welcome to your new LiveBetTips account.\nYou can log in right away and start using your new account.\n"
                  "Please take a moment to confirm your email address with us by clicking in link below.")
       encode = base64.b64encode(request.DATA["email"]+":"+request.DATA["password"])
    try:
        user = User.objects.get(email = request.DATA["email"])
    except:
        post_values = request.DATA.copy()
        password = post_values["password"]
        password = make_password(password)
        post_values["password"] = password  
        serializer =  tempUserSerializer(data=post_values)
        if serializer.is_valid():
           serializer.save()
        
           confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33)) 
           profile = Profile(username = request.DATA["email"] , confirmationCode = confirmation_code,authToken = encode)
           profile.save()
           
           send_mail("LiveBetTips Account Confirmation",content+"\n"+URL+"/confirmation/"+str(profile.confirmationCode) 
                     + "/"+profile.username,'no-reply@LiveBetTips.com',[profile.username],fail_silently=False)
           return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status = status.HTTP_409_CONFLICT)

    return Response(status = status.HTTP_409_CONFLICT)

def confirmation(request,confirmation_code,emailID):
     
   try:
      temp_user = tempUser.objects.get(email=emailID)
   except:
      return HttpResponse("Sorry your doesnt exist.Please register again")
   
   profile = Profile.objects.get(username =temp_user.email)
   if profile.confirmationCode == confirmation_code:
      user = User(username=temp_user.email, email = temp_user.email ,password = temp_user.password)                 
      user.save()
      usercredit = UserCredit(user = user , credit = 1)
      usercredit.save()      
      temp_user.delete()
      return HttpResponse("Thankyou! Your account has been activated .Now you can login")
   return HttpResponse("Sorry your account couldn't be activated this time. Please try again later")

@api_view(['POST'])
def resetPassword(request):
    if request.method=='POST':
    
     try:
        user = User.objects.get(email = request.DATA['email'])      
     except : 
        return Response(status = status.HTTP_404_NOT_FOUND)
     send_mail("LiveBetTips Password Reset","Click on the link below to reset your password.\n"+URL+"/reset-password/"
               ,'no-reply@LiveBetTips.com',[user.email],fail_silently=False)
     return Response(status = status.HTTP_200_OK) 

def setNewPassword(request):
    if request.method == 'POST':
       
      try:
        user = User.objects.get(email = request.POST['email'])  
      except:
        return HttpResponse("Sorry EmailID doesn't exist.Please go back and re-enter your email id")
      
      encode = base64.b64encode(user.email + ":" + request.POST['password'])
      pro= Profile.objects.get(username = user.email)
      pro.authToken = encode
      pro.save()
      password = make_password(request.POST['password'])
      user.password = password 
      user.save()
      return HttpResponse("Your Password has been reset.")  
    return render(request , 'Api/resetForm.html',{ })     

@api_view(['POST'])
def login(request):
   if request.method=='POST':
   
     try:
         user = User.objects.get(email = request.DATA["email"])
     except: 
         try:
            temp_user = tempUser.objects.get(email = request.DATA["email"])
         except : 
            return Response(status=status.HTTP_404_NOT_FOUND)
         return Response(status=status.HTTP_409_CONFLICT)
   
     try:
          profile = Profile.objects.get(username = user.email) 
          usercredit = UserCredit.objects.get(user_id = user.id)
          credit = usercredit.credit
     except : 
          credit = 0 
     
     response_data = {}
     response_data['id'] = user.id
     response_data['authToken'] = profile.authToken
     response_data['usercredit'] = credit 
    
     if check_password(request.DATA["password"],user.password) :
        if request.DATA["deviceType"] == "Android" :
           gcm_id = request.DATA["deviceID"]
           new_device = GCMDevice(user = user,registration_id = gcm_id)
           #check if gcm_id already exists . If so then delete the old device and create new .
           try :
              old_device = GCMDevice.objects.get(registration_id = gcm_id)
           except :
              new_device.save()
              return HttpResponse(json.dumps(response_data),content_type="application/json")
           old_device.delete()
           new_device.save()
           return HttpResponse(json.dumps(response_data),content_type="application/json")

        elif request.DATA["deviceType"] == "ios" :
             apns_id = request.DATA["deviceID"]
             new_device = APNSDevice(user = user,registration_id = apns_id)
           #check if gcm_id already exists . If so then delete the old device and create new .
             try :
                old_device = APNSDevice.objects.get(registration_id = apns_id)
             except :
                new_device.save()
                return HttpResponse(json.dumps(response_data),content_type="application/json")
             old_device.delete()
             new_device.save()
             return HttpResponse(json.dumps(response_data),content_type="application/json")
        return HttpResponse(json.dumps(response_data),content_type="application/json")

     return Response(status = status.HTTP_401_UNAUTHORIZED) 
    
@api_view(['POST'])
@permission_classes((IsAuthenticated ,))
def contactUs(request) :
   if request.method=='POST':
      adminEmail= 'sarthakmeh03@gmail.com'
      userEmail = request.DATA["email"]
      message   = request.DATA["content"]
      subject   = request.DATA["subject"]
      send_mail(subject,message,userEmail,[adminEmail],fail_silently=False)
      return Response(status = status.HTTP_200_OK)
   return Response(status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def showPredictions(request):
     
    if request.method=='GET':
      try:
       predictions = Prediction.objects.filter(isPushNotifSend=request.GET.get('isPushed',0))
      except : 
         return Response(status = status.HTTP_404_NOT_FOUND)    
           
      predictSerializer = PredictionSerializer(predictions) 
      return Response(predictSerializer.data,status = status.HTTP_200_OK)
    return Response(status =status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((IsAuthenticated ,))
def predictionDetail(request,userID,tipID):
    if request.method=='GET':
       
      try:  
        user = User.objects.get(id = userID)
      except:
        return Response(status = status.HTTP_404_NOT_FOUND)

      try:   
       tip = Prediction.objects.get(id = tipID)
      except:
       return Response(status = status.HTTP_400_BAD_REQUEST)
      
      prediction = PredictionDetail.objects.get(id = tip.tipDetail_id)      
      if tip.isCompleted == True : 
         completedText = CompletedText.objects.get(id = tip.completedText_id) 
         prediction.message = prediction.message + ". "+completedText.message   
               
         predictionSerializer = PredictionDSerializer(prediction)
         return Response(predictionSerializer.data,status = status.HTTP_200_OK)
      else : 
         try:
          purchasePrediction=PurchasedPrediction.objects.get(userID = userID,predictionID = tipID)
         except: 
           return Response(status = status.HTTP_401_UNAUTHORIZED)
    
         predictionSerializer = PredictionDSerializer(prediction)
         return Response(predictionSerializer.data , status=status.HTTP_200_OK)
      return Response(status = status.HTTP_404_NOT_FOUND)    
            
@api_view(['GET'])
@permission_classes((IsAuthenticated ,))
def userPredictions(request,userID):
    if request.method == 'GET':
       predictions = [] 
       
       try: 
         user = User.objects.get(id = userID)
       except: 
         return Response(status = status.HTTP_404_NOT_FOUND)
       
       try:      
         userPredicts = PurchasedPrediction.objects.filter(userID = userID)
       except : 
         return Response(status = status.HTTP_404_NOT_FOUND)
       error = 0 
       for predict in userPredicts :
         try:
          predicts=Prediction.objects.get(id = predict.predictionID)
         except :
          error = 1 
         if error != 1 :  
             predictions.append(predicts)
            
       predictSerializer = PredictionSerializer(predictions)
       return Response(predictSerializer.data , status = status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((IsAuthenticated ,))
def logout(request):
    if request.method == 'POST' :
       try : 
          device = GCMDevice.objects.get(registration_id = request.DATA["deviceID"])
       except :
          return Response(status = status.HTTP_400_BAD_REQUEST)
       device.active = False;
       device.save()
       return Response(status = status.HTTP_200_OK)

@api_view(['GET'])
def filter(request):
    if request.method == 'GET' :
       try : 
          leagueType = LeagueType.objects.values_list('name', flat=True).distinct()
          predictionDetail = PredictionDetail.objects.values_list('name', flat=True).distinct()
          units = Unit.objects.latest('id')
       except :  
          return Response(status = status.HTTP_400_BAD_REQUEST)
       list1 = []
       list2 = []
       response_data = {}
       for league in leagueType :
          list1.append((league))
 	
       for prediction in predictionDetail:
          list2.append((prediction))
       response_data['leagueType'] = list1
       response_data['predictionName']= list2
       response_data['units']=units.value
       return HttpResponse(json.dumps(response_data),content_type="application/json")
 
@api_view(['GET'])
def filterPredictions(request):
    if request.method == 'GET':
       league = request.GET.get('league','null')
       predictionName = request.GET.get('predictionName','null')   
       if league != 'null' and predictionName == 'null' : 
          try :
             filter_predictions = Prediction.objects.filter(leagueType_id=request.GET.get('league',0),isPushNotifSend=True)
          except :
             return Response(status = status.HTTP_404_NOT_FOUND)

          predictions = PredictionSerializer(filter_predictions) 
          return Response(predictions.data,status = status.HTTP_200_OK)
       elif league == 'null' and predictionName != 'null' :
            try :
               tips = PredictionDetail.objects.filter(name = predictionName) 
               predictions = Prediction.objects.filter(isPushNotifSend=True)
            except :
               return Response(status = status.HTTP_404_NOT_FOUND)
            
            filter_predictions = []
            for tip in tips :
                for prediction in predictions:
                      if prediction.tipDetail_id == tip.id :
                         filter_predictions.append(prediction)     
            
            predictions = PredictionSerializer(filter_predictions) 
            return Response(predictions.data,status = status.HTTP_200_OK)
       else :      
            try:
                 filter_predictions = Prediction.objects.filter(leagueType_id=request.GET.get('league',0),isPushNotifSend=True)        
                 tips = PredictionDetail.objects.filter(name = predictionName)
            except :
                 return Response(status = status.HTTP_404_NOT_FOUND)
           
            predictions = []
            for tip in tips :
                for prediction in filter_predictions:
                    if prediction.tipDetail_id == tip.id :
                       predictions.append(prediction)               

            serialPredictions = PredictionSerializer(predictions)
            return Response(serialPredictions.data,status = status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((IsAuthenticated ,))
def creditsPurchased(request):
    if request.method == 'POST':
      
       response_data = {} 
       purchaseCredit = int(request.DATA["credit"])
       try:
          user = User.objects.get(id = request.DATA["userID"])
       except:
          return Response(status= status.HTTP_400_BAD_REQUEST)                 
       
       credit = PurchasedCredit(userID = request.DATA["userID"],credit =request.DATA["credit"],creditID = request.DATA["creditID"])
       credit.save()

       try :
          user_credit = UserCredit.objects.get(user_id = user.id)
       except :
          usercredit = UserCredit ( user = user , credit = purchaseCredit)
          usercredit.save()
          return Response(status = status.HTTP_200_OK) 
       user_credit.credit += purchaseCredit 
       user_credit.save()
       response_data["credit"]= user_credit.credit

       return HttpResponse(json.dumps(response_data),content_type="application/json")

@api_view(["POST"])
@permission_classes((IsAuthenticated ,))
def predictionPurchased(request):
    if request.method == 'POST' : 
       response_data = {}
       try : 
         usercredit = UserCredit.objects.get(user_id = request.DATA["userID"])      
       except:
         return Respones(status= status.HTTP_401_UNAUTHORIZED)
       if usercredit.credit != 0 :
          purchasedPrediction = PurchasedPrediction(userID = request.DATA["userID"] , predictionID = request.DATA["predictionID"])
          purchasedPrediction.save()       
          usercredit.credit = usercredit.credit - 1
          usercredit.save()
          response_data["credit"]=usercredit.credit
          return HttpResponse(json.dumps(response_data),content_type="application/json")
       else :
          return Response(status = status.HTTP_401_UNAUTHORIZED)
