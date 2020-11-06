# Python-Files-cleanup-gz
Python script to archive the files or logs in the .gz extension by running the tar command over the ssh connection on the remote servers. The script also provides the functionality to execute commands as a sudo user.

# Usage
Python script to archive the files or logs in the .gz extension by running the tar command over the shh connection on the remote servers. Only archiveing the files the script also deletes the archived files. The script creates the threads equal to number of servers provided in the configuration(fileDeleteSetting.cfg) file.

# Configuration Parameters 
`env = DEV`
- User can mention about the environment which machines belongs to.
`enabled = 1`
- On setting this parameter to 1, this block of
`ssh_machine = x.x.x.x,x.x.x.x`
- List Server Ip's or host name separated by comma(,) delimiter on which files needs to archived.
`ssh_username = user`
- Login credentials: User name
ssh_password = password
- Login credentials: Server password
`interval = 900`
- Commands on the remote servers will be executed on every interval 900 (seconds).
`directory =/home/user/tarFileLocation/filetest.tar.gz`
- List of directory files need to be archived , separated by comma(,) delimiter.
`sudo = 1`
- If the command needs to be executed as a sudo user, set to 1 or to 0.

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc

