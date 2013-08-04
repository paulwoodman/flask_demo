import getpass
import ldap


class LDAPBackend(object):

    def __init__(self, Ldap_URL, BaseDN, TraceLevel=0):
        self.LDAP_URL = Ldap_URL
        self.BASE_DN = BaseDN
        self.TRACE_LEVEL = TraceLevel
        self.retrive_attributes = ['uid', 'mail', 'givenName', 'sn', 'sAMAccountName', 'memberOf']
        self.is_bound = False
        self.has_data = False
        self.auth_error_msg = "None"
        self.error_msg = "None"

        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        ldap.set_option(ldap.OPT_REFERRALS, 0)

        # Connect to LDAP and do a simple bind.
        self.l = ldap.initialize(self.LDAP_URL, trace_level=self.TRACE_LEVEL)

    def disconnect(self):
        if self.is_bound:
            self.l.unbind_s()

    def get_members_in_group(self, group_cn):
        try:
            self.l.simple_bind_s()
            self.is_bound = True
            search_string = "groupMembership=%s" % group_cn
            results = self.l.search_s(
                self.BASE_DN,
                ldap.SCOPE_SUBTREE,
                search_string,
                self.retrive_attributes)
            return results
        except:
            return False

    def authenticate_user(self, username, password):
        try:
            if len(password) == 0:
                return None
            binddn = "cn=%s,%s" % (username, self.BASE_DN)
            self.l.simple_bind_s(binddn, password)
            self.is_bound = True
            return True

        except ldap.LDAPError, e:
            if type(e.message) == dict and 'desc' in e.message:
                self.auth_error_msg = e.message['desc']
                return False
            else:
                self.auth_error_msg = e
                return False
        except ldap.INVALID_CREDENTIALS:
            self.auth_error_msg = "Wrong username and password"
            return False

    def get_user_details(self, username, retrive_attributes="all"):
        try:
            binddn = "cn=%s,%s" % (username, self.BASE_DN)
            self.l.simple_bind_s()
            self.is_bound = True
            search_string = "cn=%s" % username
            if retrive_attributes == "all":
                res = self.l.search_ext_s(self.BASE_DN, ldap.SCOPE_SUBTREE, search_string)
            else:
                res = self.l.search_ext_s(self.BASE_DN, ldap.SCOPE_SUBTREE, search_string, retrive_attributes)

            if not res:
                self.error_msg = "AD auth ldap backend error by searching. No result."
                return False

            assert len(res)>=1, "Result should contain at least one element: %s" % res
            result = res[0][1]
            return result

        except ldap.LDAPError, e:
            if type(e.message) == dict and 'desc' in e.message:
                self.error_msg = e.message['desc']
                return False
            else:
                self.error_msg = e
                return False
        except ldap.INVALID_CREDENTIALS:
            self.error_msg = "Wrong username and password"
            return False

    def get_user_groups(self, username):
        empty_dic = {}
        res = self.get_user_details(username, ['groupMembership'])

        if not res:
            self.error_msg = "Error in getting user groups for username : " + str(username) + ", No results."
            return False

        assert len(res)>=1, "Result should contain at least one element: %s" % res
        if 'groupMembership' in res:
            return res['groupMembership']
        else:
            self.error_msg = "No Groups found"
            return empty_dic

    def is_user_memberof(self, username, groups):
        # Let's get all the groups for user
        user_groups = self.get_user_groups(username)

        if len(user_groups) == 0:
            return False

        for req_grp in groups:
            # Buidl our search string
            group_str = "cn=%s," % req_grp
            # try to match the above group_str with user groups
            for grp in user_groups:
                if grp.find(group_str) >= 0:
                    return True

        # couldn't match anything return False
        return False

# Below are all the test functions.
# none of them is actually called from application
# and shouldn't need to be as well.
def group_members_test():
    ldap_conn = LDAPBackend("ldaps://edir1.ord1.corp.rackspace.com:636", "ou=users,o=rackspace", 1)
    g_members = ldap_conn.get_members_in_group("cn=lnx-CloudServer-Admins,ou=POSIXGroups,o=rackspace")

    for user in g_members:
        print user

    ldap_conn.disconnect()


def print_user_details(user, attributes_dic):
    for attr in attributes_dic:
        if attr in user[1]:
            print attr + ": " + str(user[1][attr][0])
        else:
            print attr + " KeyNotFound"


def auth_test():
    ldap_conn = LDAPBackend("ldaps://edir1.ord1.corp.rackspace.com:636", "ou=Users,o=rackspace", 2)
    username = raw_input('Please enter your SSO: ')
    password = getpass.getpass()
    if ldap_conn.authenticate_user(username, password):
        print "Success!"
    else:
        print "Failure"
        print ldap_conn.auth_error_msg

    search_username = raw_input('Enter the user to pull details for:')
    user_details = ldap_conn.get_user_details(search_username)

    if user_details:
        print user_details
    else:
        print "Something bad happened, ldap error below"
        print ldap_conn.error_msg

    ldap_conn.disconnect()


def details_test():
    group_membership_req = ['Group_Required', 'Alternative_Group']
    attributes = ['uid', 'mail', 'givenName', 'sn', 'displayName', 'memberOf',
                  'ipPhone', 'title', 'directSupervisorEmail', 'ou', 'homePostalAddress'
                 ]
    ldap_conn = LDAPBackend("ldaps://edir1.ord1.corp.rackspace.com:636", "ou=Users,o=rackspace", 0)
    username = raw_input('Please enter usenrame: ')
    user_details = ldap_conn.get_user_details(username)

    if user_details:
        print user_details
    else:
        print "Something bad happened, ldap error below"
        print ldap_conn.error_msg

    user_groups = ldap_conn.get_user_details(username, ['groupMembership'])
    print "Group memberships: "
    print user_groups

    groups = ldap_conn.get_user_groups(username)
    print "Group membership: "
    print groups

    print " ==> Checking Group memebers for group lnx-CloudServer-Admins "

    if ldap_conn.is_user_memberof(username, ['lnx-CloudServer-Admins']):
        print "True"
    else:
        print "False"

    # Disconnect
    ldap_conn.disconnect()


if __name__ == "__main__":
    #group_members_test()
    #auth_test()
    details_test()
