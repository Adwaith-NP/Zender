from django.http import JsonResponse
import json
from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent


def giveUserId(request):
    path = os.path.join(BASE_DIR,"topUser.json")
    with open(path,"r") as file:
        data = json.load(file)
    print(data)
    newNumber = data['topNumber'] + 1
    data['topNumber'] = newNumber
    
    with open(path, "w") as file:
        json.dump(data, file)
        
    topUserId = f"user{newNumber}"  # update after assigning
    return JsonResponse({'newUserId': topUserId})