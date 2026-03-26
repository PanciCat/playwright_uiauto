# Mock payloads used by conftest.py fixtures (save_cookies / tool_login_mock).
# Keep data here to avoid duplicating the same large dicts in multiple fixtures.

# login mock — token is filled at runtime by the fixture
LOGIN_MOCK_BODY_TEMPLATE = {
    "msg": "操作成功",
    "code": 200,
    "ip": "1.1.1.1",
    "token": "",  # replaced at runtime
}

VERSION_INFO_MOCK_BODY = {
    "msg": "操作成功",
    "code": 200,
    "data": {
        "dept": {
            "searchValue": None,
            "createBy": "admin",
            "createTime": "2000-09-04 10:15:07",
            "createTimeFrom": None,
            "createTimeTo": None,
            "updateBy": None,
            "updateTime": None,
            "remark": None,
            "params": {},
            "leader": None,
            "phone": None,
            "email": None,
            "status": "0",
            "delFlag": "0",
            "parentName": None,
            "expireTime": None,
            "storageUsed": None,
            "city": None,
            "cityCodes": None,
        },
        "expireTime": "",
    },
}

_USER_DEPT = {
    "searchValue": None,
    "createBy": None,
    "createTime": None,
    "createTimeFrom": None,
    "createTimeTo": None,
    "updateBy": None,
    "updateTime": None,
    "remark": None,
    "params": {},
    "orderNum": "0",
    "status": "0",
    "delFlag": None,
    "parentName": None,
}

_ROLE_TEMPLATE = {
    "searchValue": None,
    "createBy": None,
    "createTime": None,
    "createTimeFrom": None,
    "createTimeTo": None,
    "updateBy": None,
    "updateTime": None,
    "remark": None,
    "params": {},
    "menuCheckStrictly": False,
    "deptCheckStrictly": False,
    "status": "0",
    "delFlag": None,
    "flag": False,
    "menuIds": None,
    "deptIds": None,
    "admin": False,
}


def _make_role(role_id, role_name, role_key, role_sort, data_scope, big_ids):
    return {
        **_ROLE_TEMPLATE,
        "roleId": role_id,
        "roleName": role_name,
        "roleKey": role_key,
        "roleSort": role_sort,
        "dataScope": data_scope,
        "bigIds": big_ids,
    }


_USER_ROLES = [
    _make_role(1, "角色1", "role1", "0", "4", "1,2,3,4,6,5"),
    _make_role(2, "角色2",   "role2",    "0", "1", "1,2,3,4,5,6"),
    _make_role(3, "角色3", "role3", "0", "1", "1,2,3"),
]

USER_INFO_MOCK_BODY = {
    "msg": "操作成功",
    "code": 200,
    "permissions": [
        "example:station:add",
        "example:station:edit",
        "example:station:delete"
    ],
    "roles": ["role1", "role2"],
    "user": {
        "searchValue": None,
        "createBy": "admin",
        "createTime": "2000-07-04 12:17:21",
        "createTimeFrom": None,
        "createTimeTo": None,
        "updateBy": None,
        "updateTime": None,
        "remark": None,
        "params": {},
        "userId": 1,
        "deptId": 1,
        "userName": "-1",
        "deptName": "-1",
        "email": None,
        "phonenumber": None,
        "status": "0",
        "delFlag": "0",
        "dept": _USER_DEPT,
        "roles": _USER_ROLES,
        "roleIds": None,
        "postIds": None,
        "roleId": None,
    },
}
