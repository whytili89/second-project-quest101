import jwt

from django.test       import TestCase, Client

from users.models      import User, UserCourse
from products.models   import Course, Category, SubCategory, Level, Media
from quest101.settings import SECRET_KEY, ALGORITHM

class OrderViewTest(TestCase):
    def setUp(self):
        
        User.objects.create(
            id = 1,
            name = "이땡땡",
            kakao_id = 33243,
            is_creator = False
        )

        User.objects.create(
            id = 2,
            name = "김가나",
            kakao_id = 40343,
            is_creator = True
        )

        Category.objects.create(
            id =1,
            name = "category1"
        )

        Category.objects.create(
            id = 2,
            name = "category2"
        )

        SubCategory.objects.create(
            id=1,
            name = "sports",
            category_id = 2
        )

        SubCategory.objects.create(
            id=2,
            name = "cook",
            category_id = 1
        )

        Level.objects.create(
            id =1,
            level = "초급"
        )

        Level.objects.create(
            id =2,
            level = "중급"
        )

        Course.objects.create(
            id = 1,
            thumbnail_image_url='ewrrwaa.com',
            name = "Enjoy korean food",
            price = 30000,
            start_date = "2021-12-16",
            end_date = "2021-12-16",
            payment_period = 5,
            level_id = 1,
            user_id = 2,
            sub_category_id = 1
        )

        Course.objects.create(
            id = 2,
            thumbnail_image_url="sjflafj.com",
            name = "Enjoy Sports",
            price = 50000,
            start_date = "2021-12-16",
            end_date = "2021-12-16",
            payment_period = 3,
            level_id=2,
            user_id=1,
            sub_category_id = 2
        )

        Media.objects.create(
            id = 1,
            url = "abc.com",
            course_id = 2
        )

        Media.objects.create(
            id = 2,
            url = "def.com",
            course_id = 1
        )

        UserCourse.objects.create(
            id = 1,
            user_id = 1,
            course_id = 1
        )

        global headers
        token = jwt.encode({'user': 1}, SECRET_KEY, algorithm=ALGORITHM)
        headers = {"HTTP_Authorization" : token}

    def tearDown(self):    
        User.objects.all().delete()
        Category.objects.all().delete()
        SubCategory.objects.all().delete()
        Course.objects.all().delete()
        Media.objects.all().delete()
        UserCourse.objects.all().delete()
        Level.objects.all().delete()

    def test_orderview_success(self):
        client = Client()
        response = client.post('/products/order/2', **headers)

        self.assertEqual(response.json(),
            {"message" : "SUCCESS"}
        )

    def test_orderview_user_already_exists(self):
        client = Client()
        response = client.post('/products/order/1', **headers)

        self.assertEqual(response.json(),
            {"message" : "USER ALREADY EXISTS"}
        )

    def test_orderview_integrity_error(self):
        client = Client()
        response = client.post('/products/order/5', **headers)

        self.assertEqual(response.json(),
            {"message" : "INVALID_VALUE"}
        )