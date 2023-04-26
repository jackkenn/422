from myapp.forms import UploadFileForm
from PIL import Image, ImageOps, ImageFilter
from django.shortcuts import render, redirect
import os

def index(request, user):
	query = request.GET.get('query', "")
	photos = []
	for photo in os.listdir(os.path.normpath(os.path.dirname(__file__)).replace('\\', '/') + '/templates/static/output/' + user):
		if(query.lower() in photo.lower() or query == ""):
			photos.append(photo)
	return render(request, 'index.html', {'user': user, 'photos': photos})

def guest(request):
	photos = []
	for user in os.listdir(os.path.normpath(os.path.dirname(__file__)).replace('\\', '/') + '/templates/static/output/'):
		for photo in os.listdir(os.path.normpath(os.path.dirname(__file__)).replace('\\', '/') + '/templates/static/output/' + user):
			photos.append(user + '/' + photo)
	return render(request, 'guest.html', {'user': user, 'photos': photos})


def signup(request):
	if request.method == 'POST':
		os.mkdir('myapp/templates/static/output/' + request.POST['username'].replace(',', ''))
		userDB = open('myapp/templates/static/users.txt', 'a')
		userDB.write(request.POST['username'].replace(',', '') + ',' + request.POST['password'].replace(',', '') + '\n')
		userDB.close()
		return render(request, 'login.html')
	return render(request, 'signup.html')

def login(request):
	if request.method == 'POST':
		userDB = open('myapp/templates/static/users.txt')
		for line in userDB:
			if line.split(',')[0] == request.POST['username'].replace(',', '') and line.split(',')[1][:-1] == request.POST['password'].replace(',', ''):
				userDB.close()
				return redirect("index/" + request.POST['username'].replace(',', '') + '/')
		userDB.close()
	return render(request, 'login.html')

def resize_image(image_path, size, save_path):
    """Resize an image and save it to a new file."""
    with Image.open(image_path) as image:
        resized_image = image.resize(size)
        resized_image.save(save_path)

def resize(request, user):
    """TODO: choose size"""
    if request.method == 'POST':
        image_file = request.FILES['image']
        image_path = os.path.join('media', image_file.name)
        with open(image_path, 'wb+') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        resize_image(image_path, (int(request.POST['length']), int(request.POST['width'])), os.path.normpath(os.path.dirname(__file__)).replace('\\', '/') + '/templates/static/output/' + user + '/' + image_file.name)
        return redirect("/index/" + user + '/')
    return render(request, 'resize.html')

def applyfilter(filename, preset):
	inputfile = os.path.normpath(os.path.dirname(__file__)).replace('\\', '/') + '/../media/' + filename

	f=filename.split('.')
	outputfilename = f[0] + '-out.jpg'

	outputfile = os.path.normpath(os.path.dirname(__file__)).replace('\\', '/') + '/templates/static/output/' + outputfilename

	im = Image.open(inputfile)
	if preset=='gray':
		im = ImageOps.grayscale(im)

	if preset=='edge':
		im = ImageOps.grayscale(im)
		im = im.filter(ImageFilter.FIND_EDGES)

	if preset=='poster':
		im = ImageOps.posterize(im,3)

	if preset=='solar':
		im = ImageOps.solarize(im, threshold=80) 

	if preset=='blur':
		im = im.filter(ImageFilter.BLUR)
	
	if preset=='sepia':
		sepia = []
		r, g, b = (239, 224, 185)
		for i in range(255):
			sepia.extend((r*i/255, g*i/255, b*i/255))
		im = im.convert("L")
		im.putpalette(sepia)
		im = im.convert("RGB")

	im.save(outputfile)
	return outputfilename

def handle_uploaded_file(f,preset):
	uploadfilename='media/' + f.name
	with open(uploadfilename, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

	outputfilename=applyfilter(f.name, preset)
	return outputfilename

def home(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			preset=request.POST['preset']
			outputfilename = handle_uploaded_file(request.FILES['myfilefield'],preset)
			return render(request, 'process.html',{'outputfilename': outputfilename})
	else:
		form = UploadFileForm() 
	return render(request, 'index.html',{'form': form})

def process(request):
	return render(request, 'process.html')


