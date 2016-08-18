"""Spoken CD content models auto-generated."""
from peewee import *
from config import dbuser, dbpassword, dbname

database = MySQLDatabase(dbname, **{'password': dbpassword, 'user': dbuser})


class UnknownField(object):
    """Unknown field class."""

    def __init__(self, *_, **__):
        """Init class."""
        pass


class BaseModel(Model):
    """BaseModel class."""

    class Meta:
        """Meta class."""

        database = database


class User(BaseModel):
    """User class."""

    date_joined = DateTimeField()
    email = CharField()
    first_name = CharField()
    is_active = IntegerField()
    is_staff = IntegerField()
    is_superuser = IntegerField()
    last_login = DateTimeField(null=True)
    last_name = CharField()
    password = CharField()
    username = CharField(unique=True)

    class Meta:
        """Meta class."""

        db_table = 'auth_user'


class Fosscategory(BaseModel):
    """Fosscategory class."""

    created = DateTimeField()
    description = TextField()
    foss = CharField(unique=True)
    status = IntegerField()
    updated = DateTimeField()
    user = ForeignKeyField(db_column='user_id', rel_model=User, to_field='id')

    class Meta:
        """Meta class."""

        db_table = 'creation_fosscategory'


class Language(BaseModel):
    """Language class."""

    code = CharField()
    created = DateTimeField()
    name = CharField(unique=True)
    updated = DateTimeField()
    user = ForeignKeyField(db_column='user_id', rel_model=User, to_field='id')

    class Meta:
        """Meta class."""

        db_table = 'creation_language'


class Level(BaseModel):
    """Level class."""

    code = CharField()
    level = CharField()

    class Meta:
        """Meta class."""

        db_table = 'creation_level'


class TutorialDetail(BaseModel):
    """TutorialDetail class."""

    created = DateTimeField()
    foss = ForeignKeyField(db_column='foss_id',
                           rel_model=Fosscategory, to_field='id')
    level = ForeignKeyField(db_column='level_id',
                            rel_model=Level, to_field='id')
    order = IntegerField()
    tutorial = CharField()
    updated = DateTimeField()
    user = ForeignKeyField(db_column='user_id', rel_model=User, to_field='id')

    class Meta:
        """Meta class."""

        db_table = 'creation_tutorialdetail'
        indexes = ((('foss', 'tutorial', 'level'), True),)


class TutorialCommonContent(BaseModel):
    """TutorialCommonContent class."""

    assignment = CharField()
    assignment_status = IntegerField()
    assignment_user = ForeignKeyField(db_column='assignment_user_id',
                                      rel_model=User, to_field='id')
    code = CharField()
    code_status = IntegerField()
    code_user = ForeignKeyField(db_column='code_user_id', rel_model=User,
                                related_name='auth_user_code_user_set',
                                to_field='id')
    created = DateTimeField()
    keyword = TextField()
    keyword_status = IntegerField()
    keyword_user = ForeignKeyField(db_column='keyword_user_id', rel_model=User,
                                   related_name='auth_user_keyword_user_set',
                                   to_field='id')
    prerequisite = ForeignKeyField(db_column='prerequisite_id', null=True,
                                   rel_model=TutorialDetail, to_field='id')
    prerequisite_status = IntegerField()
    prerequisite_user = ForeignKeyField(
        db_column='prerequisite_user_id', rel_model=User,
        related_name='auth_user_prerequisite_user_set', to_field='id')
    slide = CharField()
    slide_status = IntegerField()
    slide_user = ForeignKeyField(db_column='slide_user_id', rel_model=User,
                                 related_name='auth_user_slide_user_set',
                                 to_field='id')
    tutorial_detail = ForeignKeyField(
        db_column='tutorial_detail_id', rel_model=TutorialDetail,
        related_name='creation_tutorialdetail_tutorial_detail_set',
        to_field='id', unique=True)
    updated = DateTimeField()

    class Meta:
        """Meta class."""

        db_table = 'creation_tutorialcommoncontent'


class TutorialResource(BaseModel):
    """TutorialResource class."""

    common_content = ForeignKeyField(db_column='common_content_id',
                                     rel_model=TutorialCommonContent,
                                     to_field='id')
    created = DateTimeField()
    hit_count = IntegerField()
    language = ForeignKeyField(db_column='language_id', rel_model=Language,
                               to_field='id')
    outline = TextField()
    outline_status = IntegerField()
    outline_user = ForeignKeyField(db_column='outline_user_id', rel_model=User,
                                   to_field='id')
    playlist_item = CharField(db_column='playlist_item_id', null=True)
    script = CharField()
    script_status = IntegerField()
    script_user = ForeignKeyField(db_column='script_user_id', rel_model=User,
                                  related_name='auth_user_script_user_set',
                                  to_field='id')
    status = IntegerField()
    timed_script = CharField()
    tutorial_detail = ForeignKeyField(db_column='tutorial_detail_id',
                                      rel_model=TutorialDetail, to_field='id')
    updated = DateTimeField()
    version = IntegerField()
    video = CharField()
    video_id = CharField(null=True)
    video_status = IntegerField()
    video_thumbnail_time = TimeField()
    video_user = ForeignKeyField(db_column='video_user_id', rel_model=User,
                                 related_name='auth_user_video_user_set',
                                 to_field='id')

    class Meta:
        """Meta class."""

        db_table = 'creation_tutorialresource'
        indexes = ((('tutorial_detail', 'language'), True),)
