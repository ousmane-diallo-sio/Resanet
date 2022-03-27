#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import *
from modeles import modeleResanet
from technique import datesResanet


app = Flask( __name__ )
app.secret_key = 'resanet'


@app.route( '/' , methods = [ 'GET' ] )
def index() :
	return render_template( 'vueAccueil.html' )

@app.route( '/usager/session/choisir' , methods = [ 'GET' ] )
def choisirSessionUsager() :
	return render_template( 'vueConnexionUsager.html' , carteBloquee = False , echecConnexion = False , saisieIncomplete = False )

@app.route( '/usager/seConnecter' , methods = [ 'POST' ] )
def seConnecterUsager() :
	numeroCarte = request.form[ 'numeroCarte' ]
	mdp = request.form[ 'mdp' ]

	if numeroCarte != '' and mdp != '' :
		usager = modeleResanet.seConnecterUsager( numeroCarte , mdp )
		if len(usager) != 0 :
			if usager[ 'activee' ] == True :
				session[ 'numeroCarte' ] = usager[ 'numeroCarte' ]
				session[ 'nom' ] = usager[ 'nom' ]
				session[ 'prenom' ] = usager[ 'prenom' ]
				session[ 'mdp' ] = mdp
				
				return redirect( '/usager/reservations/lister' )
				nG
			else :
				return render_template('vueConnexionUsager.html', carteBloquee = True , echecConnexion = False , saisieIncomplete = False )
		else :
			return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = True , saisieIncomplete = False )
	else :
		return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = False , saisieIncomplete = True)


@app.route( '/usager/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterUsager() :
	session.pop( 'numeroCarte' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )


@app.route( '/usager/reservations/lister' , methods = [ 'GET' ] )
def listerReservations() :
	print '[START] appResanet::listerReservations()'
	tarifRepas = modeleResanet.getTarifRepas( session[ 'numeroCarte' ] )
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	
	solde = '%.2f' % ( soldeCarte , )

	aujourdhui = datesResanet.getDateAujourdhuiISO()

	datesPeriodeISO = datesResanet.getDatesPeriodeCouranteISO()
	
	datesResas = modeleResanet.getReservationsCarte( session[ 'numeroCarte' ] , datesPeriodeISO[ 0 ] , datesPeriodeISO[ -1 ] )
	
	dates = []
	for uneDateISO in datesPeriodeISO :
		uneDate = {}
		uneDate[ 'iso' ] = uneDateISO
		uneDate[ 'fr' ] = datesResanet.convertirDateISOversFR( uneDateISO )
		
		if uneDateISO <= aujourdhui :
			uneDate[ 'verrouillee' ] = True
		else :
			uneDate[ 'verrouillee' ] = False

		if uneDateISO in datesResas :
			uneDate[ 'reservee' ] = True
		else :
			uneDate[ 'reservee' ] = False
			
		if soldeCarte < tarifRepas and uneDate[ 'reservee' ] == False :
			uneDate[ 'verrouillee' ] = True
			
			
		dates.append( uneDate )
	
	if soldeCarte < tarifRepas :
		soldeInsuffisant = True
	else :
		soldeInsuffisant = False

	print '[END] appResanet::listerReservations()'
	return render_template( 'vueListeReservations.html' , laSession = session , leSolde = solde , lesDates = dates , soldeInsuffisant = soldeInsuffisant )

	
@app.route( '/usager/reservations/annuler/<dateISO>' , methods = [ 'GET' ] )
def annulerReservation( dateISO ) :
	modeleResanet.annulerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.crediterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )
	
@app.route( '/usager/reservations/enregistrer/<dateISO>' , methods = [ 'GET' ] )
def enregistrerReservation( dateISO ) :
	modeleResanet.enregistrerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.debiterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )

@app.route( '/usager/mdp/modification/choisir' , methods = [ 'GET' ] )
def choisirModifierMdpUsager() :
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = '' )

@app.route( '/usager/mdp/modification/appliquer' , methods = [ 'POST' ] )
def modifierMdpUsager() :
	ancienMdp = request.form[ 'ancienMDP' ]
	nouveauMdp = request.form[ 'nouveauMDP' ]
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	if ancienMdp != session[ 'mdp' ] or nouveauMdp == '' :
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Nok' )
		
	else :
		modeleResanet.modifierMdpUsager( session[ 'numeroCarte' ] , nouveauMdp )
		session[ 'mdp' ] = nouveauMdp
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Ok' )


@app.route( '/gestionnaire/session/choisir' , methods = [ 'GET' ] )
def choisirSessionGestionnaire():
	return render_template('vueConnexionGestionnaire.html')



@app.route( '/gestionnaire/seConnecter', methods = [ 'POST' ] )
def seConnecterGestionnaire() :
	login = request.form[ 'login' ]
	mdp = request.form[ 'mdp' ]
	gestionnaire = modeleResanet.seConnecterGestionnaire(login, mdp)
	listePersonnel = modeleResanet.getPersonnelsAvecCarte()

	if login != '' and mdp != '':
		if gestionnaire:
			global nomGestionnaire
			nomGestionnaire = str(gestionnaire['nom'])
			global prenomGestionnaire
			prenomGestionnaire = str(gestionnaire['prenom'])
			session['login'] = gestionnaire['login']
			session['nom'] = gestionnaire['nom']
			session['prenom'] = gestionnaire['prenom']
			session['mdp'] = mdp
			return redirect("/gestionnaire/listePersonnelAvecCarte")

		else:
			return render_template('vueConnexionGestionnaire.html', echecConnexion=True)
	else:
		return render_template('vueConnexionGestionnaire.html', saisieIncomplete=True)


sommeCrediter = 0

def augmenterSommeCrediter(somme):
	sommeCrediter = somme + 1

def diminuerSommeCrediter(somme):
	sommeCrediter = somme - 1

@app.route( '/gestionnaire/listePersonnelAvecCarte', methods = [ 'GET' ] )
def listePersonnelAvecCarte() :
	return render_template('vuePersonnelAvecCarte.html',
						   personnelAvecCarte=modeleResanet.getPersonnelsAvecCarte(),
						   nomGestionnaire = nomGestionnaire, prenomGestionnaire = prenomGestionnaire,
						   lenPersonnelAvecCarte=len(modeleResanet.getPersonnelsAvecCarte()),
						   sommeCrediter = sommeCrediter, augmenterSommeCrediter = augmenterSommeCrediter(sommeCrediter),
						   diminuerSommeCrediter = diminuerSommeCrediter(sommeCrediter)
						   )



@app.route( '/gestionnaire/listePersonnelSansCarte', methods = [ 'GET' ] )
def listePersonnelSansCarte() :
	return render_template('vuePersonnelSansCarte.html',
						   personnelSansCarte=modeleResanet.getPersonnelsSansCarte(),
						   nomGestionnaire = nomGestionnaire, prenomGestionnaire = prenomGestionnaire,
						   lenPersonnelSansCarte=len(modeleResanet.getPersonnelsSansCarte())
						   )



@app.route('/gestionnaire/listePersonnelAvecCarte/bloquerCarte/<numCarte>', methods=['GET'])
def bloquerCarte(numCarte):
	modeleResanet.bloquerCarte(numCarte)
	return redirect('/gestionnaire/listePersonnelAvecCarte')


@app.route('/gestionnaire/listePersonnelAvecCarte/activerCarte/<numCarte>', methods=['GET'])
def activerCarte(numCarte):
	modeleResanet.activerCarte(numCarte)
	return redirect('/gestionnaire/listePersonnelAvecCarte')


@app.route('/gestionnaire/listePersonnelAvecCarte/reinitialiserMdp/<numCarte>', methods=['GET'])
def reinitialiserMdp(numCarte):
	modeleResanet.reinitialiserMdp(numCarte)
	return redirect('/gestionnaire/listePersonnelAvecCarte')


@app.route('/gestionnaire/listePersonnelAvecCarte/crediterCarte/<numCarte>/<somme>', methods=['GET'])
def crediterCarte(numCarte, somme):
	modeleResanet.crediterCarte(numCarte, somme)
	return redirect('/gestionnaire/listePersonnelAvecCarte')


@app.route('/gestionnaire/listePersonnelSansCarte/creerCarte/<matricule>', methods = [ 'GET' ])
def creerCarte(matricule):
	modeleResanet.creerCarte(matricule, activee=False)
	return redirect('/gestionnaire/listePersonnelSansCarte')


@app.route('/gestionnaire/listePersonnelAvecCarte/historique/<numCarte>')
def historiqueCarte(numCarte):
	historiqueCarte = modeleResanet.getHistoriqueReservationsCarte(numCarte)
	return render_template('vueHistoriqueReservationCarte.html',
						   historiqueCarte = historiqueCarte
						   )

@app.route('/gestionnaire/listePersonnelAvecCarte/reservation/<numCarte><dateDebut><dateFin>')
def reservation():
	getReservation = modeleResanet.getReservationsCarte(numCarte, dateDebut, dateFin),



@app.route('/gestionnaire/gererCarte', methods = [ 'GET' ] )
def gererCarteRestauration():
	return redirect('/gestionnaire/listePersonnelAvecCarte')


@app.route( '/gestionnaire/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterGestionnaire() :
	session.pop( 'login' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )





if __name__ == '__main__' :
	app.run( debug = True , host = '0.0.0.0' , port = 5000 )
