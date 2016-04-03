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
