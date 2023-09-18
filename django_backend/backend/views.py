from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from .models import IPCamera, history
import datetime
from datetime import timedelta
import hashlib
import csv
import os
import docker
import pytz
# Create your views here.

def Home(request):
    return render(request, "home.html", {})

def restart():
    docker.from_env().containers.get("IPCam_Controller").restart()
    docker.from_env().containers.get("video2plate").restart()
    docker.from_env().containers.get("plate2char").restart()

def Export(request, filename):
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"../data/csv/{filename}.csv"), "r") as f:
        file_data = f.read()
        # sending response 
        response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    return response

def Setting_Plate(request):
    return render(request, "Setting_Plate.html", {})

def Setting_IPCam(request):
    if request.method == "POST":
        form = IPCamera(Source = request.POST["Source"], Entrance_Code = request.POST["Entrance_Code"], Entrance_Name = request.POST["Entrance_Name"])
        form.save()
        # restart()
    IPCameras = IPCamera.objects.all()
    return render(request, "Setting_IPCam.html", {"IPCameras" : IPCameras})

def Access_Recording(request):
    startdate = datetime.datetime.today().replace(tzinfo=datetime.timezone.utc) - timedelta(days = 1)
    enddate = datetime.datetime.today().replace(tzinfo=datetime.timezone.utc)
    plate = ""
    if request.method == "POST":
        startdate = datetime.datetime.today().replace(tzinfo=datetime.timezone.utc) - timedelta(days = 1) if request.POST["startdate"] == "" else datetime.datetime.strptime(request.POST["startdate"], "%Y-%m-%dT%H:%M").replace(tzinfo=datetime.timezone.utc)
        enddate = datetime.datetime.today().replace(tzinfo=datetime.timezone.utc) if request.POST["enddate"] == "" else datetime.datetime.strptime(request.POST["enddate"], "%Y-%m-%dT%H:%M").replace(tzinfo=datetime.timezone.utc)
        plate = "" if request.POST["plate"] == "" else request.POST["plate"]
    historys = history.objects.filter(Timestamp__range = (startdate, enddate), Plate__contains=plate)
    for row in historys:
        if row.Timestamp.replace(tzinfo = pytz.timezone('Asia/Taipei')) < (datetime.datetime.now() - timedelta(days = 7)).replace(tzinfo = pytz.timezone('Asia/Taipei')):
            filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), f"../data/images/{row.Image}.jpg")
            if os.path.exists(filename):
                os.remove(filename)
    filename = hashlib.sha256(str(datetime.datetime.now()).encode("utf-8")).hexdigest()
    file = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"../data/csv/{filename}.csv"), "w")
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Plate', 'Entrance_Name', 'Color', 'Image'])
    for row in historys:
        writer.writerow([row.Timestamp, row.Plate, row.Entrance, row.Color, row.Image])
    file.close()
    return render(request, "Access_Recording.html", {"History" : historys, "csv" : filename})

def delete_IPCamera(request):
    if request.method == "POST":
        ob = IPCamera.objects.get(Source = request.POST["Source"])
        ob.delete()
        # restart()
    return redirect('/Setting_IPCam/')

def images(request, filename):
    img = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"../data/images/{filename}"), "rb")
    response = FileResponse(img)
    return response