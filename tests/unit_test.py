from server import app, loadClubs, loadCompetitions
import pytest

class Tests():

    '''
    Permet de simuler un serveur 
    pour faire des requêtes dans les test
    '''
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def test_club(self):
        return {
                    "clubs":[
                        {
                            "name":"Simply Lift",
                            "email":"john@simplylift.co",
                            "points":"13"
                        },
                        {
                            "name":"Iron Temple",
                            "email": "admin@irontemple.com",
                            "points":"4"
                        },
                        {   "name":"She Lifts",
                            "email": "kate@shelifts.co.uk",
                            "points":"12"
                        }
                    ]
                }
    
    @pytest.fixture
    def test_competition(self):
        return {
                    "competitions": [
                        {
                            "name": "Spring Festival",
                            "date": "2020-03-27 10:00:00",
                            "numberOfPlaces": "10"
                        },
                        {
                            "name": "Fall Classic",
                            "date": "2020-10-22 13:30:00",
                            "numberOfPlaces": "13"
                        }
                    ]
                }
    
    @pytest.fixture(autouse=True)
    def setup(self, test_club, test_competition):
        # Mettre à jour les listes globales avec les données de test
        global clubs, competitions
        clubs = test_club['clubs']
        competitions = test_competition['competitions']
        yield
    
    #Tests unitaires
    def test_load_clubs(self):
        test_club = loadClubs()
        assert isinstance(test_club, list)

        for club in test_club:
            assert 'name' in club
            assert 'email' in club
            assert 'points' in club

    #Tests fonctionnels
    def test_purchase_negative_places(self, client, test_club, test_competition):
        response = client.post('/purchasePlaces', data={
            'club': "Iron Temple",
            'competition': "Spring Festival",
            'places': -1
        })
        assert response.status_code == 400

    def test_purchase_too_many_places(self, client, test_club, test_competition):
        response = client.post('/purchasePlaces', data={
            'club': "Simply Lift",
            'competition': "Spring Festival",
            'places': 13
        })
        assert response.status_code == 400

    def test_purchase_insufficient_points(self, client, test_club, test_competition):
        response = client.post('/purchasePlaces', data={
            'club': "Iron Temple",
            'competition': "Spring Festival",
            'places': 5
        })
        assert response.status_code == 400

    def test_antidate_booking(self, client, test_club, test_competition):
        response = client.post('/purchasePlaces', data={
            'club': "Iron Temple",
            'competition': "Fall Classic",
            'places': 5
        })
        assert response.status_code == 200

    def test_wrong_email(self, client, test_club, test_competition):
        response = client.post('/showSummary', data={
            "email" : "root@root.fr"
        })

        assert response.status_code == 302

    def test_complete_reservation_flow(self, client, test_club, test_competition):
        """
        Test du parcours complet de réservation, vérifiant uniquement la réponse
        de l'API sans valider les changements dans les variables globales.
        """
        
        # Sauvegarde des valeurs initiales pour comparaison
        club_name = "Simply Lift"
        competition_name = "Fall Classic"
        places_to_book = 3
        
        # On utilise les variables globales clubs et competitions configurées par les fixtures
        club = next(c for c in clubs if c['name'] == club_name)
        competition = next(c for c in competitions if c['name'] == competition_name)
        
        initial_points = int(club['points'])
        initial_places = int(competition['numberOfPlaces'])
        
        # 1. Connexion avec l'email du club
        login_response = client.post('/showSummary', data={
            'email': club['email']
        }, follow_redirects=True)
        
        # 2. Vérification du contenu de la page d'accueil
        assert login_response.status_code == 200
        assert club_name.encode() in login_response.data
        assert competition_name.encode() in login_response.data
        
        # 3. Accès à la page de réservation pour une compétition spécifique
        booking_page = client.get(f'/book/{competition_name}/{club_name}')
        assert booking_page.status_code == 200
        assert club_name.encode() in booking_page.data
        assert competition_name.encode() in booking_page.data
        
        # 4. Réservation de places
        purchase_response = client.post('/purchasePlaces', data={
            'club': club_name,
            'competition': competition_name,
            'places': places_to_book
        }, follow_redirects=True)
        
        # 5. Vérification des résultats de base
        assert purchase_response.status_code == 200
        assert b'Great-booking complete!' in purchase_response.data
