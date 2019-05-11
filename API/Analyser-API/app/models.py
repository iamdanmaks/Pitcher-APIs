from app import db, login, whooshee
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


subscriptions = db.Table(
    'subscriptions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('research_id', db.Integer, db.ForeignKey('research.id'))
)


likes = db.Table(
    'likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('research_id', db.Integer, db.ForeignKey('research.id'))
)


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))
    
    def add(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)


class UserResearchPermission(db.Model):
    __tablename__ = 'user_research_permission'

    userId = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    researchId = db.Column(db.Integer, db.ForeignKey('research.id'), primary_key=True)
    permission = db.Column(db.Boolean(), server_default='0')

    researches = db.relationship(
        "Research", 
        back_populates="workers", 
        cascade='all, delete-orphan', 
        single_parent=True, 
        uselist=True
    )
    
    users = db.relationship(
        "User", 
        back_populates="my_researches", 
        uselist=True
    )


@whooshee.register_model('username', 'fullname', 'bio')
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    fullname = db.Column(db.String(150), index=True) 
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    email = db.Column(db.String(120), index=True, nullable=True, unique=True)
    bio = db.Column(db.Text, index=True)
    socialId = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128), nullable=True)
    sign_date = db.Column(db.DateTime, default=datetime.now())
    avatar_ = db.Column(db.String(300))
    isCompany = db.Column(db.Boolean(), nullable=False, server_default='0')

    my_researches = db.relationship(
        'UserResearchPermission',
        back_populates="users",
        cascade='all, delete-orphan',
        single_parent=True,
        uselist=True
    )

    owners = db.relationship(
        'Research', 
        backref='User', 
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )

    followed = db.relationship(
        'User', 
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), 
        lazy='dynamic'
    )

    subscribed = db.relationship(
        "Research",
        secondary=subscriptions,
        back_populates="subscribers"
    )

    liked = db.relationship(
        "Research",
        secondary=likes,
        back_populates="user_liked"
    )

    def __repr__(self):
        return '@{}'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user) and user.isCompany is False and self.isCompany is True:
            self.followed.append(user)
            return True
        
        return False

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return True
        
        return False

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def del_from_db(self):
        self.owners.clear()
        self.subscribed.clear()
        self.my_researches.clear()
        self.followed.clear()
        db.session.delete(self)
        db.session.commit()


    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()
    
    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.filter_by(id = user_id).first()

    @classmethod
    def find_by_email(cls, user_email):
        return cls.query.filter_by(email = user_email).first()

    @classmethod
    def return_followed(cls):
        def to_json(x):
            return {
                'username': x.username,
                'fullname': x.fullname,
                'avatar': x.avatar_
            }
        return {'workers': [to_json(worker) for worker in list(cls.followed)]}

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'id': x.id,
                'username': x.username,
                'fullname': x.fullname,
                'biography': x.bio,
                'isCompany': x.isCompany
            }
        return {'users': list(map(lambda x: to_json(x), User.query.all()))}


    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@whooshee.register_model('topic', 'appName', 'description', 'appDev')
class Research(db.Model):
    __tablename__ = 'research'

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(80), nullable=False, index=True)
    creationDate = db.Column(db.DateTime, default=datetime.now())
    description = db.Column(db.Text, index=True)
    type_of_research = db.Column(db.Boolean(), server_default='1')
    updateInterval = db.Column(db.Integer)
    views = db.Column(db.Integer, default=0)
    appId = db.Column(db.String(100))
    appDev = db.Column(db.String(100), index=True)
    appName = db.Column(db.String(100), index=True)
    algos = db.Column(db.Text)
    ownerId = db.Column(db.Integer, db.ForeignKey('user.id'))

    workers = db.relationship(
        "UserResearchPermission",
        back_populates="researches",
        uselist=True
    )

    subscribers = db.relationship(
        "User",
        secondary=subscriptions,
        back_populates="subscribed"
    )

    user_liked = db.relationship(
        "User",
        secondary=likes,
        back_populates="liked"
    )
    
    modules = db.relationship(
        'ResearchModule',  
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )
    
    keywords = db.relationship(
        'ResearchKeyword', 
        backref='Research', 
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )
    
    conducted = db.relationship(
        'ConductedResearch', 
        backref='Research', 
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )

    parents = db.relationship(
        "User",
        secondary=subscriptions,
        back_populates="subscribed"
    )

    search = db.relationship(
        'SearchTrends',
        cascade='all, delete-orphan',
        single_parent=True,
        uselist=True
    )

    def __repr__(self):
        return '{}\n{}'.format(self.topic, self.description)


class ResearchModule(db.Model):
    __tablename__ = 'research_module'

    module = db.Column(db.String(25), primary_key=True)
    researchId = db.Column(db.Integer, db.ForeignKey('research.id'), primary_key=True)

    def __repr__(self):
        return '{}.{}'.format(self.module, self.researchId)


class ResearchKeyword(db.Model):
    __tablename__ = 'research_keyword'
    __searchable__ = ['keyword']

    keyword = db.Column(db.String(80), primary_key=True)
    researchId = db.Column(db.Integer, db.ForeignKey('research.id'), primary_key=True)

    def __repr__(self):
        return '{}.{}'.format(self.keyword, self.researchId)


class ConductedResearch(db.Model):
    __tablename__ = 'conducted_research'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    researchId = db.Column(db.Integer, db.ForeignKey('research.id'))

    freq_dict = db.relationship(
        'FrequencyDictionary',
        backref='ConductedResearch', 
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )

    play_store = db.relationship(
        'PlayStoreResearch',
        backref='ConductedResearch', 
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )

    news = db.relationship(
        'NewsResearch',
        backref='ConductedResearch', 
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )

    twitter = db.relationship(
        'TwitterResearch',
        backref='ConductedResearch', 
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )


class FrequencyDictionary(db.Model):
    __tablename__ = 'frequency_dictionary'

    keyword = db.Column(db.String(150), primary_key=True)
    count = db.Column(db.Integer)
    conductedResearchId = db.Column(db.Integer, db.ForeignKey('conducted_research.id'))


class Analyzer(db.Model):
    __tablename__ = 'analyzer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    tweets = db.relationship(
        'AnalyzedTweet',
        back_populates="parent",
        cascade='all, delete-orphan',
        single_parent=True,
        uselist=True
    )

    play_store = db.relationship(
        'PlayStoreResearch',
        cascade='all, delete-orphan',
        single_parent=True,
        uselist=True
    )

    news = db.relationship(
        'NewsResearch',
        cascade='all, delete-orphan',
        single_parent=True,
        uselist=True
    )

    twitter = db.relationship(
        'TwitterResearch',
        cascade='all, delete-orphan',
        single_parent=True,
        uselist=True
    )


class PlayStoreResearch(db.Model):
    __tablename__ = 'play_store_research'

    id = db.Column(db.Integer, db.ForeignKey('conducted_research.id'), primary_key=True)
    downloads = db.Column(db.String(20))
    averageRating = db.Column(db.Float)
    maxReviews = db.Column(db.Integer)
    rateOneCount = db.Column(db.Integer)
    rateTwoCount = db.Column(db.Integer)
    rateThreeCount = db.Column(db.Integer)
    rateFourCount = db.Column(db.Integer)
    rateFiveCount = db.Column(db.Integer)
    analyzerId = db.Column(db.Integer, db.ForeignKey('analyzer.id'))

    reviews = db.relationship(
        'PlayStoreReview',
        backref="PlayStoreResearch", 
        cascade="all, delete-orphan", 
        lazy='dynamic'
    )


class PlayStoreReview(db.Model):
    __tablename__ = 'play_store_review'

    id = db.Column(db.String(100), primary_key=True)
    rate = db.Column(db.Integer)
    text = db.Column(db.String(1000))
    sentimentScore = db.Column(db.Integer)
    isBot = db.Column(db.Boolean(), server_default='0')
    playStoreResearchId = db.Column(db.Integer, db.ForeignKey('play_store_research.id'))


class NewsResearch(db.Model):
    __tablename__ = 'news_research'

    id = db.Column(db.Integer, db.ForeignKey('conducted_research.id'), primary_key=True)
    amount = db.Column(db.Integer)
    pos_count_general = db.Column(db.Integer)
    neg_count_general = db.Column(db.Integer)
    analyzerId = db.Column(db.Integer, db.ForeignKey('analyzer.id'))

    news_list = db.relationship(
        'NewsArticle',
        backref="NewsResearch", 
        cascade="all, delete-orphan", 
        lazy='dynamic'
    )


class NewsArticle(db.Model):
    __tablename__ = 'news_article'

    link = db.Column(db.String(350), primary_key=True)
    news_id = db.Column(
        db.Integer, 
        db.ForeignKey('news_research.id'), 
        primary_key=True
    )
    title = db.Column(db.String(200))
    text = db.Column(db.String(16000000))
    source = db.Column(db.String(100))


class SearchTrends(db.Model):
    __tablename__ = 'search_trends'

    id = db.Column(db.Integer, db.ForeignKey('research.id'), primary_key=True)
    query = db.Column(db.String(150))

    days = db.relationship(
        'DayInterest',
        backref="SearchTrends", 
        cascade="all, delete-orphan", 
        lazy='dynamic'
    )

    related = db.relationship(
        'RelatedTopic',
        backref="SearchTrends", 
        cascade="all, delete-orphan", 
        lazy='dynamic'
    )

    top = db.relationship(
        'TopQuery',
        backref="SearchTrends", 
        cascade="all, delete-orphan", 
        lazy='dynamic'
    )

    rising = db.relationship(
        'RisingQuery',
        backref="SearchTrends", 
        cascade="all, delete-orphan", 
        lazy='dynamic'
    )


class DayInterest(db.Model):
    __tablename__ = 'day_interest'

    date = db.Column(db.DateTime, primary_key=True)
    search_id = db.Column(
        db.Integer, 
        db.ForeignKey('search_trends.id'), 
        primary_key=True
    )
    interest = db.Column(db.Integer)


class RelatedTopic(db.Model):
    __tablename__ = 'related_topic'

    topic = db.Column(db.String(150), primary_key=True)
    search_id = db.Column(
        db.Integer, 
        db.ForeignKey('search_trends.id'), 
        primary_key=True
    )
    value = db.Column(db.Integer)
    sentiment = db.Column(db.Float)


class TopQuery(db.Model):
    __tablename__ = 'top_query'

    query = db.Column(db.String(150), primary_key=True)
    search_id = db.Column(
        db.Integer, 
        db.ForeignKey('search_trends.id'),
        primary_key=True
    )
    value = db.Column(db.Integer)
    sentiment = db.Column(db.Float)


class RisingQuery(db.Model):
    __tablename__ = 'rising_query'

    query = db.Column(db.String(150), primary_key=True)
    search_id = db.Column(
        db.Integer, 
        db.ForeignKey('search_trends.id'), 
        primary_key=True
    )
    value = db.Column(db.Integer)
    sentiment = db.Column(db.Float)


class TwitterResearch(db.Model):
    __tablename__ = 'twitter_research'

    id = db.Column(db.Integer, db.ForeignKey('conducted_research.id'), primary_key=True)
    tweetsCount = db.Column(db.Integer)
    analyzerId = db.Column(db.Integer, db.ForeignKey('analyzer.id'))

    settings = db.relationship(
        'TwitterResearchFilter',
        backref="TwitterResearch", 
        cascade="all, delete-orphan", 
        lazy='dynamic'
    )

    research_units = db.relationship(
        'TwitterResearchUnit',
        back_populates="parent",
        cascade='all, delete-orphan',
        single_parent=True,
        uselist=True
    )


class TwitterResearchFilter(db.Model):
    __tablename__ = 'twitter_research_filter'

    twitterResearchId = db.Column(db.Integer, db.ForeignKey('twitter_research.id'), primary_key=True)
    minLikes = db.Column(db.Integer)
    minRetweets = db.Column(db.Integer)
    minDate = db.Column(db.DateTime)
    maxDate = db.Column(db.DateTime)


class TwitterResearchUnit(db.Model):
    __tablename__ = 'twitter_research_unit'

    twitterResearchId = db.Column(db.Integer, db.ForeignKey('twitter_research.id'), primary_key=True)
    tweetId = db.Column(db.Integer, db.ForeignKey('tweet.id'), primary_key=True)
    likes = db.Column(db.Integer)
    retweets = db.Column(db.Integer)

    child = db.relationship(
        "Tweet", 
        back_populates="researches", 
        cascade='all, delete-orphan', 
        single_parent=True, 
        uselist=True
    )
    
    parent = db.relationship(
        "TwitterResearch", 
        back_populates="research_units", 
        uselist=True
    )


class AnalyzedTweet(db.Model):
    __tablename__ = 'analyzed_tweet'

    twitterResearchId = db.Column(db.Integer, db.ForeignKey('analyzer.id'), primary_key=True)
    tweetId = db.Column(db.Integer, db.ForeignKey('tweet.id'), primary_key=True)
    sentimentScore = db.Column(db.Integer)
    isBot = db.Column(db.Boolean(), server_default='0')

    child = db.relationship(
        "Tweet", 
        back_populates="analysis", 
        cascade='all, delete-orphan', 
        single_parent=True, 
        uselist=True
    )
    
    parent = db.relationship(
        "Analyzer", 
        #back_populates="twitter", 
        uselist=True
    )


class Tweet(db.Model):
    __tablename__ = 'tweet'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    text = db.Column(db.String(280))
    timestamp = db.Column(db.DateTime)

    researches = db.relationship(
        "TwitterResearchUnit",
        back_populates="child",
        uselist=True
    )

    analysis = db.relationship(
        "AnalyzedTweet",
        back_populates="child",
        uselist=True
    )
