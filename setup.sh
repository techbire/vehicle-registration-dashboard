mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"test@example.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = \$PORT\n\
fileWatcherType = \"none\"\n\
" > ~/.streamlit/config.toml
