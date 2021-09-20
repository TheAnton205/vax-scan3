##################################################################
# Created by    : Adamson dela Cruz
# Date Created  : 8/31/17
# Remarks       : The AWS Thing
##################################################################

from __future__ import print_function
from factories.aws import __client, initialize

client = __client

class AWSThing:
    ''' The device representation as a thing in AWS IoT '''

    ##################################################################
    #  Initializes the AWS client object
    ##################################################################
    def init_client(self):

        global client
        try:
            if client is None:
                client = initialize()
                if not type(client).__name__ == 'IoT':
                    print('The client variable resolve into an invalid type... ')
                    exit(1)

        except Exception as ex:
            print("ERROR:", ex)


    ##################################################################
    # Creates a new thing from the thing
    ##################################################################
    def new_thing(self, name, thingtype, payload):

        global client
        self.init_client()

        try:
            print("Creating new thing ", name)

            if thingtype is None:
                response = client.create_thing(
                    thingName = name,
                    attributePayload={
                        'attributes': payload,
                        'merge': False # Overwrite the property in the registry
                    }

                )
                print(response)

            else:
                response = client.create_thing(
                    thingName=name,
                    thingTypeName=thingtype,
                    attributePayload={
                        'attributes': payload,
                        'merge': False  # Overwrite the property in the registry
                    }

                )
                print(response)

        except Exception as ex:
            print("ERROR:", ex)


    ##################################################################
    # Updates a thing from the thing
    ##################################################################
    def update_thing(self, name, thingtype, payload):

        global client
        self.init_client()

        try:
            print("Updating thing ", name)

            if thingtype is None:
                response = client.update_thing(
                    thingName = name,
                    attributePayload={
                        'attributes': payload,
                        'merge': False # Overwrite the property in the registry
                    }

                )
                print(response)

            else:
                response = client.update_thing(
                    thingName=name,
                    thingTypeName=thingtype,
                    attributePayload={
                        'attributes': payload,
                        'merge': False  # Overwrite the property in the registry
                    }

                )
                print(response)

        except Exception as ex:
            print("ERROR:", ex)


    ##################################################################
    # Attaches a certificate to an existing thing
    ##################################################################
    def attach_certificate(self, name, cert_name):

        global client
        self.init_client()

        try:
            response = client.attach_thing_principal(
                thingName=name,
                principal=cert_name
            )

            print("CERTIFICATE:", response)

        except Exception as ex:
            print("ERROR:", ex)