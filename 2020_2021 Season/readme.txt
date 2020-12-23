as of dec 23 made a design decision: run the pregrame script to get opening odds. this will include games that will occur the next days (not just today). 
then run the live game script which will append to the already created files.

when i do analysis on the files, make sure to remove all csv files with less than say 10 lines as those will indicate the games that were only on the pregame list
but werent caught by the live scraper that day. (also represents faulty games where we lost data i guess)