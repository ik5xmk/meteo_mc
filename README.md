# meteo_mc
Sending Weather Messages on the Meshcom Network

This code allows sending weather messages on the APRS Meshcom network. For information on the project see here:
[MESHCOM](https://icssw.org/en/meshcom/)<br>

Edit the code by configuring your coordinates, the IP of the node/gateway connected to the meshcom network and the group (or callsign) to which to address the message. The " --extudp on " command must be activated on the node/gateway to enable the ability to manage external communications. See the project website for the use of the commands and any updates. Run the code manually to try sending the message, you can then schedule the operation from your server's cron service.<br>

![](https://github.com/ik5xmk/meteo_mc/blob/main/meteo_mc_01.jpg)<br>

Customize the message as you wish, including the detected values ​​that interest you. The information is acquired by [Open Meteo](https://open-meteo.com/)<br>

![](https://github.com/ik5xmk/meteo_mc/blob/main/meteo_mc_02.jpg)<br>

