import logging




class DataAPIListView(APIView):
    permission_classes = (IsAuthenticated,)
    level = logging.INFO
    format = '  %(message)s'
    handlers = [logging.FileHandler('../django_logs/error_log.txt'), logging.StreamHandler()]
    logging.basicConfig(level=level, format=format, handlers=handlers)


def senddatasmeplug(net,plan_id,num):
    url = "https://smeplug.ng/api/v1/data/purchase"
    payload = {"network_id": net,"plan_id":plan_id,"phone": num}
    payload = json.dumps(payload)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {config.sme_plug_secret_key}'
    }
    response = requests.request("POST", url, headers=headers, data = payload)

    logging.error('sme response: ' + response.text)

    result = json.loads(response.text)
    respx = {
        "status": 0
    }
    if response.status_code != 200:
        logging.error('response code not 200')
        pass
    else:
        if 'data' in result and 'msg' in result["data"] and 'current_status' in result["data"]:
            logging.info('array complete')
            respx["msg"] = result['data']['msg']
            respx["current_status"] = result['data']['current_status']
            if respx["current_status"] == "processing" or respx["current_status"] == "success":
                respx['status'] = 1
                respx['ident'] = result['data']['reference'],
            else:
                pass

            if result['status']:
                respx['status'] = 1
            else:
                logging.info('result status NOT true')
                pass
        else:
            logging.info('array NOT complete')
            pass
    logging.info('our response: ' + json.dumps(respx))
    return respx


###################
if Network.objects.get(name=net).corporate_data_vending_medium == "SMEPLUG":
    resp = senddatasmeplug("1",plan.smeplug_id,num)
    if resp['status'] == 1:
        status = "successful"
    elif resp['status'] == 2:
        status = "processing"
    else:
        status = "failed"




##############################
def senddatasmeplug(net,plan_id,num):
    url = "https://smeplug.ng/api/v1/data/purchase"
    payload = {"network_id": net,"plan_id":plan_id,"phone": num}
    payload = json.dumps(payload)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {config.sme_plug_secret_key}'
    }
    print("payload",payload)
    response = requests.request("POST", url, headers=headers, data = payload)
    print(response.text)
    
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



#######        
if Network.objects.get(name=net).corporate_data_vending_medium == "SMEPLUG":
    resp = senddatasmeplug("1",plan.smeplug_id,num)
    status = resp



######## MSORG WEB a
try:
    if response.status_code == 200 or response.status_code == 201:
        result = json.loads(response.text)
        
        if 'Status' in result:
            if result['Status'] == "failed":
                status =  "failed"
            else:
                status =  "successful"
except:
    status = "processing"


#######
def msorg_senddata(netid,num,plan_id):
    url = f"{config.msorg_web_url}/api/data/"

    headers = {
    'Content-Type':'application/json',
    'Authorization': f'Token {config.msorg_web_api_key}'
    }
    param = {"network": netid,"mobile_number": num,"plan": plan_id,"Ported_number":True}
    param_data = json.dumps(param)
    response = requests.post(url, headers=headers, data=param_data)
    
    try:
        if response.status_code == 200 or response.status_code == 201:
            result = json.loads(response.text)
            
            if 'Status' in result:
                if result['Status'] == "failed":
                    return  "failed"
                else:
                    return  "successful"
        else:
            return "processing"
    except:
        return "processing"






########## confus
from .tokens import *

import requests,json
def msorgWebsite_Webhook(response):
    try:
        if response.status_code == 200 or response.status_code == 201:
            result = json.loads(response.text)
            
            if 'Status' in result:
                if result['Status'] == "failed":
                    return  "failed"
                else:
                    return  "successful"
        else:
            return "processing"
    except:
        return "processing"




def sendglad(network_id,num,plan_id):
    url = "https://bardetech.com/api/data/"

    payload = {"network": "0",
                "mobile_number": "323",
                "plan": "we",
                "Ported_number":True
                }
    headers = {
        'Authorization': 'Token dsfsdfs',
        'Content-Type': 'application/json'
    }
    payload_data = json.dumps(payload)
    response = requests.request("POST", url, headers=headers, data=payload_data) 
    return response 
    
resp = msorgWebsite_Webhook(sendglad("1",num,plan.hbkonnect_id))

status = resp

print(status)


# response = requests.post(url, headers=headers, data=payload)
# status = msorgWebsite_Webhook(response)






@require_POST
@csrf_exempt
def msorgWebsite_Webhook(request):
    data = request.body
    result = json.loads(data)
    
    try:
        if result.status == "failed":
            x  = Data.objects.get(ident = result.ident)
            x.status = "failed"
            x.save()
    except:
        pass
    return HttpResponse(status=200)
