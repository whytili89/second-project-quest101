import jwt,json

from django.test import TestCase, Client
from datetime import datetime

from quest101.settings import SECRET_KEY,ALGORITHM
from products.models import *
from users.models import *

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
        response = client.post('/products/2/order', **headers)

        self.assertEqual(response.json(),
            {"message" : "SUCCESS"}
        )

    def test_orderview_user_already_exists(self):
        client = Client()
        response = client.post('/products/1/order', **headers)

        self.assertEqual(response.json(),
            {"message" : "USER ALREADY EXISTS"}
        )

    def test_orderview_integrity_error(self):
        client = Client()
        response = client.post('/products/5/order', **headers)

        self.assertEqual(response.json(),
            {"message" : "INVALID_VALUE"}
        )

class CommentTest(TestCase):
    def setUp(self):
        User.objects.create(
            id            = 1,
            name          = 'a', 
            profile_image = 'a',
            description   = 'a',
            kakao_id      = 1,
            is_creator    = False
        )
        User.objects.create(
            id          = 2,
            name        = 'b',
            description = 'b',
            kakao_id    = 2,
            is_creator  = True
        )
        Category.objects.create(
            id   = 1,
            name = 'a'
        )
        SubCategory.objects.create(
            id          = 1,
            name        = 'a1',
            category_id = 1
        )
        Level.objects.create(
            id    = 1,
            level = 'a'
        )
        Course.objects.create(
            id                  = 1,
            name                = 'a',
            thumbnail_image_url = 'a',
            description         = 'a',
            price               = 100,
            start_date          = datetime(2021,12,12,12,12,1),
            end_date            = datetime(2021,12,12,12,12,2),
            payment_period      = 1,
            user_id             = 2,
            sub_category_id     = 1,
            level_id            = 1
        )
        Course.objects.create(
            id                  = 2,
            name                = 'b',
            thumbnail_image_url = 'b',
            description         = 'b',
            price               = 100,
            start_date          = datetime(2021,12,12,12,12,1),
            end_date            = datetime(2021,12,12,12,12,2),
            payment_period      = 2,
            user_id             = 2,
            sub_category_id     = 1,
            level_id            = 1
        )
        Comment.objects.create(
            id         = 1,
            content    = 'a',
            user_id    = 1,
            course_id  = 1
        )
        Comment.objects.create(
            id         = 2,
            content    = 'b',
            user_id    = 1,
            course_id  = 1
        )
        self.token = jwt.encode({'user': 1}, SECRET_KEY,ALGORITHM)

    def tearDown(self):
        User.objects.all().delete()
        Category.objects.all().delete()
        SubCategory.objects.all().delete()
        Level.objects.all().delete()
        Course.objects.all().delete()
        Comment.objects.all().delete()

    def test_comment_post_success(self):
        client = Client()
        header = {"HTTP_Authorization" : self.token}
        
        comment = {
            'course_id' : 2,
            'content'   : 'a'
        }
        result = [{
            'id'      : 3,
            'name'    : 'a',
            'content' : 'a',
        }]
        
        response = client.post('/products/2/comments',json.dumps(comment),**header, content_type='application/json')
        self.assertEqual(response.json(), {'message':result})
        self.assertEqual(response.status_code, 200)

    def test_comment_post_key_error(self):
        client = Client()
        header = {"HTTP_Authorization" : self.token}
        
        comment = {}
        
        response = client.post('/products/1/comments',json.dumps(comment),**header, content_type='application/json')
        self.assertEqual(response.json(), {'message':'KEY_ERROR'})
        self.assertEqual(response.status_code, 401)

    def test_comment_get_success(self):
        client = Client()
        response = client.get('/products/1/comments')
        
        course_comments = [
            {
                'id'      : 1,
                'name'    : 'a',
                'content' : 'a'
            },
            {
                'id'      : 2,
                'name'    : 'a',
                'content' : 'b'
            }]

        self.assertEqual(response.json(),{'result':course_comments})
        self.assertEqual(response.status_code, 200)

    def test_comment_delete_success(self): 
        client = Client()
        header = {"HTTP_Authorization" : self.token}
        
        body = {
            'comment_id' : 1
        }

        response = client.delete('/products/1/comments',json.dumps(body),**header)
        self.assertEqual(response.json(),{'message':'SUCCESS_DELETE'})
        self.assertEqual(response.status_code, 200)

    def test_comment_delete_doesnotexist(self): 
        client = Client()
        header = {"HTTP_Authorization" : self.token}
        
        body = {
            'comment_id' : 3
        }

        response = client.delete('/products/1/comments',json.dumps(body),**header)
        self.assertEqual(response.json(),{'message':'INVAILD_COMMENT'})
        self.assertEqual(response.status_code, 401)

class LikeViewTest(TestCase):
    def setUp(self):

        User.objects.bulk_create([
                User(
                    id   = 1,
                    name = "bear",
                    kakao_id = 484248),
                User(
                    id= 2,
                    name = "tiger",
                    kakao_id = 879845)
               ])
        
        Category.objects.bulk_create([
                Category(
                    id =1,
                    name = "category1"),
                Category(
                    id = 2,
                    name = "category2")
        ])    

        SubCategory.objects.bulk_create([
                SubCategory(
                    id=1,
                    name = "sports",
                    category_id = 2),
                SubCategory(
                    id=2,
                    name = "cook",
                    category_id = 1)    
        ])

        Level.objects.bulk_create([
                Level(
                    id =1,
                    level = "초급"),
                Level(
                    id =2,
                    level = "중급")
        ])    
        
        Course.objects.bulk_create([
                Course(
                    id = 1,
                    thumbnail_image_url='ewrrwaa.com',
                    name = "Enjoy korean food",
                    price = 30000,
                    start_date = "2021-12-16",
                    end_date = "2021-12-16",
                    payment_period = 5,
                    level_id = 1,
                    user_id = 2,
                    sub_category_id = 1),
                Course(
                    id = 2,
                    thumbnail_image_url="sjflafj.com",
                    name = "Enjoy Sports",
                    price = 50000,
                    start_date = "2021-12-16",
                    end_date = "2021-12-16",
                    payment_period = 3,
                    level_id=2,
                    user_id=1,
                    sub_category_id = 2)    
        ])
        
        Stat.objects.bulk_create([
                Stat(
                    id = 1,
                    name = "wisdom"),
                Stat(
                    id = 2,
                    name = "strength"
                    )     
        ])

        CourseStat.objects.bulk_create([
            CourseStat(
                    id = 1,
                    stat_id = 1,
                    course_id = 2,
                    score = 50),
            CourseStat(
                    id = 2,
                    stat_id = 2,
                    course_id = 1,
                    score = 70)        
        ])        
        
        Like.objects.create(
            id = 1,
            user_id = 2,
            course_id = 2
        )

        global headers
        token = jwt.encode({'user': 2}, SECRET_KEY, algorithm=ALGORITHM)
        headers = {"HTTP_Authorization" : token}

    def tearDown(self):
        User.objects.all().delete()
        SubCategory.objects.all().delete()
        Course.objects.all().delete()
        Like.objects.all().delete()
        Stat.objects.all().delete()
        CourseStat.objects.all().delete()

    def test_post_likeview_success(self):
        client=Client()
        course_id = {"course_id" : 1}
        response = client.post('/products/like', json.dumps(course_id), content_type = 'application/json', **headers)

        self.assertEqual(response.json(),
            {"message" : "SUCCESS_LIKE"}         
        )
        self.assertEqual(response.status_code, 200)

    def test_likeview_post_delete_like(self):
        client = Client()
        course_id = {"course_id" : 2}
        response = client.post('/products/like', json.dumps(course_id), content_type= 'application/json', **headers)

        self.assertEqual(response.json(),
            {"message" : "DELETE_LIKE"})
        
        self.assertEqual(response.status_code, 200)

    def test_likeviews_integrityerror(self):
        client=Client()
        course_id = {"course_id" : 3}
        response = client.post('/products/like', json.dumps(course_id), content_type = 'application/json', **headers)

        self.assertEqual(response.json(),
            {"message": "INVALID_VALUE"})

        self.assertEqual(response.status_code, 400)


