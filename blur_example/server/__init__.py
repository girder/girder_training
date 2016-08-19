import os

from girder.constants import AccessType
from girder.api import access
from girder.api.describe import Description, describeRoute
from girder.api.rest import Resource, loadmodel, filtermodel, getApiUrl
from girder.plugins.worker import utils


class Blur(Resource):
    def __init__(self):
        Resource.__init__(self)

        self.resourceName = 'blur_example'
        self.route('POST', (':id',), self.createBlurImage)
        self.route('POST', ('simple_add',), self.simpleAdd)

    @access.user
    @filtermodel(model='job', plugin='jobs')
    @describeRoute(
        Description('Simple pure python addition using the worker.')
        .param('a', 'First param to be added.',
               dataType='integer', required=True)
        .param('b', 'Second param to be added.',
               dataType='integer', required=True)
    )
    def simpleAdd(self, params):
        user = self.getCurrentUser()
        token = self.getCurrentToken()
        jobTitle = 'Simple Python Addition'
        jobModel = self.model('job', 'jobs')

        job = jobModel.createJob(
            title=jobTitle, type='python_add', handler='worker_handler',
            user=user)
        jobToken = jobModel.createJobToken(job)

        scriptFile = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  'scripts', 'add_script.py')
        with open(scriptFile, 'r') as fh:
            script = fh.read()

        kwargs = {
            'task': {
                'name': 'add',
                'inputs': [
                    {
                        'name': 'a',
                        'type': 'number',
                        'format': 'number',
                        'data': int(params.get('a', 0))
                    },
                    {
                        'name': 'b',
                        'type': 'number',
                        'format': 'number',
		        'data': int(params.get('b', 1))
                    }
                ],
                'outputs': [{'name': 'c', 'type': 'number', 'format': 'number'}],
                'script': script,
                'mode': 'python'
            },
            'inputs': {
                'a': { 'format': 'number', 'data':  int(params.get('a', 0))},
                'b': { 'format': 'number', 'data':  int(params.get('b', 1))}
            },
            'jobInfo': {
                'method': 'PUT',
                'url': '/'.join((getApiUrl(), 'job', str(job['_id']))),
                'headers': {'Girder-Token': jobToken['_id']},
                'logPrint': True
            },
            'validate': False,
            'auto_convert': False
        }
        job['kwargs'] = kwargs
        job = jobModel.save(job)
        jobModel.scheduleJob(job)
        return job

    @access.user
    @loadmodel(model='item', level=AccessType.WRITE)
    @filtermodel(model='job', plugin='jobs')
    @describeRoute(
        Description('Blur an image using the worker.')
        .notes('The output image is placed in the same parent folder as the '
               'input image.')
        .param('id', 'The ID of the item containing the input image.',
               paramType='path')
    )
    def createBlurImage(self, item, params):
        user = self.getCurrentUser()
        token = self.getCurrentToken()
        jobTitle = 'ITK blur: ' + item['name']
        jobModel = self.model('job', 'jobs')
        folder = self.model('folder').load(item['folderId'], force=True)

        job = jobModel.createJob(
            title=jobTitle, type='itk_blur', handler='worker_handler',
            user=user)
        jobToken = jobModel.createJobToken(job)

        scriptFile = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  'scripts', 'cad_script.py')
        with open(scriptFile, 'r') as fh:
            script = fh.read()

        kwargs = {
            'task': {
                'name': jobTitle,
                'mode': 'python',
                'script': script,
                'inputs': [{
                    'id': 'inputFileName',
                    'type': 'string',
                    'format': 'text',
                    'target': 'filepath'
                }],
                'outputs': [{
                    'id': 'outputFileName',
                    'format': 'text',
                    'type': 'string',
                    'target': 'filepath'
                }]
            },
            'inputs': {
                'inputFileName': utils.girderInputSpec(
                    item, resourceType='item', token=token)
            },
            'outputs': {
                'outputFileName': utils.girderOutputSpec(
                    folder, token=token, parentType='folder')
            },
            'jobInfo': {
                'method': 'PUT',
                'url': '/'.join((getApiUrl(), 'job', str(job['_id']))),
                'headers': {'Girder-Token': jobToken['_id']},
                'logPrint': True
            },
            'validate': False,
            'auto_convert': False
        }
        job['kwargs'] = kwargs
        job = jobModel.save(job)
        jobModel.scheduleJob(job)
        return job

def load(info):
    info['apiRoot'].blur_example = Blur()
