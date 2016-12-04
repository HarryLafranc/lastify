# -*- coding: utf-8 -*-
import requests
import json

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from utils import LastFMUtil
from lastify.settings import LASTFM
from lastfm.models import LastfmUser
from spotify.models import SpotifyUser

def index(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse("account_settings"))
	return render_to_response('lastfm/index.html', locals(), context_instance=RequestContext(request))

@login_required
def lastfm_connect(request):
	custom_callback = request.build_absolute_uri(reverse('lastfm_callback'))
	return HttpResponseRedirect("http://www.last.fm/api/auth/?api_key={}&cb={}".format(LASTFM["API_KEY"], custom_callback))

@login_required
def lastfm_callback(request):
	token = request.GET['token']
	lastfm = LastFMUtil(token)

	user = lastfm.connectUser()

	if not user: # Erreur lors de la connexion à LFM
		return HttpResponse("Error while logging in LastFM (error no 1)")

	msg = ""

	# On vérifie si il n'y a pas déjà quelqu'un de lié à ce compte LFM
	try:
		check = LastfmUser.objects.filter(username=user)[:1].get()
		if not check.user.username == request.user.username: # Si c'est pas l'utilisateur en cours
			return HttpResponse("Someone is already linked with this LastFM user")
		else:
			msg = "Your account was already linked. We deleted the older connection with \
				 the LastFM account \"{}\" and made a new one.<br />".format(check.username)
			obj = check
	except LastfmUser.DoesNotExist:
		obj = LastfmUser()

	# C'est bon, on peut linker
	# On MàJ la tâble de relation user-lastfm
	obj.username = user
	obj.user = request.user
	obj.save()

	return HttpResponse("{} LastFM account \"{}\" is now linked with your Lastify account.<br /><br /> \
		<a href=\"{}\">Go back to my settings</a> ".format(msg, user, reverse("account_settings")))

@login_required
def lastfm_unlink(request):
	# On regarde si l'utilisateur était lié
	try:
		lfm = LastfmUser.objects.filter(user=request.user)[:1].get()
		lfm.delete()
		return HttpResponse("Your account has been unlinked. \
		<a href=\"{}\">Go back to my settings</a>".format(reverse("account_settings")))
	except LastfmUser.DoesNotExist:
		return HttpResponse("You don't have any account linked !. \
		<a href=\"{}\">Go back to my settings</a>".format(reverse("account_settings")))

@login_required
def lastfm_synchronise(request, period):
	# Avant tout, on check si la période est valide
	accepted_periods = ["overall", "7day", "1month", "3month", "6month", "12month"]
	if not period in accepted_periods:
		return HttpResponse("Invalid period.")

	# On regarde si l'utilisateur est lié à LastFM, puis à Spotify
	try:
		lfm = LastfmUser.objects.filter(user=request.user)[:1].get()
	except LastfmUser.DoesNotExist:
		return HttpResponse("Your LastFM account is not linked. \
		<a href=\"{}\">Link your LastFM account</a>".format(reverse("lastfm_connect")))

	try:
		sptf = SpotifyUser.objects.filter(user=request.user)[:1].get()
	except SpotifyUser.DoesNotExist:
		return HttpResponse("Your Spotify account is not linked. \
		<a href=\"{}\">Link your Spotify account</a>".format(reverse("spotify_connect")))

	# On va créer une playlist à l'utilisateur
	data = {"name": "Lastify Dev ({})".format(period), "public":False}
	try:
		print "Creating the playlist..."
		r = requests.post("https://api.spotify.com/v1/users/{}/playlists".format(sptf.username), \
			data=json.dumps(data), headers={'Authorization': 'Bearer {}'.format(sptf.token)})
	except:
		return HttpResponse("Error while creating the Spotify Playlist")

	if "error" in json.loads(r.content):
		error = json.loads(r.content)["error"]
		return HttpResponse("Error with Spotify : {}".format(error["message"]))
	elif "id" in json.loads(r.content):
		playlist_id = json.loads(r.content)["id"]

	# On va demander à LastFM les chansons écoutées cette semaine par l'utilisateur
	lastfm = LastFMUtil()
	print "Getting the TopTracks from LastFM..."
	response = lastfm.makeAPICall("user.gettoptracks",lfm.username, \
		"&limit=15&period={}".format(period))

	if not response:
		return HttpResponse("LastFM timed out")

	uris = ""
	notfound = ""

	# Pour chaque titre, on va chercher la chanson Spotify. Si on trouve pas, on prévient l'utilisateur
	for track in response["toptracks"]['track']:
		title = "{} {}".format(track["name"].encode('UTF-8'), track["artist"]["name"].encode('UTF-8'))

		print "[Checking Track] {}".format(title)

		# Maintenant qu'on a le titre, on peut aller chercher la musique dans l'API Spotify
		try:
			print "Searching the track in Spotify..."
			r = requests.get("https://api.spotify.com/v1/search?q={}&type={}&limit=1".format(title, "track"))
		except:
			return HttpResponse("Error while searching the track \"{}\" in Spotify".format(title))

		try:
			track_id = json.loads(r.content)["tracks"]["items"][0]["id"]
			uris += "spotify:track:{},".format(track_id)
		except IndexError:
			notfound += "{}, ".format(title)
			print "[NOT FOUND] Title: ", title, "Search: ",json.loads(r.content)["tracks"]

	# On a les id de toutes les chansons, on les ajoute à la playlist
	try:
		print "Adding songs to the playlist..."
		r = requests.post("https://api.spotify.com/v1/users/{}/playlists/{}/tracks?uris={}".format(sptf.username, \
			playlist_id, uris), headers={'Authorization': 'Bearer {}'.format(sptf.token)})
	except:
		return HttpResponse("Error while adding tracks to the playlist")

	print "Request AddPlaylist", r.content
	return HttpResponse("Your playlist is now created. Titles not found : {}<br /><br /> \
		<a href=\"https://open.spotify.com/user/{}/playlist/{}\">Click here to check your playlist !</a>".format(notfound, sptf.username, playlist_id))

