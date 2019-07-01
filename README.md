# modules-info
parsing modules information 

xmodl         - parse /var/log/messages-* files and collect indfo about loaded modules
                save output in modules-* files
parseMod      - initial parser for  files created from /var/log/messages
getModInfo.py - parses a list of available modules and checks which ones
                use "logger" and what modules  they load
modGraph.py   - imports classes form getMOdInfo, builds  dependencty graphs
