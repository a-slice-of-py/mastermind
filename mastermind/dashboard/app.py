# pylint: disable=E1120
import streamlit as st
import itertools
import plotly.graph_objects as go
from mastermind.core.mastermind import MasterMind
from mastermind.dashboard.session_state import _get_state
from mastermind.dashboard.st_rerun import rerun
from textwrap import dedent
from typing import Callable

pink_st = '#f63366'
black_st = '#262730'
gray_st = '#f5f6f8'

@st.cache(allow_output_mutation=True)
def new_game(N_SLOTS: int, N_COLORS: int) -> MasterMind:
    """

    Args:
        N_SLOTS (int): length of code
        N_COLORS (int): number of distinct colors available

    Returns:
        MasterMind: mastermind game instance
    """
    return MasterMind(N_SLOTS=N_SLOTS, N_COLORS=N_COLORS)

@st.cache(allow_output_mutation=True)
def new_session() -> Callable:
    """Generate a new streamlit session (cached)

    Returns:
        Callable: state function
    """
    state = _get_state()
    state.name = ''
    state.code_submitted = False
    return state

def reset_game() -> None:
    """Reset game
    """
    st.caching.clear_cache()
    rerun()

@st.cache
def odds_gauge(value: float) -> go.Figure:
    """Implements a gauge to display winning chances on next turn

    Args:
        value (float): Winning odds

    Returns:
        go.Figure: Gauge charts
    """
    fig = go.Figure(
        go.Indicator(
            mode = "gauge+number",
            value = value,
            domain = dict(
                x=[0, 1],
                y=[0, 1]
                ),
            title = dict(text="Next turn winning odds", font=dict(size=16)),
            gauge=dict(axis=dict(range=[None, 100], tickcolor=black_st), bordercolor=black_st, bar=dict(color=pink_st)),
            number=dict(suffix='%')
            )
    )
    fig.update_layout(height=250, paper_bgcolor = gray_st, font = {'color': black_st})
    return fig

def main() -> None:
    """Implements streamlit app to play with MasterMind
    """
    st.sidebar.markdown('# MasterMind')
    wiki = 'ℹ️ [Game info](https://en.wikipedia.org/wiki/Mastermind_(board_game))'
    st.sidebar.markdown(wiki, unsafe_allow_html=True)
    session = new_session()
    reset = st.sidebar.button('Reset game')

    if reset:
        session.code_submitted = False
        reset_game()

    roles = {
        'code_breaker': {
            'emoji': '🙈',
            'rules': f"""
            Your aim is to guess the _secret code_ chosen by The CodeMaker (played here by the underlying game agent).<br><br>
            You can choose the _complexity_ of such code, both in terms of code length and number of available distinct colors,
            in the **Game options** menu _(remember, each color can appear in a given code more than once)_.<br><br>
            At each turn, you have to choose a guess code through the **Code selection** menu in the sidebar.<br>
            You will then receive an _hint_, in terms of black and white pegs, which abide the following legend:<br><br>
            ◼️ = right color and right location<br>
            ◻️ = right color but wrong location<br><br>
            _(remember, pegs locations aren't related with colors locations within the code!)_<br><br>
            You are now ready to submit new guesses, one after the other, following the obtained hints in order to crack the secret code!
            If your moves are coherent with the hints, you should see the _next turn winning odds_ increase in the gauge.
            """.strip()
            },
        'code_maker': {
            'emoji': '🙊',
            'rules': f"""
            Your aim is to choose the _secret code_ and play it against The CodeBreaker (played here by the underlying game agent).<br><br>
            You can choose the _complexity_ of such code, both in terms of code length and number of available distinct colors,
            in the **Game options** menu _(remember, each color can appear in a given code more than once)_.<br><br>
            First of all you have to submit the chosen secret code through the **Code selection** menu in the sidebar.<br>
            Then, at each turn you will have to choose the hint corresponding to the agent guess through the **Hint selection** menu,
            by chosing the right combination of black and white pegs
            which must abide the following legend:<br><br>
            ◼️ = right color and right location<br>
            ◻️ = right color but wrong location<br><br>
            _(remember, pegs locations aren't related with colors locations within the code!)_<br><br>
            You are now ready to submit new hints, one after the other, following the guesses received from the agent.
            If your hints are coherent with the guesses, you will see the _next turn winning odds_ increase in the gauge.
            """.strip()
            }
        }

    st.sidebar.markdown('## Game options')
    user_role = st.sidebar.radio(
        'You are playing as',
        sorted(roles),
        format_func=lambda x: f"{roles.get(x).get('emoji')} The {x.title().replace('_','')}",
        index=0
        )
    locations = st.sidebar.slider(
        'Code length',
        min_value=2,
        max_value=6,
        value=4,
        step=1,
        key='locations'
        )
    new_line = '<br><br>' if locations >= 5 else ''
    colors = st.sidebar.slider(
        'Number of colors',
        min_value=2,
        max_value=6,
        value=6,
        step=1,
        key='colors'
        )

    game = new_game(N_SLOTS=locations, N_COLORS=colors)

    st.markdown(f'''
    # {roles.get(user_role).get('emoji')} The {user_role.title().replace('_','')}
    {roles.get(user_role).get('rules')}
    ''', unsafe_allow_html=True)

    secret_code = st.sidebar.empty()
    secret_code.markdown(f"# Secret code: {''.join(game.N_SLOTS*[game.secret])}")
    winning_odds = st.sidebar.empty()
    winning_odds.plotly_chart(odds_gauge(100*game.calculate_win_odds()), use_container_width=True)

    empty_md = st.sidebar.empty()
    empty_hint = st.sidebar.empty()
    empty_submit = st.sidebar.empty()

    for log in game.history:
        st.markdown(log, unsafe_allow_html=True)

    if not session.code_submitted:
        st.sidebar.markdown('# Code selection')
        selection = [
            st.sidebar.selectbox(
                '',
                game.colors,
                key=f'c{k}'
                )
            for k in range(game.N_SLOTS)
            ]
        code = tuple(game.inv_dict.get(i) for c in selection for i in c)
        submit_code = st.sidebar.button('Submit code')
    else:
        code = game.user_code
        submit_code = False

    if user_role == 'code_breaker':
        if submit_code:
            game.user_guess(code)
            st.markdown(game.history[-1], unsafe_allow_html=True)
            game.memory = game.memory.union(
                    set(
                        filter(
                            lambda guess: game.get_hint(guess, versus=game.turns[-1]) != game.get_hint(code),
                            list(game.complement(game.memory))
                            )
                        )
                    )
            winning_odds.plotly_chart(odds_gauge(100*game.calculate_win_odds()), use_container_width=True)
            if game.success:
                st.balloons()
                secret_code.markdown(f"# Secret code: {new_line}{game.paint(game.secret_code)}", unsafe_allow_html=True)
                st.caching.clear_cache()

    elif user_role == 'code_maker':

        if submit_code:
            session.code_submitted = True
            game.user_code = code
            game.agent_guess()
            st.markdown(game.history[-1], unsafe_allow_html=True)

        if session.code_submitted:
            game.secret_code = code
            secret_code.markdown(f"# Secret code: {new_line}{game.paint(game.secret_code)}", unsafe_allow_html=True)
            empty_md.markdown('# Hint selection')
            hint = empty_hint.selectbox(
                'Select hint',
                game.possible_hints,
                format_func=lambda x: ''.join(x) if x else 'No match'
            )
            submit_hint = empty_submit.button('Submit hint')
            if submit_hint:

                if game.translate_hint(hint) == (locations, 0):
                    game.success = True

                if game.success:
                    st.balloons()
                    st.caching.clear_cache()
                else:
                    game.history[-1] += (
                        dedent(f'''
                        ## _Hint_: {''.join(hint)}
                        ---
                        ''')
                        )
                    game.memory = game.memory.union(
                    set(
                        filter(
                            lambda code: game.get_hint(code, versus=game.turns[-1]) != game.translate_hint(hint),
                            list(game.complement(game.memory))
                            )
                        )
                    )
                    try:
                        game.agent_guess()
                    except IndexError:
                        st.error("How dare you! _Hints are incoherent..._ Please reset game, I'm too confused to handle this!")
                    winning_odds.plotly_chart(odds_gauge(100*game.calculate_win_odds()), use_container_width=True)
                    st.markdown(game.history[-1], unsafe_allow_html=True)

    repo = '💻 [GitHub repo](https://github.com/a-slice-of-py/mastermind)'
    linkedin = '💼 [Linkedin profile](https://it.linkedin.com/in/silviolugaro)'
    contact = '✉️ <a href="mailto:silvio.lugaro@gmail.com">Contact me</a>'
    st.sidebar.markdown('---')
    st.sidebar.markdown(repo, unsafe_allow_html=True)
    st.sidebar.markdown(linkedin, unsafe_allow_html=True)
    st.sidebar.markdown(contact, unsafe_allow_html=True)

    session.sync()

if __name__ == '__main__':
    main()