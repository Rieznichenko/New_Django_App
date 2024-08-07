# myapp/forms.py
from django import forms
from .models import AanlyticsSchedule
from django.utils.safestring import mark_safe

class CodeMirrorWidget(forms.Textarea):
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/codemirror.min.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/codemirror.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/mode/python/python.min.js',
        )

    def render(self, name, value, attrs=None, renderer=None):
        # Render the default textarea
        textarea_html = super().render(name, value, attrs, renderer)

        # Add CodeMirror and Run button script
        script = f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                var editor = CodeMirror.fromTextArea(document.getElementById('id_{name}'), {{
                    lineNumbers: true,
                    mode: 'python',
                    theme: 'default',
                    matchBrackets: true,
                    autoCloseBrackets: true,
                    indentUnit: 4,
                    tabSize: 4,
                }});
                
                // Update the hidden textarea before form submission
                var form = document.querySelector('form');
                form.addEventListener('submit', function() {{
                    document.getElementById('id_{name}').value = editor.getValue();
                }});
            }});
        </script>
        """
        return mark_safe(textarea_html + script)


class AanlyticsScheduleAdminForm(forms.ModelForm):
    class Meta:
        model = AanlyticsSchedule
        fields = '__all__'
        widgets = {
            'embedded_code': CodeMirrorWidget(),
        }
