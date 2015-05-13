"""
Test case for JIRA ticket HCC-652:
https://apixio.atlassian.net/browse/HCC-652?jql=key%20in%20(HCC-652)

This script assumes that the username in the settings file exists in the ACL system and has access
to the 'Hometown Health' organization.  Further, it is assumed that a rule exists on the sorting hat
to deal out opportunities to that user.
"""

import unittest
import csv
import requests
import json

__author__ = 'Richard J. Belcinski'
__version__ = '0.0.1'
__maintainer__ = 'Richard J. Belcinski'
__email__ = 'rbelcinski@apixio.com'


class OpportunityComparator:
    """
    This class is used to encapsulate the process of comparing two opportunities.  The constructor
    takes a single argument, a list of attributes to compare.  Only these attributes must match for
    the comparison to work.
    """
    def __init__(self, check_these):
        """
        Stash the check list.
        """
        self.check_these = check_these

    @staticmethod
    def find_all(name, packet, output_list):
        """
        Recursively walk a dictionary, adding in all simple items that match the indicated name.
        :param name: The name of items to look for.
        :param packet: The packet to search.
        :param output_list: The list of values of found items.
        :return: The final value of the output list.
        """
        if type(packet) == dict:
            # Grab the item if it is in the dictionary:
            if name in packet:
                v = packet[name]
                if type(v) != list and type(v) != dict:
                    # Add scalar type.  The above logic should probably test for iterable rather than distinct
                    # type, but I don't have time right now to learn how to do that.  Also, stuff things into
                    # the output as string so that we know that it will be sortable and comparable across
                    # polymorphic types:
                    output_list.append(str(packet[name]))
            # Grab collections and recurse:
            for k, v in packet.items():
                if type(v) == list or type(v) == dict:
                    OpportunityComparator.find_all(name, v, output_list)
        elif type(packet) == list:
            # Grab value from dictionaries and recurse over lists:
            for v in packet:
                OpportunityComparator.find_all(name, v, output_list)
        # Done:
        return output_list

    def compare(self, a, b):
        """
        Compare specific fields in the two opportunities given by a and b.
        :return True if the indicated fields are the same.
        """
        # Some locals:
        a_list = []
        b_list = []
        # Grab items in a:
        for name in self.check_these:
            OpportunityComparator.find_all(name, a, a_list)
        # Grab items in b:
        for name in self.check_these:
            OpportunityComparator.find_all(name, b, b_list)
        # Test list equivalence:
        return sorted(a_list) == sorted(b_list)


class Hcc652(unittest.TestCase):
    """
    This is the test driver for testing compatibility of the HCC 3.0 Opportunity Router against the spec
    defined in the following document:

    https://docs.google.com/a/apixio.com/document/d/1vxOsxQo8lyH9CkqQFSOf8-q0Kefjb3g3O1U2NDJOWpM/edit#heading=h.tdp2u5am3m34

    This class will assume that the targeted router server has been restarted in a configuration that will
    serve up opportunities from a well-understood data set.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up connection information for the test.
        :return: None
        """
        settings = Hcc652.readConfiguration('Settings.txt')
        cls.username = settings['username']
        cls.password = settings['password']
        cls.auth_url = settings['auth_url']
        cls.tokens_url = settings['tokens_url']
        cls.referenceSetPath = settings['referenceSetPath']
        cls.hat_url = settings['hat_url']
        cls.check_these = int(settings['check_these'])
        cls.comparator = OpportunityComparator(list(settings['tags'].split(",")))
        cls.active = True

    @staticmethod
    def readConfiguration(file_name):
        """
        Load a series of configuration parameters from the settings file and load them into a dictionary.
        :param file_name: The file name to load.
        :return: The dictionary of settings.
        """
        # Open up the file and wrap with a reader:
        rdr = csv.reader(open(file_name, 'r'), delimiter='=', quotechar='"')
        # Construct dictionary using comprehension:
        return {row[0]: row[1] for row in rdr}

    @staticmethod
    def readReferenceSet(file_name):
        """
        Read a reference set from a file.
        :param file_name: The file to read.
        :return: A dictionary of json strings by Patient-HCC.
        """
        # Open up the file and wrap with a reader:
        rdr = csv.reader(open(file_name, 'r'), delimiter='|', quotechar='"')
        # Construct dictionary using comprehension:
        return {row[0]: row[1] for row in rdr}

    def unpackToken(self, response):
        """
        Get the token string from a JSON packet in the passed response object.
        :param response: A response object that we can use to pull JSON.
        :return: The JSON string, or an error message, or None.
        """
        # Test for 401 explicitly... JSON retrieval will throw otherwise:
        if response.status_code == 401:
            return "Unauthorized"
        # Get json:
        r = response.json()
        # Unpack the JSON and replace the response dictionary with the simple string:
        if r is not None:
            # Is the token there?
            if 'token' not in r:
                # Give the user some idea what is going on:
                if 'message' in r:
                    # Message if present:
                    r = r['message']
                if 'description' in r:
                    # Problem description if present:
                    r = r['description']
            else:
                # Got the token:
                r = r['token']
        return r

    def getExternalToken(self):
        """
        Attempt to get the external token.
        :return: A tuple containing the status code and a token, which can be None.
        """
        # Form up request:
        response = requests.post(
            self.auth_url, data={'email': self.username, 'password': self.password}, headers={})
        # Package stuff up:
        return response.status_code, self.unpackToken(response)

    def getInternalToken(self, ext):
        """
        Attempt to get an internal token.
        :param ext: The external token to swap.
        :return: A tuple containing the status code and a token, which can be None.
        """
        # Form up request:
        response = requests.post(self.tokens_url, data={}, headers={'Authorization': 'Apixio ' + ext})
        # Package stuff up:
        return response.status_code, self.unpackToken(response)

    def getToken(self):
        """
        Bootstrap ourselves to an internal token.
        :return: An internal token.  Will throw if unsuccessful.
        """
        # Token swapping stuff:
        external = self.getExternalToken()
        if not external[0] == 200:
            raise ValueError('Cannot get external token: ' + str(external))
        internal = self.getInternalToken(external[1])
        if not internal[0] == 201:
            raise ValueError('Cannot get internal token: ' + str(internal))
        # Done:
        return internal[1]

    def initialize(self):
        """
        Send an initialize command to the hat for this class's username.
        :return: The status code for the command.  Normally should be 201.
        """
        # Form the initialization URL:
        url = self.hat_url + '/' + self.username + '/initialize'
        # Token swapping stuff:
        tok = self.getToken()
        # Post it off:
        response = requests.put(url, data={}, headers={'Authorization': 'Apixio ' + tok})
        # Done:
        return response.status_code

    def getNext(self):
        """
        Get a work item from the sorting hat, assuming initialization worked.
        :return: A tuple containing a response code and the JSON of the response.
        """
        # Form the next_work_item URL:
        url = self.hat_url + '/' + self.username + '/next_work_item'
        # Token swapping stuff:
        tok = self.getToken()
        # Post it off:
        response = requests.get(url, data={}, headers={'Authorization': 'Apixio ' + tok})
        # Done:
        return response.status_code, response.json()

    def test_get_set(self):
        """
        Read a bunch of opportunities and assure that they match against the reference
        set.
        """
        # Construct reference set:
        references = self.readReferenceSet(self.referenceSetPath)
        # The test should succeed for all tries:
        count = 0
        # Loop:
        
        # initialize if the user has not already been initialized.
        self.initialize()
        
        for i in range(1, self.check_these):
            # Pull opportunity:
            o = self.getNext()
            # Success?
            if o[0] == 200:
                # Unpack the JSON into a dictionary:
                #print o[1]
                #quit()
                ojs = json.loads(json.dumps(o[1]))
                #print ojs
                # Form a FQ-HCC key:
                key = ojs['patient_id'] + '-' + \
                    str(ojs['hcc']) + '-' + str(ojs['model_year']) + '-' + str(ojs['model_run']) + '-' + \
                    str(ojs['payment_year'])
                # Reference opp as a dictionary:
                r = json.loads(json.dumps(references[key]))
                # compare:
                if self.comparator.compare(ojs, r):
                    count += 1
               
        # Done:
        self.failIf(count < self.check_these)

    @classmethod
    def tearDownClass(cls):
        """
        Close connections, if any...
        :return: None
        """
        cls.active = False

# Run the script as a test if this is the main module:
if __name__ == "__main__":
    h = Hcc652()
    h.setUpClass()
    external_token = h.getExternalToken()
    print(external_token)
    internal_token = h.getInternalToken(external_token[1])
    print(internal_token)
    ini = h.initialize()
    print(ini)
    refer = h.readReferenceSet(h.referenceSetPath)
    all_keys = list(refer.keys())
    first = refer[all_keys[0]]
    second = refer[all_keys[1]]
    ad = json.loads(first)
    bd = json.loads(second)
    result1 = h.comparator.compare(ad, ad)
    result2 = h.comparator.compare(ad, bd)
    result3 = h.comparator.compare(bd, bd)
    print(result1, result2, result3)
