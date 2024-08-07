from RestrictedPython import compile_restricted
from RestrictedPython.Eval import default_guarded_getitem, default_guarded_getiter
import traceback


def execute_code(code):
    try:
        # Compile the code with restrictions
        byte_code = compile_restricted(code, '<string>', 'exec')

        # Define the environment
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                # Add other safe built-ins if needed
            },
            '_getattr_': getattr,
            '_getitem_': default_guarded_getitem,
            '_getiter_': default_guarded_getiter,
        }

        safe_locals = {}

        # Execute the code in a restricted environment
        exec(byte_code, safe_globals, safe_locals)

        # Return success message or any specific output
        result = safe_locals.get('output', 'Code executed successfully.')
        return result
    except Exception as e:
        # Handle and log exceptions
        return str(e) + "\n" + traceback.format_exc()

