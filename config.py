import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yBK#cqT^hv4hVDu@Ns3eBLRRnK654y86AHY7'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app/instance/site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
