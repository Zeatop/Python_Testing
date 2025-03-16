from server import app, loadClubs, loadCompetitions
import pytest

class TestFunctional():

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

 