# pylint: disable=E1120
try:
    from streamlit.script_request_queue import RerunData
    from streamlit.script_runner import RerunException
except ModuleNotFoundError:
    from streamlit.ScriptRequestQueue import RerunData
    from streamlit.ScriptRunner import RerunException

from mastermind.dashboard.session_state import _get_state

'''
Modified version of https://gist.github.com/goraj/47f4e365a13b11c4c0eba4f233acda76 to handle Streamlit >= 0.65.0.
'''

def rerun():
    """Rerun a Streamlit app from the top!"""
    widget_states = _get_widget_states()
    raise RerunException(RerunData(widget_states))


def _get_widget_states():
    return _get_state()._widget_states