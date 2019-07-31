from flask import Flask, render_template, session, request, jsonify
import work
import logging
import database
from pprint import pprint
app = Flask(__name__)
app.logger.setLevel(logging.INFO)
handler = logging.FileHandler('movedocument.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.config.from_pyfile('config.py')
work.routes.register(app)

@app.after_request
def add_header(response):
	if 'Cache-Control' not in response.headers:
		response.headers['Cache-Control'] = 'no-store'
	return response
	
@app.route('/')
def home():
  return render_template('home.html')
  
@app.route('/mj-move-document')
@work.token.required
def move_document():
  doc_number = request.args.get('number')  
  doc = work.api.find_document(doc_number)
  current_user = work.api.get_current_user()
  lock_status = database.check_lock(doc_number)
  if lock_status == '':
    database.lock_scan(doc_number, current_user)
  elif lock_status != current_user:
    return render_template('locked.html', doc_name=doc.name, lock_user=work.api.get_user_display_name(lock_status))
    
  assistants = database.get_assistants(doc.authorid)
  preview_url = work.api.get_preview_url(doc.id)
  dialog_url = work.api.get_folder_browser_url()
  number_tag = 'doc.number::{}'.format(doc_number);
  return render_template('movedocument.html', doc_name=doc.name, author=doc.author, assistants=assistants, doc_id=doc.id, src_folder=doc.folder, preview_url=preview_url, dialog_url=dialog_url, doc_number=doc_number, doc_number_tag=number_tag)
  
@app.route('/mj-scanned-mail-folder')
@work.token.required
def find_scanned_mail_folder():  
  author = request.args.get('author')
  workspace = work.api.find_personal_workspace(author)
  folder = work.api.find_folder(workspace, 'Scanned Mail')
  
  return jsonify(folder.__dict__)

@app.route('/mj-get-folder')
@work.token.required
def find_folder():
  folder_id = request.args.get('id')
  folder = work.api.find_folder_by_id(folder_id)  
  return jsonify(folder.__dict__)
  
@app.route('/mj-get-folder-documents')
@work.token.required
def get_folder_documents():
  folder_id = request.args.get('id')
  documents = work.api.get_documents_in_folder(folder_id)
  return jsonify(docs=[d.serialize() for d in documents])
	
@app.route('/mj-folder-dialog-url')
@work.token.required
def getdialogurl():
  return work.api.get_folder_browser_url()

@app.route('/mj-move', methods=['POST'])
@work.token.required
def move_document_to_folder():
  doc_id = request.form.get('document-id')
  source_id = request.form.get('source-id')
  destination_id = request.form.get('destination-id')
  response = work.api.move_document_to_folder(doc_id, source_id, destination_id)
  
  if response.status != 200:
    logging.warn('failed to move {} from {} to {}: {}'.format(doc_id, source_id, destination_id, response.status))

  return app.make_response((jsonify(response.data), response.status))
	
@app.route('/mj-rename', methods=['POST'])
@work.token.required
def rename_document():
  doc_id = request.form.get('document-id')
  name = request.form.get('name')
  response = work.api.rename_document(doc_id, name)

  if response.status != 200:
    logging.warn('failed to rename {} to {}: {}'.format(doc_id, name, response.status))
    
  return app.make_response((jsonify(response.data), response.status))

@app.route('/mj-unlock-scan', methods=['POST'])
@work.token.required
def unlock_document():
  doc_number = request.form.get('number')
  try:
    database.unlock_scan(doc_number)
    return app.make_response(("OK", 200))
  except Exception as ex:
    print(ex)
    return app.make_response((ex, 500))
    
if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', ssl_context=('certificate/star_061918.crt', 'certificate/star_061918_nophrase.key'))
