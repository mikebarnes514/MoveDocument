class Document(object):
  def __init__(self, data):
    self.id = data.get('id')
    self.name = data.get('name')
    self.number = data.get('document_number')
    self.author = data.get('author_description')
    self.authorid = data.get('author')
    self.folder = ''
	
  def set_folder(self, folder_id):
    self.folder = folder_id
  
  def serialize(self):
    return {'id': self.id, 'name': self.name, 'number': self.number, 'author': self.author, 'authorid': self.authorid, 'folder': self.folder}