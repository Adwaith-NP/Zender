from django.http import JsonResponse
import json


def giveUserId(request):
    with open("relay/topUser.json","r") as file:
        data = json.load(file)
    print(data)
    newNumber = data['topNumber'] + 1
    data['topNumber'] = newNumber
    
    with open("relay/topUser.json", "w") as file:
        json.dump(data, file)
        
    topUserId = f"user{newNumber}"  # update after assigning
    return JsonResponse({'newUserId': topUserId})