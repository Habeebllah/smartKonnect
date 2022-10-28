from.models import *
from django.contrib.sites.models import Site
Site = Site.objects.first()



def categories_processor(request):
    config = WebsiteConfiguration.objects.all().first()
    net = Network.objects.all()
    checkbank = Disable_Service.objects.filter(service="Bankpayment")
    monnifybank = Disable_Service.objects.filter(service="Monnfy bank")
    monnifyATM = Disable_Service.objects.filter(service="Monnify ATM")
    paystack = Disable_Service.objects.filter(service="paystack")
    aircash = Disable_Service.objects.filter( service="Airtime_Funding")

    return {"banks":BankAccount.objects.all(), "networks":net,'whatsapp_group_link': config.whatsapp_group_link ,"support_phone":config.support_phone_number,"air2cash": aircash,"bank2": checkbank,"monnifyatm2": monnifyATM, "paystack2": paystack,"monnifybank2": monnifybank, "config":config, "mysite":Site}
