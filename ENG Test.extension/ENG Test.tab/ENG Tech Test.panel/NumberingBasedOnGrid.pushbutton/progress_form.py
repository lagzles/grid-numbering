import clr
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")
from System.Windows import Window, WindowStartupLocation
from System.Windows.Controls import ProgressBar, TextBlock, StackPanel
from System.Windows import Thickness
from System.Windows.HorizontalAlignment import Center
from System.Windows.Threading import Dispatcher, DispatcherPriority

class ProgressBarWindow(Window):
    def __init__(self):
        self.Title = "Progresso da Tarefa"
        self.Width = 400
        self.Height = 200
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen

        self.panel = StackPanel()
        self.panel.Margin = Thickness(20)
        self.Content = self.panel

        self.label = TextBlock()
        self.label.Text = "Progresso:"
        self.label.Margin = Thickness(0, 0, 0, 10)
        self.label.HorizontalAlignment = Center
        self.panel.Children.Add(self.label)

        self.progress_bar = ProgressBar()
        self.progress_bar.Width = 320
        self.progress_bar.Height = 30
        self.progress_bar.Minimum = 0
        self.progress_bar.Maximum = 100
        self.progress_bar.Value = 0
        self.panel.Children.Add(self.progress_bar)

    def update_progress(self, value, item_i, item_max):
        self.label.Text = "Progress: {0} / {1}".format(item_i, item_max)

        self.Dispatcher.Invoke(lambda: self._update_ui(value), DispatcherPriority.Background)

    def _update_ui(self, value):
        self.progress_bar.Value = value
