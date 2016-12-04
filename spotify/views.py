# -*- coding: utf-8 -*-
import requests
import json
import base64

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from spotify.models import SpotifyUser
from lastify.settings import SPOTIFY

@login_required
def spotify_connect(request):
	# TODO : Implémenter un state pour + de sécurité
	custom_callback = request.build_absolute_uri(reverse('spotify_callback'))
	scope = "playlist-modify-private playlist-read-private playlist-modify-public"
	return HttpResponseRedirect("https://accounts.spotify.com/authorize?\
client_id={}&response_type=code&redirect_uri={}&scope={}".format(SPOTIFY['CLIENT_KEY'], \
	custom_callback, scope))

@login_required
def spotify_callback(request):
	if "code" in request.GET:
		code = request.GET["code"]
		custom_callback = request.build_absolute_uri(reverse('spotify_callback'))
		data = {"grant_type": "authorization_code", "code": code, "redirect_uri": custom_callback, \
				"client_id": SPOTIFY['CLIENT_KEY'], "client_secret": SPOTIFY['CLIENT_SECRET']}

		r = requests.post("https://accounts.spotify.com/api/token", data=data)
		result = json.loads(r.content)

		if "access_token" in result and "refresh_token" in result:
			# On a le token et le refresh token, on stock tout ça en bdd

			# On a chercher le username Spotify de l'utilisateur
			r = requests.get("https://api.spotify.com/v1/me", headers={'Authorization': 'Bearer {}'.format(result["access_token"])})
			username = json.loads(r.content)["id"]

			# On vérifie que le user soit pas déjà linké 
			try: # L'utilisateur est déjà lié, on va écraser la liaison
				check = SpotifyUser.objects.filter(user=request.user)[:1].get()
				if not check.user.username == request.user.username:
					return HttpResponse("Someone is already linked with this Spotify user")
				check.token = result["access_token"]
				check.refresh_token = result["refresh_token"]
				check.username = username
				check.save()

				return HttpResponse("Votre compte était déjà lié, l'ancienne liaison a été écrasée<br /><br /> \
		<a href=\"{}\">Go back to my settings</a>".format(reverse("account_settings")))
			except SpotifyUser.DoesNotExist: # Il est pas lié, on va save oklm
				user = SpotifyUser(user=request.user, username=username, token=result["access_token"], \
								 refresh_token=result["refresh_token"])
				user.save()
				return HttpResponse("Votre compte Spotify est maintenant lié !<br /><br /> \
		<a href=\"{}\">Go back to my settings</a>".format(reverse("account_settings")))
		elif "error" in result:
			return HttpResponse("Erreur: {}".format(result['error']))
		else:
			return HttpResponse("Spotify account is not linked : Error no1")
	elif "error" in result:
		return HttpResponse(result['error'])
	else:
		return HttpResponse("Spotify account is not linked : code is missing.")

@login_required
def spotify_unlink(request):
	# On regarde si l'utilisateur était lié
	try:
		sptf = SpotifyUser.objects.filter(user=request.user)[:1].get()
		sptf.delete()
		return HttpResponse("Your account has been unlinked. \
		<a href=\"{}\">Go back to my settings</a>".format(reverse("account_settings")))
	except SpotifyUser.DoesNotExist:
		return HttpResponse("You don't have any account linked !. \
		<a href=\"{}\">Go back to my settings</a>".format(reverse("account_settings")))