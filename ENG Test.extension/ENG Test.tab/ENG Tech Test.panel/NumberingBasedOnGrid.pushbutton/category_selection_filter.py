import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI.Selection import ISelectionFilter

# Custom selection filter to allow only elements of a specific category
class CategorySelectionFilter(ISelectionFilter):
    def __init__(self, category_name):
        self.category_name = category_name

    def AllowElement(self, element):
        # Allow elements that belong to the specified category
        if element.Category and element.Category.Name == self.category_name:
            return True
        return False



    def AllowReference(self, reference, point):
        # Allow references to elements that belong to the specified category
        element = reference.Element
        if element.Category and element.Category.Name == self.category_name:
            return True
        return False