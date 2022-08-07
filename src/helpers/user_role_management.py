from model.user import UserModel
from model.role import RoleModel
from rsc.permissions import PERMISSIONS

def assign_permissions(role_name, permissions, permission_action="append"):
    # if new role: add role and permissions; if existing role and action=replace: replace existing permissions
    if role_name not in PERMISSIONS or permission_action == "replace":
        PERMISSIONS[role_name] = permissions
    # if existing role and action=append: append to existing role
    else: 
        for resource_name in permissions:
            # merge existing and new permissions for this resource
            if resource_name in PERMISSIONS[role_name]:
                updated_permissions = set(PERMISSIONS[role_name][resource_name]).union(set(permissions[resource_name]))
                PERMISSIONS[role_name][resource_name] = updated_permissions
            else:
                PERMISSIONS[role_name][resource_name] = permissions[resource_name]
    print(PERMISSIONS)

def create_role_and_user(role_name, permissions, username=None, password=None):
    role = RoleModel.find_by(name=role_name)
    if not role:
        role = RoleModel(name=role_name)
        role.save_to_db() 
        assign_permissions(role_name=role_name, permissions=permissions, permission_action="replace")
    if username and password:
        user = UserModel.find_by(username=username)
        if not user:
            user = UserModel(username=username, password=password, role_id=role.id)
            user.save_to_db()
