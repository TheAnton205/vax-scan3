##################################################################
# Created by    : Adamson dela Cruz
# Date Created  : 8/31/17
# Remarks       : The commandline interface for creating things in
#                 AWS IoT
##################################################################

from __future__ import print_function
from factories.aws.thingtype import AWSThingType
from factories.aws.thing import AWSThing
import os, json
import click

@click.group()
def main():
    '''
    Entry point of the script
    '''
    pass

def check_env():
    '''
    Checks environment variables if set. If not, do not proceed
    '''
    #
    if not 'AWS_PROFILE' in os.environ:
        print('AWS_PROFILE is not set. To set the environment run the command below.\nexport AWS_PROFILE=MYAWSPROFILE\n')
        exit(1)

    if not 'AWS_REGION' in os.environ:
        print('AWS_REGION is not set. To set the environment run the command below.\nexport AWS_REGION=region-name\n')
        exit(1)



@click.option('-d','--description', default='', help='Describes the type')
@click.option('-a', 'attributes', help='Json attribute of the type.')
@click.argument('name')
@main.command()
def newthingtype(name, attributes, description):
    check_env()

    fields = None
    with open(attributes,'r') as data:
        fields = data.read().replace("\n","").split(",")
    


    payload = {
        "thingTypeDescription": description,
        "searchableAttributes": fields
    }

    result = AWSThingType(name, payload)

    return result

@click.option('-t','--type', help='Derive from this type')
@click.option('-a', 'attributes', help='Json attribute file for the thing. Maximum of 3 attributes e.g. name,color,temperature')
@click.argument('name')
@main.command()
def newthing(name, attributes, type):

    check_env()

    payload = None
    with open(attributes) as json_data:
        payload = json.load(json_data)

    thing = AWSThing()
    result = thing.new_thing(name, type, payload)

    return result


@click.option('-a', 'attributes', help='Json attribute file for the thing. Maximum of 3 attributes e.g. name,color,temperature')
@click.argument('name')
@main.command()
def updatething(name, provider, attributes):

    check_env()

    payload = None
    with open(attributes) as json_data:
        payload = json.load(json_data)

    thing = AWSThing()
    result = thing.update_thing(name, None, payload)

    return result

@click.argument('certname')
@click.argument('name')
@main.command()
def attachcert(name, certname):

    check_env()

    thing = AWSThing()
    result = thing.attach_certificate(name, certname)

    return result
