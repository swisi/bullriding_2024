import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yBK#cqT^hv4hVDu@Ns3eBLRRnK654y86AHY7'

    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'database', 'site.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False