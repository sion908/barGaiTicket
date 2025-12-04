from django.shortcuts import render

from config import setting


def trans(request):
    context = {'liff_id': setting.LIFF_ID}
    # print(request.GET.get("poe"))
    # if "poe" in request.GET:
    #     print(request.GET.get("poe"))
    #     context['name'] = request.GET.get("poe")

    return render(request, 'trans/trans.html', context)


def showDashboad(request):
    context = {'liff_id': setting.LIFF_ID_OWNER}
    # print(request.GET.get("poe"))
    # if "poe" in request.GET:
    #     print(request.GET.get("poe"))
    #     context['name'] = request.GET.get("poe")

    return render(request, 'trans/dashboard.html', context)
