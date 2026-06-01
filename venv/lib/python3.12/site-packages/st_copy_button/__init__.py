import os
import streamlit.components.v1 as components
import streamlit as st

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "st_copy_button",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_copy_button", path=build_dir)


def _validate_input(key: str):
    if key is None:
        raise ValueError("A unique key is required for st_copy_button.")


def _init_session_state(counter_key: str):
    if counter_key not in st.session_state:
        st.session_state[counter_key] = 0


def _process_component_output(component_raw_value, counter_key: str, status_key: str):
    if component_raw_value is not None:
        status = component_raw_value["status"]
        new_counter = component_raw_value["counter"]
        if new_counter == st.session_state[counter_key] + 1:
            st.session_state[status_key] = status
            st.session_state[counter_key] = new_counter
            st.rerun()

    if status_key in st.session_state:
        status = st.session_state[status_key]
        del st.session_state[status_key]
        return status
    else:
        return None


def st_copy_button(
    text: str,
    before_copy_label: str = "📋",
    after_copy_label: str = "✅",
    show_text: bool = False,
    key: str = "key",
):
    """Create a button that copies text to the user's clipboard when
    clicked.

    Parameters
    ----------
    text: str
        The text to be copied to the clipboard.
    before_copy_label: str
        The button label before copying occurs. Defaults to "📋".
    after_copy_label: str
        The button label after copying occurs. Defaults to "✅".
    show_text: bool
        If True, displays the text to be copied as a second, also
        clickable button, to the left of the first.
    key: str
        An optional key that uniquely identifies this component.

    Returns
    -------
    component_value: bool
        True if the button was clicked and the text successfully copied
        to the user's clipboard on this run of the app, false otherwise.
    """
    _validate_input(key)

    counter_key = f"st_copy_button_counter_{key}"
    status_key = f"st_copy_button_status_{key}"

    _init_session_state(counter_key)

    component_raw_value = _component_func(
        text=text,
        before_copy_label=before_copy_label,
        after_copy_label=after_copy_label,
        show_text=show_text,
        counter=st.session_state[counter_key],
        key=key,
    )

    component_return_value = _process_component_output(
        component_raw_value, counter_key, status_key
    )

    return component_return_value
