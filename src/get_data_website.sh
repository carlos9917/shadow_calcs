#Grab data from the website
today=`date +'%Y%m%d_%H%M%S'`
curl http://gimli.dmi.dk:8081/glatinfoservice/GlatInfoServlet?command=stationlist | iconv -f iso8859-1 -t utf-8 > station_data.csv
