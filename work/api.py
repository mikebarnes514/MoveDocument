import requests
import config
import urllib
import pprint
from flask import session, jsonify
from .document import Document
from .folder import Folder
from .oauth import client

base_url = config.WORK_CONFIG['base_url']

def find_document(document_number):
  assert document_number, 'No document number has been specified'
  doc = None
  response = client.get('/api/v2/customers/1/libraries/MJ_DMS/documents/search?document_number={}'.format(document_number))
  if response.status == 200:
    doc = Document(response.data['data'][0])
    if doc.id:
			doc.set_folder(get_document_folder(doc.id).get('id'))
	
  return doc
  
def get_document_folder(document_id):
	assert document_id, 'No document id has been specified'
	folder = None
	response = client.get('/api/v2/customers/1/libraries/MJ_DMS/documents/{}/path'.format(document_id))
	if response.status == 200:
		folders = response.data['data'][0]
		folder = folders[len(folders) - 1];

	return folder
  
def get_preview_url(document_id):
  assert document_id, 'No document ID has been specified'
  return '{}/link/d/{}'.format(base_url, document_id)

def get_folder_browser_url():
  url = ''
  response = client.post('/api/v1/session/dialog-tokens')
  if response.status == 201:
    dialog_token = response.data.get('data').get('dialog_token')
    url = base_url + '/web/dialogs/file-picker/?protocol=postmessage&dialogToken={}&mode=browse&types=folder'.format(dialog_token)
  
  return url

def find_personal_workspace(employee_name):
  assert employee_name, 'No employee name has been specified'
  workspace = None
  #if employee_name.endswith('.'):
  #  employee_name = employee_name[:-2]
    
  search_term = urllib.quote('Personal Workspace {}'.format(employee_name.replace(',', '')))
  response = client.get('/api/v2/customers/1/libraries/MJ_DMS/workspaces/search?name={}'.format(search_term))
  if response.status == 200:
    workspace = response.data.get('data')[0]
  
  return workspace
  
def find_folder(workspace, name):
  assert workspace, 'No personal workspace has been specified'
  assert name, 'No folder name has been specified'
  folder = None
  response = client.get('/api/v2/customers/1/libraries/MJ_DMS/workspaces/{}/children?limit=500'.format(workspace['id']))
  if response.status == 200:
    folder_json = next((x for x in response.data.get('data') if x['name'] == name), None)
    if folder_json:
      folder = Folder(folder_json)
      if folder.id:
        folder.set_path(build_folder_path(folder.id))
        folder.set_clientmatter(get_folder_clientmatter(folder.id))
  
  return folder
  
def find_folder_by_id(folderid):
	assert folderid, 'No folder id has been specified'
	folder = None
	response = client.get('/api/v2/customers/1/libraries/MJ_DMS/folders/{}'.format(folderid))
	if response.status == 200:
		folder = Folder(response.data.get('data'))
		if folder.id:
			folder.set_path(build_folder_path(folder.id))
			folder.set_clientmatter(get_folder_clientmatter(folder.id))
  
	return folder
	  
def build_folder_path(folder_id):
  assert folder_id, 'No folder id has been specified'
  path = ''
  response = client.get('/api/v2/customers/1/libraries/MJ_DMS/folders/{}/path'.format(folder_id))
  if response.status == 200:
    path = '/'.join([x['name'] for x in response.data.get('data')])
  
  return path
  
def move_document_to_folder(doc_id, source_id, destination_id):
  assert doc_id, 'No document id has been specified'
  assert source_id, 'No source folder id has been specified'
  assert destination_id, 'No destination folder id has been specified'
  payload = {'destination_folder_id': destination_id}
  response = client.post('/api/v2/customers/1/libraries/MJ_DMS/folders/{}/documents/{}/move'.format(source_id, doc_id), data=payload, format='json')
  if response.status == 200:
    response = refile_document(destination_id, doc_id)
  
  return response
    
def get_documents_in_folder(folder_id):
  documents = []
  assert folder_id, 'No folder id has been specified'
  response = client.get('/api/v2/customers/1/libraries/MJ_DMS/folders/{}/documents'.format(folder_id))
  if response.status == 200:
    for doc in response.data.get('data'):
      documents.append(Document(doc))
    
  return documents
  
def rename_document(doc_id, new_name):
  assert doc_id, 'No document id has been specified'
  assert new_name, 'No name has been specified'
  payload = {'name': new_name}
  response = client.patch('/api/v2/customers/1/libraries/MJ_DMS/documents/{}'.format(doc_id), data=payload, format='json')
  return response
    
def get_current_user():
  username = None
  response = client.get('/api/v2/customers/1/libraries/MJ_DMS/users/me')
  if response.status == 200:
    username = response.data.get('data')['id']
    
  return username

def get_user_display_name(user_id):
  assert user_id, 'No user id has been specified'
  full_name = ''
  response = client.get('/api/v2/customers/1/libraries/MJ_DMS/users/{}'.format(user_id))
  if response.status == 200:
    full_name = response.data.get('data')['full_name']
    
  return full_name

def get_folder_clientmatter(folder_id):
  clientmatter = ''
  assert folder_id, 'No folder id has been specified'
  response = client.get('/api/v2/customers/1/libraries/MJ_DMS/folders/{}/name-value-pairs'.format(folder_id))
  if response.status == 200:
    clientmatter = '{}-{}'.format(response.data.get('data').get('iMan___25'), response.data.get('data').get('iMan___26'))
      
  return clientmatter
  
def refile_document(folder_id, doc_id):
  assert folder_id, 'No folder id has been specified'
  assert doc_id, 'No document id has been specified'
  folder_security = get_folder_security(folder_id)
  folder_profile = get_folder_profile(folder_id)
  print('\n\r')
  pprint.pprint(folder_security)
  print('\n\r')
  if folder_security.get('default_security'):
    folder_profile['default_security'] = folder_security.get('default_security')
    
  if folder_profile:
    response = client.patch('/api/v2/customers/1/libraries/MJ_DMS/documents/{}'.format(doc_id), data=folder_profile, format='json')
    
  if folder_security and folder_security.get('include'):
    response = client.post('/api/v2/customers/1/libraries/MJ_DMS/documents/{}/security'.format(doc_id), data=folder_security, format='json')
             
  return response
  
def get_folder_security(folder_id):
  security = None
  assert folder_id, 'No folder id has been specified'
  response = client.get('/api/v2/customers/1/libraries/MJ_DMS/folders/{}/security'.format(folder_id))
  if response.status == 200:
    security = {'include': response.data.get('data'), 'default_security': response.data.get('default_security')}
    if security.get('default_security') == 'inherit':
      response = client.get('/api/v2/customers/1/libraries/MJ_DMS/folders/{}'.format(folder_id))
      if response.status == 200:
        security['default_security'] = response.data.get('data').get('inherited_default_security')
        
  return security
  
def get_folder_profile(folder_id):
  profile = {}
  assert folder_id, 'No folder id has been specified'
  response = client.get('/api/v2/customers/1/libraries/MJ_DMS/folders/{}/name-value-pairs'.format(folder_id))
  if response.status == 200:
    dict = response.data.get('data')
    if 'iMan___25' in dict:
      profile['custom1'] = dict['iMan___25']
    if 'iMan___26' in dict:
      profile['custom2'] = dict['iMan___26']
    if 'iMan___8' in dict:
      profile['class'] = dict['iMan___8']
    if 'iMan___28' in dict:
      profile['custom4'] = dict['iMan___28']
    if 'iMan___29' in dict:
      profile['custom5'] = dict['iMan___29']
    if 'iMan___30' in dict:
      profile['custom6'] = dict['iMan___30']      
        
  return profile
  
