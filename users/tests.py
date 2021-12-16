import json
from django.test   import TestCase, Client
from unittest.mock import patch, MagicMock

from users.models  import User

class KakaoLoginTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            kakao_id      = "01924234",
            name          = "박정현",
            email         = "hailey@gmail.com",
            profile_image = "https://ifh.cc/g/ElNIU1.jpg",
            phone_number  = "01012341234",
        )

    def tearDown(self):
        User.objects.all().delete()
        
    @patch('users.views.requests')
    def test_kakaologinview_get_success(self, mocked_requests):
        client = Client()
        class MockedResponse:
            def json(self):
                return{
                    "id": 2008761000,
                    "connected_at": "2021-12-10T03:56:15Z",
                    "properties": {
                        "nickname": "박정현",
                        "profile_image": "https://ifh.cc/g/ElNIU1.jpg",
                        "thumbnail_image": "https://ifh.cc/g/ElNIU1.jpg"
                    },
                    "kakao_account": {
                        "profile_needs_agreement": False,
                        "profile": {
                            "nickname": "박정현",
                            "thumbnail_image_url": "https://ifh.cc/g/ElNIU1.jpg",
                            "profile_image_url": "https://ifh.cc/g/ElNIU1.jpg",
                            "is_default_image": False
                        },
                        "has_email": True,
                        "email_needs_agreement": False,
                        "is_email_valid": True,
                        "is_email_verified": True,
                        "email": "hailey@gmail.com",
                        "has_phone_number": True,
                        "phone_number_needs_agreement": False,
                        "phone_number": "+82 10-9109-5601",
                        "has_birthday": True,
                        "birthday_needs_agreement": True,
                        "has_gender": True,
                        "gender_needs_agreement": False,
                        "gender": "female",
                        "is_kakaotalk_user": True
                }
                }

        mocked_requests.get = MagicMock(return_value = MockedResponse())
        headers = {"HTTP_Authorization" : "가짜 access_token"}
        response = client.get("/users/kakaosignin", **headers)
        
        access_token = response.json()['access_token']
        
        self.assertEqual(response.json(),{'message':'SUCCESS','access_token': access_token})
        self.assertEqual(response.status_code, 200 | 201) 