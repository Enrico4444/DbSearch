# from model.merged_view import MergedViewModel

# def get_user_permissions(identity):
#     filters = {
#         "user.id":identity,
#         "return":["role"]
#     }
#     role = MergedViewModel.join(**filters)
#     if identity == 1: 
#         return {'is_admin': True}
#     return {'is_admin': False}