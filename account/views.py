# -*- coding: utf-8 -*-
from django.shortcuts import render, render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from account.forms import LoginForm
from lastfm.models import LastfmUser
from spotify.models import SpotifyUser

def login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('account_settings'))

	if request.method == "POST":
		form = LoginForm(request.POST)

		if form.is_valid():
			# On a des données, on peut les traiter
			username = form.cleaned_data["username"]
			password = form.cleaned_data["password"]

			user = auth.authenticate(username=username, password=password)

			if user is not None:
				if user.is_active:
					# User trouvé ! On peut le connecter
					auth.login(request, user)

					# On va check si l'utilisateur venait d'une page ou pas, si oui on le redirige, sinon on l'envoi sur les settings
					if "next" in request.GET:
						return HttpResponseRedirect(request.GET["next"])
					else:
						return HttpResponseRedirect(reverse('account_settings'))
				else:
					#Utilisateur trouvé mais inactif
					error, msg = True, "Un utilisateur a été trouvé mais celui-ci est désactivé."
			else:
				#Utilisateur introuvable
				error, msg = True, "Votre nom d'utilisateur ou mot de passe est incorrect."
	else:
		# Page de base
		form = LoginForm()

	return render(request, 'account/login.html', locals())

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect(reverse('account_login'))

@login_required
def settings(request):
	request.user.isLinked = {}

	# On regarde si l'utilisateur a lié son compte LastFM
	try:
		lfm = LastfmUser.objects.filter(user=request.user)[:1].get()
		request.user.isLinked['lfm'] = True
	except LastfmUser.DoesNotExist:
		request.user.isLinked['lfm'] = False

	# On regarde si l'utilisateur a lié son compte Spotify
	try:
		sptf = SpotifyUser.objects.filter(user=request.user)[:1].get()
		request.user.isLinked['sptf'] = True
	except SpotifyUser.DoesNotExist:
		request.user.isLinked['sptf'] = False

	return render(request, 'account/settings.html', locals())
