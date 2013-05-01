pool-notification
=================

SMS Pool notification for Crytographic Currency Mining. 
Currently only supprts give-me-ltc.com - in addition, requires
amazon SNS service with a topic and subscription already created.

<b>Will send an SMS to your phone when a worker gets below a hashing threshold. </b>

Setup

1) Install submodules
git submodule update --init --recursive

2) Install boto
cd externals/boto
python setup.py install

3) Move config.fill to config.py and fill out values.

4) Setup cron to execute every 10 minutes
*/10 * * * * python /.../pool-notification/monitor.py
