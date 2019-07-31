class Folder(object):
  def __init__(self, data):
    self.id = data.get('id')
    self.name = data.get('name')
    self.path = ''
    self.workspace = ''
    self.clientmatter = ''
    
  def set_path(self, path):
    self.path = path
    self.workspace = path.split('/')[0]
    
  def set_clientmatter(self, cm):
    self.clientmatter = cm
   