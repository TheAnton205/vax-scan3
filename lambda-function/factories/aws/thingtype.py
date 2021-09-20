##################################################################
# Created by    : Adamson dela Cruz
# Date Created  : 8/31/17
# Remarks       : AWS Thing Type
##################################################################

from __future__ import print_function
from factories.aws import __client, initialize

client = __client

class AWSThingType:
    ''' The device representation as a thing type in AWS IoT '''

    def __init__(self, name, props):
        ''' Creates a new thing type. Thing Types has a maximum of only 3 attributes '''
        global client
        try:

            if client is None:
                client = initialize()
                if not type(client).__name__ == 'IoT':
                    print('The client variable resolve into an invalid type... ')
                    exit(1)
                response = client.create_thing_type(
                    thingTypeName=name,
                    thingTypeProperties=props
                )
                print(response)

        except Exception as ex:
            print("ERROR:", ex)