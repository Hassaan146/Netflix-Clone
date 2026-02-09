from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from .models import *
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
import re
from django.http import JsonResponse
from django.shortcuts import get_list_or_404

# Create your views here.

@login_required(login_url='/login/')
def index(request):
    movies = Movie.objects.all()
    featured_movie = movies[len(movies) - 1]
    return render(request,'index.html', {'movies' : movies , 'featured_movie' : featured_movie})

def login_page(request):
    if request.method == "POST":
        username =  request.POST.get('username')
        password = request.POST.get('password')
        user  = User.objects.filter(username=username)
        if user is not None:
            user_auth = authenticate(username=username,password=password)
            if user_auth is not None:
               login(request,user_auth)
               messages.success(request,"Login Successful")
               return redirect('/')
            else:
                messages.error(request,"Incorrect Password")
                return redirect(request,'/login/')
        else:
            messages.error(request,"Username doesnot exists")
            return redirect(request,'/login/')

    return render(request,'login.html')

@login_required(login_url='/login/')
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_pass = request.POST.get('confirm_password')
        if password == confirm_pass:
            if User.objects.filter(email=email).exists():
                messages.error(request,"Email already exists")
                return redirect('/register/')
            elif User.objects.filter(username=username).exists():
                messages.error(request,"Username already exists")
                return redirect('/register/')
            else:
                user = User.objects.create_user(username=username)
                user_pass = user.set_password(password=password)
                messages.success(request,"User created succesfuly")
                user.save()
                return redirect('/login/')
        else:
            messages.error(request,"Fields dont match")
            return redirect('/register/')
    return render(request,'register.html')

@login_required(login_url='/login/')
def movie(request, pk):
    movie_uuid = pk
    movie_details = Movie.objects.get(uu_id = movie_uuid)
    return render(request,'movie.html', {'movie_details' : movie_details}) 

@login_required(login_url='/login/')
def my_list(request):
    user = request.user
    movie_list = MovieList.objects.filter(owner_user=user)
    user_movie_list = []
    for movie in movie_list:
        user_movie_list.append(movie.movie)
    return render(request,'my_list.html', {'movie' : user_movie_list})



@login_required(login_url='/login/')
def logout_page(request):
   logout(request)
   return redirect('/login/')

@login_required(login_url='/login/')
def add_to_list(request):
    if request.method == "POST":
        movie_url_id =  request.POST.get('movie_id')
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern,movie_url_id)
        movie_id = match.group() if match else None
        movie = get_list_or_404(Movie,uu_id = movie_id )
        user =  request.user
        movie_list_created = MovieList.objects.get_or_create(owner_user = user)
        if movie_list_created:
           response_data = {'status' : 'success' , 'message' : 'Added'}
        else:
           response_data = {'status' : 'info' , 'message' : 'Already Added'}
        JsonResponse(response_data)
    return render(request,'my_list.html')

@login_required(login_url='/login/')
def search(request):
        search_term = request.POST['search_term']
        movies = Movie.objects.filter(title__icontains=search_term)
        return render(request,'search.html', {'movies' : movies , 'search_term' : search_term})
        
@login_required(login_url='/login/')
def genre(request,pk):
        movie_genre = pk
        movies = Movie.objects.filter(genre=movie_genre)
        return render(request, 'genre.html' , {'movies' : movies , 'movies_genre' : movie_genre})

