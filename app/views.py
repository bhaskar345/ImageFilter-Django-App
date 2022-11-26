import cv2
import os
import numpy as np
from django.shortcuts import render
from django.http import HttpResponse
from .forms import *
from django.conf import settings
from unidecode import unidecode


def gamma_function(channel, gamma):
    invGamma = 1/gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8") #creating lookup table
    channel = cv2.LUT(channel, table)
    return channel

def image_view(request):

    form = ImageForm()

    if request.method == 'POST':
        try:
            file = request.FILES['Original']
            obj_got, created = Image.objects.get_or_create(Original = file)
            image = cv2.imread(obj_got.Original.path)

            if request.POST.get('filter') == 'B&W':
                effect=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

            if request.POST.get('filter') == 'Blur':           
                kernel = np.ones((5,5),np.float32)/25
                effect = cv2.filter2D(image,-1,kernel)

            if request.POST.get('filter') == 'Bright':
                effect=cv2.convertScaleAbs(image, beta=60)

            if request.POST.get('filter') == 'LessBright':
                effect=cv2.convertScaleAbs(image, beta=-60)

            if request.POST.get('filter') == 'Sharp':
                kernel = np.array([[-1, -1, -1], [-1, 9.5, -1], [-1, -1, -1]])
                effect = cv2.filter2D(image, -1, kernel)

            if request.POST.get('filter') == 'Sepia':
                img_sepia = np.array(image, dtype=np.float64)
                img_sepia = cv2.transform(img_sepia, np.matrix([[0.272, 0.534, 0.131],
                                        [0.349, 0.686, 0.168],
                                        [0.393, 0.769, 0.189]]))
                img_sepia[np.where(img_sepia > 255)] = 255
                effect = np.array(img_sepia, dtype=np.uint8)

            if request.POST.get('filter') == 'Sketch(B&W)':
                effect, sk_color = cv2.pencilSketch(image, sigma_s=60, sigma_r=0.07, shade_factor=0.1)

            if request.POST.get('filter') == 'Sketch(Colour)':
                sk_grey, effect = cv2.pencilSketch(image, sigma_s=60, sigma_r=0.07, shade_factor=0.1)

            if request.POST.get('filter') == 'HDR':
                effect=cv2.detailEnhance(image, sigma_s=12, sigma_r=0.15)

            if request.POST.get('filter') == 'Invert':
                effect=cv2.bitwise_not(image)

            if request.POST.get('filter') == 'Summer':
                image[:, :, 0] = gamma_function(image[:, :, 0], 0.75) # down scaling blue channel
                image[:, :, 2] = gamma_function(image[:, :, 2], 1.25) # up scaling red channel
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                hsv[:, :, 1] = gamma_function(hsv[:, :, 1], 1.2) # up scaling saturation channel
                effect = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            if request.POST.get('filter') == 'Winter':
                image[:, :, 0] = gamma_function(image[:, :, 0], 1.25)
                image[:, :, 2] = gamma_function(image[:, :, 2], 0.75)
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                hsv[:, :, 1] = gamma_function(hsv[:, :, 1], 0.8)
                effect = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            cv2.imwrite(os.path.join(settings.MEDIA_ROOT, f'filtered_{obj_got.Original}'), effect)
            obj_got.Img = f'filtered_{obj_got.Original}'
            obj_got.save()
            return render(request, 'filtered.html',{'obj': obj_got})
        except Exception as err:
            print(err)
            return HttpResponse(status=500)
    return render(request, 'Image.html', {'form' : form})