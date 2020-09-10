# mkdir -p ~/.streamlit/
# echo "\
# [general]\n\
# email = \"silvio.lugaro@gmail.com\"\n\
# " > ~/.streamlit/credentials.toml
# echo "\
# [server]\n\
# headless = true\n\
# enableCORS=false\n\
# port = $PORT\n\

mkdir -p /root/.streamlit
bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'
bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'