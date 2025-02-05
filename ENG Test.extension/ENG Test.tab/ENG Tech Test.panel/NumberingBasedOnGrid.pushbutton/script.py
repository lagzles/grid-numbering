import clr
clr.AddReference('RevitServices')

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import ObjectType

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import MessageBox

clr.AddReference('System.Drawing')
from System import Enum

from progress_form import ProgressBarWindow
from category_selection_filter import CategorySelectionFilter

# Get the current Revit document
doc = __revit__.ActiveUIDocument.Document # DocumentManager.Instance.CurrentDBDocument
uidoc = __revit__.ActiveUIDocument # = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument



valid_cateogries = [
        BuiltInCategory.OST_Walls,
        BuiltInCategory.OST_Floors,
        BuiltInCategory.OST_Doors,
        BuiltInCategory.OST_Windows,
        BuiltInCategory.OST_Ceilings,
        BuiltInCategory.OST_StructuralFraming,
        BuiltInCategory.OST_StructuralColumns,
        BuiltInCategory.OST_Columns,
        BuiltInCategory.OST_CurtainWallPanels,
        BuiltInCategory.OST_Furniture,
        BuiltInCategory.OST_PlumbingFixtures,
        BuiltInCategory.OST_PlumbingEquipment,
        BuiltInCategory.OST_ElectricalFixtures,
        BuiltInCategory.OST_MechanicalEquipment
    ]

######################################
###### PARAMETERS FUNCTIONS ##########

def is_category_valid(category):
    """
    Verify if category is valid in accepting Shared parameters

    Args:
        category: Autodesk.Revit.DB.BuiltInCategory.

    Returns:
        boolean: Return true for valid, false for not valid.

    Raises:

    """
    categories = get_categories()

    return category.Id.IntegerValue in [int(cat) for cat in categories]


# Function to check if a parameter exists, and create it if it doesn't
def ensure_parameter_exists(param_name, param_type):
    """
        Verify if the group for the parameters is already created. If not: is created
        Verify if the param_name is already in use. If not: is created
        And creates a instance binding, if it doesn't exists already

        Args:
            param_name: string
            param_type: SpecTypeId - RVT > 22 | ParameterType RVT < 22
        """

    group_name = "GridTools"
    binding = doc.ParameterBindings
    iterator = binding.ForwardIterator()
    while iterator.MoveNext():
        if iterator.Key.Name == param_name:
            return True
    # Create the parameter if it doesn't exist
    category_set = CategorySet()
    for category in doc.Settings.Categories:
        if is_category_valid(category):
            category_set.Insert(category)

    new_param = ExternalDefinitionCreationOptions(param_name, param_type)
    shared_param_file = doc.Application.OpenSharedParameterFile()
    if not shared_param_file:
        raise Exception("Arquivo de parametros compartilhados nao encontrado!")

    # Verifica se o grupo ja existe
    group = shared_param_file.Groups.get_Item(group_name)
    if not group:
        group = shared_param_file.Groups.Create(group_name)

    existing_param = group.Definitions.get_Item(param_name)
    if existing_param:
        definition = existing_param
    else:
        definition = group.Definitions.Create(new_param)

    instance_binding = doc.Application.Create.NewInstanceBinding(category_set)
    t = Transaction(doc, "Transaction to setting params values")
    t.Start()
    try:
        binding_map = binding.Insert(definition, instance_binding, BuiltInParameterGroup.PG_DATA)
        t.Commit()
    except:
        t.RollBack()

    # binding_map = binding.Insert(definition, BuiltInParameterGroup.PG_TEXT, category_set)
    return binding_map

# function to create both parameter the script needs
def verify_grid_parameters():
    """
        Check the revit version
        Creates the parameters

        Return:
            boolean: If the verification was successful
        """
    revit_version = int(doc.Application.VersionNumber)

    text_param_type = SpecTypeId.String.Text
    number_param_type = SpecTypeId.String.Text # SpecTypeId.Number
    # Verific condicional para versoes antes e depois de 2021
    if revit_version < 2023:
        text_param_type = ParameterType.Text
        number_param_type = ParameterType.Text # Number

    try:
        ensure_parameter_exists("Grid Square", text_param_type)# ParameterType.Text)
        ensure_parameter_exists("Number", number_param_type)

        return True
    except Exception as e:
        return False

#####################################
#### grind numbering functions ######

# Function to find the closest grid intersection
def find_closest_grid_intersection(element):
    """
        Find grids closest to the element

        Args:
            element (element): Element
    """
    grids = FilteredElementCollector(doc).OfClass(Grid).ToElements()
    closest_intersection = None
    min_distance = float('inf')
    element_location = element.Location.Point

    # Separate grids into vertical and horizontal
    vertical_grids = []
    horizontal_grids = []

    for grid in grids:
        curve = grid.Curve
        direction = curve.GetEndPoint(1) - curve.GetEndPoint(0)  # Direction vector of the grid line
        direction = direction.Normalize()  # Normalize the vector

        # Check if the grid is vertical (aligned with Y-axis)
        if abs(direction.X) < 0.1 and abs(direction.Y) > 0.9:
            vertical_grids.append(grid)
        # Check if the grid is horizontal (aligned with X-axis)
        elif abs(direction.X) > 0.9 and abs(direction.Y) < 0.1:
            horizontal_grids.append(grid)

    # Find the closest intersection
    closest_intersection = None
    min_distance = float('inf')
    element_location = element.Location.Point

    for vertical_grid in vertical_grids:
        for horizontal_grid in horizontal_grids:
            curve1 = vertical_grid.Curve
            curve2 = horizontal_grid.Curve
            intersection_result = curve1.Intersect(curve2)
            if intersection_result == SetComparisonResult.Overlap:
                intersection_point = curve1.Project(curve2.GetEndPoint(0)).XYZPoint
                distance = element_location.DistanceTo(intersection_point)
                if distance < min_distance:
                    min_distance = distance
                    closest_intersection = "{0}-{1}".format(vertical_grid.Name,
                                                            horizontal_grid.Name)  # Format: Vertical-Horizontal
    return closest_intersection

# Function to number elements based on spatial proximity
def number_elements(elements, start_element):
    """
        Number elements in the array, due to their distance to the first element

        Args:
            start_element: Element
            elements: Element[]
    """
    sorted_elements = sorted(elements, key=lambda x: x.Location.Point.DistanceTo(start_element.Location.Point))
    for i, element in enumerate(sorted_elements, start=1):
        param = element.LookupParameter("Number")
        if param:
            param.Set(str(i))

# Function to get the location point of an element
def get_element_location(element):
    """
        Gets the element location point. If is based on Curve, it returns it first point

        Args:
            element: Element
        Return:
            point: Autodesk.Revit.DB.XYZ
        Raise:
            Exception: Element location type not supported.
    """
    location = element.Location
    if isinstance(location, LocationPoint):
        return location.Point
    elif isinstance(location, LocationCurve):
        return location.Curve.GetEndPoint(0)  # Use the start point of the curve
    else:
        raise Exception("Element location type not supported.")





# Main function for the tool
def grid_based_numbering(selector_filter):
    """
        Main script fuction.
        Verifies if the params are created.
        Asks for the Elements array
        Asks for the starting Element
        Find the closest grids for each Element
        Give's each Element a number due it distance to the first Element
    Args:
        selector_filter: ISelectionFilter
    """
    parameters_verified = verify_grid_parameters()

    if not parameters_verified:
        MessageBox.Show("Parameters could not be verified... something went wrong. Please check if you have a shared parameters file", "Problem With Shared Parameters File")
        return

    try:
        elements = select_elements(selector_filter)
        start_element = select_first_element(selector_filter)
    except Exception as e:
        MessageBox.Show("The tool need's the user to select one or more elements", "Elements Selection")
        return

    # Convert the elements array to a set of ElementIds
    element_ids = {element.Id for element in elements}

    # Check if start_element is in the set
    if start_element.Id not in element_ids:
        elements.insert(0, start_element)

    progress_form = ProgressBarWindow()
    progress_form.Show()
    progress_form.update_progress(0, 0, len(elements))

    # Assign Grid Square and Number
    t = Transaction(doc, "Transaction to setting params values")
    t.Start()
    try:
        for  i, element in enumerate(elements, start=1):
            grid_square = find_closest_grid_intersection(element)
            if grid_square:
                param = element.LookupParameter("Grid Square")
                if param:
                    param.Set(grid_square)

            progress_bar_value = (float(i) / float(len(elements))) * 100.0
            progress_form.update_progress(progress_bar_value, str(i), len(elements))

        number_elements(elements, start_element)
        t.Commit()

        progress_form.Close()
        MessageBox.Show("All elements where numbered with great success", "Successfull")

    except Exception as e:
        t.RollBack()
        progress_form.Close()
        MessageBox.Show("Grid-based numbering failed.", "Error")


######################################
###### USER ELEMENTS SELECTION ##########

# Function to select elements
def select_elements(selector_filter):
    # Prompt the user to select multiple elements
    if selector_filter is not None:
        element_refs = uidoc.Selection.PickObjects(ObjectType.Element, selector_filter, "Select elements")
    else:
        element_refs = uidoc.Selection.PickObjects(ObjectType.Element, "Select elements")

    selected_elements = [doc.GetElement(ref.ElementId) for ref in element_refs]

    return selected_elements

def select_first_element(selector_filter):
    # Prompt the user to select one element
    if selector_filter is None:
        element_ref = uidoc.Selection.PickObject(ObjectType.Element, "Select the starting element")
    else:
        element_ref = uidoc.Selection.PickObject(ObjectType.Element, selector_filter, "Select the starting element")

    selected_element = doc.GetElement(element_ref.ElementId)

    return selected_element

######################################
###### USER ELEMENTS SELECTION ##########

def get_categories():
    categories = doc.Settings.Categories
    allowed_categories = [cat.Name for cat in categories if cat.AllowsBoundParameters]
    allowed_categories.sort()
    return allowed_categories

def get_builtin_category_from_string(category_name):
    try:
        categories = doc.Settings.Categories
        builtin_category = [category for category in categories if category.Name == category_name]
        return builtin_category[0]
    except Exception as e:
        print("Categoria '{0}' nao encontrada em BuiltInCategory.".format(category_name))
        return None


clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")

from System.Windows import Window, Application, WindowStartupLocation
from System.Windows.Controls import Button, StackPanel, ToolTip, TextBlock, Label, ComboBox
from System.Windows import Thickness
from System.Windows.TextWrapping import Wrap
from System.Collections.Generic import List

class GridBasedNumberingWindow(Window):
    def __init__(self):
        self.Title = "Grid-Based Numbering"
        self.Width = 300
        self.Height = 400

        self.panel = StackPanel()
        self.panel.Margin = Thickness(20)
        self.Content = self.panel
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen

        tooltip_text = "Execute the script"

        label_description = "This tool assigns a 'Grid Square' parameter to selected elements based on "
        label_description+= "the closest grid intersection (e.g., A-1) and "
        label_description+= "a 'Number' parameter based on their spatial proximity, "
        label_description+= "starting from a user-selected element"

        self.text_block = TextBlock()
        self.text_block.Text = label_description
        self.text_block.TextWrapping = Wrap
        self.text_block.Margin = Thickness(0, 0, 0, 20)
        self.panel.Children.Add(self.text_block)

        self.button_execute_numbering = Button()
        self.button_execute_numbering.Content = "Execute Numbering"
        self.button_execute_numbering.Margin = Thickness(0, 10, 0, 10)
        self.button_execute_numbering.Height = 40
        self.button_execute_numbering.Click += self.run_tool
        self.button_execute_numbering.ToolTip = ToolTip(Content=tooltip_text)
        self.panel.Children.Add(self.button_execute_numbering)

        # Add a label
        self.label = Label()
        self.label.Margin = Thickness(0, 10, 0, 10)
        self.label.Height = 10
        self.label.Content = "Select a category to filter:"
        self.panel.Children.Add(self.label)

        # Add a ComboBox for categories
        self.category_combo = ComboBox()
        self.category_combo.ItemsSource = get_categories()
        self.category_combo.Margin = Thickness(0, 2, 0, 2)
        self.category_combo.Height = 30
        self.panel.Children.Add(self.category_combo)

        # Add a button to filter and select elements
        self.filter_button = Button()
        self.filter_button.Content = "Execute Numbering With Filter"
        self.filter_button.Margin = Thickness(0, 10, 0, 10)
        self.filter_button.Height = 40
        self.filter_button.Click += self.on_filter_button_click
        self.panel.Children.Add(self.filter_button)

    def run_tool(self, sender, args):
        self.Close()
        grid_based_numbering(None)

    def on_filter_button_click(self, sender, args):
        selected_category_name = self.category_combo.SelectedItem
        if not selected_category_name:
            MessageBox.Show("Please select a category.", "Category Selector")
            return

        self.Close()
        # selected_category = get_builtin_category_from_string(selected_category_name)
        # print(selected_category_name)
        # print(selected_category)
        # category_filters = [ElementCategoryFilter(selected_category.Id)]
        #
        # combined_filter = LogicalOrFilter(category_filters)

        # selection_filter = FilteredElementCollector(doc).WherePasses(combined_filter).WhereElementIsNotElementType()
        selection_filter = CategorySelectionFilter(selected_category_name)

        grid_based_numbering(selection_filter)









# Register the button in the pyRevit ribbon
if __name__ == "__main__":
    window = GridBasedNumberingWindow()
    window.ShowDialog()

