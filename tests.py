from datetime import datetime, timedelta
import unittest
from appz import db, create_app
from appz.models import User, Post, Role, Permission, AnonymousUser
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User()
        u.set_password('cat')
        self.assertTrue(u.password_hash is not None)

    # def test_no_password_getter(self):
    #     u = User()
    #     u.set_password('cat')
    #     with self.assertRaises(AttributeError):
    #         u.password

    def test_password_verification(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_password_hashes_are_random(self):
        u = User()
        u2 = User()
        u.set_password('cat')
        u2.set_password('cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User()
        u.set_password('cat')
        db.session.add(u)
        db.session.commit()
        token = u.get_token()
        self.assertTrue(u.check_token(token))

    def test_invalid_confirmation_token(self):
        u1 = User()
        u2 = User()
        u1.set_password('cat')
        u2.set_password('dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.get_token()
        self.assertEqual(u2.check_token(token), u1)

    def test_valid_password_change_token(self):
        u = User()
        u.set_password('cat')
        db.session.add(u)
        db.session.commit()
        token = u.get_reset_password_token()
        self.assertEqual(u.verify_reset_password_token(token), u)
        self.assertTrue(u.check_password('cat'))

    def test_invalid_password_change_token(self):
        u1 = User()
        u2 = User()
        u1.set_password('cat')
        u2.set_password('dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.get_reset_password_token()
        self.assertEqual(u2.verify_reset_password_token(token), u1)
        self.assertTrue(u2.check_password('dog'))

    def test_duplicate_password_change_token(self):
        u1 = User()
        u2 = User()
        u1.set_password('cat')
        u2.set_password('dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.get_reset_password_token()
        self.assertEqual(u1.verify_reset_password_token(token), u2)
        self.assertTrue(u1.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?d=identicon&s=128'))
    def test_follows(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followed.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1, timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2, timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3, timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4, timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

    def test_to_dict(self):
        u = User(email='susan@example.com')
        u.set_password('cat')
        db.session.add(u)
        db.session.commit()
        with self.app.test_request_context('/'):
            json_user = u.to_dict()
        expected_keys = ['id', 'username', 'last_seen', 'about_me', 'post_count',
                         'follower_count', 'followed_count', '_links']
        self.assertEqual(sorted(json_user.keys()), sorted(expected_keys))
        self.assertEqual('/api/users/' + str(u.id), json_user['_links']['self'])


    def test_user_role(self):
        u = User()
        u.set_password('cat')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_moderator_role(self):
        r = Role.query.filter_by(name='Moderator').first()
        u = User( role=r)
        u.set_password('cat')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_administrator_role(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User(role=r)
        u.set_password('cat')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertTrue(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

if __name__ == '__main__':
    unittest.main(verbosity=2)
