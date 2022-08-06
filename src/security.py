# from werkzeug.security import safe_str_cmp
from model.user import UserModel

def authenticate(username, password):
  user = UserModel.find_by(**{"username":username})[0]
  # use safe_str_comparison(safe_str_cmp) instead of == as == can change between python versions 
  # if user and safe_str_cmp(user.password, password): # TODO: fix import error 
  if user and user.password == password:
    return user

def identity(payload):
  user_id = payload['identity']
  return UserModel.find_by(**{"id":user_id})
