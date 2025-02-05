# Grid-Based Numbering Tool for Revit (pyRevit)

## Overview

The Grid-Based Numbering Tool is a custom pyRevit add-in designed to streamline the numbering of elements in Revit models based on their position relative to grid intersections. It also assigns grid location parameters to selected elements, enhancing model organization and ensuring consistent data handling across projects.

## Features

Custom Tab and Button: Adds a new tab in pyRevit named "Grid Tools" with a button labeled "Grid-Based Numbering".

Automatic Parameter Creation: Verifies and creates "Grid Square" and "Number" parameters if they do not exist in the model.

User Interaction: Opens a form to allow users to select elements and define a starting element for sequential numbering.

Grid-Based Numbering: Assigns grid intersection names to elements in the format {Vertical Grid}-{Horizontal Grid}.

Sequential Numbering: Numbers elements based on their spatial proximity starting from a user-selected element.

## Installation

Install pyRevit:

Download the latest version of pyRevit from pyRevit GitHub.

Run the installer and follow the on-screen instructions.

Clone or Download this Repository:

Place the GridTools.extension folder into your pyRevit extensions directory (usually found at %APPDATA%\pyRevit\Extensions).

### Directory Structure:

ENG Test.extension/
├── ENG Test.tab/
├    ├── ENG Tech Test.panel/
├        ├── NumberingBasedOnGrid.pushbutton/
├            ├── script.py
├            ├── progress_form.py
├            ├── category_selection_filter.py
├            ├── icon.png
├            └── button.yaml
├──config.yaml

Configure Button Appearance (Optional):

Edit the button.yaml to customize the button name, description, and tooltip.

Example button.yaml:

title: Grid-Based Numbering
tooltip: Automatically number elements based on their grid position.
description: This tool assigns grid locations and sequential numbers to selected elements.

## Usage

Launch Revit and Open a Model.

Navigate to the "Grid Tools" Tab and click on "Grid-Based Numbering".

Select Elements: A form will open, allowing you to select elements to be modified.

Define Starting Element: Choose the first element for sequential numbering directly in the Revit model.

Run the Tool: The script will assign grid locations and numbers to the selected elements.

## Technical Details

### Compatibility

This tool is compatible with Revit versions 2019 to 2024.

### Parameters Created

Grid Square: Text parameter indicating the closest grid intersection (e.g., A-1).

Number: Sequential number assigned based on spatial proximity.

### Customization

Icons: Replace icon.png with your custom icon.

Form Customization: Modify the form in script.py for additional functionality.

## Troubleshooting

Error: "Shared parameter file not found."

Ensure you have a shared parameter file set up in Revit.

Elements Not Numbering Correctly:

Verify that the elements are properly aligned with grids and the parameters exist.

Script Not Appearing in pyRevit:

Ensure the GridTools.extension folder is in the correct pyRevit extensions directory.

## License

This project is open-source and available under the MIT License.

Acknowledgments

Developed with pyRevit API.

Special thanks to the Revit API community for continuous support and resources.

Contact

For questions, suggestions, or issues, please open an issue on the GitHub repository or contact leandro.arns@gmail.com
